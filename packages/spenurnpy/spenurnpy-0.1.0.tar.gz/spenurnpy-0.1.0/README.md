# nurnpy

A Python educational library for data preprocessing, clustering, and classical ML algorithms (Apriori, DBSCAN, etc.).

## Installation

```bash
pip install nurnpy
```

## Example Usage

```python
from nurnpy import dbscan

data = [[1, 2], [2, 3], [8, 9]]
labels = dbscan(data, eps=2, min_pts=2)
print(labels)
```

## Author
Developed by **S P Ecialise Srinivasan**
