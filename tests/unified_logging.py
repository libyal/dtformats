# -*- coding: utf-8 -*-
"""Tests for Apple Unified Logging and Activity Tracing files."""

import unittest

import lz4.block

from dtformats import unified_logging

from tests import test_lib


class DSCFileTest(test_lib.BaseTestCase):
  """Shared-Cache Strings (dsc) file tests."""

  # pylint: disable=protected-access

  def testReadFileHeader(self):
    """Tests the _ReadFileHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.DSCFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', 'dsc', 'dsc-version2'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      file_header = test_file._ReadFileHeader(file_object)

    self.assertEqual(file_header.signature, b'hcsd')
    self.assertEqual(file_header.major_format_version, 2)
    self.assertEqual(file_header.minor_format_version, 0)
    self.assertEqual(file_header.number_of_ranges, 263)
    self.assertEqual(file_header.number_of_uuids, 200)

  def testReadRangeDescriptors(self):
    """Test the _ReadRangeDescriptors function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.DSCFile(output_writer=output_writer)

    # Testing Version 1
    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', 'dsc', 'dsc-version1'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      ranges = list(test_file._ReadRangeDescriptors(file_object, 16, 1, 252))

    self.assertEqual(len(ranges), 252)
    self.assertEqual(ranges[64].range_offset, 1756712)
    self.assertEqual(ranges[64].range_size, 3834)

    # Testing version 2
    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', 'dsc', 'dsc-version2'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      ranges = list(test_file._ReadRangeDescriptors(file_object, 16, 2, 263))

    self.assertEqual(len(ranges), 263)
    self.assertEqual(ranges[10].range_offset, 64272)
    self.assertEqual(ranges[10].range_size, 39755)

  def testReadUUIDPath(self):
    """Tests the _ReadUUIDPath function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.DSCFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', 'dsc', 'dsc-version1'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      uuid_path = test_file._ReadUUIDPath(file_object, 3202606)

    expected_uuid_path = (
        '/System/Library/Extensions/AppleBCMWLANFirmware_Hashstore.kext/'
        'AppleBCMWLANFirmware_Hashstore')
    self.assertEqual(uuid_path, expected_uuid_path)

  def testReadUUIDDescriptors(self):
    """Test the _ReadUUIDDescriptors function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.DSCFile(output_writer=output_writer)

    # Testing Version 1
    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', 'dsc', 'dsc-version1'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      uuids = list(test_file._ReadUUIDDescriptors(file_object, 4048, 1, 196))

    self.assertEqual(len(uuids), 196)
    self.assertEqual(uuids[42].text_offset, 9191424)
    self.assertEqual(uuids[42].text_size, 223732)
    expected_path = '/System/Library/Extensions/AppleH8ADBE0.kext/AppleH8ADBE0'
    self.assertEqual(uuids[42].path, expected_path)

    # Testing Version 2
    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', 'dsc', 'dsc-version2'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      uuids = list(test_file._ReadUUIDDescriptors(file_object, 6328, 2, 200))

    self.assertEqual(len(uuids), 200)
    self.assertEqual(uuids[197].text_offset, 26816512)
    self.assertEqual(uuids[197].text_size, 43736)
    expected_path = (
        '/System/Library/Extensions/AppleD2207PMU.kext/AppleD2207PMU')
    self.assertEqual(uuids[197].path, expected_path)

  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.DSCFile(
        debug=True, output_writer=output_writer)

    # TODO: test of 8E21CAB1DCF936B49F85CF860E6F34EC currently failing.
    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', 'dsc', 'dsc-version1'])
        # 'unified_logging', 'uuidtext', 'dsc',
        # '8E21CAB1DCF936B49F85CF860E6F34EC'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)
    test_file.Close()


