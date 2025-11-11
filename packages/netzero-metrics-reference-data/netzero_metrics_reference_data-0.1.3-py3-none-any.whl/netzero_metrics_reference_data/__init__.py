from importlib.resources import files
from frictionless import Package

PTH_PKG = (
    files("netzero_metrics_reference_data")
    .joinpath("data")
    .joinpath("datapackage.yaml")
)


def load_datapackage() -> Package:
    return Package(PTH_PKG)
