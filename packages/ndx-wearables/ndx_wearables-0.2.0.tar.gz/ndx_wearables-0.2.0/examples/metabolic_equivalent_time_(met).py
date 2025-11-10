"""
Run: python examples/test_met_extension.py
Creates an NWB file with MetSeries and verifies a roundtrip (write → read).
"""

import numpy as np
from datetime import datetime
from pynwb import NWBFile, NWBHDF5IO
from pynwb.device import Device
from pynwb.file import ProcessingModule
from ndx_wearables import WearableDevice, WearableTimeSeries

def main():
    # 1) Create the NWB container
    nwbfile = NWBFile(
        session_description="Wearables MET example",
        identifier="MET-001",
        session_start_time=datetime.now()
    )

    # 2) Add a device and processing module
    device = WearableDevice(
        name="wearable_device",
        manufacturer="ExampleCo",
        description="Example wearable",
        location="wrist"
    )
    nwbfile.add_device(device)

    wearables = ProcessingModule(
        name="wearables",
        description="Wearables derived data"
    )
    nwbfile.add_processing_module(wearables)

    # 3) Generate synthetic MET data (every 30s for 1 hour)
    timestamps = np.arange(0.0, 3600.0, 30.0)
    np.random.seed(42)
    met_values = np.random.uniform(1.0, 10.0, size=timestamps.size)

    # 4) Create MetSeries and add to the processing module
    series = WearableTimeSeries(
        name="Met Data",
        data=met_values,
        unit="MET",
        timestamps=timestamps,
        description="Example metabolic equivalent values",
        wearable_device=device,
        algorithm="test_algorithm"
    )
    wearables.add(series)

    # 5) Write to disk
    out_path = "met_example.nwb"
    with NWBHDF5IO(out_path, "w") as io:
        io.write(nwbfile)
    print(f"Wrote: {out_path}")

    # 6) Read back (roundtrip) and print a summary
    with NWBHDF5IO(out_path, "r") as io:
        read_nwb = io.read()
        pm = read_nwb.processing["wearables"]
        s = pm.get("Met Data")
        print("Series:", s.name)
        print("Samples:", len(s.data[:]))
        print("First 5 values:", s.data[:5])
        print("Timestamps length:", len(s.timestamps[:]))

if __name__ == "__main__":
    main()