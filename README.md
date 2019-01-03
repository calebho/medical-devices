# medical-devices
A library for querying medical device data from the FDA. Requires at least Python 3.7.
To install, `cd` into the repository root, then `pip install .`.

## Usage
This package consists of 3 modules, each of which is responsible for downloading
data from a single database. An example of usage is provided in 
`scripts/insert_mongo.py`. Currently the data is downloaded to a directory
`data/` sharing the root of its caller, e.g.
```
.
├── caller.py
└── data
    ├── 510k
    ├── gudid
    └── pma
```

## Development
To install packages for development, use the `environment.yaml` or `requirements.txt`, i.e.
```
conda env create -f environment.yml  # if you use Anaconda
pip install -r requirements.txt  # if you use pip
```

