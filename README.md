## normalsparser 
----------------

[![CI](https://github.com/bsnacks000/normalsparser/actions/workflows/CI.yaml/badge.svg)](https://github.com/bsnacks000/normalsparser/actions/workflows/CI.yaml)

A small library that parses hourly normalized wheaher data files found in `ftp://ftp.ncdc.noaa.gov/pub/data/normals/1981-2010/products/hourly/`. 

Turns this:
```
AQW00061705 01 01   804P   803C   801C   799C   797C   797C   796C   808C   833C   844C   850C   856C   858C   857C   857C   854C   849C   843C   835C   824C   817C   813C   809C   808C
```

Into this:
```python 
{'identifier': 'AQW00061705',
  'month': 1,
  'day': 1,
  'name': 'hly-temp-normal',
  'source': 'ftp://ftp.ncdc.noaa.gov/pub/data/normals/1981-2010/',
  'unit': 'degrees_F',
  'measurements': [{'value': 80.4,
    'flag': 'P',
    'desc': 'provisional (at least 10 years used, but not sufficiently complete to be labeled as standard or representative). Also used for parameter values on February 29 as well as for interpolated daily precipitation, snowfall, and snow depth percentiles.'},
   {'value': 80.3, 'flag': 'C', 'desc': 'complete (all 30 years used)'},
   {'value': 80.1, 'flag': 'C', 'desc': 'complete (all 30 years used)'},
   {'value': 79.9, 'flag': 'C', 'desc': 'complete (all 30 years used)'},
   {'value': 79.7, 'flag': 'C', 'desc': 'complete (all 30 years used)'},
   {'value': 79.7, 'flag': 'C', 'desc': 'complete (all 30 years used)'},
   {'value': 79.6, 'flag': 'C', 'desc': 'complete (all 30 years used)'},
   {'value': 80.8, 'flag': 'C', 'desc': 'complete (all 30 years used)'},
   {'value': 83.3, 'flag': 'C', 'desc': 'complete (all 30 years used)'},
   {'value': 84.4, 'flag': 'C', 'desc': 'complete (all 30 years used)'},
   {'value': 85.0, 'flag': 'C', 'desc': 'complete (all 30 years used)'},
   {'value': 85.6, 'flag': 'C', 'desc': 'complete (all 30 years used)'},
   {'value': 85.8, 'flag': 'C', 'desc': 'complete (all 30 years used)'},
   {'value': 85.7, 'flag': 'C', 'desc': 'complete (all 30 years used)'},
   {'value': 85.7, 'flag': 'C', 'desc': 'complete (all 30 years used)'},
   {'value': 85.4, 'flag': 'C', 'desc': 'complete (all 30 years used)'},
   {'value': 84.9, 'flag': 'C', 'desc': 'complete (all 30 years used)'},
   {'value': 84.3, 'flag': 'C', 'desc': 'complete (all 30 years used)'},
   {'value': 83.5, 'flag': 'C', 'desc': 'complete (all 30 years used)'},
   {'value': 82.4, 'flag': 'C', 'desc': 'complete (all 30 years used)'},
   {'value': 81.7, 'flag': 'C', 'desc': 'complete (all 30 years used)'},
   {'value': 81.3, 'flag': 'C', 'desc': 'complete (all 30 years used)'},
   {'value': 80.9, 'flag': 'C', 'desc': 'complete (all 30 years used)'},
   {'value': 80.8, 'flag': 'C', 'desc': 'complete (all 30 years used)'}]}
```

This has a similar API and usage as its sister library ![isdparser](https://github.com/bsnacks000/isdparser) which deals specifically with isd files from the same ftp server. 

## Notes 

This should be able to handle any of the `/normals/` data found in the ftp directory. 

I've included the readme file associated with the directory which contains notes as to how the data was collected and was where I derived the descriptions for the various flags.

### Install 

For now install from here with pip. The master branch will contain the most up to date version.   
```
pip install git+https://github.com/bsnacks000/isdparser.git
```
or a specific version 
```
pip install git+https://github.com/bsnacks000/isdparser.git@v0.1.0
```

### Usage 

The API is almost identical to `isdparser` except that here the strings are well formed and we are able to pass in arrays of determined lengths.  

```python

with open('hly-temp-normal.txt', 'r') as f:
  lines = f.readlines()

# optionally filter the file by identifier (the first 10 chars)
filtered = LineObjectFilter(key='AQW00061705').filter(lines)

# process into records
records = [HourlyNormalsRecordFactory().create(line) for line in filtered.values()]

# pull the schemas
data = [r.schema() for r in records]

# do things...
```