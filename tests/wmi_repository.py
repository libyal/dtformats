"""Tests for WMI Common Information Model (CIM) repository files."""

import itertools
import os
import sys
import unittest

from dtformats import wmi_repository

from tests import test_lib

# TODO: add tests for IndexBinaryTreePage
# TODO: add tests for ObjectRecord
# TODO: add tests for ObjectsDataPage


class IndexBinaryTreeFileTest(test_lib.BaseTestCase):
    """Index binary-tree (Index.btr) file tests."""

    # pylint: disable=protected-access

    # TODO: add tests for _DebugPrintPageBody

    # TODO: add tests for _GetPage
    # TODO: add tests for _ReadPage
    # TODO: add tests for _ReadPageKeyData
    # TODO: add tests for _ReadPageValueData
    # TODO: add tests for _ReadSubPages
    # TODO: add tests for GetFirstMappedPage
    # TODO: add tests for GetMappedPage
    # TODO: add tests for GetRootPage

    def testReadFileObject(self):
        """Tests the ReadFileObject."""
        test_file_path = self._GetTestFilePath(["cim", "INDEX.MAP"])
        self._SkipIfPathNotExists(test_file_path)

        output_writer = test_lib.TestOutputWriter()
        test_file = wmi_repository.IndexBinaryTreeFile(output_writer=output_writer)

        test_file_path = self._GetTestFilePath(["cim", "INDEX.BTR"])
        self._SkipIfPathNotExists(test_file_path)

        test_file.Open(test_file_path)

        test_file.Close()


class MappingFileTest(test_lib.BaseTestCase):
    """Mappings (*.map) file tests."""

    # pylint: disable=protected-access

    # TODO: add tests _DebugPrintMappingTable
    # TODO: add tests _DebugPrintUnknownTable

    def testReadFileFooter(self):
        """Tests the _ReadFileFooter function."""
        output_writer = test_lib.TestOutputWriter()
        test_file = wmi_repository.MappingFile(output_writer=output_writer)

        test_file_path = self._GetTestFilePath(["cim", "INDEX.MAP"])
        self._SkipIfPathNotExists(test_file_path)

        with open(test_file_path, "rb") as file_object:
            file_object.seek(-4, os.SEEK_END)

            test_file._ReadFileFooter(file_object)

    def testReadFileHeader(self):
        """Tests the _ReadFileHeader function."""
        output_writer = test_lib.TestOutputWriter()
        test_file = wmi_repository.MappingFile(output_writer=output_writer)

        test_file_path = self._GetTestFilePath(["cim", "INDEX.MAP"])
        self._SkipIfPathNotExists(test_file_path)

        with open(test_file_path, "rb") as file_object:
            test_file._ReadFileHeader(file_object, format_version=1)

    def testReadMappingTable(self):
        """Tests the _ReadMappingTable function."""
        output_writer = test_lib.TestOutputWriter()
        test_file = wmi_repository.MappingFile(output_writer=output_writer)
        test_file.format_version = 1

        test_file_path = self._GetTestFilePath(["cim", "INDEX.MAP"])
        self._SkipIfPathNotExists(test_file_path)

        with open(test_file_path, "rb") as file_object:
            file_object.seek(12, os.SEEK_SET)

            test_file._ReadMappingTable(file_object)

    def testReadUnknownTable(self):
        """Tests the _ReadUnknownTable function."""
        output_writer = test_lib.TestOutputWriter()
        test_file = wmi_repository.MappingFile(output_writer=output_writer)

        test_file_path = self._GetTestFilePath(["cim", "INDEX.MAP"])
        self._SkipIfPathNotExists(test_file_path)

        with open(test_file_path, "rb") as file_object:
            file_object.seek(572, os.SEEK_SET)

            test_file._ReadUnknownTable(file_object)

    def testReadFileObject(self):
        """Tests the ReadFileObject."""
        output_writer = test_lib.TestOutputWriter()
        test_file = wmi_repository.MappingFile(output_writer=output_writer)

        test_file_path = self._GetTestFilePath(["cim", "INDEX.MAP"])
        self._SkipIfPathNotExists(test_file_path)

        test_file.Open(test_file_path)

        test_file.Close()


class ObjectsDataFileTest(test_lib.BaseTestCase):
    """Index binary-tree (Index.btr) file tests."""

    # TODO: add tests _GetKeyValues
    # TODO: add tests _GetPage
    # TODO: add tests _ReadPage
    # TODO: add tests GetMappedPage
    # TODO: add tests GetObjectRecordByKey

    def testReadFileObject(self):
        """Tests the ReadFileObject."""
        test_file_path = self._GetTestFilePath(["cim", "OBJECTS.MAP"])
        self._SkipIfPathNotExists(test_file_path)

        output_writer = test_lib.TestOutputWriter()
        test_file = wmi_repository.ObjectsDataFile(output_writer=output_writer)

        test_file_path = self._GetTestFilePath(["cim", "OBJECTS.DATA"])
        self._SkipIfPathNotExists(test_file_path)

        test_file.Open(test_file_path)


