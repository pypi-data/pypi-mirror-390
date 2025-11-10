"""
Run: python examples/test_met_extension.py
Creates an NWB file with MetSeries and verifies a roundtrip (write → read).
"""

import numpy as np
import pandas as pd
from datetime import datetime
from pynwb import NWBFile, NWBHDF5IO
from hdmf.common.table import VectorData
from ndx_events import DurationVectorData
from pynwb.file import ProcessingModule
from ndx_wearables import WearableDevice, WearableEvents



def main():
    # 1) Create the NWB container
    nwbfile = NWBFile(
        session_description="Wearables Sleep Epochs example",
        identifier="SE-001",
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

    # 3) Generate some synthetic sleep intervals
    fake_sleep_intervals = pd.DataFrame.from_dict({
        'start_times': [13.0, 20.0, 44.0, 52.0],      # Entered here in hours, needs to be converted to seconds
        'durations': [1.2, 8.0, 7.3, 2.1],    # Entered here in hours, needs to be converted to seconds
        'classified_types': ['nap', 'long_rest', 'long_rest', 'nap'],
        'time_in_bed': [1.2, 8.5, 9.2, 2.4]   # Entered here in hours, needs to be converted to seconds
    })

    # 4) Create the SleepEpochs table, including custom columns and add to the processing module
    duration = DurationVectorData(
        name="duration",
        description="The duration, in seconds, of the sleep epoch"
    )
    sleep_type = VectorData(
        name='sleep_type',
        description='Type of sleep this was categorized as',
    )
    time_in_bed = VectorData(
        name='time_in_bed',
        description='Total time (in seconds) in bed (more than just sleeping)',
    )
    sleep_epochs = WearableEvents(
        name='SleepEpochs',
        description=f"Sleep epochs collected from {device.name}",
        wearable_device=device,
        columns=[duration, sleep_type, time_in_bed],
        algorithm='proprietary algorithm',
    )
    for row_data in fake_sleep_intervals.itertuples():
        sleep_epochs.add_row(
            timestamp=row_data.start_times*3600,     # converting to seconds since start of file,
            duration=row_data.durations*3600,         # Converting hours to seconds
            sleep_type=row_data.classified_types,
            time_in_bed=row_data.time_in_bed*3600,
        )

    wearables.add(sleep_epochs)

    # 5) Write to disk
    out_path = "sleep_epoch_example.nwb"
    with NWBHDF5IO(out_path, "w") as io:
        io.write(nwbfile)
    print(f"Wrote: {out_path}")

    # 6) Read back (roundtrip) and print a summary
    with NWBHDF5IO(out_path, "r") as io:
        n_rows = 4
        read_nwb = io.read()
        pm = read_nwb.processing["wearables"]
        s_df = pm.get("SleepEpochs").to_dataframe()
        print(f'Loaded the following sleep epochs from NWB:')
        print(s_df.head())
        print(f'Showing the first {n_rows} (out of {len(s_df)}) rows')

if __name__ == "__main__":
    main()
