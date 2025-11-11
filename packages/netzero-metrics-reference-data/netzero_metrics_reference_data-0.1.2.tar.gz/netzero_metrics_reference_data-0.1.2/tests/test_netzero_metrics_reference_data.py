from netzero_metrics_reference_data import nzm_pkg


def test_nzm_pkg():
    assert nzm_pkg is not None
    li = [
        "energy-use-intensity",
        "building-types",
        "life-cycle-modules",
        "rics-building-element-category",
        "color-energy-end-use",
        "color-fuel-type",
    ]
    assert nzm_pkg.resource_names == li

    print("done")
