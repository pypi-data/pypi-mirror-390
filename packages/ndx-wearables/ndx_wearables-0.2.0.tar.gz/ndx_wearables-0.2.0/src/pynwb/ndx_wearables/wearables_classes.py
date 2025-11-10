import copy

from pynwb import register_class, get_class
from pynwb.device import Device
from pynwb.base import TimeSeries
from ndx_events import EventsTable
from hdmf.utils import docval, popargs, get_docval, getargs  # <-- added getargs
import numpy as np
from enum import Enum
from hdmf.common import DynamicTable

from ndx_wearables.categorical_enums import ENUM_MAP

    
class WearableBase(object):
    """
    HDMF and by extension NWB does not really support multiple inheritance.
    As a result, this class is "invisibly" inherited as a mixin

    For this to work properly, the inheriting class (at the time of writing, WearableTimeSeries and WearableEvents)
    must append the result of get_wearables_docval() to the docval of the init method, and call the function
    wearables_init_helper in the init method.
    """

    @staticmethod
    def get_wearables_docval():
        return (
            {
                'name': 'wearable_device',
                'type': 'WearableDevice',
                'doc': 'Link to the WearableDevice used to record the data'
            },
            {
                'name': 'algorithm',
                'type': str,
                'doc': 'Algorithm used to extract data from raw sensor readings'
            }
        )

    def wearables_init_helper(self, **kwargs):
        wearable_device = popargs('wearable_device', kwargs)
        algorithm = popargs('algorithm', kwargs)

        self.wearable_device = wearable_device
        self.algorithm = algorithm
        return kwargs


def update_docval(original, *updates, to_remove=None):
    """Helper function to allow modification of docval attributes on the fly"""
    updated = list(copy.deepcopy(original))
    for update in updates:
        for doc_dict in updated:
            if doc_dict['name'] == update['name']:
                doc_dict.update(update)
                break
    if to_remove is not None:
        idx_to_remove = []
        for remove_name in to_remove:
            for idx, doc_dict in enumerate(updated):
                if doc_dict['name'] == remove_name:
                    idx_to_remove.append(idx)
        desc_removals = sorted(idx_to_remove, reverse=True) # process in desc order to avoid errors. probs a better way
        for i in desc_removals:
            del updated[i]
    return tuple(updated)


# Device and existing classes (unchanged except for Placement handling)
@register_class("WearableDevice", "ndx-wearables")
class WearableDevice(Device):
    '''
    - name
    - description
    - manufacturer
    - location (on body)
    '''
    __nwbfields__ = ("location",)

    @docval(
        *get_docval(Device.__init__)
        + (
            {"name":"location", "type": str, "doc": "Location on body of device"},
            {"name":"os_software_version", "type": str,
             "doc":"The version number of the OS/software for the WearableDevice", "default": None}
        )
    )
    def __init__(self, **kwargs):
        location = popargs("location", kwargs)
        os_software_version = popargs("os_software_version", kwargs)
        super().__init__(**kwargs)

        self.location = location
        self.os_software_version = os_software_version

@register_class("WearableTimeSeries", "ndx-wearables")
class WearableTimeSeries(WearableBase, TimeSeries):
    @docval(
        *(get_docval(TimeSeries.__init__) + WearableBase.get_wearables_docval())
    )
    def __init__(self, **kwargs):
        kwargs = self.wearables_init_helper(**kwargs)
        super().__init__(**kwargs)


# Categorical Wearable TimeSeries container, with a required meanings table
@register_class('WearableEnumSeries', 'ndx-wearables')
class WearableEnumSeries(WearableTimeSeries):
    """
    A categorical TimeSeries for wearable data.
    Stores category values (strings or integer indices), the allowed categories,
    and an optional meanings table with human-readable descriptions.
    """

    @docval(
        *update_docval(
            get_docval(WearableTimeSeries.__init__),
            {'name': 'data', 'type': ('array_data',), 'doc': 'categorical values as strings or int indices'},
            to_remove=['unit']
        )
        + (
            {'name': 'meanings', 'type': (DynamicTable, type(None)), 'doc': 'optional category->description table', 'default': None},
         )
    )
    def __init__(self, **kwargs):
        meanings = kwargs.pop('meanings')
        self.meanings = meanings
        super().__init__(unit='category', **kwargs)


@register_class("WearableEvents", "ndx-wearables")
class WearableEvents(WearableBase, EventsTable):
    @docval(
        *(get_docval(EventsTable.__init__) + WearableBase.get_wearables_docval())
    )
    def __init__(self, **kwargs):
        kwargs = self.wearables_init_helper(**kwargs)
        super().__init__(**kwargs)

PhysiologicalMeasure = get_class("PhysiologicalMeasure", "ndx-wearables")
