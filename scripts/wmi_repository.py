#!/usr/bin/env python3
"""Script to parse WMI Common Information Model (CIM) repository files."""

import argparse
import logging
import os
import sys

from dfdatetime import filetime as dfdatetime_filetime

from dtformats import output_writers
from dtformats import wmi_repository


def FormatFiletime(timestamp):
    """Formats a FILETIME timestamp.

    Args:
      timestamp (int): FILETIME timestamp or None if not available.

    Returns:
      str: formatted FILETIME timestamp.
    """
    if timestamp is None:
        return ""

    date_time = dfdatetime_filetime.Filetime(timestamp=timestamp)
    date_time_string = date_time.CopyToDateTimeString()
    if not date_time_string:
        return f"0x{timestamp:08x}"

    return f"{date_time_string:s} UTC"


def PrintClassDefinition(class_definition):
    """Writes a class definition to stdout.

    Args:
      class_definition (ClassDefinition): class definition.
    """
    namespace = class_definition.namespace or ""
    super_class_name = class_definition.super_class_name or ""
    date_time_string = FormatFiletime(class_definition.date_time)

    print(
        f"{namespace:s}\t{class_definition.name:s}\t{super_class_name:s}\t"
        f"{date_time_string:s}"
    )


def PrintInstance(instance):
    """Writes an instance to stdout.

    Args:
      instance (Instance): instance.
    """
    name_property = instance.properties.get("Name")

    genus = "2"
    super_class_name = instance.super_class_name or ""
    dynasty = instance.dynasty or ""

    if name_property:
        relpath = f'{instance.class_name:s}.Name="{name_property:s}"'
    else:
        relpath = f"{instance.class_name:s}=@"

    number_of_properties = len(instance.properties)
    derivation = ", ".join(instance.derivation)
    server = "."
    namespace = instance.namespace or "ROOT"

    name_value_pairs = [
        ("__GENUS", genus),
        ("__CLASS", instance.class_name),
        ("__SUPERCLASS", super_class_name),
        ("__DYNASTY", dynasty),
        ("__RELPATH", relpath),
        ("__PROPERTY_COUNT", f"{number_of_properties:d}"),
        ("__DERIVATION", f"{{{derivation:s}}}"),
        ("__SERVER", server),
        ("__NAMESPACE", namespace),
        ("__PATH", f"\\\\{server:s}\\{namespace:s}:{relpath:s}"),
    ]

    for property_name, property_value in sorted(instance.properties.items()):
        if property_value is None:
            property_value = ""
        else:
            property_value = f"{property_value!s}"

        name_value_pairs.append((property_name, property_value))

    largest_name = max(len(name) for name, _ in name_value_pairs)

    for name, value in name_value_pairs:
        alignment_string = " " * (largest_name - len(name))
        print(f"{name:s}{alignment_string:s} : {value:s}")

    print("")


def PrintNamespace(instance):
    """Writes a namespace to stdout.

    Args:
      instance (Instance): instance.
    """
    print(instance.namespace or "")


def Main():
    """The main program function.

    Returns:
      bool: True if successful or False if not.
    """
    argument_parser = argparse.ArgumentParser(
        description=(
            "Extracts information from WMI Common Information Model (CIM) "
            "repository files."
        )
    )

    argument_parser.add_argument(
        "-d",
        "--debug",
        dest="debug",
        action="store_true",
        default=False,
        help="enable debug output.",
    )

    argument_parser.add_argument(
        "--class",
        dest="class_name",
        action="store",
        default=None,
        metavar="NAME",
        help=(
            "name of the class of which to print the instances, sub classes are "
            "not included."
        ),
    )

    argument_parser.add_argument(
        "--output_mode",
        "--output-mode",
        dest="output_mode",
        action="store",
        choices=["classes", "debug", "index", "instances", "namespaces"],
        default="instances",
        help=(
            "output mode, where classes prints the class definitions, index "
            "the index keys, instances the instances and namespaces the "
            "namespaces."
        ),
    )

    argument_parser.add_argument(
        "source",
        nargs="?",
        action="store",
        metavar="PATH",
        default=None,
        help=(
            "path of the directory containing the WMI Common Information "
            "Model (CIM) repository files."
        ),
    )

    options = argument_parser.parse_args()

    if not options.source:
        print("Source file missing.")
        print("")
        argument_parser.print_help()
        print("")
        return False

    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    output_writer = output_writers.StdoutWriter()

    try:
        output_writer.Open()
    except OSError as exception:
        print(f"Unable to open output writer with error: {exception!s}")
        print("")
        return False

    source_basename = os.path.basename(options.source).lower()
    if source_basename == "index.btr":
        options.output_mode = "index"

    elif source_basename.endswith(".map"):
        # The content of a mapping file is only printed in debug mode.
        options.output_mode = "mapping"

    cim_repository = wmi_repository.CIMRepository(
        debug=options.debug, output_writer=output_writer
    )

    # The CIM repository requires an absolute path.
    source_path = os.path.abspath(options.source)

    cim_repository.Open(source_path)

    if options.output_mode == "index":
        for key_path in cim_repository.GetIndexKeys():
            print(key_path)

    elif options.output_mode == "classes":
        for class_definition in cim_repository.GetClassDefinitions():
            PrintClassDefinition(class_definition)

    elif options.output_mode == "instances":
        for instance in cim_repository.GetInstances(class_name=options.class_name):
            PrintInstance(instance)

    elif options.output_mode == "namespaces":
        for instance in sorted(
            cim_repository.GetNamespaces(), key=lambda instance: instance.namespace
        ):
            PrintNamespace(instance)

    elif options.output_mode == "debug":
        for key in cim_repository.GetIndexKeys():
            if "." in key:
                key_segment = key.split("\\")[-1]
                data_type, _, _ = key_segment.partition("_")

                if data_type == "R":
                    if options.output_mode == "debug":
                        object_record = cim_repository.GetObjectRecordByKey(key)
                        registration = wmi_repository.Registration(
                            debug=options.debug, output_writer=output_writer
                        )
                        registration.ReadObjectRecord(object_record.data)

    cim_repository.Close()

    output_writer.Close()

    return True


if __name__ == "__main__":
    if not Main():
        sys.exit(1)
    else:
        sys.exit(0)
