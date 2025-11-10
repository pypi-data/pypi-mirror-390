
import numpy as np
from datetime import datetime
import pytz
from pynwb import NWBFile, NWBHDF5IO
import pandas as pd
from pynwb.file import ProcessingModule
from hdmf.common.table import VectorData
from ndx_events import DurationVectorData
from ndx_wearables import WearableDevice, WearableTimeSeries, WearableEnumSeries, WearableEvents, PhysiologicalMeasure
from ndx_wearables.categorical_enums import build_sleep_phase_meanings
from pynwb.file import Subject

def main():

    now = datetime.now(pytz.timezone('America/new_york'))
    subjectid = f'synthetic-pre-release-0-2'

    nwb = NWBFile("NDX Wearables Example", "pre-release-0-2_2025-11", now)

    subj = Subject(
        age='P0D',
        description='Nonexistent subject for a synthetic data example',
        subject_id=subjectid,
        species='Homo sapiens',
        sex='O'
    )
    nwb.subject = subj

    #Two example devices
    deviceRing = WearableDevice(
        name="ExampleRing",
        manufacturer="Examplon LLC",
        description="Example device to demonstrate how data is stored by NDX-Wearables",
        location='Right ring finger'
    )
    nwb.add_device(deviceRing)
    deviceWatch = WearableDevice(
        name="ExampleWatch",
        manufacturer="Test Industries Inc",
        description="Example device to demonstrate how data is stored by NDX-Wearables",
        location='Left wrist'
    )
    nwb.add_device(deviceWatch)

    #Example Sleep Data for Wearables Enum
    wearables = ProcessingModule(name="wearables", description="Wearables derived data")
    nwb.add_processing_module(wearables)

    meanings = build_sleep_phase_meanings()
    wearables.add(meanings)

    labels = np.array(["awake", "n1", "n2", "n2", "n3", "rem", "awake"])
    timestamps = np.arange(labels.size, dtype=float)
    
    series = WearableEnumSeries(
        name="sleep_phase",
        data=labels,              # labels map to codes internally
        timestamps=timestamps,
        description=f"Toy sleep stage labels over time from {deviceWatch.name}",
        wearable_device=deviceWatch,
        algorithm="sleep_stager_v1",
        meanings=meanings,
    )
    wearables.add(series)
    
    # Example Heart Rate Wearables Time Series- Generate synthetic heart-rate data (every 5s for 1h)
    timestamps = np.arange(0.0, 3600.0, 5.0)   # 720 samples
    np.random.seed(42)
    heart_rate_values = np.random.uniform(low=60, high=100, size=timestamps.size)

    #Create series and add to module
    series = WearableTimeSeries(
        name="Heart Rate Data",
        data=heart_rate_values,
        unit="bpm",
        timestamps=timestamps,
        description=f"Example Heart Rate data from {deviceRing.name}",
        wearable_device=deviceRing,
        algorithm="simulated data"
    )
    wearables.add(series)

    # Example Physiological Measures
    timestamps = np.arange(0.0, 3600.0, 30.0)
    np.random.seed(0)
    wearable_values = np.random.random(size=(120, 2))

    modality = PhysiologicalMeasure(
        name="TestMeasure",
    )

    # Build out a meanings table to use in the events file
    ts = WearableTimeSeries(
        name=f"{deviceWatch.name}_TestTimeseries",
        data=wearable_values,
        timestamps=timestamps,
        description="test",
        unit="unit",
        wearable_device=deviceWatch,
        algorithm='placeholder'
    )

    wearables.add([modality])

    added_ts = modality.add_wearable_time_series(ts)

    # generate fake wearables data
    timestamps = np.arange(0.0, 3600.0, 30.0)
    np.random.seed(0)
    wearable_values = np.random.random(size=(120, 2))

    # Build out a meanings table to use in the events file
    ts2 = WearableTimeSeries(
        name=f"{deviceRing.name}_TestTimeseries",
        data=wearable_values,
        timestamps=timestamps,
        description="test2",
        unit="unit",
        wearable_device=deviceRing,
        algorithm='placeholder'
    )

    added_ts2 = modality.add_wearable_time_series(ts2)

    out_path = "pre-release-0-2_2025-11.nwb"
    with NWBHDF5IO(out_path, "w") as io:
        io.write(nwb)
    print("Wrote:", out_path)

if __name__ == "__main__":
    main()