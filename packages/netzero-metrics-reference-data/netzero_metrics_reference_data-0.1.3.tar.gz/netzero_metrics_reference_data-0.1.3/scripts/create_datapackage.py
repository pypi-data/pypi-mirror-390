import pathlib
from frictionless import Package, Resource
from frictionless import describe

# DIR_PKG = files("aecreference").joinpath("nzc")
# PTH_PKG = DIR_PKG.joinpath("datapackage.yaml")
# PTH_BUILDING_TYPES = DIR_PKG.joinpath("building-types.txt")
# PTH_EUI_DATA = DIR_PKG.joinpath("energy-use-intensity.csv")
# PTH_LCM_DATA = DIR_PKG.joinpath("life-cycle-modules.csv")
# PTH_RICS_V1 = DIR_PKG.joinpath("rics-building-element-category.csv")
# PTH_COLOR_ENERGY_END_USE = DIR_PKG.joinpath("color-energy-end-use.csv")
# PTH_COLOR_FUEL_TYPE = DIR_PKG.joinpath("color-fuel-type.csv")

DIR_PKG = pathlib.Path(__file__).parent.parent

PTH_PKG = DIR_PKG / "datapackage.yaml"
PTH_BUILDING_TYPES = DIR_PKG / "building-types.txt"
PTH_EUI_DATA = DIR_PKG / "energy-use-intensity.csv"
PTH_LCM_DATA = DIR_PKG / "life-cycle-modules.csv"
PTH_RICS_V1 = DIR_PKG / "rics-building-element-category.csv"
PTH_COLOR_ENERGY_END_USE = DIR_PKG / "color-energy-end-use.csv"
PTH_COLOR_FUEL_TYPE = DIR_PKG / "color-fuel-type.csv"

res_eui = Resource(
    path=PTH_EUI_DATA.name,
    name="energy-use-intensity",
    title="UK NZCBS Operational Energy Use intensity targets",
    schema=describe(PTH_EUI_DATA, type="schema"),
    sources=[
        {
            "UK Net Zero Carbon Building Standard Pilot Version (Sept 2024), TableOE-1 & TableOE-2": "https://www.nzcbuildings.co.uk/pilotversion"
        }
    ],
)

res_building_types = Resource(
    path=PTH_BUILDING_TYPES.name,
    name="building-types",
    title="UK NZCBS Operational Energy Use intensity targets - unique building types from TableOE-1 & TableOE-2",
    sources=[
        {
            "UK Net Zero Carbon Building Standard Pilot Version (Sept 2024), TableOE-1 & TableOE-2": "https://www.nzcbuildings.co.uk/pilotversion"
        }
    ],
)

res_life_cycle = Resource(
    path=PTH_LCM_DATA.name,
    name="life-cycle-modules",
    title="life cycle carbon stages",
    description="Modules of the life cycle carbon stages taken from BS EN 15643:2021",
    schema=describe(PTH_LCM_DATA, type="schema"),
    sources=[
        {
            "BS EN 15643:2021": "https://knowledge.bsigroup.com/products/sustainability-of-construction-works-framework-for-assessment-of-buildings-and-civil-engineering-works?version=standard"
        }
    ],
)

res_rics_v1 = Resource(
    path=PTH_RICS_V1.name,
    name="rics-building-element-category",
    title="RICS Building Element Categories for Life Cycle Carbon Assessment (v1)",
    description="for categorising the embodied carbon intensity of materials in a building by function",
    schema=describe(PTH_RICS_V1, type="schema"),
    # sources= TODO
)

energy_end_use_color_config = Resource(
    path=PTH_COLOR_ENERGY_END_USE.name,
    name="color-energy-end-use",
    title="Color configuration for energy end uses",
    description="Color configuration for energy end uses",
    schema=describe(PTH_COLOR_ENERGY_END_USE, type="schema"),
)

fuel_type_color_config = Resource(
    path=PTH_COLOR_FUEL_TYPE.name,
    name="color-fuel-type",
    title="Color configuration for fuel types",
    description="Color configuration for fuel types",
    schema=describe(PTH_COLOR_FUEL_TYPE, type="schema"),
)

description = """structured data to support setting targets and benchmarks
for the Carbon usage (operational and embodied), within buildings"""
pkg = Package(
    name="nzc-data",
    title="Net Zero Carbon Data",
    description="structured data to support setting ",
    resources=[
        res_eui,
        res_building_types,
        res_life_cycle,
        res_rics_v1,
        energy_end_use_color_config,
        fuel_type_color_config,
    ],
)  # from a descriptor


pkg.to_yaml(PTH_PKG)  # Save as YAML
print("Created frictionless data package at", PTH_PKG)
