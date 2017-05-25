# -*- coding: utf-8 -*-
"""Windows (Enhanced) Metafile Format (WMF and EMF) files."""

import os

from dtfabric import errors as dtfabric_errors
from dtfabric.runtime import fabric as dtfabric_fabric

from dtformats import data_format
from dtformats import errors


class Record(object):
  """Windows (Enhanced) Metafile Format (WMF and EMF) record.

  Attributes:
    data_offset (int): record data offset.
    data_size (int): record data size.
    record_type (int): record type.
    size (int): record size.
  """

  def __init__(self, record_type, size, data_offset, data_size):
    """Initializes an EMF or WMF record.

    Args:
      record_type (int): record type.
      size (int): record size.
      data_offset (int): record data offset.
      data_size (int): record data size.
    """
    super(Record, self).__init__()
    self.data_offset = data_offset
    self.data_size = data_size
    self.record_type = record_type
    self.size = size


class EMFFile(data_format.BinaryDataFile):
  """Enhanced Metafile Format (EMF) file."""

  FILE_TYPE = u'Windows Enhanced Metafile'

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
      b'name: emf_record_type',
      b'type: enumeration',
      b'urls: ["https://msdn.microsoft.com/en-us/library/cc230533.aspx"]',
      b'values:',
      b'- name: EMR_HEADER',
      b'  number: 0x00000001',
      b'- name: EMR_POLYBEZIER',
      b'  number: 0x00000002',
      b'- name: EMR_POLYGON',
      b'  number: 0x00000003',
      b'- name: EMR_POLYLINE',
      b'  number: 0x00000004',
      b'- name: EMR_POLYBEZIERTO',
      b'  number: 0x00000005',
      b'- name: EMR_POLYLINETO',
      b'  number: 0x00000006',
      b'- name: EMR_POLYPOLYLINE',
      b'  number: 0x00000007',
      b'- name: EMR_POLYPOLYGON',
      b'  number: 0x00000008',
      b'- name: EMR_SETWINDOWEXTEX',
      b'  number: 0x00000009',
      b'- name: EMR_SETWINDOWORGEX',
      b'  number: 0x0000000a',
      b'- name: EMR_SETVIEWPORTEXTEX',
      b'  number: 0x0000000b',
      b'- name: EMR_SETVIEWPORTORGEX',
      b'  number: 0x0000000c',
      b'- name: EMR_SETBRUSHORGEX',
      b'  number: 0x0000000d',
      b'- name: EMR_EOF',
      b'  number: 0x0000000e',
      b'- name: EMR_SETPIXELV',
      b'  number: 0x0000000f',
      b'- name: EMR_SETMAPPERFLAGS',
      b'  number: 0x00000010',
      b'- name: EMR_SETMAPMODE',
      b'  number: 0x00000011',
      b'- name: EMR_SETBKMODE',
      b'  number: 0x00000012',
      b'- name: EMR_SETPOLYFILLMODE',
      b'  number: 0x00000013',
      b'- name: EMR_SETROP2',
      b'  number: 0x00000014',
      b'- name: EMR_SETSTRETCHBLTMODE',
      b'  number: 0x00000015',
      b'- name: EMR_SETTEXTALIGN',
      b'  number: 0x00000016',
      b'- name: EMR_SETCOLORADJUSTMENT',
      b'  number: 0x00000017',
      b'- name: EMR_SETTEXTCOLOR',
      b'  number: 0x00000018',
      b'- name: EMR_SETBKCOLOR',
      b'  number: 0x00000019',
      b'- name: EMR_OFFSETCLIPRGN',
      b'  number: 0x0000001a',
      b'- name: EMR_MOVETOEX',
      b'  number: 0x0000001b',
      b'- name: EMR_SETMETARGN',
      b'  number: 0x0000001c',
      b'- name: EMR_EXCLUDECLIPRECT',
      b'  number: 0x0000001d',
      b'- name: EMR_INTERSECTCLIPRECT',
      b'  number: 0x0000001e',
      b'- name: EMR_SCALEVIEWPORTEXTEX',
      b'  number: 0x0000001f',
      b'- name: EMR_SCALEWINDOWEXTEX',
      b'  number: 0x00000020',
      b'- name: EMR_SAVEDC',
      b'  number: 0x00000021',
      b'- name: EMR_RESTOREDC',
      b'  number: 0x00000022',
      b'- name: EMR_SETWORLDTRANSFORM',
      b'  number: 0x00000023',
      b'- name: EMR_MODIFYWORLDTRANSFORM',
      b'  number: 0x00000024',
      b'- name: EMR_SELECTOBJECT',
      b'  number: 0x00000025',
      b'- name: EMR_CREATEPEN',
      b'  number: 0x00000026',
      b'- name: EMR_CREATEBRUSHINDIRECT',
      b'  number: 0x00000027',
      b'- name: EMR_DELETEOBJECT',
      b'  number: 0x00000028',
      b'- name: EMR_ANGLEARC',
      b'  number: 0x00000029',
      b'- name: EMR_ELLIPSE',
      b'  number: 0x0000002a',
      b'- name: EMR_RECTANGLE',
      b'  number: 0x0000002b',
      b'- name: EMR_ROUNDRECT',
      b'  number: 0x0000002c',
      b'- name: EMR_ARC',
      b'  number: 0x0000002d',
      b'- name: EMR_CHORD',
      b'  number: 0x0000002e',
      b'- name: EMR_PIE',
      b'  number: 0x0000002f',
      b'- name: EMR_SELECTPALETTE',
      b'  number: 0x00000030',
      b'- name: EMR_CREATEPALETTE',
      b'  number: 0x00000031',
      b'- name: EMR_SETPALETTEENTRIES',
      b'  number: 0x00000032',
      b'- name: EMR_RESIZEPALETTE',
      b'  number: 0x00000033',
      b'- name: EMR_REALIZEPALETTE',
      b'  number: 0x00000034',
      b'- name: EMR_EXTFLOODFILL',
      b'  number: 0x00000035',
      b'- name: EMR_LINETO',
      b'  number: 0x00000036',
      b'- name: EMR_ARCTO',
      b'  number: 0x00000037',
      b'- name: EMR_POLYDRAW',
      b'  number: 0x00000038',
      b'- name: EMR_SETARCDIRECTION',
      b'  number: 0x00000039',
      b'- name: EMR_SETMITERLIMIT',
      b'  number: 0x0000003a',
      b'- name: EMR_BEGINPATH',
      b'  number: 0x0000003b',
      b'- name: EMR_ENDPATH',
      b'  number: 0x0000003c',
      b'- name: EMR_CLOSEFIGURE',
      b'  number: 0x0000003d',
      b'- name: EMR_FILLPATH',
      b'  number: 0x0000003e',
      b'- name: EMR_STROKEANDFILLPATH',
      b'  number: 0x0000003f',
      b'- name: EMR_STROKEPATH',
      b'  number: 0x00000040',
      b'- name: EMR_FLATTENPATH',
      b'  number: 0x00000041',
      b'- name: EMR_WIDENPATH',
      b'  number: 0x00000042',
      b'- name: EMR_SELECTCLIPPATH',
      b'  number: 0x00000043',
      b'- name: EMR_ABORTPATH',
      b'  number: 0x00000044',
      b'- name: EMR_COMMENT',
      b'  number: 0x00000046',
      b'- name: EMR_FILLRGN',
      b'  number: 0x00000047',
      b'- name: EMR_FRAMERGN',
      b'  number: 0x00000048',
      b'- name: EMR_INVERTRGN',
      b'  number: 0x00000049',
      b'- name: EMR_PAINTRGN',
      b'  number: 0x0000004a',
      b'- name: EMR_EXTSELECTCLIPRGN',
      b'  number: 0x0000004b',
      b'- name: EMR_BITBLT',
      b'  number: 0x0000004c',
      b'- name: EMR_STRETCHBLT',
      b'  number: 0x0000004d',
      b'- name: EMR_MASKBLT',
      b'  number: 0x0000004e',
      b'- name: EMR_PLGBLT',
      b'  number: 0x0000004f',
      b'- name: EMR_SETDIBITSTODEVICE',
      b'  number: 0x00000050',
      b'- name: EMR_STRETCHDIBITS',
      b'  number: 0x00000051',
      b'- name: EMR_EXTCREATEFONTINDIRECTW',
      b'  number: 0x00000052',
      b'- name: EMR_EXTTEXTOUTA',
      b'  number: 0x00000053',
      b'- name: EMR_EXTTEXTOUTW',
      b'  number: 0x00000054',
      b'- name: EMR_POLYBEZIER16',
      b'  number: 0x00000055',
      b'- name: EMR_POLYGON16',
      b'  number: 0x00000056',
      b'- name: EMR_POLYLINE16',
      b'  number: 0x00000057',
      b'- name: EMR_POLYBEZIERTO16',
      b'  number: 0x00000058',
      b'- name: EMR_POLYLINETO16',
      b'  number: 0x00000059',
      b'- name: EMR_POLYPOLYLINE16',
      b'  number: 0x0000005a',
      b'- name: EMR_POLYPOLYGON16',
      b'  number: 0x0000005b',
      b'- name: EMR_POLYDRAW16',
      b'  number: 0x0000005c',
      b'- name: EMR_CREATEMONOBRUSH',
      b'  number: 0x0000005d',
      b'- name: EMR_CREATEDIBPATTERNBRUSHPT',
      b'  number: 0x0000005e',
      b'- name: EMR_EXTCREATEPEN',
      b'  number: 0x0000005f',
      b'- name: EMR_POLYTEXTOUTA',
      b'  number: 0x00000060',
      b'- name: EMR_POLYTEXTOUTW',
      b'  number: 0x00000061',
      b'- name: EMR_SETICMMODE',
      b'  number: 0x00000062',
      b'- name: EMR_CREATECOLORSPACE',
      b'  number: 0x00000063',
      b'- name: EMR_SETCOLORSPACE',
      b'  number: 0x00000064',
      b'- name: EMR_DELETECOLORSPACE',
      b'  number: 0x00000065',
      b'- name: EMR_GLSRECORD',
      b'  number: 0x00000066',
      b'- name: EMR_GLSBOUNDEDRECORD',
      b'  number: 0x00000067',
      b'- name: EMR_PIXELFORMAT',
      b'  number: 0x00000068',
      b'- name: EMR_DRAWESCAPE',
      b'  number: 0x00000069',
      b'- name: EMR_EXTESCAPE',
      b'  number: 0x0000006a',
      b'- name: EMR_SMALLTEXTOUT',
      b'  number: 0x0000006c',
      b'- name: EMR_FORCEUFIMAPPING',
      b'  number: 0x0000006d',
      b'- name: EMR_NAMEDESCAPE',
      b'  number: 0x0000006e',
      b'- name: EMR_COLORCORRECTPALETTE',
      b'  number: 0x0000006f',
      b'- name: EMR_SETICMPROFILEA',
      b'  number: 0x00000070',
      b'- name: EMR_SETICMPROFILEW',
      b'  number: 0x00000071',
      b'- name: EMR_ALPHABLEND',
      b'  number: 0x00000072',
      b'- name: EMR_SETLAYOUT',
      b'  number: 0x00000073',
      b'- name: EMR_TRANSPARENTBLT',
      b'  number: 0x00000074',
      b'- name: EMR_GRADIENTFILL',
      b'  number: 0x00000076',
      b'- name: EMR_SETLINKEDUFIS',
      b'  number: 0x00000077',
      b'- name: EMR_SETTEXTJUSTIFICATION',
      b'  number: 0x00000078',
      b'- name: EMR_COLORMATCHTOTARGETW',
      b'  number: 0x00000079',
      b'- name: EMR_CREATECOLORSPACEW',
      b'  number: 0x0000007a',
      b'---',
      b'name: emf_stock_object',
      b'type: enumeration',
      b'urls: ["https://msdn.microsoft.com/en-us/library/cc231191.aspx"]',
      b'values:',
      b'- name: WHITE_BRUSH',
      b'  number: 0x80000000',
      b'- name: LTGRAY_BRUSH',
      b'  number: 0x80000001',
      b'- name: GRAY_BRUSH',
      b'  number: 0x80000002',
      b'- name: DKGRAY_BRUSH',
      b'  number: 0x80000003',
      b'- name: BLACK_BRUSH',
      b'  number: 0x80000004',
      b'- name: NULL_BRUSH',
      b'  number: 0x80000005',
      b'- name: WHITE_PEN',
      b'  number: 0x80000006',
      b'- name: BLACK_PEN',
      b'  number: 0x80000007',
      b'- name: NULL_PEN',
      b'  number: 0x80000008',
      b'- name: OEM_FIXED_FONT',
      b'  number: 0x8000000A',
      b'- name: ANSI_FIXED_FONT',
      b'  number: 0x8000000B',
      b'- name: ANSI_VAR_FONT',
      b'  number: 0x8000000C',
      b'- name: SYSTEM_FONT',
      b'  number: 0x8000000D',
      b'- name: DEVICE_DEFAULT_FONT',
      b'  number: 0x8000000E',
      b'- name: DEFAULT_PALETTE',
      b'  number: 0x8000000F',
      b'- name: SYSTEM_FIXED_FONT',
      b'  number: 0x80000010',
      b'- name: DEFAULT_GUI_FONT',
      b'  number: 0x80000011',
      b'- name: DC_BRUSH',
      b'  number: 0x80000012',
      b'- name: DC_PEN',
      b'  number: 0x80000013',
      b'---',
      b'name: emf_file_header',
      b'type: structure',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: record_type',
      b'  data_type: uint32',
      # TODO: link to emf_record_type
      b'- name: record_size',
      b'  data_type: uint32',
      b'- name: bounds_rectangle',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 16',
      b'- name: frame_rectangle',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 16',
      b'- name: signature',
      b'  data_type: uint32',
      b'- name: format_version',
      b'  data_type: uint32',
      b'- name: file_size',
      b'  data_type: uint32',
      b'- name: number_of_records',
      b'  data_type: uint32',
      b'- name: number_of_handles',
      b'  data_type: uint16',
      b'- name: unknown1',
      b'  data_type: uint16',
      b'- name: description_string_size',
      b'  data_type: uint32',
      b'- name: description_string_offset',
      b'  data_type: uint32',
      b'- name: number_of_palette_entries',
      b'  data_type: uint32',
      b'- name: reference_device_resolution_pixels',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 8',
      b'- name: reference_device_resolution_millimeters',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 8',
      b'- name: pixel_format_descriptor_size',
      b'  data_type: uint32',
      b'- name: pixel_format_descriptor_offset',
      b'  data_type: uint32',
      b'- name: has_opengl',
      b'  data_type: uint32',
      b'- name: reference_device_resolution_micrometers',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 8',
      b'---',
      b'name: emf_record_header',
      b'type: structure',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: record_type',
      b'  data_type: uint32',
      # TODO: link to emf_record_type
      b'- name: record_size',
      b'  data_type: uint32',
      b'---',
      b'name: emf_settextcolor',
      b'type: structure',
      b'urls: ["https://msdn.microsoft.com/en-us/library/cc250420.aspx"]',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: color',
      b'  data_type: uint32',
      b'---',
      b'name: emf_selectobject',
      b'type: structure',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: object_identifier',
      b'  data_type: uint32',
  ])

  _DATA_TYPE_FABRIC = dtfabric_fabric.DataTypeFabric(
      yaml_definition=_DATA_TYPE_FABRIC_DEFINITION)

  _RECORD_TYPE = _DATA_TYPE_FABRIC.CreateDataTypeMap(u'emf_record_type')

  _FILE_HEADER = _DATA_TYPE_FABRIC.CreateDataTypeMap(u'emf_file_header')

  _FILE_HEADER_SIZE = _FILE_HEADER.GetByteSize()

  _RECORD_HEADER = _DATA_TYPE_FABRIC.CreateDataTypeMap(u'emf_record_header')

  _RECORD_HEADER_SIZE = _RECORD_HEADER.GetByteSize()

  _EMF_SIGNATURE = b'FME\x20'

  # Here None represents that the record has no additional data.
  _EMF_RECORD_DATA_STRUCT_TYPES = {
      0x0018: _DATA_TYPE_FABRIC.CreateDataTypeMap(u'emf_settextcolor'),
      0x0025: _DATA_TYPE_FABRIC.CreateDataTypeMap(u'emf_selectobject')}

  _EMF_STOCK_OBJECT = _DATA_TYPE_FABRIC.CreateDataTypeMap(u'emf_stock_object')

  def _DebugPrintFileHeader(self, file_header):
    """Prints file header debug information.

    Args:
      file_header (emf_file_header): file header.
    """
    record_type_string = self._RECORD_TYPE.GetName(file_header.record_type)
    value_string = u'0x{0:04x} ({1:s})'.format(
        file_header.record_type, record_type_string or u'UNKNOWN')
    self._DebugPrintValue(u'Record type', value_string)

    value_string = u'{0:d}'.format(file_header.record_size)
    self._DebugPrintValue(u'Record size', value_string)

    value_string = u'0x{0:04x}'.format(file_header.signature)
    self._DebugPrintValue(u'Signature', value_string)

    value_string = u'0x{0:04x}'.format(file_header.format_version)
    self._DebugPrintValue(u'Format version', value_string)

    value_string = u'{0:d}'.format(file_header.file_size)
    self._DebugPrintValue(u'File size', value_string)

    value_string = u'{0:d}'.format(file_header.number_of_records)
    self._DebugPrintValue(u'Number of records', value_string)

    value_string = u'{0:d}'.format(file_header.number_of_handles)
    self._DebugPrintValue(u'Number of handles', value_string)

    value_string = u'0x{0:04x}'.format(file_header.unknown1)
    self._DebugPrintValue(u'Unknown (reserved)', value_string)

    value_string = u'{0:d}'.format(file_header.description_string_size)
    self._DebugPrintValue(u'Description string size', value_string)

    value_string = u'0x{0:04x}'.format(file_header.description_string_offset)
    self._DebugPrintValue(u'Description string offset', value_string)

    self._DebugPrintText(u'\n')

  def _DebugPrintRecordHeader(self, record_header):
    """Prints record header debug information.

    Args:
      record_header (emf_record_header): record header.
    """
    record_type_string = self._RECORD_TYPE.GetName(record_header.record_type)
    value_string = u'0x{0:04x} ({1:s})'.format(
        record_header.record_type, record_type_string or u'UNKNOWN')
    self._DebugPrintValue(u'Record type', value_string)

    value_string = u'{0:d}'.format(record_header.record_size)
    self._DebugPrintValue(u'Record size', value_string)

    self._DebugPrintText(u'\n')

  def _ReadFileHeader(self, file_object):
    """Reads a file header.

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

    # TODO: check record type
    # TODO: check record size
    # TODO: check signature

  def _ReadRecord(self, file_object, file_offset):
    """Reads a record.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the data relative from the start of
          the file-like object.

    Raises:
      ParseError: if the record cannot be read.
    """
    record_header = self._ReadStructure(
        file_object, file_offset, self._RECORD_HEADER_SIZE, self._RECORD_HEADER,
        u'record header')

    if self._debug:
      self._DebugPrintRecordHeader(record_header)

    data_offset = file_offset + self._RECORD_HEADER_SIZE
    data_size = record_header.record_size - self._RECORD_HEADER_SIZE

    if self._debug:
      self._ReadRecordData(
          file_object, record_header.record_type, data_size)

    return Record(
        record_header.record_type,
        record_header.record_size, data_offset, data_size)

  def _ReadRecordData(self, file_object, record_type, data_size):
    """Reads a record.

    Args:
      file_object (file): file-like object.
      record_type (int): record type.
      data_size (int): size of the record data.

    Raises:
      ParseError: if the record data cannot be read.
    """
    record_data = file_object.read(data_size)

    if self._debug and data_size > 0:
      self._DebugPrintData(u'Record data', record_data)

    # TODO: use lookup dict with callback.
    data_type_map = self._EMF_RECORD_DATA_STRUCT_TYPES.get(record_type, None)
    if not data_type_map:
      return

    try:
      record = data_type_map.MapByteStream(record_data)
    except dtfabric_errors.MappingError as exception:
      raise errors.ParseError((
          u'Unable to parse record data with error: {0:s}').format(exception))

    if self._debug:
      if record_type == 0x0018:
        value_string = u'0x{0:04x}'.format(record.color)
        self._DebugPrintValue(u'Color', value_string)

      elif record_type == 0x0025:
        stock_object_string = self._EMF_STOCK_OBJECT.GetName(
            record.object_identifier)

        if stock_object_string:
          value_string = u'0x{0:08x} ({1:s})'.format(
              record.object_identifier, stock_object_string)
        else:
          value_string = u'0x{0:08x}'.format(
              record.object_identifier)

        self._DebugPrintValue(u'Object identifier', value_string)

      self._DebugPrintText(u'\n')

  def ReadFileObject(self, file_object):
    """Reads a Enhanced Metafile Format (EMF) file-like object.

    Args:
      file_object (file): file-like object.
    """
    self._ReadFileHeader(file_object)

    file_offset = file_object.tell()
    while file_offset < self._file_size:
      record = self._ReadRecord(file_object, file_offset)

      file_offset += record.size


class WMFFile(data_format.BinaryDataFile):
  """Windows Metafile Format (WMF) file."""

  FILE_TYPE = u'Windows Metafile'

  # https://msdn.microsoft.com/en-us/library/cc250370.aspx
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
      b'name: wmf_map_mode',
      b'type: enumeration',
      b'urls: ["https://msdn.microsoft.com/en-us/library/cc250397.aspx"]',
      b'values:',
      b'- name: MM_TEXT',
      b'  number: 0x0001',
      b'- name: MM_LOMETRIC',
      b'  number: 0x0002',
      b'- name: MM_HIMETRIC',
      b'  number: 0x0003',
      b'- name: MM_LOENGLISH',
      b'  number: 0x0004',
      b'- name: MM_HIENGLISH',
      b'  number: 0x0005',
      b'- name: MM_TWIPS',
      b'  number: 0x0006',
      b'- name: MM_ISOTROPIC',
      b'  number: 0x0007',
      b'- name: MM_ANISOTROPIC',
      b'  number: 0x0008',
      b'---',
      b'name: wmf_raster_operation_code',
      b'aliases: [TernaryRasterOperation]',
      b'type: enumeration',
      b'urls: ["https://msdn.microsoft.com/en-us/library/cc250408.aspx"]',
      b'values:',
      b'- name: BLACKNESS',
      b'  number: 0x00',
      b'- name: DPSOON',
      b'  number: 0x01',
      b'- name: DPSONA',
      b'  number: 0x02',
      b'- name: PSON',
      b'  number: 0x03',
      b'- name: SDPONA',
      b'  number: 0x04',
      b'- name: DPON',
      b'  number: 0x05',
      b'- name: PDSXNON',
      b'  number: 0x06',
      b'- name: PDSAON',
      b'  number: 0x07',
      b'- name: SDPNAA',
      b'  number: 0x08',
      b'- name: PDSXON',
      b'  number: 0x09',
      b'- name: DPNA',
      b'  number: 0x0a',
      b'- name: PSDNAON',
      b'  number: 0x0b',
      b'- name: SPNA',
      b'  number: 0x0c',
      b'- name: PDSNAON',
      b'  number: 0x0d',
      b'- name: PDSONON',
      b'  number: 0x0e',
      b'- name: PN',
      b'  number: 0x0f',
      b'- name: PDSONA',
      b'  number: 0x10',
      b'- name: NOTSRCERASE',
      b'  number: 0x11',
      b'- name: SDPXNON',
      b'  number: 0x12',
      b'- name: SDPAON',
      b'  number: 0x13',
      b'- name: DPSXNON',
      b'  number: 0x14',
      b'- name: DPSAON',
      b'  number: 0x15',
      b'- name: PSDPSANAXX',
      b'  number: 0x16',
      b'- name: SSPXDSXAXN',
      b'  number: 0x17',
      b'- name: SPXPDXA',
      b'  number: 0x18',
      b'- name: SDPSANAXN',
      b'  number: 0x19',
      b'- name: PDSPAOX',
      b'  number: 0x1a',
      b'- name: SDPSXAXN',
      b'  number: 0x1b',
      b'- name: PSDPAOX',
      b'  number: 0x1c',
      b'- name: DSPDXAXN',
      b'  number: 0x1d',
      b'- name: PDSOX',
      b'  number: 0x1e',
      b'- name: PDSOAN',
      b'  number: 0x1f',
      b'- name: DPSNAA',
      b'  number: 0x20',
      b'- name: SDPXON',
      b'  number: 0x21',
      b'- name: DSNA',
      b'  number: 0x22',
      b'- name: SPDNAON',
      b'  number: 0x23',
      b'- name: SPXDSXA',
      b'  number: 0x24',
      b'- name: PDSPANAXN',
      b'  number: 0x25',
      b'- name: SDPSAOX',
      b'  number: 0x26',
      b'- name: SDPSXNOX',
      b'  number: 0x27',
      b'- name: DPSXA',
      b'  number: 0x28',
      b'- name: PSDPSAOXXN',
      b'  number: 0x29',
      b'- name: DPSANA',
      b'  number: 0x2a',
      b'- name: SSPXPDXAXN',
      b'  number: 0x2b',
      b'- name: SPDSOAX',
      b'  number: 0x2c',
      b'- name: PSDNOX',
      b'  number: 0x2d',
      b'- name: PSDPXOX',
      b'  number: 0x2e',
      b'- name: PSDNOAN',
      b'  number: 0x2f',
      b'- name: PSNA',
      b'  number: 0x30',
      b'- name: SDPNAON',
      b'  number: 0x31',
      b'- name: SDPSOOX',
      b'  number: 0x32',
      b'- name: NOTSRCCOPY',
      b'  number: 0x33',
      b'- name: SPDSAOX',
      b'  number: 0x34',
      b'- name: SPDSXNOX',
      b'  number: 0x35',
      b'- name: SDPOX',
      b'  number: 0x36',
      b'- name: SDPOAN',
      b'  number: 0x37',
      b'- name: PSDPOAX',
      b'  number: 0x38',
      b'- name: SPDNOX',
      b'  number: 0x39',
      b'- name: SPDSXOX',
      b'  number: 0x3a',
      b'- name: SPDNOAN',
      b'  number: 0x3b',
      b'- name: PSX',
      b'  number: 0x3c',
      b'- name: SPDSONOX',
      b'  number: 0x3d',
      b'- name: SPDSNAOX',
      b'  number: 0x3e',
      b'- name: PSAN',
      b'  number: 0x3f',
      b'- name: PSDNAA',
      b'  number: 0x40',
      b'- name: DPSXON',
      b'  number: 0x41',
      b'- name: SDXPDXA',
      b'  number: 0x42',
      b'- name: SPDSANAXN',
      b'  number: 0x43',
      b'- name: SRCERASE',
      b'  number: 0x44',
      b'- name: DPSNAON',
      b'  number: 0x45',
      b'- name: DSPDAOX',
      b'  number: 0x46',
      b'- name: PSDPXAXN',
      b'  number: 0x47',
      b'- name: SDPXA',
      b'  number: 0x48',
      b'- name: PDSPDAOXXN',
      b'  number: 0x49',
      b'- name: DPSDOAX',
      b'  number: 0x4a',
      b'- name: PDSNOX',
      b'  number: 0x4b',
      b'- name: SDPANA',
      b'  number: 0x4c',
      b'- name: SSPXDSXOXN',
      b'  number: 0x4d',
      b'- name: PDSPXOX',
      b'  number: 0x4e',
      b'- name: PDSNOAN',
      b'  number: 0x4f',
      b'- name: PDNA',
      b'  number: 0x50',
      b'- name: DSPNAON',
      b'  number: 0x51',
      b'- name: DPSDAOX',
      b'  number: 0x52',
      b'- name: SPDSXAXN',
      b'  number: 0x53',
      b'- name: DPSONON',
      b'  number: 0x54',
      b'- name: DSTINVERT',
      b'  number: 0x55',
      b'- name: DPSOX',
      b'  number: 0x56',
      b'- name: DPSOAN',
      b'  number: 0x57',
      b'- name: PDSPOAX',
      b'  number: 0x58',
      b'- name: DPSNOX',
      b'  number: 0x59',
      b'- name: PATINVERT',
      b'  number: 0x5a',
      b'- name: DPSDONOX',
      b'  number: 0x5b',
      b'- name: DPSDXOX',
      b'  number: 0x5c',
      b'- name: DPSNOAN',
      b'  number: 0x5d',
      b'- name: DPSDNAOX',
      b'  number: 0x5e',
      b'- name: DPAN',
      b'  number: 0x5f',
      b'- name: PDSXA',
      b'  number: 0x60',
      b'- name: DSPDSAOXXN',
      b'  number: 0x61',
      b'- name: DSPDOAX',
      b'  number: 0x62',
      b'- name: SDPNOX',
      b'  number: 0x63',
      b'- name: SDPSOAX',
      b'  number: 0x64',
      b'- name: DSPNOX',
      b'  number: 0x65',
      b'- name: SRCINVERT',
      b'  number: 0x66',
      b'- name: SDPSONOX',
      b'  number: 0x67',
      b'- name: DSPDSONOXXN',
      b'  number: 0x68',
      b'- name: PDSXXN',
      b'  number: 0x69',
      b'- name: DPSAX',
      b'  number: 0x6a',
      b'- name: PSDPSOAXXN',
      b'  number: 0x6b',
      b'- name: SDPAX',
      b'  number: 0x6c',
      b'- name: PDSPDOAXXN',
      b'  number: 0x6d',
      b'- name: SDPSNOAX',
      b'  number: 0x6e',
      b'- name: PDXNAN',
      b'  number: 0x6f',
      b'- name: PDSANA',
      b'  number: 0x70',
      b'- name: SSDXPDXAXN',
      b'  number: 0x71',
      b'- name: SDPSXOX',
      b'  number: 0x72',
      b'- name: SDPNOAN',
      b'  number: 0x73',
      b'- name: DSPDXOX',
      b'  number: 0x74',
      b'- name: DSPNOAN',
      b'  number: 0x75',
      b'- name: SDPSNAOX',
      b'  number: 0x76',
      b'- name: DSAN',
      b'  number: 0x77',
      b'- name: PDSAX',
      b'  number: 0x78',
      b'- name: DSPDSOAXXN',
      b'  number: 0x79',
      b'- name: DPSDNOAX',
      b'  number: 0x7a',
      b'- name: SDPXNAN',
      b'  number: 0x7b',
      b'- name: SPDSNOAX',
      b'  number: 0x7c',
      b'- name: DPSXNAN',
      b'  number: 0x7d',
      b'- name: SPXDSXO',
      b'  number: 0x7e',
      b'- name: DPSAAN',
      b'  number: 0x7f',
      b'- name: DPSAA',
      b'  number: 0x80',
      b'- name: SPXDSXON',
      b'  number: 0x81',
      b'- name: DPSXNA',
      b'  number: 0x82',
      b'- name: SPDSNOAXN',
      b'  number: 0x83',
      b'- name: SDPXNA',
      b'  number: 0x84',
      b'- name: PDSPNOAXN',
      b'  number: 0x85',
      b'- name: DSPDSOAXX',
      b'  number: 0x86',
      b'- name: PDSAXN',
      b'  number: 0x87',
      b'- name: SRCAND',
      b'  number: 0x88',
      b'- name: SDPSNAOXN',
      b'  number: 0x89',
      b'- name: DSPNOA',
      b'  number: 0x8a',
      b'- name: DSPDXOXN',
      b'  number: 0x8b',
      b'- name: SDPNOA',
      b'  number: 0x8c',
      b'- name: SDPSXOXN',
      b'  number: 0x8d',
      b'- name: SSDXPDXAX',
      b'  number: 0x8e',
      b'- name: PDSANAN',
      b'  number: 0x8f',
      b'- name: PDSXNA',
      b'  number: 0x90',
      b'- name: SDPSNOAXN',
      b'  number: 0x91',
      b'- name: DPSDPOAXX',
      b'  number: 0x92',
      b'- name: SPDAXN',
      b'  number: 0x93',
      b'- name: PSDPSOAXX',
      b'  number: 0x94',
      b'- name: DPSAXN',
      b'  number: 0x95',
      b'- name: DPSXX',
      b'  number: 0x96',
      b'- name: PSDPSONOXX',
      b'  number: 0x97',
      b'- name: SDPSONOXN',
      b'  number: 0x98',
      b'- name: DSXN',
      b'  number: 0x99',
      b'- name: DPSNAX',
      b'  number: 0x9a',
      b'- name: SDPSOAXN',
      b'  number: 0x9b',
      b'- name: SPDNAX',
      b'  number: 0x9c',
      b'- name: DSPDOAXN',
      b'  number: 0x9d',
      b'- name: DSPDSAOXX',
      b'  number: 0x9e',
      b'- name: PDSXAN',
      b'  number: 0x9f',
      b'- name: DPA',
      b'  number: 0xa0',
      b'- name: PDSPNAOXN',
      b'  number: 0xa1',
      b'- name: DPSNOA',
      b'  number: 0xa2',
      b'- name: DPSDXOXN',
      b'  number: 0xa3',
      b'- name: PDSPONOXN',
      b'  number: 0xa4',
      b'- name: PDXN',
      b'  number: 0xa5',
      b'- name: DSPNAX',
      b'  number: 0xa6',
      b'- name: PDSPOAXN',
      b'  number: 0xa7',
      b'- name: DPSOA',
      b'  number: 0xa8',
      b'- name: DPSOXN',
      b'  number: 0xa9',
      b'- name: D',
      b'  number: 0xaa',
      b'- name: DPSONO',
      b'  number: 0xab',
      b'- name: SPDSXAX',
      b'  number: 0xac',
      b'- name: DPSDAOXN',
      b'  number: 0xad',
      b'- name: DSPNAO',
      b'  number: 0xae',
      b'- name: DPNO',
      b'  number: 0xaf',
      b'- name: PDSNOA',
      b'  number: 0xb0',
      b'- name: PDSPXOXN',
      b'  number: 0xb1',
      b'- name: SSPXDSXOX',
      b'  number: 0xb2',
      b'- name: SDPANAN',
      b'  number: 0xb3',
      b'- name: PSDNAX',
      b'  number: 0xb4',
      b'- name: DPSDOAXN',
      b'  number: 0xb5',
      b'- name: DPSDPAOXX',
      b'  number: 0xb6',
      b'- name: SDPXAN',
      b'  number: 0xb7',
      b'- name: PSDPXAX',
      b'  number: 0xb8',
      b'- name: DSPDAOXN',
      b'  number: 0xb9',
      b'- name: DPSNAO',
      b'  number: 0xba',
      b'- name: MERGEPAINT',
      b'  number: 0xbb',
      b'- name: SPDSANAX',
      b'  number: 0xbc',
      b'- name: SDXPDXAN',
      b'  number: 0xbd',
      b'- name: DPSXO',
      b'  number: 0xbe',
      b'- name: DPSANO',
      b'  number: 0xbf',
      b'- name: MERGECOPY',
      b'  number: 0xc0',
      b'- name: SPDSNAOXN',
      b'  number: 0xc1',
      b'- name: SPDSONOXN',
      b'  number: 0xc2',
      b'- name: PSXN',
      b'  number: 0xc3',
      b'- name: SPDNOA',
      b'  number: 0xc4',
      b'- name: SPDSXOXN',
      b'  number: 0xc5',
      b'- name: SDPNAX',
      b'  number: 0xc6',
      b'- name: PSDPOAXN',
      b'  number: 0xc7',
      b'- name: SDPOA',
      b'  number: 0xc8',
      b'- name: SPDOXN',
      b'  number: 0xc9',
      b'- name: DPSDXAX',
      b'  number: 0xca',
      b'- name: SPDSAOXN',
      b'  number: 0xcb',
      b'- name: SRCCOPY',
      b'  number: 0xcc',
      b'- name: SDPONO',
      b'  number: 0xcd',
      b'- name: SDPNAO',
      b'  number: 0xce',
      b'- name: SPNO',
      b'  number: 0xcf',
      b'- name: PSDNOA',
      b'  number: 0xd0',
      b'- name: PSDPXOXN',
      b'  number: 0xd1',
      b'- name: PDSNAX',
      b'  number: 0xd2',
      b'- name: SPDSOAXN',
      b'  number: 0xd3',
      b'- name: SSPXPDXAX',
      b'  number: 0xd4',
      b'- name: DPSANAN',
      b'  number: 0xd5',
      b'- name: PSDPSAOXX',
      b'  number: 0xd6',
      b'- name: DPSXAN',
      b'  number: 0xd7',
      b'- name: PDSPXAX',
      b'  number: 0xd8',
      b'- name: SDPSAOXN',
      b'  number: 0xd9',
      b'- name: DPSDANAX',
      b'  number: 0xda',
      b'- name: SPXDSXAN',
      b'  number: 0xdb',
      b'- name: SPDNAO',
      b'  number: 0xdc',
      b'- name: SDNO',
      b'  number: 0xdd',
      b'- name: SDPXO',
      b'  number: 0xde',
      b'- name: SDPANO',
      b'  number: 0xdf',
      b'- name: PDSOA',
      b'  number: 0xe0',
      b'- name: PDSOXN',
      b'  number: 0xe1',
      b'- name: DSPDXAX',
      b'  number: 0xe2',
      b'- name: PSDPAOXN',
      b'  number: 0xe3',
      b'- name: SDPSXAX',
      b'  number: 0xe4',
      b'- name: PDSPAOXN',
      b'  number: 0xe5',
      b'- name: SDPSANAX',
      b'  number: 0xe6',
      b'- name: SPXPDXAN',
      b'  number: 0xe7',
      b'- name: SSPXDSXAX',
      b'  number: 0xe8',
      b'- name: DSPDSANAXXN',
      b'  number: 0xe9',
      b'- name: DPSAO',
      b'  number: 0xea',
      b'- name: DPSXNO',
      b'  number: 0xeb',
      b'- name: SDPAO',
      b'  number: 0xec',
      b'- name: SDPXNO',
      b'  number: 0xed',
      b'- name: SRCPAINT',
      b'  number: 0xee',
      b'- name: SDPNOO',
      b'  number: 0xef',
      b'- name: PATCOPY',
      b'  number: 0xf0',
      b'- name: PDSONO',
      b'  number: 0xf1',
      b'- name: PDSNAO',
      b'  number: 0xf2',
      b'- name: PSNO',
      b'  number: 0xf3',
      b'- name: PSDNAO',
      b'  number: 0xf4',
      b'- name: PDNO',
      b'  number: 0xf5',
      b'- name: PDSXO',
      b'  number: 0xf6',
      b'- name: PDSANO',
      b'  number: 0xf7',
      b'- name: PDSAO',
      b'  number: 0xf8',
      b'- name: PDSXNO',
      b'  number: 0xf9',
      b'- name: DPO',
      b'  number: 0xfa',
      b'- name: PATPAINT',
      b'  number: 0xfb',
      b'- name: PSO',
      b'  number: 0xfc',
      b'- name: PSDNOO',
      b'  number: 0xfd',
      b'- name: DPSOO',
      b'  number: 0xfe',
      b'- name: WHITENESS',
      b'  number: 0xff',
      b'---',
      b'name: wmf_record_type',
      b'aliases: [RecordType]',
      b'type: enumeration',
      b'urls: ["https://msdn.microsoft.com/en-us/library/cc250589.aspx"]',
      b'values:',
      b'- name: META_EOF',
      b'  number: 0x0000',
      b'- name: META_SAVEDC',
      b'  number: 0x001e',
      b'- name: META_REALIZEPALETTE',
      b'  number: 0x0035',
      b'- name: META_SETPALENTRIES',
      b'  number: 0x0037',
      b'- name: META_CREATEPALETTE',
      b'  number: 0x00f7',
      b'- name: META_SETBKMODE',
      b'  number: 0x0102',
      b'- name: META_SETMAPMODE',
      b'  number: 0x0103',
      b'- name: META_SETROP2',
      b'  number: 0x0104',
      b'- name: META_SETRELABS',
      b'  number: 0x0105',
      b'- name: META_SETPOLYFILLMODE',
      b'  number: 0x0106',
      b'- name: META_SETSTRETCHBLTMODE',
      b'  number: 0x0107',
      b'- name: META_SETTEXTCHAREXTRA',
      b'  number: 0x0108',
      b'- name: META_RESTOREDC',
      b'  number: 0x0127',
      b'- name: META_INVERTREGION',
      b'  number: 0x012a',
      b'- name: META_PAINTREGION',
      b'  number: 0x012b',
      b'- name: META_SELECTCLIPREGION',
      b'  number: 0x012c',
      b'- name: META_SELECTOBJECT',
      b'  number: 0x012d',
      b'- name: META_SETTEXTALIGN',
      b'  number: 0x012e',
      b'- name: META_RESIZEPALETTE',
      b'  number: 0x0139',
      b'- name: META_DIBCREATEPATTERNBRUSH',
      b'  number: 0x0142',
      b'- name: META_SETLAYOUT',
      b'  number: 0x0149',
      b'- name: META_DELETEOBJECT',
      b'  number: 0x01f0',
      b'- name: META_CREATEPATTERNBRUSH',
      b'  number: 0x01f9',
      b'- name: META_SETBKCOLOR',
      b'  number: 0x0201',
      b'- name: META_SETTEXTCOLOR',
      b'  number: 0x0209',
      b'- name: META_SETTEXTJUSTIFICATION',
      b'  number: 0x020a',
      b'- name: META_SETWINDOWORG',
      b'  number: 0x020b',
      b'- name: META_SETWINDOWEXT',
      b'  number: 0x020c',
      b'- name: META_SETVIEWPORTORG',
      b'  number: 0x020d',
      b'- name: META_SETVIEWPORTEXT',
      b'  number: 0x020e',
      b'- name: META_OFFSETWINDOWORG',
      b'  number: 0x020f',
      b'- name: META_OFFSETVIEWPORTORG',
      b'  number: 0x0211',
      b'- name: META_LINETO',
      b'  number: 0x0213',
      b'- name: META_MOVETO',
      b'  number: 0x0214',
      b'- name: META_OFFSETCLIPRGN',
      b'  number: 0x0220',
      b'- name: META_FILLREGION',
      b'  number: 0x0228',
      b'- name: META_SETMAPPERFLAGS',
      b'  number: 0x0231',
      b'- name: META_SELECTPALETTE',
      b'  number: 0x0234',
      b'- name: META_CREATEPENINDIRECT',
      b'  number: 0x02fa',
      b'- name: META_CREATEFONTINDIRECT',
      b'  number: 0x02fb',
      b'- name: META_CREATEBRUSHINDIRECT',
      b'  number: 0x02fc',
      b'- name: META_POLYGON',
      b'  number: 0x0324',
      b'- name: META_POLYLINE',
      b'  number: 0x0325',
      b'- name: META_SCALEWINDOWEXT',
      b'  number: 0x0410',
      b'- name: META_SCALEVIEWPORTEXT',
      b'  number: 0x0412',
      b'- name: META_EXCLUDECLIPRECT',
      b'  number: 0x0415',
      b'- name: META_INTERSECTCLIPRECT',
      b'  number: 0x0416',
      b'- name: META_ELLIPSE',
      b'  number: 0x0418',
      b'- name: META_FLOODFILL',
      b'  number: 0x0419',
      b'- name: META_RECTANGLE',
      b'  number: 0x041B',
      b'- name: META_SETPIXEL',
      b'  number: 0x041F',
      b'- name: META_FRAMEREGION',
      b'  number: 0x0429',
      b'- name: META_ANIMATEPALETTE',
      b'  number: 0x0436',
      b'- name: META_TEXTOUT',
      b'  number: 0x0521',
      b'- name: META_POLYPOLYGON',
      b'  number: 0x0538',
      b'- name: META_EXTFLOODFILL',
      b'  number: 0x0548',
      b'- name: META_ROUNDRECT',
      b'  number: 0x061C',
      b'- name: META_PATBLT',
      b'  number: 0x061d',
      b'- name: META_ESCAPE',
      b'  number: 0x0626',
      b'- name: META_CREATEREGION',
      b'  number: 0x06ff',
      b'- name: META_ARC',
      b'  number: 0x0817',
      b'- name: META_PIE',
      b'  number: 0x081a',
      b'- name: META_CHORD',
      b'  number: 0x0830',
      b'- name: META_BITBLT',
      b'  number: 0x0922',
      b'- name: META_DIBBITBLT',
      b'  number: 0x0940',
      b'- name: META_EXTTEXTOUT',
      b'  number: 0x0a32',
      b'- name: META_STRETCHBLT',
      b'  number: 0x0b23',
      b'- name: META_DIBSTRETCHBLT',
      b'  number: 0x0b41',
      b'- name: META_SETDIBTODEV',
      b'  number: 0x0d33',
      b'- name: META_STRETCHDIB',
      b'  number: 0x0f43',
      b'---',
      b'name: wmf_stretch_mode',
      b'aliases: [StretchMode]',
      b'type: enumeration',
      b'urls: ["https://msdn.microsoft.com/en-us/library/cc250407.aspx"]',
      b'values:',
      b'- name: BLACKONWHITE',
      b'  number: 0x0001',
      b'- name: WHITEONBLACK',
      b'  number: 0x0002',
      b'- name: COLORONCOLOR',
      b'  number: 0x0003',
      b'- name: HALFTONE',
      b'  number: 0x0004',
      b'---',
      b'name: wmf_header',
      b'aliases: [META_HEADER]',
      b'type: structure',
      b'urls: ["https://msdn.microsoft.com/en-us/library/cc250418.aspx"]',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: file_type',
      b'  aliases: [Type]',
      b'  data_type: uint16',
      b'- name: record_size',
      b'  aliases: [HeaderSize]',
      b'  data_type: uint16',
      b'- name: format_version',
      b'  aliases: [Version]',
      b'  data_type: uint16',
      b'- name: file_size_lower',
      b'  aliases: [SizeLow]',
      b'  data_type: uint16',
      b'- name: file_size_upper',
      b'  aliases: [SizeHigh]',
      b'  data_type: uint16',
      b'- name: maximum_number_of_objects',
      b'  aliases: [NumberOfObjects]',
      b'  data_type: uint16',
      b'- name: largest_record_size',
      b'  aliases: [MaxRecord]',
      b'  data_type: uint32',
      b'- name: number_of_records',
      b'  aliases: [NumberOfMembers]',
      b'  data_type: uint16',
      b'---',
      b'name: wmf_placeable',
      b'aliases: [META_PLACEABLE]',
      b'urls: ["https://msdn.microsoft.com/en-us/library/cc669452.aspx"]',
      b'type: structure',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: signature',
      b'  aliases: [Key]',
      b'  data_type: uint32',
      b'- name: resource_handle',
      b'  aliases: [HWmf]',
      b'  data_type: uint16',
      b'- name: bounding_box',
      b'  aliases: [BoundingBox]',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 8',
      b'- name: number_of_units_per_inch',
      b'  aliases: [Inch]',
      b'  data_type: uint16',
      b'- name: unknown1',
      b'  aliases: [Reserved]',
      b'  data_type: uint32',
      b'- name: checksum',
      b'  aliases: [Checksum]',
      b'  data_type: uint16',
      b'---',
      # TODO: deprecate wmf_record_header in favor of wmf_record
      b'name: wmf_record_header',
      b'type: structure',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: record_size',
      b'  data_type: uint32',
      b'- name: record_type',
      b'  data_type: uint16',
      # TODO: link to wmf_record_type
      b'---',
      b'name: wmf_restoredc',
      b'type: structure',
      b'description: Restores the playback device context',
      b'urls: ["https://msdn.microsoft.com/en-us/library/cc250469.aspx"]',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: number_of_saved_device_context',
      b'  data_type: uint16',
      b'---',
      b'name: wmf_setmapmode',
      b'type: structure',
      b'description: Defines the mapping mode',
      b'urls: ["https://msdn.microsoft.com/en-us/library/cc250483.aspx"]',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: map_mode',
      b'  data_type: uint16',
      # TODO: map to wmf_map_mode
      b'---',
      b'name: wmf_setstretchbltmode',
      b'type: structure',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: stretch_mode',
      b'  data_type: uint16',
      # TODO: map to wmf_stretch_mode
      # TODO: documentation indicates there should be 16-bit reserved field.
      b'---',
      b'name: wmf_setwindowext',
      b'type: structure',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: x_coordinate',
      b'  data_type: uint16',
      b'- name: y_coordinate',
      b'  data_type: uint16',
      b'---',
      b'name: wmf_setwindoworg',
      b'type: structure',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: x_coordinate',
      b'  data_type: uint16',
      b'- name: y_coordinate',
      b'  data_type: uint16',
      b'---',
      b'name: wmf_dibstretchblt',
      b'type: structure',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: raster_operation',
      b'  data_type: uint32',
      b'- name: source_height',
      b'  data_type: uint16',
      b'- name: source_width',
      b'  data_type: uint16',
      b'- name: source_x_coordinate',
      b'  data_type: uint16',
      b'- name: source_y_coordinate',
      b'  data_type: uint16',
      b'- name: destination_height',
      b'  data_type: uint16',
      b'- name: destination_width',
      b'  data_type: uint16',
      b'- name: destination_x_coordinate',
      b'  data_type: uint16',
      b'- name: destination_y_coordinate',
      b'  data_type: uint16',
      # TODO: add device_indepent_bitmap stream.
  ])

  _TODO = b'\n'.join([
      b'---',
      b'name: wmf_record',
      b'type: structure',
      b'description: WMF record',
      b'urls: ["https://msdn.microsoft.com/en-us/library/cc250387.aspx"]',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: record_size',
      b'  aliases: [RecordSize]',
      b'  description: Size of the record as number of 16-bit values',
      b'  data_type: uint32',
      # TODO: link to wmf_record_type
      b'- name: record_type',
      b'  aliases: [RecordFunction]',
      b'  data_type: uint16',
      b'- name: record_data',
      b'  aliases: [rdParam]',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  element_data_size: (wmf_record.record_size * 2) - 6',
      b'---',
      b'name: wmf_restoredc_record',
      b'type: structure',
      b'description: Restores the playback device context',
      b'urls: ["https://msdn.microsoft.com/en-us/library/cc250469.aspx"]',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: record_size',
      b'  data_type: uint32',
      b'- name: record_type',
      b'  data_type: uint16',
      # TODO: or support wmf_record_type.META_RESTOREDC
      b'  value: 0x0127',
      b'- name: number_of_saved_device_context',
      b'  data_type: uint16',
      b'---',
      b'name: wmf_setmapmode_record',
      b'type: structure',
      b'description: Defines the mapping mode',
      b'urls: ["https://msdn.microsoft.com/en-us/library/cc250483.aspx"]',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: record_size',
      b'  data_type: uint32',
      b'- name: record_type',
      b'  data_type: uint16',
      # TODO: or support wmf_record_type.META_SETMAPMODE
      b'  value: 0x0103',
      b'- name: map_mode',
      b'  data_type: uint16',
      # TODO: map to wmf_map_mode
  ])

  _DATA_TYPE_FABRIC = dtfabric_fabric.DataTypeFabric(
      yaml_definition=_DATA_TYPE_FABRIC_DEFINITION)

  _HEADER = _DATA_TYPE_FABRIC.CreateDataTypeMap(u'wmf_header')

  _HEADER_SIZE = _HEADER.GetByteSize()

  _PLACEABLE = _DATA_TYPE_FABRIC.CreateDataTypeMap(u'wmf_placeable')

  _PLACEABLE_SIZE = _PLACEABLE.GetByteSize()

  _RECORD_TYPE = _DATA_TYPE_FABRIC.CreateDataTypeMap(u'wmf_record_type')

  _RECORD_HEADER = _DATA_TYPE_FABRIC.CreateDataTypeMap(u'wmf_record_header')

  _RECORD_HEADER_SIZE = _RECORD_HEADER.GetByteSize()

  _WMF_PLACEABLE_SIGNATURE = b'\xd7\xcd\xc6\x9a'

  _MAP_MODE = _DATA_TYPE_FABRIC.CreateDataTypeMap(u'wmf_map_mode')

  _STRETCH_MODE = _DATA_TYPE_FABRIC.CreateDataTypeMap(u'wmf_stretch_mode')

  # record_size == ((record_type >> 8) + 3)
  # DIB: https://msdn.microsoft.com/en-us/library/cc250593.aspx

  # Here None represents that the record has no additional data.
  _WMF_RECORD_DATA_STRUCT_TYPES = {
      0x0000: None,
      0x001e: None,
      0x0103: _DATA_TYPE_FABRIC.CreateDataTypeMap(u'wmf_setmapmode'),
      0x0107: _DATA_TYPE_FABRIC.CreateDataTypeMap(u'wmf_setstretchbltmode'),
      0x0127: _DATA_TYPE_FABRIC.CreateDataTypeMap(u'wmf_restoredc'),
      0x020b: _DATA_TYPE_FABRIC.CreateDataTypeMap(u'wmf_setwindoworg'),
      0x020c: _DATA_TYPE_FABRIC.CreateDataTypeMap(u'wmf_setwindowext'),
      0x0b41: _DATA_TYPE_FABRIC.CreateDataTypeMap(u'wmf_dibstretchblt')}

  # Reverse Polish wmf_raster_operation_code
  _WMF_RASTER_OPERATIONS = {
      0x00000042: u'BLACKNESS',
      0x00010289: u'DPSOO',
      0x00020C89: u'DPSON',
      0x000300AA: u'PSO',
      0x00040C88: u'SDPON',
      0x000500A9: u'DPO',
      0x00060865: u'PDSXNO',
      0x000702C5: u'PDSAO',
      0x00080F08: u'SDPNA',
      0x00090245: u'PDSXO',
      0x000A0329: u'DPN',
      0x000B0B2A: u'PSDNAO',
      0x000C0324: u'SPN',
      0x000D0B25: u'PDSNAO',
      0x000E08A5: u'PDSONO',
      0x000F0001: u'P',
      0x00100C85: u'PDSON',
      0x001100A6: u'NOTSRCERAS',
      0x00120868: u'SDPXNO',
      0x001302C8: u'SDPAO',
      0x00140869: u'DPSXNO',
      0x001502C9: u'DPSAO',
      0x00165CCA: u'PSDPSANAX',
      0x00171D54: u'SSPXDSXAX',
      0x00180D59: u'SPXPDX',
      0x00191CC8: u'SDPSANAX',
      0x001A06C5: u'PDSPAO',
      0x001B0768: u'SDPSXAX',
      0x001C06CA: u'PSDPAO',
      0x001D0766: u'DSPDXAX',
      0x001E01A5: u'PDSO',
      0x001F0385: u'PDSOA',
      0x00200F09: u'DPSNA',
      0x00210248: u'SDPXO',
      0x00220326: u'DSN',
      0x00230B24: u'SPDNAO',
      0x00240D55: u'SPXDSX',
      0x00251CC5: u'PDSPANAX',
      0x002606C8: u'SDPSAO',
      0x00271868: u'SDPSXNOX',
      0x00280369: u'DPSXA',
      0x002916CA: u'PSDPSAOXXN',
      0x002A0CC9: u'DPSANA',
      0x002B1D58: u'SSPXPDXAXN',
      0x002C0784: u'SPDSOAX',
      0x002D060A: u'PSDNOX',
      0x002E064A: u'PSDPXOX',
      0x002F0E2A: u'PSDNOAN',
      0x0030032A: u'PSNA',
      0x00310B28: u'SDPNAON',
      0x00320688: u'SDPSOOX',
      0x00330008: u'NOTSRCCOPY',
      0x003406C4: u'SPDSAOX',
      0x00351864: u'SPDSXNOX',
      0x003601A8: u'SDPOX',
      0x00370388: u'SDPOAN',
      0x0038078A: u'PSDPOAX',
      0x00390604: u'SPDNOX',
      0x003A0644: u'SPDSXOX',
      0x003B0E24: u'SPDNOAN',
      0x003C004A: u'PSX',
      0x003D18A4: u'SPDSONOX',
      0x003E1B24: u'SPDSNAOX',
      0x003F00EA: u'PSAN',
      0x00400F0A: u'PSDNAA',
      0x00410249: u'DPSXON',
      0x00420D5D: u'SDXPDXA',
      0x00431CC4: u'SPDSANAXN',
      0x00440328: u'SRCERASE',
      0x00450B29: u'DPSNAON',
      0x004606C6: u'DSPDAOX',
      0x0047076A: u'PSDPXAXN',
      0x00480368: u'SDPXA',
      0x004916C5: u'PDSPDAOXXN',
      0x004A0789: u'DPSDOAX',
      0x004B0605: u'PDSNOX',
      0x004C0CC8: u'SDPANA',
      0x004D1954: u'SSPXDSXOXN',
      0x004E0645: u'PDSPXOX',
      0x004F0E25: u'PDSNOAN',
      0x00500325: u'PDNA',
      0x00510B26: u'DSPNAON',
      0x005206C9: u'DPSDAOX',
      0x00530764: u'SPDSXAXN',
      0x005408A9: u'DPSONON',
      0x00550009: u'DSTINVERT',
      0x005601A9: u'DPSOX',
      0x000570389: u'DPSOAN',
      0x00580785: u'PDSPOAX',
      0x00590609: u'DPSNOX',
      0x005A0049: u'PATINVERT',
      0x005B18A9: u'DPSDONOX',
      0x005C0649: u'DPSDXOX',
      0x005D0E29: u'DPSNOAN',
      0x005E1B29: u'DPSDNAOX',
      0x005F00E9: u'DPAN',
      0x00600365: u'PDSXA',
      0x006116C6: u'DSPDSAOXXN',
      0x00620786: u'DSPDOAX',
      0x00630608: u'SDPNOX',
      0x00640788: u'SDPSOAX',
      0x00650606: u'DSPNOX',
      0x00660046: u'SRCINVERT',
      0x006718A8: u'SDPSONOX',
      0x006858A6: u'DSPDSONOXXN',
      0x00690145: u'PDSXXN',
      0x006A01E9: u'DPSAX',
      0x006B178A: u'PSDPSOAXXN',
      0x006C01E8: u'SDPAX',
      0x006D1785: u'PDSPDOAXXN',
      0x006E1E28: u'SDPSNOAX',
      0x006F0C65: u'PDXNAN',
      0x00700CC5: u'PDSANA',
      0x00711D5C: u'SSDXPDXAXN',
      0x00720648: u'SDPSXOX',
      0x00730E28: u'SDPNOAN',
      0x00740646: u'DSPDXOX',
      0x00750E26: u'DSPNOAN',
      0x00761B28: u'SDPSNAOX',
      0x007700E6: u'DSAN',
      0x007801E5: u'PDSAX',
      0x00791786: u'DSPDSOAXXN',
      0x007A1E29: u'DPSDNOAX',
      0x007B0C68: u'SDPXNAN',
      0x007C1E24: u'SPDSNOAX',
      0x007D0C69: u'DPSXNAN',
      0x007E0955: u'SPXDSXO',
      0x007F03C9: u'DPSAAN',
      0x008003E9: u'DPSAA',
      0x00810975: u'SPXDSXON',
      0x00820C49: u'DPSXNA',
      0x00831E04: u'SPDSNOAXN',
      0x00840C48: u'SDPXNA',
      0x00851E05: u'PDSPNOAXN',
      0x008617A6: u'DSPDSOAXX',
      0x008701C5: u'PDSAXN',
      0x008800C6: u'SRCAND',
      0x00891B08: u'SDPSNAOXN',
      0x008A0E06: u'DSPNOA',
      0x008B0666: u'DSPDXOXN',
      0x008C0E08: u'SDPNOA',
      0x008D0668: u'SDPSXOXN',
      0x008E1D7C: u'SSDXPDXAX',
      0x008F0CE5: u'PDSANAN',
      0x00900C45: u'PDSXNA',
      0x00911E08: u'SDPSNOAXN',
      0x009217A9: u'DPSDPOAXX',
      0x009301C4: u'SPDAXN',
      0x009417AA: u'PSDPSOAXX',
      0x009501C9: u'DPSAXN',
      0x00960169: u'DPSXX',
      0x0097588A: u'PSDPSONOXX',
      0x00981888: u'SDPSONOXN',
      0x00990066: u'DSXN',
      0x009A0709: u'DPSNAX',
      0x009B07A8: u'SDPSOAXN',
      0x009C0704: u'SPDNAX',
      0x009D07A6: u'DSPDOAXN',
      0x009E16E6: u'DSPDSAOXX',
      0x009F0345: u'PDSXAN',
      0x00A000C9: u'DPA',
      0x00A11B05: u'PDSPNAOXN',
      0x00A20E09: u'DPSNOA',
      0x00A30669: u'DPSDXOXN',
      0x00A41885: u'PDSPONOXN',
      0x00A50065: u'PDXN',
      0x00A60706: u'DSPNAX',
      0x00A707A5: u'PDSPOAXN',
      0x00A803A9: u'DPSOA',
      0x00A90189: u'DPSOXN',
      0x00AA0029: u'D',
      0x00AB0889: u'DPSONO',
      0x00AC0744: u'SPDSXAX',
      0x00AD06E9: u'DPSDAOXN',
      0x00AE0B06: u'DSPNAO',
      0x00AF0229: u'DPNO',
      0x00B00E05: u'PDSNOA',
      0x00B10665: u'PDSPXOXN',
      0x00B21974: u'SSPXDSXOX',
      0x00B30CE8: u'SDPANAN',
      0x00B4070A: u'PSDNAX',
      0x00B507A9: u'DPSDOAXN',
      0x00B616E9: u'DPSDPAOXX',
      0x00B70348: u'SDPXAN',
      0x00B8074A: u'PSDPXAX',
      0x00B906E6: u'DSPDAOXN',
      0x00BA0B09: u'DPSNAO',
      0x00BB0226: u'MERGEPAINT',
      0x00BC1CE4: u'SPDSANAX',
      0x00BD0D7D: u'SDXPDXAN',
      0x00BE0269: u'DPSXO',
      0x00BF08C9: u'DPSANO',
      0x00C000CA: u'MERGECOPY',
      0x00C11B04: u'SPDSNAOXN',
      0x00C21884: u'SPDSONOXN',
      0x00C3006A: u'PSXN',
      0x00C40E04: u'SPDNOA',
      0x00C50664: u'SPDSXOXN',
      0x00C60708: u'SDPNAX',
      0x00C707AA: u'PSDPOAXN',
      0x00C803A8: u'SDPOA',
      0x00C90184: u'SPDOXN',
      0x00CA0749: u'DPSDXAX',
      0x00CB06E4: u'SPDSAOXN',
      0x00CC0020: u'SRCCOPY',
      0x00CD0888: u'SDPONO',
      0x00CE0B08: u'SDPNAO',
      0x00CF0224: u'SPNO',
      0x00D00E0A: u'PSDNOA',
      0x00D1066A: u'PSDPXOXN',
      0x00D20705: u'PDSNAX',
      0x00D307A4: u'SPDSOAXN',
      0x00D41D78: u'SSPXPDXAX',
      0x00D50CE9: u'DPSANAN',
      0x00D616EA: u'PSDPSAOXX',
      0x00D70349: u'DPSXAN',
      0x00D80745: u'PDSPXAX',
      0x00D906E8: u'SDPSAOXN',
      0x00DA1CE9: u'DPSDANAX',
      0x00DB0D75: u'SPXDSXAN',
      0x00DC0B04: u'SPDNAO',
      0x00DD0228: u'SDNO',
      0x00DE0268: u'SDPXO',
      0x00DF08C8: u'SDPANO',
      0x00E003A5: u'PDSOA',
      0x00E10185: u'PDSOXN',
      0x00E20746: u'DSPDXAX',
      0x00E306EA: u'PSDPAOXN',
      0x00E40748: u'SDPSXAX',
      0x00E506E5: u'PDSPAOXN',
      0x00E61CE8: u'SDPSANAX',
      0x00E70D79: u'SPXPDXAN',
      0x00E81D74: u'SSPXDSXAX',
      0x00E95CE6: u'DSPDSANAXXN',
      0x00EA02E9: u'DPSAO',
      0x00EB0849: u'DPSXNO',
      0x00EC02E8: u'SDPAO',
      0x00ED0848: u'SDPXNO',
      0x00EE0086: u'SRCPAINT',
      0x00EF0A08: u'SDPNOO',
      0x00F00021: u'PATCOPY',
      0x00F10885: u'PDSONO',
      0x00F20B05: u'PDSNAO',
      0x00F3022A: u'PSNO',
      0x00F40B0A: u'PSDNAO',
      0x00F50225: u'PDNO',
      0x00F60265: u'PDSXO',
      0x00F708C5: u'PDSANO',
      0x00F802E5: u'PDSAO',
      0x00F90845: u'PDSXNO',
      0x00FA0089: u'DPO',
      0x00FB0A09: u'PATPAINT',
      0x00FC008A: u'PSO',
      0x00FD0A0A: u'PSDNOO',
      0x00FE02A9: u'DPSOO',
      0x00FF0062: u'WHITENESS'}

  def _DebugPrintHeader(self, file_header):
    """Prints header debug information.

    Args:
      file_header (wmf_header): file header.
    """
    value_string = u'0x{0:04x}'.format(file_header.file_type)
    self._DebugPrintValue(u'File type', value_string)

    value_string = u'{0:d}'.format(file_header.record_size)
    self._DebugPrintValue(u'Record size', value_string)

    value_string = u'{0:d}'.format(file_header.format_version)
    self._DebugPrintValue(u'Format version', value_string)

    value_string = u'{0:d}'.format(file_header.file_size_lower)
    self._DebugPrintValue(u'File size lower', value_string)

    value_string = u'{0:d}'.format(file_header.file_size_upper)
    self._DebugPrintValue(u'File size upper', value_string)

    value_string = u'{0:d}'.format(file_header.maximum_number_of_objects)
    self._DebugPrintValue(u'Maximum number of object', value_string)

    value_string = u'{0:d}'.format(file_header.largest_record_size)
    self._DebugPrintValue(u'Largest record size', value_string)

    value_string = u'{0:d}'.format(file_header.number_of_records)
    self._DebugPrintValue(u'Number of records', value_string)

    self._DebugPrintText(u'\n')

  def _DebugPrintPlaceable(self, placeable):
    """Prints placeable debug information.

    Args:
      placeable (wmf_placeable): placeable.
    """
    value_string = u'0x{0:08x}'.format(placeable.signature)
    self._DebugPrintValue(u'Signature', value_string)

    value_string = u'0x{0:04x}'.format(placeable.resource_handle)
    self._DebugPrintValue(u'Resource handle', value_string)

    self._DebugPrintData(u'Bounding box', placeable.bounding_box)

    value_string = u'{0:d}'.format(placeable.number_of_units_per_inch)
    self._DebugPrintValue(u'Number of units per inch', value_string)

    value_string = u'0x{0:08x}'.format(placeable.unknown1)
    self._DebugPrintValue(u'Unknown1', value_string)

    value_string = u'0x{0:04x}'.format(placeable.checksum)
    self._DebugPrintValue(u'Checksum', value_string)

    self._DebugPrintText(u'\n')

  def _DebugPrintRecordHeader(self, record_header):
    """Prints record header debug information.

    Args:
      record_header (wmf_record_header): record header.
    """
    value_string = u'{0:d} ({1:d} bytes)'.format(
        record_header.record_size, record_header.record_size * 2)
    self._DebugPrintValue(u'Record size', value_string)

    record_type_string = self._RECORD_TYPE.GetName(record_header.record_type)
    value_string = u'0x{0:04x} ({1:s})'.format(
        record_header.record_type, record_type_string or u'UNKNOWN')
    self._DebugPrintValue(u'Record type', value_string)

    self._DebugPrintText(u'\n')

  def _ReadHeader(self, file_object):
    """Reads a header.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the header cannot be read.
    """
    file_offset = file_object.tell()
    file_header = self._ReadStructure(
        file_object, file_offset, self._HEADER_SIZE, self._HEADER, u'header')

    if self._debug:
      self._DebugPrintHeader(file_header)

    if file_header.file_type not in (1, 2):
      raise errors.ParseError(u'Unsupported file type: {0:d}'.format(
          file_header.file_type))

    if file_header.record_size != 9:
      raise errors.ParseError(u'Unsupported record size: {0:d}'.format(
          file_header.record_size))

  def _ReadPlaceable(self, file_object):
    """Reads a placeable.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the placeable cannot be read.
    """
    file_offset = file_object.tell()
    placeable = self._ReadStructure(
        file_object, file_offset, self._PLACEABLE_SIZE, self._PLACEABLE,
        u'placeable')

    if self._debug:
      self._DebugPrintPlaceable(placeable)

  def _ReadRecord(self, file_object, file_offset):
    """Reads a record.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the data relative from the start of
          the file-like object.

    Raises:
      ParseError: if the record cannot be read.
    """
    record_header = self._ReadStructure(
        file_object, file_offset, self._RECORD_HEADER_SIZE, self._RECORD_HEADER,
        u'record header')

    if self._debug:
      self._DebugPrintRecordHeader(record_header)

    record_size = record_header.record_size * 2

    data_offset = file_offset + self._RECORD_HEADER_SIZE
    data_size = record_size - self._RECORD_HEADER_SIZE

    if self._debug:
      self._ReadRecordData(
          file_object, record_header.record_type, data_size)

    return Record(
        record_header.record_type, record_size, data_offset, data_size)

  def _ReadRecordData(self, file_object, record_type, data_size):
    """Reads a record.

    Args:
      file_object (file): file-like object.
      record_type (int): record type.
      data_size (int): size of the record data.

    Raises:
      ParseError: if the record cannot be read.
    """
    record_data = file_object.read(data_size)

    if self._debug and data_size > 0:
      self._DebugPrintData(u'Record data', record_data)

    # TODO: use lookup dict with callback.
    data_type_map = self._WMF_RECORD_DATA_STRUCT_TYPES.get(record_type, None)
    if not data_type_map:
      return

    try:
      record = data_type_map.MapByteStream(record_data)
    except dtfabric_errors.MappingError as exception:
      raise errors.ParseError((
          u'Unable to parse record data with error: {0:s}').format(exception))

    if self._debug:
      if record_type == 0x0103:
        map_mode_string = self._MAP_MODE.GetName(record.map_mode)
        value_string = u'0x{0:04x} ({1:s})'.format(
            record.map_mode, map_mode_string or u'UNKNOWN')
        self._DebugPrintValue(u'Map mode', value_string)

      elif record_type == 0x0107:
        stretch_mode_string = self._MAP_MODE.GetName(
            record.stretch_mode)
        value_string = u'0x{0:04x} ({1:s})'.format(
            record.stretch_mode, stretch_mode_string or u'UNKNOWN')
        self._DebugPrintValue(u'Stretch mode', value_string)

      elif record_type == 0x0127:
        value_string = u'{0:d}'.format(
            record.number_of_saved_device_context)
        self._DebugPrintValue(u'Number of saved device context', value_string)

      elif record_type in (0x020b, 0x020c):
        value_string = u'{0:d}'.format(record.x_coordinate)
        self._DebugPrintValue(u'X coordinate', value_string)

        value_string = u'{0:d}'.format(record.y_coordinate)
        self._DebugPrintValue(u'Y coordinate', value_string)

      elif record_type == 0x0b41:
        raster_operation_string = self._WMF_RASTER_OPERATIONS.get(
            record.raster_operation, u'UNKNOWN')
        value_string = u'0x{0:08x} ({1:s})'.format(
            record.raster_operation, raster_operation_string)
        self._DebugPrintValue(u'Raster operation', value_string)

        value_string = u'{0:d}'.format(record.source_height)
        self._DebugPrintValue(u'Source height', value_string)

        value_string = u'{0:d}'.format(record.source_width)
        self._DebugPrintValue(u'Source width', value_string)

        value_string = u'{0:d}'.format(record.source_x_coordinate)
        self._DebugPrintValue(u'Source X coordinate', value_string)

        value_string = u'{0:d}'.format(record.source_y_coordinate)
        self._DebugPrintValue(u'Source Y coordinate', value_string)

        value_string = u'{0:d}'.format(record.destination_height)
        self._DebugPrintValue(u'Destination height', value_string)

        value_string = u'{0:d}'.format(record.destination_width)
        self._DebugPrintValue(u'Destination width', value_string)

        value_string = u'{0:d}'.format(record.destination_x_coordinate)
        self._DebugPrintValue(u'Destination X coordinate', value_string)

        value_string = u'{0:d}'.format(record.destination_y_coordinate)
        self._DebugPrintValue(u'Destination Y coordinate', value_string)

      self._DebugPrintText(u'\n')

  def ReadFileObject(self, file_object):
    """Reads a Windows Metafile Format (WMF) file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    try:
      signature = file_object.read(4)
      file_object.seek(-4, os.SEEK_CUR)
    except IOError as exception:
      raise errors.ParseError(
          u'Unable to read file signature with error: {0!s}'.format(
              exception))

    if signature == self._WMF_PLACEABLE_SIGNATURE:
      self._ReadPlaceable(file_object)

    self._ReadHeader(file_object)

    file_offset = file_object.tell()
    while file_offset < self._file_size:
      record = self._ReadRecord(file_object, file_offset)

      file_offset += record.size
