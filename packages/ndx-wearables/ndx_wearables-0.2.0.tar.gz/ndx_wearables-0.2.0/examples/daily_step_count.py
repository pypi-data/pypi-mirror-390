
import numpy as np
from datetime import datetime
import pytz
from pynwb import NWBFile, NWBHDF5IO
from pynwb.file import ProcessingModule
from ndx_wearables import WearableDevice, WearableTimeSeries

def main():
    # 1) Create NWB container
    nwbfile = NWBFile(
        session_description="Wearables StepCount example",
        identifier="STEP-001",
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

    wearables = ProcessingModule(name="wearables", description="Wearables derived data")
    nwbfile.add_processing_module(wearables)

    # 3) Generate synthetic step-count data (every 30s for 1h)
    timestamps = np.arange(0.0, 3600.0, 30.0)  # 120 samples
    np.random.seed(42)
    stepcount_values = np.floor(np.random.uniform(low=0, high=200, size=timestamps.size))

    # 4) Create series and add to processing module
    series = WearableTimeSeries(
        name="StepCount Data",
        data=stepcount_values,
        unit="steps",
        timestamps=timestamps,
        description="Example step count values",
        wearable_device=device,
        algorithm="test_algorithm",
    )
    wearables.add(series)

    # 5) Write to disk
    out_path = "stepcount_example.nwb"
    with NWBHDF5IO(out_path, "w") as io:
        io.write(nwbfile)
    print(f"Wrote: {out_path}")

    # 6) Read back (roundtrip) and summarize
    with NWBHDF5IO(out_path, "r") as io:
        read_nwb = io.read()
        pm = read_nwb.processing["wearables"]
        s = pm.get("StepCount Data")
        print("Series:", s.name)
        print("Samples:", len(s.data[:]))
        print("First 5 step counts:", s.data[:5])
        print("Timestamps length:", len(s.timestamps[:]))

if __name__ == "__main__":
    main()