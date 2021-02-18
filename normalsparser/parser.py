from typing import Any, Dict, List, Tuple, Union

FLAGS = {
    'C': 'complete (all 30 years used)',
    'S': """standard (no more than 5 years missing and no more than 3 consecutive \
        years missing among the sufficiently complete years)""",
    'R': """representative (observed record utilized incomplete, but value was scaled \
         or based on filled values to be representative of the full period of record)""",
    'P': """provisional (at least 10 years used, but not sufficiently complete to be labeled \
        as standard or representative). Also used for parameter values on  February 29 as well \
            as for interpolated daily precipitation, snowfall, and snow depth percentiles.  """,
    'Q': """quasi-normal (at least 2 years per month, but not sufficiently complete to be \
        labeled as provisional or any other higher flag code. The associated value was \
            computed using a pseudonormals approach or derived from monthly pseudonormals."""
}

        
class NormalsMeasure(object): 
    __slots__ = ('_scaling_factor', '_value')
    _flags = FLAGS
    _missing = {
        '-9999': (None, 'Missing'), 
        '-7777': (0.0, 'a non-zero value that would round to zero, for variables bound by zero.'),
        '-6666': (None, """parameter undefined; used in precipitation/snowfall/snow depth percentiles 
           when number of nonzero values is insufficient"""),
        '-5555':(None, 'parameter not available because it was inconsistent with another parameter'),
    }
    
    def __init__(self, scaling_factor: int=10) -> None:
        """Represents the numeric values parsed from a single line of text from a
        normalized weather file.

        Args:
            scaling_factor (int, optional): The number to divide by to produce a float. Defaults to 10.
        """
        self._scaling_factor = scaling_factor 
        self._value = None
    
    def set_value(self, value: str) -> "NormalsMeasure":
        """Set the value of the string representation from the file and return self.

        Returns:
            self: the instance
        """
        self._value = value  
        return self
    
    def schema(self) -> Dict[str, Union[str, float, None]]:
        """Create a schema from the measure which includes the value, flag and a description.

        Returns:
            Dict[str, Union[str, float]]: A dictionary of the schema
        """
        out = {}
        if self._value in self._missing:  # if missing there is no flag
            val, desc = self._missing[self._value]
            out['value'] = val
            out['desc'] = desc 
        else:
            val = self._value[:-1]
            flag = self._value[-1:]
            out['value'] = float(val) / self._scaling_factor 
            out['flag'] = flag
            out['desc'] = self._flags[flag]
        return out



class NormalsRecord(object): 
    __slots__ = ('_identifier', '_month', '_day', '_name', '_measures','_source','_unit')
    
    def __init__(self, 
                 identifier: str, 
                 month: str, 
                 day: str, 
                 measures: List[NormalsMeasure],
                 name: str='hly-temp-normal',
                 unit: str='degrees_F',
                 source: str='ftp://ftp.ncdc.noaa.gov/pub/data/normals/1981-2010/') -> None:
        """[summary]

        Args:
            identifier (str): A usaf identifier 
            month (int): The month
            day (int): The day
            measures (List[NormalsMeasure]): A List of measures
            name (str, optional): The name of the file. 
                Defaults to 'hly-temp-normal'.
            unit (str, optional): Unit of measure. Defaults to 'degrees_F'.
            source (str, optional): ftp source folder default. 
                Defaults to 'ftp://ftp.ncdc.noaa.gov/pub/data/normals/1981-2010/'.
        """
        if len(measures) != 24:
            raise ValueError(f'Length of measures must be 24. Got {len(measures)}')

        self._identifier = identifier 
        self._month = month 
        self._day = day 
        self._measures = measures 
        self._name = name 
        self._unit = unit
        self._source = source

        
    def schema(self) -> Dict[str, Union[str, int, List[NormalsMeasure]]]:
        """Returns the schema of the individual record from a list of measures and metadata.

        Returns:
            Dict[str, Union[str, int, List[NormalsMeasure]]]: Dictionary of the parsed line data.
        """
        return {
            'identifier': self._identifier, 
            'month': int(self._month),
            'day': int(self._day),
            'name': self._name,
            'source': self._source,
            'unit': self._unit,
            'measurements': [m.schema() for m in self._measures]
        }


    
class NormalsRecordFactory(object):
    __slots__ = ('_name', '_scaling_factor', '_unit', '_source')
    
    def __init__(self,
                 name: str='hly-temp-normal',
                 source: str='ftp://ftp.ncdc.noaa.gov/pub/data/normals/1981-2010/', 
                 scaling_factor: int=10, 
                 unit: str='degrees_F') -> None:
        """A high level factory that creates the complete record from a single line of 
        text from a normalized weather file.

        Args:
            name (str, optional): The name of the file. Defaults to 'hly-temp-normal'.
            source (str, optional): The name of the source ftp folder. 
                Defaults to 'ftp://ftp.ncdc.noaa.gov/pub/data/normals/1981-2010/'.
            scaling_factor (int, optional): [description]. Defaults to 10.
            unit (str, optional): [description]. Defaults to 'degrees_F'.
        """
        self._name = name
        self._scaling_factor = scaling_factor 
        self._unit = unit
        self._source = source
    
    def create(self, line: List[str]) -> NormalsRecord:
        """Parses an array of text from a normalized weather file.

        Args:
            line (List[str]): A list of text values.

        Returns:
            NormalsRecord: An object that represents the line of text.
        """
        if len(line) != 27:
            raise ValueError(f"""Line should be exactly 27 values (id,mm,day + 24 measurements).\
                 Got {len(line)}... Line:{line}""")
        
        ident, month, day = line[:3]
        measures = [NormalsMeasure(self._scaling_factor).set_value(m) for m in  line[3:]]
        return NormalsRecord(ident, month, day, measures, self._name, self._unit, self._source)

    
class LineObjectFilter(object):
    __slot__ = ('_identifiers',)
    
    def __init__(self, identifiers: Tuple[str]) -> None:
        """Filters a list of lines from a normalized weather file. This is useful 
        convenience if you want to read the complete file into memory and then filter by multiple 
        station identifiers. This should be guaranteed to be the first 12 characters.

        Args:
            identifiers (Tuple[str]): A tuple of usaf identifiers used as a filter criteria.
        """
        self._identifiers = identifiers
    
    def filter(self, lines: str) -> List[str]:
        """Filters a list of line strings by the given key. Also assures that the strings 
        are formatted appropriately for NormalsRecordFactory.

        Returns:
            List[List[str]]: A list of lists of strings parsed from the lines
        """
        
        # note that his makes an assumption that id is always 10 chars.. i believe it is consistent
        # This call to filter speeds the whole thing up alot
        lines = list(filter(lambda line: line[:11] in self._identifiers, lines))
        return [[ item for item in l.replace('\n', '').split(' ') if item != ''] for l in lines]
        