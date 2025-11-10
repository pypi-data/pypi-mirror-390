"""
Note, tests expect to be run from the ndc-wearables root directory
"""


import numpy as np
from datetime import datetime
import pytz
from pynwb import NWBFile, NWBHDF5IO
from pynwb.base import TimeSeries
from pynwb.file import ProcessingModule
from pathlib import Path
import pytest

from hdmf.common.table import VectorData
from ndx_events import NdxEventsNWBFile, MeaningsTable, CategoricalVectorData
from ndx_wearables import WearableDevice, WearableTimeSeries, WearableEvents, WearableEnumSeries, PhysiologicalMeasure
from ndx_wearables.categorical_enums import build_sleep_phase_meanings

def add_wearable_physiological_measure(nwbfile, device):
    # generate fake wearables data
    timestamps = np.arange(0.0, 3600.0, 30.0)
    np.random.seed(0)
    wearable_values = np.random.random(size=(120,2))

    modality = PhysiologicalMeasure(
        name="TestMeasure",
    )

    # Build out a meanings table to use in the events file
    ts = WearableTimeSeries(
        name=f"TestTimeseries1",
        data=wearable_values,
        timestamps=timestamps,
        description="test",
        unit="unit",
        wearable_device=device,
        algorithm='placeholder'
    )
    # add wearables objects to processing module
    nwbfile.processing["wearables"].add([modality])
    added_ts = modality.add_wearable_time_series(ts)

    # generate fake wearables data
    timestamps = np.arange(0.0, 3600.0, 30.0)
    np.random.seed(0)
    wearable_values = np.random.random(size=(120,2))

    # Build out a meanings table to use in the events file
    ts2 = WearableTimeSeries(
        name=f"TestTimeseries2",
        data=wearable_values,
        timestamps=timestamps,
        description="test2",
        unit="unit",
        wearable_device=device,
        algorithm='placeholder'
    )

    added_ts2 = modality.add_wearable_time_series(ts2)
    return nwbfile

def add_wearable_enumseries(nwbfile, device):
    # generate fake wearables data
    expected_labels = np.array(["awake", "n1", "n2", "n2", "n3", "rem", "awake"])
    np.random.seed(0)
    expected_timestamps = np.arange(expected_labels.size, dtype=float)
    meanings = build_sleep_phase_meanings()
    nwbfile.processing["wearables"].add(meanings)

    # create wearable timeseries
    series = WearableEnumSeries(
        name="test_enum_series",
        data=expected_labels,              # labels map to codes internally
        timestamps=expected_timestamps,
        description="test sleep stage labels over time",
        wearable_device=device,
        algorithm="test_algorithm",
        meanings=meanings,
    )

    # add wearables objects to processing module
    nwbfile.processing["wearables"].add(series)
    return nwbfile

def add_wearable_timeseries(nwbfile, device):
    # generate fake wearables data
    timestamps = np.arange(0.0, 3600.0, 30.0)
    np.random.seed(0)
    wearable_values = np.random.random(size=(120, 2))

    # create wearable timeseries
    ts = WearableTimeSeries(
        name="test_wearable_timeseries",
        data=wearable_values,
        timestamps=timestamps,
        unit='tests/s',
        wearable_device=device,
        algorithm='test_algorithm',
    )

    # add wearables objects to processing module
    nwbfile.processing["wearables"].add(ts)
    return nwbfile

def add_wearable_events(nwbfile, device):
    # Build out a meanings table to use in the events file
    test_meanings = MeaningsTable(name="test_meanings", description="test")
    test_meanings.add_row(value='a', meaning="first value entered")
    test_meanings.add_row(value='b', meaning="second value entered")
    cat_column = CategoricalVectorData(name='cat_column', description='test categories description',
                                       meanings=test_meanings)
    text_column = VectorData(
        name='text_column',
        description='test columns description',
    )

    events = WearableEvents(
        name="test_wearable_events",
        description=f"test events collected from {device.name}",
        wearable_device=device,
        columns=[cat_column, text_column],
        meanings_tables=[test_meanings],
        algorithm='test_algorithm',
    )
    events.add_row(timestamp=10.0, cat_column="a", text_column="first row text")
    events.add_row(timestamp=30.0, cat_column="b", text_column="second row text")
    events.add_row(timestamp=120.0, cat_column="a", text_column="third row text")

    nwbfile.processing["wearables"].add(events)
    return nwbfile

