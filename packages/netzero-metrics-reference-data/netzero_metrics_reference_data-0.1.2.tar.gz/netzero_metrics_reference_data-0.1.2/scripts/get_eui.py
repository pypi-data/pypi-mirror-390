import pandas as pd
import pathlib
import casefy

CWD = pathlib.Path(__file__).parent.parent
PTH_EUI_IN = CWD / "scripts" / "energy-use-intensity.xlsx"
DIR_OUT = CWD
PTH_EUI = DIR_OUT / "energy-use-intensity.csv"
PTH_BUILDING_TYPES = DIR_OUT / "building-types.txt"


def get_sheet_data(PTH, sheet_name):
    construction_deleivery_type = sheet_name
    meta = pd.read_excel(PTH, sheet_name=sheet_name, nrows=2)
    meta = (
        meta.set_index("building-type-shorthand")
        .T.reset_index(drop=False)
        .rename(columns={"year": "building-type", "index": "building-type-shorthand"})
    )
    col_index_w_gia = [0] + [
        n + 1 for n, x in enumerate(meta.unit) if "GIA" in x
    ]  # +1 as yr is first column
    data = pd.read_excel(PTH, sheet_name=sheet_name, skiprows=2)
    data = data.iloc[:, col_index_w_gia]
    if not data.columns.is_unique:
        msg = "There must only be one row per building type. Duplicates implies multiple metrics of the same unit for a building type."
        raise ValueError(msg)
    data = pd.melt(
        data, id_vars="year", var_name="building-type", value_name="benchmark-target"
    )

    data = data.join(meta.set_index("building-type"), on="building-type")
    data["construction-delivery-type"] = construction_deleivery_type
    cols = [
        "building-type",
        "building-type-shorthand",
        "unit",
        "construction-delivery-type",
    ]
    for x in cols:
        data[x] = data[x].str.strip()

    for x in [" (GIA)", " (NIA)"]:
        data["building-type"] = data["building-type"].str.replace(x, "")

    li = [" ".join(x.split("-")) for x in data.columns]
    data.columns = [casefy.pascalcase(casefy.snakecase(x)) for x in li]
    return data


def get_eui_data():
    sheet_names = ["newbuild", "retrofit-in-one-go", "retrofit-stepped"]
    return pd.concat(
        [get_sheet_data(PTH_EUI_IN, sheet_name=s) for s in sheet_names], axis=0
    )


def get_building_types(df_eui):
    return list(df_eui["BuildingType"].unique())


df_eui = get_eui_data()
df_eui.to_csv(PTH_EUI, index=False)

PTH_BUILDING_TYPES.write_text("\n".join(get_building_types(df_eui)))
