# -*- coding: utf-8 -*-
"""MacOS fseventsd files."""

import pygzipf

from dtformats import data_format


class FseventsFile(data_format.BinaryDataFile):
  """MacOS fseventsd file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric and dtFormats definition files.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('fseventsd.yaml')

  _DEBUG_INFORMATION = data_format.BinaryDataFile.ReadDebugInformationFile(
      'fseventsd.debug.yaml', custom_format_callbacks={
          'signature': '_FormatStreamAsString'})

  # The version 1 format was used in Mac OS X 10.5 (Leopard) through macOS 10.12
  # (Sierra).
  _DLS_V1_SIGNATURE = b'1SLD'

  # The version 2 format was introduced in MacOS High Sierra (10.13).
  _DLS_V2_SIGNATURE = b'2SLD'

  def __init__(self, debug=False, output_writer=None):
    """Initializes a MacOS fseventsd file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(FseventsFile, self).__init__(
        debug=debug, output_writer=output_writer)

  def _ReadDLSPageHeader(self, file_object, file_offset):
    """Reads a DLS page header.

    Args:
      file_object (pygzipf.file): file-like object of the uncompressed data
          within a gzip file.
      file_offset (int): offset of the start of the page header, relative
          to the start of the file.

    Returns:
      tuple[dls_page_header, int]: page header and number of bytes read.

    Raises:
      ParseError: if the page header cannot be read.
    """
    data_type_map = self._GetDataTypeMap('dls_page_header')

    dls_page_header, bytes_read = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'DLS page header')

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get('dls_page_header', None)
      self._DebugPrintStructureObject(dls_page_header, debug_info)

    return dls_page_header, bytes_read

  def _ReadDLSRecord(self, file_object, file_offset, format_version):
    """Reads a DLS record.

    Args:
      file_object (pygzipf.file): file-like object of the uncompressed data
          within a gzip file.
      file_offset (int): offset of the start of the page entry, relative
          to the start of the file.
      format_version (int): format version.

    Returns:
      tuple[dls_record_v1|dls_record_v2, int]: record and number of bytes read.

    Raises:
      ParseError: if the record cannot be read.
    """
    if format_version == 1:
      data_type_map = self._GetDataTypeMap('dls_record_v1')
    elif format_version == 2:
      data_type_map = self._GetDataTypeMap('dls_record_v2')
    else:
      data_type_map = None

    dls_record, bytes_read = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'DLS record')

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get('dls_record', None)
      self._DebugPrintStructureObject(dls_record, debug_info)

    return dls_record, bytes_read

  def ReadFileObject(self, file_object):
    """Reads a MacOS fseventsd file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    gzipf_file = pygzipf.file()
    gzipf_file.open_file_object(file_object)

    try:
      file_offset = 0
      file_size = gzipf_file.get_uncompressed_data_size()

      while file_offset < file_size:
        page_header, bytes_read = self._ReadDLSPageHeader(
            gzipf_file, file_offset)

        page_end_offset = file_offset + page_header.page_size
        file_offset += bytes_read

        while file_offset < page_end_offset:
          if page_header.signature == self._DLS_V1_SIGNATURE:
            format_version = 1
          elif page_header.signature == self._DLS_V2_SIGNATURE:
            format_version = 2
          else:
            format_version = 0

          _, bytes_read = self._ReadDLSRecord(
              gzipf_file, file_offset, format_version)

          file_offset += bytes_read

    finally:
      gzipf_file.close()