@pytest.fixture
def nwb_with_wearable_ts(wearables_nwbfile_device):
    nwbfile, device = wearables_nwbfile_device
    nwbfile = add_wearable_timeseries(nwbfile, device)
    return nwbfile

@pytest.fixture
def write_nwb_with_wearable_timeseries(tmp_path, nwb_with_wearable_ts):
    with NWBHDF5IO(tmp_path, 'w') as io:
        io.write(nwb_with_wearable_ts)

    return tmp_path

@pytest.fixture
def nwb_with_wearable_events(wearables_nwbfile_device):
    nwbfile, device = wearables_nwbfile_device
    nwbfile = add_wearable_events(nwbfile, device)
    return nwbfile


@pytest.fixture
def write_nwb_with_wearable_events(tmp_path, nwb_with_wearable_events):
    with NWBHDF5IO(tmp_path, 'w') as io:
        io.write(nwb_with_wearable_events)

    return tmp_path

@pytest.fixture
def nwb_with_wearable_enum(wearables_nwbfile_device):
    nwbfile, device = wearables_nwbfile_device
    nwbfile = add_wearable_enumseries(nwbfile, device)
    return nwbfile

@pytest.fixture
def nwb_with_physiological_measure(wearables_nwbfile_device):
    nwbfile, device = wearables_nwbfile_device
    nwbfile = add_wearable_physiological_measure(nwbfile, device)
    return nwbfile

@pytest.fixture
def write_nwb_with_wearable_enum(tmp_path, nwb_with_wearable_enum):
    with NWBHDF5IO(tmp_path, 'w') as io:
        io.write(nwb_with_wearable_enum)

    return tmp_path

@pytest.fixture
def write_nwb_with_physiological_measure(tmp_path, nwb_with_physiological_measure):
    with NWBHDF5IO(tmp_path, 'w') as io:
        io.write(nwb_with_physiological_measure)

    return tmp_path


def test_wearables_timeseries(write_nwb_with_wearable_timeseries):
    expected_timestamps = np.arange(0.0, 3600.0, 30.0)
    np.random.seed(0)
    expected_wearable_values = np.random.random(size=(120,2))

    with NWBHDF5IO(write_nwb_with_wearable_timeseries, 'r') as io:
        nwbfile = io.read()

        # ensure processing module is in the file
        assert 'wearables' in nwbfile.processing, 'Wearables processing module is missing.'
        wearables_module = nwbfile.processing["wearables"]

        # ensure wearable timeseries is in file
        assert 'test_wearable_timeseries' in wearables_module.data_interfaces, "Wearable timeseries data not present in processing module"
        # ensure data is correct
        wearable_timeseries = wearables_module.get('test_wearable_timeseries')
        # validate shape
        assert wearable_timeseries.data.shape == expected_wearable_values.shape, "Incorrect wearables timeseries data shape"
        assert wearable_timeseries.timestamps.shape == expected_timestamps.shape, "Incorrect timestamp shape"
        # validate data values
        np.testing.assert_array_equal(wearable_timeseries.data[:], expected_wearable_values, "Mismatch in wearable timeseries values")
        np.testing.assert_array_equal(wearable_timeseries.timestamps[:], expected_timestamps, "Mismatch in timestamps")
        
        # validate metadata
        assert 'test_wearable_device' in nwbfile.devices, "Wearable device is missing"

        # ensure wearabletimeseries has link to wearabledevice
        assert wearable_timeseries.wearable_device is nwbfile.devices['test_wearable_device']

