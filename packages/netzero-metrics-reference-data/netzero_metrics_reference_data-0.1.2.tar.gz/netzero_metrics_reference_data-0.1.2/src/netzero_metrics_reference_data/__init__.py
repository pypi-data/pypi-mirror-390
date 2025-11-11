from importlib.resources import files
from frictionless import Package

PTH_PKG = (
    files("netzero_metrics_reference_data")
    .joinpath("data")
    .joinpath("datapackage.yaml")
)
nzm_pkg = Package(PTH_PKG)

__all__ = ["nzm_pkg"]