class ClassValueDataMapTest(test_lib.BaseTestCase):
    """Class value data map tests."""

    def testBuild(self):
        """Tests the Build function."""
        base_class_definition = wmi_repository.ClassDefinition()
        base_class_definition.name = "__SystemClass"

        parent_class_definition = wmi_repository.ClassDefinition()
        parent_class_definition.name = "__IndicationRelated"
        parent_class_definition.super_class_name = "__SystemClass"

        class_definition = wmi_repository.ClassDefinition()
        class_definition.name = "__EventFilter"
        class_definition.super_class_name = "__IndicationRelated"

        class_value_data_map = wmi_repository.ClassValueDataMap()
        class_value_data_map.Build(
            [base_class_definition, parent_class_definition, class_definition]
        )

        self.assertEqual(class_value_data_map.class_name, "__EventFilter")
        self.assertEqual(
            class_value_data_map.derivation, ["__IndicationRelated", "__SystemClass"]
        )
        self.assertEqual(class_value_data_map.dynasty, "__SystemClass")
        self.assertEqual(class_value_data_map.super_class_name, "__IndicationRelated")

        class_value_data_map = wmi_repository.ClassValueDataMap()
        class_value_data_map.Build([base_class_definition])

        self.assertEqual(class_value_data_map.derivation, [])
        self.assertEqual(class_value_data_map.dynasty, "__SystemClass")
        self.assertIsNone(class_value_data_map.super_class_name)


