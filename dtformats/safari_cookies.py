# -*- coding: utf-8 -*-
"""Safari Cookies (Cookies.binarycookies) files."""

import datetime

from dtfabric.runtime import data_maps as dtfabric_data_maps

from dtformats import data_format
from dtformats import errors


class BinaryCookiesFile(data_format.BinaryDataFile):
  """Safari Cookies (Cookies.binarycookies) file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('safari_cookies.yaml')

  def __init__(self, debug=False, output_writer=None):
    """Initializes a Safari Cookies (Cookies.binarycookies) file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(BinaryCookiesFile, self).__init__(
        debug=debug, output_writer=output_writer)
    self._page_sizes = []

  def _DebugPrintFileHeader(self, file_header):
    """Prints file header debug information.

    Args:
      file_header (binarycookies_file_header): file header.
    """
    self._DebugPrintValue('Signature', f'{file_header.signature!s}')

    self._DebugPrintValue('Number of pages', f'{file_header.number_of_pages:d}')

    self._DebugPrintText('\n')

  def _DebugPrintRecordHeader(self, record_header):
    """Prints record header debug information.

    Args:
      record_header (binarycookies_record_header): record header.
    """
    self._DebugPrintValue('Size', f'{record_header.size:d}')
    self._DebugPrintValue('Unknown1', f'0x{record_header.unknown1:08x}')
    self._DebugPrintValue('Flags', f'0x{record_header.flags:08x}')
    self._DebugPrintValue('Unknown2', f'0x{record_header.unknown2:08x}')
    self._DebugPrintValue('URL offset', f'{record_header.url_offset:d}')
    self._DebugPrintValue('Name offset', f'{record_header.name_offset:d}')
    self._DebugPrintValue('Path offset', f'{record_header.path_offset:d}')
    self._DebugPrintValue('Value offset', f'{record_header.value_offset:d}')
    self._DebugPrintValue('Unknown3', f'0x{record_header.unknown3:08x}')

    date_time = (datetime.datetime(2001, 1, 1) + datetime.timedelta(
        seconds=int(record_header.expiration_time)))
    self._DebugPrintValue(
        'Expiration time', f'{date_time!s} ({record_header.expiration_time:f})')

    date_time = (datetime.datetime(2001, 1, 1) + datetime.timedelta(
        seconds=int(record_header.creation_time)))
    self._DebugPrintValue(
        'Creation time', f'{date_time!s} ({record_header.creation_time:f})')

    self._DebugPrintText('\n')

  def _ReadCString(self, page_data, string_offset):
    """Reads a string from the page data.

    Args:
      page_data (bytes): page data.
      string_offset (int): offset of the string relative to the start
          of the page.

    Returns:
      str: string.

    Raises:
      ParseError: if the string cannot be read.
    """
    data_type_map = self._GetDataTypeMap('cstring')

    try:
      value_string = self._ReadStructureFromByteStream(
          page_data[string_offset:], string_offset, data_type_map, 'cstring')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError((
          f'Unable to parse string at offset: 0x{string_offset:08x} with '
          f'error: {exception!s}'))

    return value_string.rstrip('\x00')

  def _ReadFileFooter(self, file_object):
    """Reads the file footer.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file footer cannot be read.
    """
    file_offset = file_object.tell()
    data_type_map = self._GetDataTypeMap('binarycookies_file_footer')

    file_footer, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'file footer')

    # TODO: add _DebugPrintFileFooter
    _ = file_footer

  def _ReadFileHeader(self, file_object):
    """Reads the file header.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file header cannot be read.
    """
    data_type_map = self._GetDataTypeMap('binarycookies_file_header')

    file_header, file_header_data_size = self._ReadStructureFromFileObject(
        file_object, 0, data_type_map, 'file header')

    if self._debug:
      self._DebugPrintFileHeader(file_header)

    file_offset = file_header_data_size

    # TODO: move page sizes array into file header, this will require dtFabric
    # to compare signature as part of data map.
    # TODO: check for upper limit.
    page_sizes_data_size = file_header.number_of_pages * 4

    page_sizes_data = file_object.read(page_sizes_data_size)

    if self._debug:
      self._DebugPrintData('Page sizes data', page_sizes_data)

    context = dtfabric_data_maps.DataTypeMapContext(values={
        'binarycookies_file_header': file_header})

    data_type_map = self._GetDataTypeMap('binarycookies_page_sizes')

    try:
      page_sizes_array = self._ReadStructureFromByteStream(
          page_sizes_data, file_offset, data_type_map, 'page sizes',
          context=context)
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError((
          f'Unable to map page sizes data at offset: 0x{file_offset:08x} with '
          f'error: {exception!s}'))

    self._page_sizes = []
    if file_header.number_of_pages > 0:
      for index, page_size in enumerate(page_sizes_array):
        self._page_sizes.append(page_size)

        if self._debug:
          self._DebugPrintValue(f'Page: {index:d} size', f'{page_size:d}')

      if self._debug:
        self._DebugPrintText('\n')

  def _ReadPage(self, file_object, file_offset, page_size):
    """Reads a page.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the data relative to the start of
          the file-like object.
      page_size (int): page size.

    Raises:
      ParseError: if the page cannot be read.
    """
    page_data = self._ReadData(
        file_object, file_offset, page_size, 'page data')

    data_type_map = self._GetDataTypeMap('binarycookies_page_header')

    try:
      page_header = self._ReadStructureFromByteStream(
          page_data, file_offset, data_type_map, 'page header')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError((
          f'Unable to map page header data at offset: 0x{file_offset:08x} '
          f'with error: {exception!s}'))

    page_header_data_size = 8 + (4 * page_header.number_of_records)

    if self._debug:
      self._DebugPrintData(
          'Page header data', page_data[:page_header_data_size])

    if self._debug:
      self._DebugPrintValue('Signature', f'0x{page_header.signature:08x}')

      self._DebugPrintValue(
          'Number of records', f'{page_header.number_of_records:d}')

    record_offsets = []
    if page_header.number_of_records > 0:
      for index, record_offset in enumerate(page_header.offsets):
        record_offsets.append(record_offset)

        if self._debug:
          self._DebugPrintValue(
              f'Record: {index:d} offset', f'{record_offset:d}')

      if self._debug:
        self._DebugPrintText('\n')

    for record_offset in record_offsets:
      self._ReadRecord(page_data, record_offset)

  def _ReadPages(self, file_object):
    """Reads the pages.

    Args:
      file_object (file): file-like object.
    """
    file_offset = file_object.tell()
    for page_size in self._page_sizes:
      self._ReadPage(file_object, file_offset, page_size)
      file_offset += page_size

  def _ReadRecord(self, page_data, record_offset):
    """Reads a record from the page data.

    Args:
      page_data (bytes): page data.
      record_offset (int): offset of the record relative to the start
          of the page.

    Raises:
      ParseError: if the record cannot be read.
    """
    data_type_map = self._GetDataTypeMap('binarycookies_record_header')

    try:
      record_header = self._ReadStructureFromByteStream(
          page_data[record_offset:], record_offset, data_type_map,
          'record header')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError((
          f'Unable to map record header data at offset: 0x{record_offset:08x} '
          f'with error: {exception!s}'))

    record_data_size = record_offset + record_header.size

    if self._debug:
      self._DebugPrintData(
          'Record data', page_data[record_offset:record_data_size])

    if self._debug:
      self._DebugPrintRecordHeader(record_header)

    value_string = ''
    if record_header.url_offset:
      data_offset = record_offset + record_header.url_offset
      value_string = self._ReadCString(page_data, data_offset)

    if self._debug:
      self._DebugPrintValue('URL', value_string)

    value_string = ''
    if record_header.name_offset:
      data_offset = record_offset + record_header.name_offset
      value_string = self._ReadCString(page_data, data_offset)

    if self._debug:
      self._DebugPrintValue('Name', value_string)

    value_string = ''
    if record_header.path_offset:
      data_offset = record_offset + record_header.path_offset
      value_string = self._ReadCString(page_data, data_offset)

    if self._debug:
      self._DebugPrintValue('Path', value_string)

    value_string = ''
    if record_header.value_offset:
      data_offset = record_offset + record_header.value_offset
      value_string = self._ReadCString(page_data, data_offset)

    if self._debug:
      self._DebugPrintValue('Value', value_string)

    if self._debug:
      self._DebugPrintText('\n')

  def ReadFileObject(self, file_object):
    """Reads a Safari Cookies (Cookies.binarycookies) file-like object.

    Args:
      file_object (file): file-like object.
    """
    self._ReadFileHeader(file_object)
    self._ReadPages(file_object)
    self._ReadFileFooter(file_object)
