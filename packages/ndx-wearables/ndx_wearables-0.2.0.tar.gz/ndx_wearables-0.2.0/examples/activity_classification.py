import numpy as np
from datetime import datetime
from pynwb import NWBFile, NWBHDF5IO
from pynwb.device import Device
from pynwb.file import ProcessingModule
from ndx_wearables import WearableEnumSeries, WearableDevice
from ndx_wearables.categorical_enums import build_activity_class_meanings

def main():
    nwb = NWBFile("Wearables ActivityClass example", "ACT-001", datetime.now())

    device = WearableDevice(
        name="wearable_device",
        manufacturer="ExampleCo",
        description="Example wearable",
        location="Wrist"
    )
    nwb.add_device(device)

    wearables = ProcessingModule(name="wearables", description="Wearables derived data")
    nwb.add_processing_module(wearables)

    # categorical labels every 30s for 1h
    timestamps = np.arange(0.0, 3600.0, 30.0)
    np.random.seed(42)
    labels = np.array(["sitting", "walking", "running"])
    data = np.tile(labels, 40)[:timestamps.size]

    meanings = build_activity_class_meanings()
    wearables.add(meanings)

    series = WearableEnumSeries(
        name="ActivityClass Data",
        data=data,
        timestamps=timestamps,
        description="Example activity classification labels",
        wearable_device=device,
        meanings=meanings,
        algorithm="model_v1",
    )
    wearables.add(series)

    out_path = "activity_class_example.nwb"
    with NWBHDF5IO(out_path, "w") as io:
        io.write(nwb)
    print("Wrote:", out_path)

    with NWBHDF5IO(out_path, "r") as io:
        read = io.read()
        s = read.processing["wearables"].get("ActivityClass Data")
        print("Series:", s.name)
        print("Samples:", len(s.data[:]))
        print("First 5 labels:", s.data[:5])
        # If your base exposes categories/meanings, this will show the vocabulary:
        print("Categories:", getattr(s, "categories", None))

if __name__ == "__main__":
    main()