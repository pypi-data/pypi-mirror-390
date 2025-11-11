# NetZero Metrics Reference Data

This repository provides reference data and resources for NetZero metrics calculations.

The data is provided as a [datapackage](https://datapackage.org/) directly from the root of this repo.
This can be accessed using datapackage tools, for example using [frictionless-py](https://github.com/frictionlessdata/frictionless-py) package:

```python
from frictionless import Package

package = Package("https://github.com/maxfordham/netzero-metrics-reference-data")
```

It has also been packaged as a Python package to enable easy, version-controlled offline usage, which can be installed via pip:

```bash
pip install netzero-metrics-reference-data
```

**Usage**

```python
import netzero_metrics_reference_data as nz_data

data = nz_data.load_datapackage()
```

> [!NOTE]
> The data in the root of the repo is active and up-to-date. The data in the src directory is overwritten by the root data when the package is built.