@unittest.skipIf(sys.platform.startswith("win"), "Windows not supported")
class CIMRepositoryTest(test_lib.BaseTestCase):
    """CIM repository tests."""

    # pylint: disable=protected-access

    _NAMESPACE_SUBSCRIPTION = "ROOT\\subscription"

    def _OpenTestRepository(self):
        """Opens the test CIM repository.

        Returns:
          CIMRepository: CIM repository.
        """
        test_directory_path = self._GetTestFilePath(["cim"])
        self._SkipIfPathNotExists(test_directory_path)

        test_repository = wmi_repository.CIMRepository()
        test_repository.Open(test_directory_path)

        return test_repository

    def testGetClassDefinition(self):
        """Tests the _GetClassDefinition function."""
        test_repository = self._OpenTestRepository()

        try:
            namespace_hash = test_repository._GetHashFromString(
                self._NAMESPACE_SUBSCRIPTION
            )

            # A class definition defined in the namespace itself.
            class_name_hash = test_repository._GetHashFromString(
                "CommandLineEventConsumer"
            )
            defining_namespace_hash, class_definition = (
                test_repository._GetClassDefinition(namespace_hash, class_name_hash)
            )
            self.assertEqual(defining_namespace_hash, namespace_hash)
            self.assertIsNotNone(class_definition)
            self.assertEqual(class_definition.name, "CommandLineEventConsumer")
            self.assertEqual(class_definition.super_class_name, "__EventConsumer")
            self.assertEqual(class_definition.date_time, 130073815545779510)
            self.assertIn("CommandLineTemplate", class_definition.properties)
            self.assertIn("ExecutablePath", class_definition.properties)

            # A system class definition defined in the "__SystemClass" namespace.
            class_name_hash = test_repository._GetHashFromString("__EventFilter")
            defining_namespace_hash, class_definition = (
                test_repository._GetClassDefinition(namespace_hash, class_name_hash)
            )
            self.assertEqual(
                defining_namespace_hash,
                test_repository._GetHashFromString("__SystemClass"),
            )
            self.assertIsNotNone(class_definition)
            self.assertEqual(class_definition.name, "__EventFilter")
            self.assertEqual(class_definition.date_time, 130073815545777537)
            self.assertEqual(
                sorted(class_definition.properties.keys()),
                [
                    "CreatorSID",
                    "EventAccess",
                    "EventNamespace",
                    "Name",
                    "Query",
                    "QueryLanguage",
                ],
            )

            class_name_hash = test_repository._GetHashFromString("Bogus")
            defining_namespace_hash, class_definition = (
                test_repository._GetClassDefinition(namespace_hash, class_name_hash)
            )
            self.assertIsNone(defining_namespace_hash)
            self.assertIsNone(class_definition)

        finally:
            test_repository.Close()

    def testGetClassDefinitions(self):
        """Tests the GetClassDefinitions function."""
        test_repository = self._OpenTestRepository()

        try:
            number_of_class_definitions = len(test_repository._GetClassDefinitionKeys())
            self.assertEqual(number_of_class_definitions, 3651)

            # Only read a subset of the class definitions to keep the test fast.
            class_definitions = list(
                itertools.islice(test_repository.GetClassDefinitions(), 25)
            )
            self.assertEqual(len(class_definitions), 25)

            for class_definition in class_definitions:
                self.assertIsNotNone(class_definition.name)
                self.assertIsNotNone(class_definition.namespace)
                self.assertIsNotNone(class_definition.date_time)

        finally:
            test_repository.Close()

    def testGetInstances(self):
        """Tests the GetInstances function."""
        test_repository = self._OpenTestRepository()

        try:
            instances = list(test_repository.GetInstances(class_name="__EventFilter"))
            self.assertEqual(len(instances), 2)

            instances_by_name = {
                instance.properties.get("Name"): instance for instance in instances
            }
            instance = instances_by_name.get("SCM Event Log Filter")
            self.assertIsNotNone(instance)
            self.assertEqual(instance.class_name, "__EventFilter")
            self.assertEqual(
                instance.derivation, ["__IndicationRelated", "__SystemClass"]
            )
            self.assertEqual(instance.dynasty, "__SystemClass")
            self.assertEqual(instance.namespace, self._NAMESPACE_SUBSCRIPTION)
            self.assertEqual(instance.super_class_name, "__IndicationRelated")
            self.assertEqual(instance.date_time1, 130073815545779748)
            self.assertEqual(instance.date_time2, 130073815545777537)

            expected_properties = {
                "CreatorSID": None,
                "EventAccess": None,
                "EventNamespace": "root\\cimv2",
                "Name": "SCM Event Log Filter",
                "Query": "select * from MSFT_SCMEventLogEvent",
                "QueryLanguage": "WQL",
            }
            self.assertEqual(instance.properties, expected_properties)

            instances = list(
                test_repository.GetInstances(class_name="__FilterToConsumerBinding")
            )
            self.assertEqual(len(instances), 2)

            consumers = sorted(
                instance.properties.get("Consumer") for instance in instances
            )
            self.assertEqual(
                consumers,
                [
                    'NTEventLogEventConsumer.Name="SCM Event Log Consumer"',
                    (
                        "\\\\.\\root\\subscription:MSFT_UCScenarioControl.Name="
                        '"Microsoft WMI Updating Consumer Scenario Control"'
                    ),
                ],
            )

            # Sub classes are not included.
            instances = list(test_repository.GetInstances(class_name="__EventConsumer"))
            self.assertEqual(len(instances), 0)

            instances = list(
                test_repository.GetInstances(class_name="NTEventLogEventConsumer")
            )
            self.assertEqual(len(instances), 1)

            instance = instances[0]
            self.assertEqual(instance.namespace, self._NAMESPACE_SUBSCRIPTION)
            self.assertEqual(instance.dynasty, "__SystemClass")
            self.assertEqual(instance.properties.get("Name"), "SCM Event Log Consumer")
            self.assertEqual(
                instance.properties.get("SourceName"), "Service Control Manager"
            )

            # An 8-bit integer array property value.
            instances = list(test_repository.GetInstances(class_name="__thisNAMESPACE"))
            self.assertEqual(len(instances), 33)

            for instance in instances:
                security_descriptor = instance.properties.get("SECURITY_DESCRIPTOR")
                self.assertIsNotNone(security_descriptor)
                # Revision 1 of a self-relative security descriptor.
                self.assertEqual(security_descriptor[0], 1)

        finally:
            test_repository.Close()

    def testGetNamespaces(self):
        """Tests the GetNamespaces function."""
        test_repository = self._OpenTestRepository()

        try:
            namespaces = [
                instance.namespace for instance in test_repository.GetNamespaces()
            ]
            self.assertEqual(len(namespaces), 32)
            self.assertIn("ROOT\\CIMV2", namespaces)
            self.assertIn(self._NAMESPACE_SUBSCRIPTION, namespaces)

            # Every namespace referenced by the index keys can be resolved.
            namespaces_by_hash = test_repository._GetNamespacesByHash()
            for key in test_repository.GetIndexKeys():
                key_segments = key.split("\\")
                namespace_hash = key_segments[1][3:].lower()
                self.assertIn(namespace_hash, namespaces_by_hash)

        finally:
            test_repository.Close()

    def testOpenAndClose(self):
        """Tests the Open and Close functions."""
        test_repository = self._OpenTestRepository()

        try:
            self.assertEqual(test_repository.format_version, "2.1")
            self.assertEqual(len(list(test_repository.GetIndexKeys())), 10288)
        finally:
            test_repository.Close()


if __name__ == "__main__":
    unittest.main()
