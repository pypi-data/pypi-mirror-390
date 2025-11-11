# nasrparse

nasrparse is a parser for the National Airspace System Resources CSV files,
released every 28 days by the FAA. It allows pilots, dispatchers, and others
interested in flight data to quickly parse the files into Python dictionaries
or a SQLite database for use in other programs. For example, the parsed data
can then be used as a database for flight planning tools.

If you are interested in seeing the differences between each data cycle, have
a look at [NASRDiff](https://github.com/misterrodg/NASRDiff).

## Versions

| Version | Description                    | Release Date |
| ------- | ------------------------------ | ------------ |
| 1.0.1   | `__repr()__` Bugfix for enums. | 2025-11-06   |
| 1.0.0   | Initial public release.        | 2025-11-06   |

A changelog is available in the [CHANGELOG.md](./CHANGELOG.md) with additional detail and guidance.

## Installation

Install using `pip`:

```
pip install nasrparse
```

## Usage

Usage is relatively straightforward. Setting the path to the files can be
somewhat finnicky, as it will only accept relative paths. To keep things simple,
place the NASR files in subdirectory of your project directory. Otherwise, if
you want to go up several folders into a download folder, it might end up
looking like `../../../../Downloads/28DaySubscription_Effective_[date]/CSV_Data/[date]_CSV`.

Given the amount of data, parsing can take a moment. If dumping the data to a
file, that can also add time. Dumping every airport to JSON can take around
10 seconds, and the result file is about 16MB.

### Examples

Start by importing `nasrparse`, setting the path to the NASR CSV directory, and
then parsing the data.

```python
import nasrparse

# Initialize the parser:
from nasrparse import NASR

# Set the relative path to where you have the NASR CSV files:
n = NASR("./data/CSV_DATA/20_MAR_2025_CSV")

# Parse the data in the file:
n.parse()
```

#### Exporting Data

##### Database

Each object has its own `to_db()` method. This is useful when you would like
the data to persist, or query it using standard database methods:

```python
from nasrparse import NASR

n = NASR("./data/CSV_DATA/20_MAR_2025_CSV")
n.parse()
n.to_db("NASR.db")
```

### NASR Objects

The individual NASR objects are exposed in the package and include the FAA
descriptions in the code documentation. More detail can also be found in the
individual `[section] DATA LAYOUT.pdf` (e.g. `APT DATA LAYOUT.pdf`) files
included with the CSV files in the same directory.

![Code Documentation](./docs/images/code_doc.png)
