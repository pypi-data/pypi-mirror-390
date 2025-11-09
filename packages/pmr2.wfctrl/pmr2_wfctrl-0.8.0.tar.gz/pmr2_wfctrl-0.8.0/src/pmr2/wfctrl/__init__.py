from importlib import metadata

try:
    __version__ = metadata.version('pmr2.wfctrl')
except metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
