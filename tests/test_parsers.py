import unittest 
tc = unittest.TestCase()
import pytest

from normalsparser.parser import LineObjectFilter, NormalsMeasure, NormalsRecord, NormalsRecordFactory


def test_normalsmeasure():

    m = NormalsMeasure()

    m.set_value('100C')

    expected= {
        'value': 10.0, 
        'flag': 'C', 
        'desc': 'complete (all 30 years used)'
    }
    tc.assertDictEqual(expected, m.schema())

    m.set_value('-9999')

    expected['value'] = None 
    expected['desc'] = 'Missing'
    expected.pop('flag')

    tc.assertDictEqual(expected, m.schema())


    m.set_value('-7777')
    assert m.schema()['value'] == 0

    m.set_value('-7777C')
    assert m.schema()['value'] == 0



def test_normals_record(mocker):

    mocker.patch.object(NormalsMeasure, 'schema', return_value='some-data')

    # check that we give the exact number of things
    with pytest.raises(ValueError):
        NormalsRecord('id', '01', '01', measures=[i for i in range(23)])

    with pytest.raises(ValueError):
        NormalsRecord('id', '01', '01', measures=[i for i in range(25)])

    measures = [NormalsMeasure() for _ in range(24)]

    record = NormalsRecord('id', '01', '01', measures)

    expected = {
        'identifier': 'id', 
        'month': 1, 
        'day': 1, 
        'measurements': ['some-data' for _ in range(24)], 
        'unit': 'degrees_F',
        'name': 'hly-temp-normal', 
        'source': 'ftp://ftp.ncdc.noaa.gov/pub/data/normals/1981-2010/'
    }

    tc.assertDictEqual(expected, record.schema())


def test_normalsrecordfactory(normalized_temp_string):

    with pytest.raises(ValueError):
        NormalsRecordFactory().create([])

    line_arr = [l for l in normalized_temp_string.replace('\n', '').split(' ') if l != '']

    record = NormalsRecordFactory().create(line_arr).schema()

    assert record['identifier'] == 'AQW00061705'
    assert record['month'] == 1 
    assert record['day'] == 1 
    assert record['name'] == 'hly-temp-normal'
    assert record['source'] == 'ftp://ftp.ncdc.noaa.gov/pub/data/normals/1981-2010/' 
    assert len(record['measurements']) == 24
    
    

def test_lineobjectfilter(): 

    f = LineObjectFilter(identifiers=('AQW00061705', 'BQW00061705'))
    test = [
        'AQW00061705 01 01    420C', 
        'BQW00061705 01 01    420C', 
        'CCCCCCCCCCC 01 01    420C', 
        'DDDDDDDDDDD 01 01    420C'
    ]

    lines = f.filter(test)

    expected = [
        ['AQW00061705', '01', '01', '420C'], 
        ['BQW00061705', '01', '01', '420C'],
    ]

    assert lines == expected