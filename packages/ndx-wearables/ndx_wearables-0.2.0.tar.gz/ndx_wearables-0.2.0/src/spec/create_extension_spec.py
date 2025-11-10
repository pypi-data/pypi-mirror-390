# -*- coding: utf-8 -*-
import os.path
from pynwb.spec import NWBNamespaceBuilder, export_spec
from wearables_infrastructure import make_wearables_infrastructure
# TODO: import other spec classes as needed
# from pynwb.spec import NWBDatasetSpec, NWBLinkSpec, NWBDtypeSpec, NWBRefSpec

def main():
    # these arguments were auto-generated from your cookiecutter inputs
    ns_builder = NWBNamespaceBuilder(
        name="""ndx-wearables""",
        version="""0.1.1""",
        doc="""Store data from human wearable devices in NWB""",
        author=[
            "Tomasz M. Fraczek",
            "Lauren Diaz",
            "Nicole Guittari",
            "Rick Hanish",
            "Timon Merk",
            "Nicole Tregoning",
            "Sandy Hider",
            "Wayne K. Goodman",
            "Sameer A. Sheth",
            "Han Yi",
            "Brock A. Wester",
            "Jeffery A. Herron",
            "Erik C. Johnson",
            "Nicole R. Provenza"
        ],
        contact=[
            "tomek.fraczek@bcm.edu", 
        ],
    )
    ns_builder.include_namespace("core")
    ns_builder.include_namespace("ndx-events")
    wearables_infra_datastructures = make_wearables_infrastructure()


# TODO: add all of your new data types to this list

    # Combine all series types
    new_data_types = [
        *wearables_infra_datastructures,
    ]


    # export the spec to yaml files in the spec folder
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "spec"))
    export_spec(ns_builder, new_data_types, output_dir)


if __name__ == "__main__":
    # usage: python create_extension_spec.py
    main()