class TimesyncDatabaseFileTest(test_lib.BaseTestCase):
  """Tests for the timesync database file."""

  # pylint: disable=protected-access

  def testReadFileRecord(self):
    """Tests the _ReadRecord method."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TimesyncDatabaseFile(
        output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', 'timesync', '0000000000000002.timesync'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      # Boot record
      record, _ = test_file._ReadRecord(file_object, 0)

      self.assertEqual(record.signature, b'\xb0\xbb')
      self.assertEqual(record.record_size, 48)
      self.assertEqual(record.timebase_numerator, 125)
      self.assertEqual(record.timebase_denominator, 3)
      self.assertEqual(record.timestamp, 1541730321839294000)
      self.assertEqual(record.time_zone_offset, 480)
      self.assertEqual(record.daylight_saving_flag, 0)

      # sync record
      record, _ = test_file._ReadRecord(file_object, 48)

      self.assertEqual(record.signature, b'Ts')
      self.assertEqual(record.record_size, 32)
      self.assertEqual(record.kernel_time, 494027973)
      self.assertEqual(record.timestamp, 1541730337313716000)
      self.assertEqual(record.time_zone_offset, 480)
      self.assertEqual(record.daylight_saving_flag, 0)

  def testReadFileObject(self):
    """Tests the ReadFileObject method."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TimesyncDatabaseFile(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', 'timesync', '0000000000000002.timesync'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)


