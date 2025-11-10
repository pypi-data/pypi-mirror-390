import pvlib
from typing import Annotated
import pandas as pd
import numpy as np
from ...modeling.decorators import standard_resource_type
from ...modeling import R
from ...modeling.basics import LambdaArgument
from ...modeling import ModelContext
from ..design import (
    ArrayDesign,
    FixedStructureDesign,
    TrackerStructureDesign,
    StructureDesign,
    ModuleDesign,
    ModuleOrientation,
)


@standard_resource_type(R.collector_shading_fraction, override_unit=True)  # TODO rename to collector_shaded_fraction ??
def pvlib_shaded_fraction1d(
    context: ModelContext,
    solar_zenith: Annotated[pd.Series, R.solar_zenith_angle],
    solar_azimuth: Annotated[pd.Series, R.solar_azimuth_angle],
    collector_width: Annotated[
        float, LambdaArgument(ArrayDesign, lambda d: d.collector_width)
    ],  # TODO move to StructureDesign
    pitch: Annotated[float, LambdaArgument(ArrayDesign, lambda d: d.pitch)],
    structure: StructureDesign,
) -> pd.Series:
    if isinstance(structure, FixedStructureDesign):
        axis_azimuth = structure.azimuth + 90
        surface_rotation_angle = structure.tilt
    elif isinstance(structure, TrackerStructureDesign):
        axis_azimuth = structure.axis_azimuth
        surface_rotation_angle = context.resource(R.tracker_rotation_angle)

    shaded_fraction: pd.Series = pvlib.shading.shaded_fraction1d(
        solar_zenith=solar_zenith,
        solar_azimuth=solar_azimuth,
        axis_azimuth=axis_azimuth,
        shaded_row_rotation=surface_rotation_angle,
        shading_row_rotation=surface_rotation_angle,
        collector_width=collector_width,
        pitch=pitch,
        axis_tilt=0,  # TODO: add to design, already part of TrackerStructureDesign, but not FixedStructureDesign
        surface_to_axis_offset=0,  # TODO: add to design
        cross_axis_slope=0,  # TODO: add to design
    )
    shaded_fraction[shaded_fraction < 0.01] = 0  # remove very small values belos 1%
    return shaded_fraction


@standard_resource_type(R.shading_loss_factor, override_unit=True)
def pvradar_shading_loss_factor(
    shaded_fraction: Annotated[pd.Series, R.collector_shading_fraction],
    module_orientation: Annotated[ModuleOrientation, LambdaArgument(ArrayDesign, lambda d: d.module_orientation)],
    num_mod_cross_section: Annotated[int, LambdaArgument(ArrayDesign, lambda d: d.number_modules_cross_section)],
    cell_string_count: Annotated[int, LambdaArgument(ModuleDesign, lambda d: d.cell_string_count)],
    is_half_cell: Annotated[bool, LambdaArgument(ModuleDesign, lambda d: d.half_cell)],
) -> pd.Series:
    if module_orientation == 'horizontal':
        total_blocks = cell_string_count * num_mod_cross_section
    else:
        if is_half_cell:
            # half cell: module separated in two parts along long side
            total_blocks = num_mod_cross_section * 2
        else:
            total_blocks = num_mod_cross_section
    shaded_blocks = np.ceil(total_blocks * shaded_fraction)
    shading_loss_fraction = pd.Series(shaded_blocks / total_blocks, index=shaded_fraction.index)
    return shading_loss_fraction
