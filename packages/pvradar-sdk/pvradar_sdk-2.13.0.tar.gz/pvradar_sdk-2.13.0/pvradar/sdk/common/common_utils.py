from functools import cache
import importlib.util
from geopy.geocoders import Nominatim


def check_package_installed(package_name: str) -> bool:
    return importlib.util.find_spec(package_name) is not None


@cache
def get_nominatim_client() -> Nominatim:
    return Nominatim(user_agent='pvradar-sdk')
