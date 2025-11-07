# ekgtools

Utilities for working with multi-format ECG waveforms in research and production settings.

## Features
- Unified parser interface for Philips iECG, GE MUSE, ELI, WFDB, and MIMIC records.
- Centralised configuration with per-call overrides for filter settings and signal scaling.
- `ECGDataset` that reads from local storage or S3/MinIO buckets with transparent caching.
- Plotting helpers for rapid visual inspection of 12-lead rhythms.

## Installation

```bash
pip install ekgtools
```

Python 3.10+ is required. Install the appropriate PyTorch/TorchVision wheels for your platform separately if needed.

## Quick Start

### Parse an ECG file

```python
from ekgtools.parser import ECGParser

parser = ECGParser(
    path="/data/ecg/philips_001.xml",
    config_overrides={
        "bandpass_lower": 1.0,
        "bandpass_higher": 40.0,
        "median_filter_size": 3,
    },
)

ecg = parser.float_array        # (12, n_samples)
metadata = parser.text_data     # demographics & machine measurements
```

### Local datasets for PyTorch

```python
import pandas as pd
from torch.utils.data import DataLoader

from ekgtools.dataset import ECGDataset

df = pd.read_csv("/data/labels.csv")

dataset = ECGDataset(
    directory="/data/ecg",
    df=df,
    filename_column="filename",
    label_column="label",
    specify_leads=["I", "II", "V1", "V2", "V3", "V4", "V5", "V6"],
    fast=True,
)

loader = DataLoader(dataset, batch_size=32, shuffle=True, num_workers=4)

signals, labels, complete = next(iter(loader))
```

### Stream from S3 with caching

```python
from ekgtools.dataset import ECGDataset
from ekgtools.s3 import S3Setup

s3 = S3Setup(
    bucket="ecg-data",
    prefix="records",
    endpoint_url="https://minio.example.com",
    access_key_id="ACCESS",
    secret_key="SECRET",
    region_name="us-east-1",
    use_ssl=True,
)

dataset = ECGDataset(
    directory="public/12lead",   # prefix under the bucket
    df=df,
    filename_column="filename",
    label_column="label",
    storage="s3",
    s3_setup=s3,
    cache_dir="~/.cache/ekgtools",
)
```

### Plotting helpers

```python
import numpy as np
from ekgtools.plot import plot

signals = np.random.randn(12, 5000)
fig = plot(signals, sample_rate=500)
fig.savefig("preview.png", dpi=200)
```

## Configuration

Default values live in `ekgtools/config.py` and can be overridden per parser invocation via `config_overrides`. To reuse overrides across multiple parsers:

```python
from ekgtools.config import resolve_config

custom_config = resolve_config(overrides={"bandpass_lower": 0.67})
parser = ECGParser(path, config=custom_config)
```

## Development

```bash
pip install -e .[dev]
pytest
```

## License

MIT
