from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("genexpressor")
except PackageNotFoundError:
    # package isn't installed (e.g., running from source without build)
    __version__ = "0+unknown"