class TraceV3FileTest(test_lib.BaseTestCase):
  """Apple Unified Logging and Activity Tracing (tracev3) file tests."""

  # pylint: disable=protected-access

  # TODO: add tests for _FormatArrayOfStrings
  # TODO: add tests for _FormatArrayOfUUIDS
  # TODO: add tests for _FormatStreamAsSignature

  def testReadChunkHeader(self):
    """Tests the _ReadChunkHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', '0000000000000030.tracev3'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      test_file._ReadChunkHeader(file_object, 0)

  # TODO: add tests for _ReadCatalog
  # TODO: add tests for _ReadChunkSet

  def testReadFirehoseChunkData(self):
    """Tests the _ReadFirehoseChunkData as well as the
      _ReadFirehoseTracepointData functions."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['0000000000000f85.tracev3'])
    self._SkipIfPathNotExists(test_file_path)

    # The 8th chunkset chunk of the first set
    with open(test_file_path, 'rb') as file_object:
      file_object.seek(0x1CC48)
      chunk_data = file_object.read(16519)
      uncompressed_data_size = 64624
      compressed_data_size = 16503

    uncompressed_data = lz4.block.decompress(
        chunk_data[12:compressed_data_size + 12],
        uncompressed_size=uncompressed_data_size)

    # data block #3
    data_offset = 0x17F8
    data_type_map = test_file._GetDataTypeMap('tracev3_chunk_header')
    chunkset_chunk_header = test_file._ReadStructureFromByteStream(
        uncompressed_data[data_offset:], data_offset, data_type_map,
        'chunk header')

    self.assertEqual(chunkset_chunk_header.chunk_tag, 0x6001)
    self.assertEqual(chunkset_chunk_header.chunk_data_size, 3976)

    data_offset += 16
    data_end_offset = data_offset + chunkset_chunk_header.chunk_data_size
    chunkset_chunk_data = uncompressed_data[data_offset:data_end_offset]

    firehose_data = test_file._ReadFirehoseChunkData(
        chunkset_chunk_data, chunkset_chunk_header.chunk_data_size,
        data_offset)

    self.assertEqual(firehose_data.process_identifier1, 449241)
    self.assertEqual(firehose_data.process_identifier2, 1345727)
    self.assertEqual(firehose_data.public_data_size, 3960)
    self.assertEqual(firehose_data.base_continuous_time, 100589149045772)

    # Testing the Tracepoints
    self.assertEqual(
        firehose_data.firehose_tracepoints[0].thread_identifier, 11479028)
    self.assertEqual(
        firehose_data.firehose_tracepoints[1].format_string_location,
        1355888928)
    self.assertEqual(
        firehose_data.firehose_tracepoints[3].continuous_time_lower, 7695)
    self.assertEqual(
        firehose_data.firehose_tracepoints[7].data_size, 76)

  def testReadOversizeChunkData(self):
    """Tests the _ReadOversizeChunkData function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['0000000000000f85.tracev3'])
    self._SkipIfPathNotExists(test_file_path)

    # The 8th chunkset chunk of the first set
    with open(test_file_path, 'rb') as file_object:
      file_object.seek(0x1CC48)
      chunk_data = file_object.read(16519)
      uncompressed_data_size = 64624
      compressed_data_size = 16503

    uncompressed_data = lz4.block.decompress(
        chunk_data[12:compressed_data_size + 12],
        uncompressed_size=uncompressed_data_size)

    # data block #17
    data_offset = 0xFC8
    data_type_map = test_file._GetDataTypeMap('tracev3_chunk_header')
    chunkset_chunk_header = test_file._ReadStructureFromByteStream(
        uncompressed_data[data_offset:], data_offset, data_type_map,
        'chunk header')

    self.assertEqual(chunkset_chunk_header.chunk_tag, 0x6002)
    self.assertEqual(chunkset_chunk_header.chunk_data_size, 2078)

    data_offset += 16
    data_end_offset = data_offset + chunkset_chunk_header.chunk_data_size
    chunkset_chunk_data = uncompressed_data[data_offset:data_end_offset]

    oversize_chunk = test_file._ReadOversizeChunkData(chunkset_chunk_data)

    self.assertEqual(oversize_chunk.continuous_time, 100657868900985)
    self.assertEqual(oversize_chunk.data_reference_index, 82)
    self.assertEqual(oversize_chunk.data_size, 2046)

  def testReadStatedumpChunkData(self):
    """Tests the _ReadStatedumpChunkData function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['0000000000000f85.tracev3'])
    self._SkipIfPathNotExists(test_file_path)

    # The 8th chunkset chunk of the first set
    with open(test_file_path, 'rb') as file_object:
      file_object.seek(0x1CC48)
      chunk_data = file_object.read(16519)
      uncompressed_data_size = 64624
      compressed_data_size = 16503

    uncompressed_data = lz4.block.decompress(
        chunk_data[12:compressed_data_size + 12],
        uncompressed_size=uncompressed_data_size)

    # data block #17
    data_offset = 0xDF38
    data_type_map = test_file._GetDataTypeMap('tracev3_chunk_header')
    chunkset_chunk_header = test_file._ReadStructureFromByteStream(
        uncompressed_data[data_offset:], data_offset, data_type_map,
        'chunk header')

    self.assertEqual(chunkset_chunk_header.chunk_tag, 0x6003)
    self.assertEqual(chunkset_chunk_header.chunk_data_size, 320)

    data_offset += 16
    data_end_offset = data_offset + chunkset_chunk_header.chunk_data_size
    chunkset_chunk_data = uncompressed_data[data_offset:data_end_offset]

    statedump_chunk = test_file._ReadStatedumpChunkData(chunkset_chunk_data)

    self.assertEqual(statedump_chunk.continuous_time, 100658002488678)
    self.assertEqual(statedump_chunk.activity_identifier, 15382799)
    self.assertEqual(
        str(statedump_chunk.uuid), 'ea02a60c-4989-3ab2-a032-c0e6f412ee5f')
    self.assertEqual(
        statedump_chunk.object_type_string1.rstrip(b'\x00'), b'location')

  def testReadHeader(self):
    """Tests the _ReadHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', '0000000000000f85.tracev3'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      header_chunk = test_file._ReadHeader(file_object, 16)

    self.assertEqual(header_chunk.timebase_numerator, 125)
    self.assertEqual(header_chunk.timebase_denominator, 3)
    self.assertEqual(header_chunk.time_zone_offset, 300)

    self.assertEqual(header_chunk.continuous.sub_chunk_tag, 0x6100)

    self.assertEqual(header_chunk.system_information.sub_chunk_tag, 0x6101)
    self.assertEqual(header_chunk.system_information.build_version, '19D52')
    self.assertEqual(header_chunk.system_information.hardware_model, 'J96AP')

    self.assertEqual(header_chunk.generation.sub_chunk_tag, 0x6102)
    self.assertEqual(str(header_chunk.generation.boot_identifier), (
        'a6ebc8e3-0a1c-40e8-93b9-da3a7f671d19'))

    self.assertEqual(header_chunk.time_zone.sub_chunk_tag, 0x6103)
    self.assertEqual(header_chunk.time_zone.path, (
        '/var/db/timezone/zoneinfo/America/Toronto'))

  @unittest.skip('improve format support')
  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', '0000000000000030.tracev3'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)
    test_file.Close()


class UUIDTextFileTest(test_lib.BaseTestCase):
  """Apple Unified Logging and Activity Tracing (uuidtext) file tests."""

  # pylint: disable=protected-access

  def testReadFileHeader(self):
    """Tests the _ReadFileHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.UUIDTextFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', '22', '0D3C2953A33917B333DD8366AC25F2'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      test_file._ReadFileHeader(file_object)

  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.UUIDTextFile(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', '22', '0D3C2953A33917B333DD8366AC25F2'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)
    test_file.Close()


if __name__ == '__main__':
  unittest.main()
