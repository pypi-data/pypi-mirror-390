"""
Run: python examples/test_heart_rate_extension.py
Creates an NWB file with HeartRateSeries and verifies a roundtrip (write → read).
"""

import numpy as np
from datetime import datetime
from pynwb import NWBFile, NWBHDF5IO
from pynwb.file import ProcessingModule
from ndx_wearables import WearableDevice, WearableTimeSeries

def main():
    # 1) Create NWB container
    nwbfile = NWBFile(
        session_description="Wearables HeartRate example",
        identifier="HR-001",
        session_start_time=datetime.now()
    )

    # 2) Add device + processing module
    device = WearableDevice(
        name="wearable_device",
        manufacturer="ExampleCo",
        description="Example wearable",
        location="wrist"
    )
    nwbfile.add_device(device)

    wearables = ProcessingModule(name="wearables", description="Wearables derived data")
    nwbfile.add_processing_module(wearables)

    # 3) Generate synthetic heart-rate data (every 5s for 1h)
    timestamps = np.arange(0.0, 3600.0, 5.0)   # 720 samples
    np.random.seed(42)
    heart_rate_values = np.random.uniform(low=60, high=100, size=timestamps.size)

    # 4) Create series and add to module
    series = WearableTimeSeries(
        name="Heart Rate Data",
        data=heart_rate_values,
        unit="bpm",
        timestamps=timestamps,
        description="Example Heart Rate data",
        wearable_device=device,
        algorithm="simulated data"
    )
    wearables.add(series)

    # 5) Write file
    out_path = "heart_rate_example.nwb"
    with NWBHDF5IO(out_path, "w") as io:
        io.write(nwbfile)
    print(f"Wrote: {out_path}")

    # 6) Read back (roundtrip) and summarize
    with NWBHDF5IO(out_path, "r") as io:
        read_nwb = io.read()
        pm = read_nwb.processing["wearables"]
        s = pm.get("Heart Rate Data")
        print("Series:", s.name)
        print("Samples:", len(s.data[:]))
        print("First 5 bpm:", s.data[:5])
        print("Timestamps length:", len(s.timestamps[:]))

if __name__ == "__main__":
    main()
