<h1 align="center">arrakis-python</h1>

<p align="center">Arrakis Python client library</p>

<p align="center">
  <a href="https://git.ligo.org/ngdd/arrakis-python/-/pipelines/latest">
    <img alt="ci" src="https://git.ligo.org/ngdd/arrakis-python/badges/main/pipeline.svg" />
  </a>
  <a href="https://git.ligo.org/ngdd/arrakis-python/-/pipelines/latest">
    <img alt="ci" src="https://git.ligo.org/ngdd/arrakis-python/badges/main/coverage.svg" />
  </a>
  <a href="https://ngdd.docs.ligo.org/arrakis-python/">
    <img alt="documentation" src="https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat" />
  </a>
  <a href="https://pypi.org/project/arrakis/">
    <img alt="pypi version" src="https://img.shields.io/pypi/v/arrakis.svg" />
  </a>
  <a href="https://anaconda.org/conda-forge/arrakis-python">
    <img alt="conda version" src="https://img.shields.io/conda/vn/conda-forge/arrakis-python.svg" />
  </a>
</p>

---

## Resources

* [Documentation](https://docs.ligo.org/ngdd/arrakis-python)
* [Source Code](https://git.ligo.org/ngdd/arrakis-python)
* [Issue Tracker](https://git.ligo.org/ngdd/arrakis-python/-/issues)

## Installation

With `pip`:

```
pip install arrakis
```

With `conda`:

```
conda install -c conda-forge arrakis-python
```

## Features

* Query live and historical timeseries data
* Describe channel metadata
* Search for channels matching a set of conditions
* Publish timeseries data

## Quickstart

### Fetch timeseries

``` python
import arrakis

start = 1187000000
end = 1187001000
channels = [
    "H1:CAL-DELTAL_EXTERNAL_DQ",
    "H1:LSC-POP_A_LF_OUT_DQ",
]

block = arrakis.fetch(channels, start, end)
for channel, series in block.items():
    print(channel, series)
```

where `block` is a [arrakis.block.SeriesBlock][] and `series` is a
[arrakis.block.Series][].

### Stream timeseries

##### 1. Live data

``` python
import arrakis

channels = [
    "H1:CAL-DELTAL_EXTERNAL_DQ",
    "H1:LSC-POP_A_LF_OUT_DQ",
]

for block in arrakis.stream(channels):
	print(block)
```

##### 2. Historical data

``` python
import arrakis

start = 1187000000
end = 1187001000
channels = [
    "H1:CAL-DELTAL_EXTERNAL_DQ",
    "H1:LSC-POP_A_LF_OUT_DQ",
]

for block in arrakis.stream(channels, start, end):
    print(block)
```

### Describe metadata

``` python
import arrakis

channels = [
    "H1:CAL-DELTAL_EXTERNAL_DQ",
    "H1:LSC-POP_A_LF_OUT_DQ",
]

metadata = arrakis.describe(channels)
```

where `metadata` is a dictionary mapping channel names to
[arrakis.channel.Channel][].

### Find channels

``` python
import arrakis

for channel in arrakis.find("H1:LSC-*"):
    print(channel)
```

where `channel` is a [arrakis.channel.Channel][].

### Count channels

``` python
import arrakis

count = arrakis.count("H1:LSC-*")
```

### Publish timeseries

``` python
from arrakis import Channel, Publisher, SeriesBlock, Time
import numpy

# admin-assigned ID
publisher_id = "my_producer"

# define channel metadata
metadata = {
    "H1:FKE-TEST_CHANNEL1": Channel(
        "H1:FKE-TEST_CHANNEL1",
        data_type=numpy.float64,
        sample_rate=64,
    ),
    "H1:FKE-TEST_CHANNEL2": Channel(
        "H1:FKE-TEST_CHANNEL2",
        data_type=numpy.int32,
        sample_rate=32,
    ),
}

publisher = Publisher(publisher_id)
publisher.register()

with publisher:
    # create block to publish
    series = {
        "H1:FKE-TEST_CHANNEL1": numpy.array([0.1, 0.2, 0.3, 0.4], dtype=numpy.float64),
        "H1:FKE-TEST_CHANNEL2": numpy.array([1, 2], dtype=numpy.int32),
    }
    block = SeriesBlock(
        1234567890 * Time.SECONDS,  # time in nanoseconds for first sample
        series,                     # the data to publish
        metadata,                   # the channel metadata
    )

    # publish timeseries
    publisher.publish(block)
```
