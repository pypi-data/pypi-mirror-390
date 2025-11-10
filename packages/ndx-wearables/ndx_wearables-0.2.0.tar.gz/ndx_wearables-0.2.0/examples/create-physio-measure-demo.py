
import numpy as np
from datetime import datetime
import pytz
from pynwb import NWBHDF5IO
from pynwb.file import ProcessingModule
from pathlib import Path
from ndx_events import NdxEventsNWBFile

from ndx_wearables import WearableDevice, WearableTimeSeries, WearableEvents, PhysiologicalMeasure


nwbfile = NdxEventsNWBFile(
    session_description="Example wearables study session",
    identifier='TEST_WEARABLES',
    session_start_time=datetime.now(pytz.timezone('America/Chicago')),
)

# generate fake wearables data
timestamps = np.arange(0.0, 3600.0, 30.0)
np.random.seed(0)
wearable_values = np.random.random(size=(120, 2))

# create processing module
wearables = ProcessingModule(
    name="wearables",
    description="Wearables data",
)

modality = PhysiologicalMeasure(
    name="TestMeasure",
)

# create wearables device
device = WearableDevice(name="TestDevice", description="test", location="arm", manufacturer="test")
nwbfile.add_device(device)

# Build out a meanings table to use in the events file
ts = WearableTimeSeries(
    name=f"{device.name}_TestTimeseries",
    data=wearable_values,
    timestamps=timestamps,
    description="test",
    unit="unit",
    wearable_device=device,
    algorithm='placeholder'
)

nwbfile.add_processing_module(wearables)

wearables.add([modality])

added_ts = modality.add_wearable_time_series(ts)

# create second wearables device
device = WearableDevice(name="TestDevice2", description="second_test", location="leg", manufacturer="test2")
nwbfile.add_device(device)

# generate fake wearables data
timestamps = np.arange(0.0, 3600.0, 30.0)
np.random.seed(0)
wearable_values = np.random.random(size=(120, 2))

# Build out a meanings table to use in the events file
ts2 = WearableTimeSeries(
    name=f"{device.name}_TestTimeseries",
    data=wearable_values,
    timestamps=timestamps,
    description="test2",
    unit="unit",
    wearable_device=device,
    algorithm='placeholder'
)

added_ts2 = modality.add_wearable_time_series(ts2)

# add wearables objects to processing module
file_path = "physio_measure_demo.nwb"
with NWBHDF5IO(file_path, 'w') as io:
    io.write(nwbfile)

#Print a quick summary
with NWBHDF5IO(file_path, "r") as io:
    read_nwb = io.read()
    pm = read_nwb.processing["wearables"]
    s = pm.get("TestMeasure")
    print("Physiological Measure Examples:")
    count = 0
    for example_data in s.wearable_time_series:
        print(f"Physiological Series {count}")
        print("Series:", s.wearable_time_series[example_data].name)
        print("Length:", len(s.wearable_time_series[example_data].data[:]))
        print("First 5 values:", s.wearable_time_series[example_data].data[:5])
        print("Timestamps length:", len(s.wearable_time_series[example_data].timestamps[:]))
        print("Device Name:", s.wearable_time_series[example_data].wearable_device.name)
        count = count + 1