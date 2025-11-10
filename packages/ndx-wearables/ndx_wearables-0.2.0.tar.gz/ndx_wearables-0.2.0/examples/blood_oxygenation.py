
import numpy as np
from datetime import datetime
import pytz
from pynwb import NWBFile, NWBHDF5IO
from pynwb.file import ProcessingModule
from ndx_wearables import WearableDevice, WearableTimeSeries


def main():
    # 1) Create an NWBFile container
    nwbfile = NWBFile(
        session_description="Wearables BloodOxygen example",
        identifier="SPO2-001",
        session_start_time=datetime.now()
    )

    # 2) Add a device and a wearables processing module
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

    # 3) Generate synthetic SpO2 data (every 30s for 1 hour)
    timestamps = np.arange(0.0, 3600.0, 30.0)
    np.random.seed(42)
    blood_oxygen_values = np.random.uniform(low=90, high=100, size=timestamps.size)

    # 4) Create the series and add it to the processing module
    series = WearableTimeSeries(
        name="BloodOxygen Data",
        data=blood_oxygen_values,
        unit="percent",
        timestamps=timestamps,
        description="Example blood oxygen data",
        wearable_device=device,
        algorithm="proprietary Company algorithm v3"
    )
    wearables.add(series)

    # 5) Write to disk
    out_path = "blood_oxygen_example.nwb"
    with NWBHDF5IO(out_path, "w") as io:
        io.write(nwbfile)
    print(f"Wrote: {out_path}")

    # 6) Read back (roundtrip) and print a quick summary
    with NWBHDF5IO(out_path, "r") as io:
        read_nwb = io.read()
        pm = read_nwb.processing["wearables"]
        s = pm.get("BloodOxygen Data")
        print("Series:", s.name)
        print("Length:", len(s.data[:]))
        print("First 5 values:", s.data[:5])
        print("Timestamps length:", len(s.timestamps[:]))

if __name__ == "__main__":
    main()
