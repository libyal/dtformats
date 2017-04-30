# -*- coding: utf-8 -*-
"""Safari Cookies (Cookies.binarycookies) files."""

import datetime

from dtfabric import errors as dtfabric_errors
from dtfabric import fabric as dtfabric_fabric
from dtfabric import data_maps as dtfabric_data_maps

from dtformats import data_format
from dtformats import errors


class BinaryCookiesFile(data_format.BinaryDataFile):
  """Safari Cookies (Cookies.binarycookies) file."""

  _DATA_TYPE_FABRIC_DEFINITION = b'\n'.join([
      b'name: byte',
      b'type: integer',
      b'attributes:',
      b'  format: unsigned',
      b'  size: 1',
      b'  units: bytes',
      b'---',
      b'name: uint16',
      b'type: integer',
      b'attributes:',
      b'  format: unsigned',
      b'  size: 2',
      b'  units: bytes',
      b'---',
      b'name: uint32',
      b'type: integer',
      b'attributes:',
      b'  format: unsigned',
      b'  size: 4',
      b'  units: bytes',
      b'---',
      b'name: uint32be',
      b'type: integer',
      b'attributes:',
      b'  byte_order: big-endian',
      b'  format: unsigned',
      b'  size: 4',
      b'  units: bytes',
      b'---',
      b'name: uint64',
      b'type: integer',
      b'attributes:',
      b'  format: unsigned',
      b'  size: 8',
      b'  units: bytes',
      b'---',
      b'name: float64',
      b'type: floating-point',
      b'attributes:',
      b'  size: 8',
      b'  units: bytes',
      b'---',
      b'name: cstring',
      b'type: stream',
      b'element_data_type: byte',
      b'elements_terminator: "\\x00"',
      b'---',
      b'name: binarycookies_file_header',
      b'type: structure',
      b'attributes:',
      b'  byte_order: big-endian',
      b'members:',
      b'- name: signature',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 4',
      b'- name: number_of_pages',
      b'  data_type: uint32',
      b'---',
      b'name: binarycookies_page_sizes',
      b'type: sequence',
      b'element_data_type: uint32be',
      b'number_of_elements: binarycookies_file_header.number_of_pages',
      b'---',
      b'name: binarycookies_file_footer',
      b'type: structure',
      b'attributes:',
      b'  byte_order: big-endian',
      b'members:',
      b'- name: unknown1',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 8',
      b'---',
      b'name: binarycookies_page_header',
      b'type: structure',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: signature',
      b'  data_type: uint32',
      b'- name: number_of_records',
      b'  data_type: uint32',
      b'- name: offsets',
      b'  type: sequence',
      b'  element_data_type: uint32',
      b'  number_of_elements: binarycookies_page_header.number_of_records',
      b'---',
      b'name: binarycookies_record_header',
      b'type: structure',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: size',
      b'  data_type: uint32',
      b'- name: unknown1',
      b'  data_type: uint32',
      b'- name: flags',
      b'  data_type: uint32',
      b'- name: unknown2',
      b'  data_type: uint32',
      b'- name: url_offset',
      b'  data_type: uint32',
      b'- name: name_offset',
      b'  data_type: uint32',
      b'- name: path_offset',
      b'  data_type: uint32',
      b'- name: value_offset',
      b'  data_type: uint32',
      b'- name: unknown3',
      b'  data_type: uint64',
      b'- name: expiration_time',
      b'  data_type: float64',
      b'- name: creation_time',
      b'  data_type: float64',
  ])

   # TODO: combine binarycookies_file_header and binarycookies_page_sizes into
   # binarycookies_file_header. Have means to incrementally map.

  _DATA_TYPE_FABRIC = dtfabric_fabric.DataTypeFabric(
      yaml_definition=_DATA_TYPE_FABRIC_DEFINITION)

  _FILE_HEADER = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'binarycookies_file_header')

  _FILE_HEADER_SIZE = _FILE_HEADER.GetByteSize()

  _PAGE_SIZES = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'binarycookies_page_sizes')

  _FILE_FOOTER = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'binarycookies_file_footer')

  _FILE_FOOTER_SIZE = _FILE_FOOTER.GetByteSize()

  _PAGE_HEADER = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'binarycookies_page_header')

  _RECORD_HEADER = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'binarycookies_record_header')

  _RECORD_HEADER_SIZE = _RECORD_HEADER.GetByteSize()

  _CSTRING = _DATA_TYPE_FABRIC.CreateDataTypeMap(u'cstring')

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
    value_string = u'{0!s}'.format(file_header.signature)
    self._DebugPrintValue(u'Signature', value_string)

    value_string = u'{0:d}'.format(file_header.number_of_pages)
    self._DebugPrintValue(u'Number of pages', value_string)

    self._DebugPrintText(u'\n')

  def _DebugPrintRecordHeader(self, record_header):
    """Prints record header debug information.

    Args:
      record_header (binarycookies_record_header): record header.
    """
    value_string = u'{0:d}'.format(record_header.size)
    self._DebugPrintValue(u'Size', value_string)

    value_string = u'0x{0:08x}'.format(record_header.unknown1)
    self._DebugPrintValue(u'Unknown1', value_string)

    value_string = u'0x{0:08x}'.format(record_header.flags)
    self._DebugPrintValue(u'Flags', value_string)

    value_string = u'0x{0:08x}'.format(record_header.unknown2)
    self._DebugPrintValue(u'Unknown2', value_string)

    value_string = u'{0:d}'.format(record_header.url_offset)
    self._DebugPrintValue(u'URL offset', value_string)

    value_string = u'{0:d}'.format(record_header.name_offset)
    self._DebugPrintValue(u'Name offset', value_string)

    value_string = u'{0:d}'.format(record_header.path_offset)
    self._DebugPrintValue(u'Path offset', value_string)

    value_string = u'{0:d}'.format(record_header.value_offset)
    self._DebugPrintValue(u'Value offset', value_string)

    value_string = u'0x{0:08x}'.format(record_header.unknown3)
    self._DebugPrintValue(u'Unknown3', value_string)

    date_time = (datetime.datetime(2001, 1, 1) + datetime.timedelta(
        seconds=int(record_header.expiration_time)))
    value_string = u'{0!s} ({1:f})'.format(
        date_time, record_header.expiration_time)
    self._DebugPrintValue(u'Expiration time', value_string)

    date_time = (datetime.datetime(2001, 1, 1) + datetime.timedelta(
        seconds=int(record_header.creation_time)))
    value_string = u'{0!s} ({1:f})'.format(
        date_time, record_header.creation_time)
    self._DebugPrintValue(u'Creation time', value_string)

    self._DebugPrintText(u'\n')

  def _ReadFileFooter(self, file_object):
    """Reads the file footer.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file footer cannot be read.
    """
    file_offset = file_object.tell()
    self._ReadStructure(
        file_object, file_offset, self._FILE_FOOTER_SIZE, self._FILE_FOOTER,
        u'file footer')

  def _ReadFileHeader(self, file_object):
    """Reads the file header.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file header cannot be read.
    """
    file_offset = file_object.tell()
    file_header = self._ReadStructure(
        file_object, file_offset, self._FILE_HEADER_SIZE, self._FILE_HEADER,
        u'file header')

    if self._debug:
      self._DebugPrintFileHeader(file_header)

    # TODO: check for upper limit.
    page_sizes_data_size = file_header.number_of_pages * 4

    page_sizes_data = file_object.read(page_sizes_data_size)

    if self._debug:
      self._DebugPrintData(u'Page sizes data', page_sizes_data)

    context = dtfabric_data_maps.DataTypeMapContext(values={
        u'binarycookies_file_header': file_header})

    try:
      page_sizes_array = self._PAGE_SIZES.MapByteStream(
          page_sizes_data, context=context)
    except dtfabric_errors.MappingError as exception:
      raise errors.ParseError((
          u'Unable to map page sizes data at offset: 0x{0:08x} with error: '
          u'{1!s}').format(file_offset, exception))

    self._page_sizes = []
    if file_header.number_of_pages > 0:
      for index, page_size in enumerate(page_sizes_array):
        self._page_sizes.append(page_size)

        if self._debug:
          description = u'Page: {0:d} size'.format(index)
          value_string = u'{0:d}'.format(page_size)
          self._DebugPrintValue(description, value_string)

      if self._debug:
        self._DebugPrintText(u'\n')

  def _ReadPage(self, file_object, file_offset, page_size):
    """Reads the page.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the data relative from the start of
          the file-like object.
      page_size (int): page size.

    Raises:
      ParseError: if the page cannot be read.
    """
    page_data = self._ReadData(
        file_object, file_offset, page_size, u'page data')

    try:
      page_header = self._PAGE_HEADER.MapByteStream(page_data)
    except dtfabric_errors.MappingError as exception:
      raise errors.ParseError((
          u'Unable to map page header data at offset: 0x{0:08x} with error: '
          u'{1!s}').format(file_offset, exception))

    page_header_data_size = 8 + (4 * page_header.number_of_records)

    if self._debug:
      self._DebugPrintData(
          u'Page header data', page_data[:page_header_data_size])

    if self._debug:
      value_string = u'0x{0:08x}'.format(page_header.signature)
      self._DebugPrintValue(u'Signature', value_string)

      value_string = u'{0:d}'.format(page_header.number_of_records)
      self._DebugPrintValue(u'Number of records', value_string)

    record_offsets = []
    if page_header.number_of_records > 0:
      for index, record_offset in enumerate(page_header.offsets):
        record_offsets.append(record_offset)

        if self._debug:
          description = u'Record: {0:d} offset'.format(index)
          value_string = u'{0:d}'.format(record_offset)
          self._DebugPrintValue(description, value_string)

      if self._debug:
        self._DebugPrintText(u'\n')

    for record_offset in iter(record_offsets):
      self._ReadRecord(page_data, record_offset)

  def _ReadPages(self, file_object):
    """Reads the pages.

    Args:
      file_object (file): file-like object.
    """
    file_offset = file_object.tell()
    for page_size in iter(self._page_sizes):
      self._ReadPage(file_object, file_offset, page_size)
      file_offset += page_size

  def _ReadRecord(self, page_data, record_offset):
    """Reads a record from the page data.

    Args:
      page_data (bytes): page data.
      record_offset (int): record offset.

    Raises:
      ParseError: if the record cannot be read.
    """
    try:
      record_header = self._RECORD_HEADER.MapByteStream(
          page_data[record_offset:])
    except dtfabric_errors.MappingError as exception:
      raise errors.ParseError((
          u'Unable to map record header data at offset: 0x{0:08x} with error: '
          u'{1!s}').format(record_offset, exception))

    record_data_size = record_offset + record_header.size

    if self._debug:
      self._DebugPrintData(
          u'Record data', page_data[record_offset:record_data_size])

    if self._debug:
      self._DebugPrintRecordHeader(record_header)

      value_string = u''
      if record_header.url_offset:
        data_offset = record_offset + record_header.url_offset
        try:
          value_string = self._CSTRING.MapByteStream(
              page_data[data_offset:record_data_size])

        except dtfabric_errors.MappingError as exception:
          raise errors.ParseError((
              u'Unable to map URL data at offset: 0x{0:08x} with error: '
              u'{1!s}').format(data_offset, exception))

      self._DebugPrintValue(u'URL', value_string)

      value_string = u''
      if record_header.name_offset:
        data_offset = record_offset + record_header.name_offset
        try:
          value_string = self._CSTRING.MapByteStream(
              page_data[data_offset:record_data_size])

        except dtfabric_errors.MappingError as exception:
          raise errors.ParseError((
              u'Unable to map name data at offset: 0x{0:08x} with error: '
              u'{1!s}').format(data_offset, exception))

      self._DebugPrintValue(u'Name', value_string)

      value_string = u''
      if record_header.path_offset:
        data_offset = record_offset + record_header.path_offset
        try:
          value_string = self._CSTRING.MapByteStream(
              page_data[data_offset:record_data_size])

        except dtfabric_errors.MappingError as exception:
          raise errors.ParseError((
              u'Unable to map path data at offset: 0x{0:08x} with error: '
              u'{1!s}').format(data_offset, exception))

      self._DebugPrintValue(u'Path', value_string)

      value_string = u''
      if record_header.value_offset:
        data_offset = record_offset + record_header.value_offset
        try:
          value_string = self._CSTRING.MapByteStream(
              page_data[data_offset:record_data_size])

        except dtfabric_errors.MappingError as exception:
          raise errors.ParseError((
              u'Unable to map value data at offset: 0x{0:08x} with error: '
              u'{1!s}').format(data_offset, exception))

      self._DebugPrintValue(u'Value', value_string)

      self._DebugPrintText(u'\n')

  def ReadFileObject(self, file_object):
    """Reads a Safari Cookies (Cookies.binarycookies) file-like object.

    Args:
      file_object (file): file-like object.
    """
    self._ReadFileHeader(file_object)
    self._ReadPages(file_object)
    self._ReadFileFooter(file_object)
