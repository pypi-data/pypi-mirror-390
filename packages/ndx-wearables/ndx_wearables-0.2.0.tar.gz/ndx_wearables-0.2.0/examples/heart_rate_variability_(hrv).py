
import numpy as np
from datetime import datetime
import pytz
from pynwb import NWBFile, NWBHDF5IO
from pynwb.file import ProcessingModule
from ndx_wearables import WearableDevice, WearableTimeSeries

def main():
    # 1) Create NWB container
    nwbfile = NWBFile(
        session_description="Wearables HRV example",
        identifier="HRV-001",
        session_start_time=datetime.now()
    )

    # 2) Add device and processing module
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

    # 3) Generate synthetic HRV data (every 30s for 1h)
    timestamps = np.arange(0.0, 3600.0, 30.0)
    np.random.seed(42)
    hrv_values = np.random.uniform(low=60, high=100, size=timestamps.size)

    # 4) Create the HRVSeries and add it to the processing module
    series = WearableTimeSeries(
        name="HRV Data",
        data=hrv_values,
        unit="bpm",
        timestamps=timestamps,
        description="Example HRV data",
        wearable_device=device,
        algorithm="test_algorithm"
    )
    wearables.add(series)

    # 5) Write to disk
    out_path = "hrv_example.nwb"
    with NWBHDF5IO(out_path, "w") as io:
        io.write(nwbfile)
    print(f"Wrote: {out_path}")

    # 6) Read back (roundtrip) and print summary
    with NWBHDF5IO(out_path, "r") as io:
        read_nwb = io.read()
        pm = read_nwb.processing["wearables"]
        s = pm.get("HRV Data")
        print("Series:", s.name)
        print("Samples:", len(s.data[:]))
        print("First 5 values:", s.data[:5])
        print("Timestamps length:", len(s.timestamps[:]))

if __name__ == "__main__":
    main()