# Testing WearableEvents based on EventsRecord inheritance
def test_wearable_events(write_nwb_with_wearable_events):

    with NWBHDF5IO(write_nwb_with_wearable_events, 'r') as io:
        nwbfile = io.read()

        assert 'wearables' in nwbfile.processing, "Wearables processing module is missing"
        wearables = nwbfile.processing["wearables"]

        assert 'test_wearable_events' in wearables.data_interfaces.keys(), 'Missing wearable events data!'
        events = wearables.get('test_wearable_events')

        workout_event = events.get(slice(None)) # get all events
        np.testing.assert_array_equal(workout_event.timestamp[:], [10.0, 30.0, 120.0])
        assert events.wearable_device.name == "test_wearable_device"

def test_enum_timeseries(write_nwb_with_wearable_enum):
    expected_labels = np.array(["awake", "n1", "n2", "n2", "n3", "rem", "awake"])
    np.random.seed(0)
    expected_timestamps = np.arange(expected_labels.size, dtype=float)

    with NWBHDF5IO(write_nwb_with_wearable_enum, 'r') as io:
        nwbfile = io.read()

        # ensure processing module is in the file
        assert 'wearables' in nwbfile.processing, 'Wearables processing module is missing.'
        wearables_module = nwbfile.processing["wearables"]

        # ensure wearable timeseries is in file
        assert 'test_enum_series' in wearables_module.data_interfaces, "Wearable enum eries data not present in processing module"
        # ensure data is correct
        wearable_timeseries = wearables_module.get('test_enum_series')
        # validate shape
        assert wearable_timeseries.data.shape == expected_labels.shape, "Incorrect wearables enum data shape"
        assert wearable_timeseries.timestamps.shape == expected_timestamps.shape, "Incorrect timestamp shape"
        # validate data values
        np.testing.assert_array_equal(wearable_timeseries.data[:], expected_labels, "Mismatch in wearable enum values")
        np.testing.assert_array_equal(wearable_timeseries.timestamps[:], expected_timestamps, "Mismatch in timestamps")
        
        # validate metadata
        assert 'test_wearable_device' in nwbfile.devices, "Wearable device is missing"

        # ensure wearabletimeseries has link to wearabledevice
        assert wearable_timeseries.wearable_device is nwbfile.devices['test_wearable_device']


def test_physiological_measure(write_nwb_with_physiological_measure):
    expected_timestamps1 = np.arange(0.0, 3600.0, 30.0)
    np.random.seed(0)
    expected_wearable_values1 = np.random.random(size=(120,2))

    expected_timestamps2 = np.arange(0.0, 3600.0, 30.0)
    np.random.seed(0)
    expected_wearable_values2 = np.random.random(size=(120,2))

    with NWBHDF5IO(write_nwb_with_physiological_measure, 'r') as io:
        nwbfile = io.read()
        assert 'wearables' in nwbfile.processing, 'Wearables processing module is missing.'
        pm = nwbfile.processing["wearables"]
        s = pm.get("TestMeasure")

        for example_data in s.wearable_time_series:
            if s.wearable_time_series[example_data].name == 'TestTimeseries1':
                assert s.wearable_time_series[example_data].data.shape == expected_wearable_values1.shape, "Incorrect wearables enum data shape for series 1"
                assert s.wearable_time_series[example_data].timestamps.shape == expected_timestamps1.shape, "Incorrect timestamp shape for series 1"
                np.testing.assert_array_equal(s.wearable_time_series[example_data].data, expected_wearable_values1, "Mismatch in values for series 1")
                np.testing.assert_array_equal(s.wearable_time_series[example_data].timestamps, expected_timestamps1, "Mismatch in timestamps for series 1")
        
            if s.wearable_time_series[example_data].name == 'TestTimeseries2':
                assert s.wearable_time_series[example_data].data.shape == expected_wearable_values2.shape, "Incorrect wearables enum data shape for series 2"
                assert s.wearable_time_series[example_data].timestamps.shape == expected_timestamps2.shape, "Incorrect timestamp shape for series 2"
                np.testing.assert_array_equal(s.wearable_time_series[example_data].data, expected_wearable_values2, "Mismatch in values for series 2")
                np.testing.assert_array_equal(s.wearable_time_series[example_data].timestamps, expected_timestamps2, "Mismatch in timestamps for series 2")
        
        # validate metadata
        assert 'test_wearable_device' in nwbfile.devices, "Wearable device is missing"
