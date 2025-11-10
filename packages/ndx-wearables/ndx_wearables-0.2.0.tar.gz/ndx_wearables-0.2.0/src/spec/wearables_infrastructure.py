from networkx.utils.misc import groups
from pynwb.spec import NWBGroupSpec, NWBDatasetSpec, NWBNamespaceBuilder, NWBAttributeSpec, RefSpec, LinkSpec


def make_wearables_infrastructure():
    
    wearable_device = NWBGroupSpec(
        neurodata_type_def="WearableDevice",
        neurodata_type_inc="Device",
        doc="Wearable device from which data was recorded",
        quantity="*",
        attributes=[
            NWBAttributeSpec(
                name="location", doc="Location of wearable device on body", dtype="text", required=True
            ),
            NWBAttributeSpec(
                name="os_software_version", doc="The version number of the OS/software for the WearableDevice", dtype="text", required=False
            )
        ],
    )

    wearable_timeseries = NWBGroupSpec(
        neurodata_type_def="WearableTimeSeries",
        neurodata_type_inc="TimeSeries",
        quantity="*",
        doc="Data recorded from wearable sensor/device",
        datasets=[
            NWBDatasetSpec(
                name="data",
                dtype="float64",
                shape=((None, None)),
                dims=(("measurement_duration", "data")),
                doc="Data which was collected from sensor",
            )
        ],
        attributes=[
            NWBAttributeSpec(
                name="algorithm", doc="Algorithm used to extract data from raw sensor readings", dtype="text", required=True
            )
        ],
        links=[
            LinkSpec(
                name= 'wearable_device',
                target_type='WearableDevice',
                doc= 'Link to WearableDevice used to record WearableTimeSeries'
            )
        ]
    )

    physiological_measure = NWBGroupSpec(
        neurodata_type_def="PhysiologicalMeasure",
        neurodata_type_inc="NWBDataInterface",
        doc="Group collecting multiple wearable device's concurrent estimates of a single metric",
        groups=[
            NWBGroupSpec(
                doc="A single wearable device's time series data",
                neurodata_type_inc="WearableTimeSeries",
                quantity="*",
            ),
            NWBGroupSpec(
                doc="A single wearable device's categorical time series data",
                neurodata_type_inc="WearableEnumSeries",
                quantity="*",
            ),
            NWBGroupSpec(
                doc="A single wearable device's collection of events with additional data columns",
                neurodata_type_inc="WearableEvents",
                quantity="*",
            )
        ]
    )

    wearable_events = NWBGroupSpec(
        neurodata_type_def="WearableEvents",
        neurodata_type_inc="EventsTable",
        doc="Interval-style data (e.g., workouts) from wearable sensors/devices",
        quantity="*",
        attributes=[
            NWBAttributeSpec(
                name="algorithm", doc="Algorithm used to extract data from raw sensor readings", dtype="text", required=True
            )
        ],
        links=[
            LinkSpec(
                name= 'wearable_device',
                target_type='WearableDevice',
                doc= 'Link to WearableDevice used to record WearableEvents'
            )
        ]
    )
    
    enum_timeseries = NWBGroupSpec(
        neurodata_type_def="WearableEnumSeries",
        neurodata_type_inc="WearableTimeSeries",
        doc="A wearable time series intended for storing enumerated string labels",
        datasets=[
            NWBDatasetSpec(   # Overwrite the default dataset to always require strings
                name="data",
                dtype="text",
                doc="String labels representing enumerated classes (e.g., 'walking', 'sitting')"
            )
        ],
        groups=[
            NWBGroupSpec(
                name="meanings",
                doc="Dynamic table with detailed descriptions for all category labels used in the dataset",
                neurodata_type_inc="DynamicTable"
            )
        ],
        links=[
            LinkSpec(
                name='wearable_device',
                target_type='WearableDevice',
                doc='Link to WearableDevice used to record this data'
            ),
            # TODO: Should we explicitly store meanings tables somewhere better than the wearables module?
            # LinkSpec(
            #     name='meanings',
            #     target_type='DynamicTable',
            #     doc="Dynamic table storing the descriptions of all categories used in this dataset"
            # )
        ]
    )

    return [wearable_device, wearable_timeseries, physiological_measure, wearable_events, enum_timeseries]

