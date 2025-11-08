from functools import lru_cache

try:
    from importlib_metadata import PackageNotFoundError, version
except ImportError:
    from importlib.metadata import PackageNotFoundError, version


@lru_cache
def user_agent(name=__package__):
    if "." in name:
        name = name.split(".")[0]
    try:
        v = version(distribution_name=name)
    except PackageNotFoundError:
        v = "unknown"

    return f"{name}/{v}"


DEFAULT_USER_AGENT = user_agent(__package__)


def set_default_user_agent(value):
    global DEFAULT_USER_AGENT
    DEFAULT_USER_AGENT = value
