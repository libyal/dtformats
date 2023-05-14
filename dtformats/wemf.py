# -*- coding: utf-8 -*-
"""Windows (Enhanced) Metafile Format (WMF and EMF) files."""

import os

from dtfabric import errors as dtfabric_errors

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

  FILE_TYPE = 'Windows Enhanced Metafile'

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('emf.yaml')

  _RECORD_TYPE = _FABRIC.CreateDataTypeMap('emf_record_type')

  _EMF_SIGNATURE = b'FME\x20'

  # Here None represents that the record has no additional data.
  _EMF_RECORD_DATA_STRUCT_TYPES = {
      0x0018: _FABRIC.CreateDataTypeMap('emf_settextcolor'),
      0x0025: _FABRIC.CreateDataTypeMap('emf_selectobject')}

  _EMF_STOCK_OBJECT = _FABRIC.CreateDataTypeMap('emf_stock_object')

  def _DebugPrintFileHeader(self, file_header):
    """Prints file header debug information.

    Args:
      file_header (emf_file_header): file header.
    """
    record_type_string = self._RECORD_TYPE.GetName(
        file_header.record_type) or 'UNKNOWN'
    self._DebugPrintValue('Record type', (
        f'0x{file_header.record_type:04x} ({record_type_string:s})'))

    self._DebugPrintValue('Record size', f'{file_header.record_size:d}')

    self._DebugPrintValue('Signature', f'0x{file_header.signature:04x}')

    self._DebugPrintValue(
        'Format version', f'0x{file_header.format_version:04x}')

    self._DebugPrintValue('File size', f'{file_header.file_size:d}')

    self._DebugPrintValue(
        'Number of records', f'{file_header.number_of_records:d}')

    self._DebugPrintValue(
        'Number of handles', f'{file_header.number_of_handles:d}')

    self._DebugPrintValue('Unknown (reserved)', f'0x{file_header.unknown1:04x}')

    self._DebugPrintValue(
        'Description string size', f'{file_header.description_string_size:d}')

    self._DebugPrintValue(
        'Description string offset',
        f'0x{file_header.description_string_offset:04x}')

    self._DebugPrintText('\n')

  def _DebugPrintRecordHeader(self, record_header):
    """Prints record header debug information.

    Args:
      record_header (emf_record_header): record header.
    """
    record_type_string = self._RECORD_TYPE.GetName(
        record_header.record_type) or 'UNKNOWN'
    self._DebugPrintValue('Record type', (
        f'0x{record_header.record_type:04x} ({record_type_string:s})'))

    self._DebugPrintValue('Record size', f'{record_header.record_size:d}')

    self._DebugPrintText('\n')

  def _ReadFileHeader(self, file_object):
    """Reads a file header.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file header cannot be read.
    """
    file_offset = file_object.tell()

    data_type_map = self._GetDataTypeMap('emf_file_header')

    file_header, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'file header')

    if self._debug:
      self._DebugPrintFileHeader(file_header)

    # TODO: check record type
    # TODO: check record size
    # TODO: check signature

  def _ReadRecord(self, file_object, file_offset):
    """Reads a record.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the data relative to the start of
          the file-like object.

    Returns:
      Record: a record.

    Raises:
      ParseError: if the record cannot be read.
    """
    data_type_map = self._GetDataTypeMap('emf_record_header')

    record_header, data_offset = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'record header')

    if self._debug:
      self._DebugPrintRecordHeader(record_header)

    data_size = record_header.record_size - (data_offset - file_offset)

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
      self._DebugPrintData('Record data', record_data)

    # TODO: use lookup dict with callback.
    data_type_map = self._EMF_RECORD_DATA_STRUCT_TYPES.get(record_type, None)
    if not data_type_map:
      return

    try:
      record = data_type_map.MapByteStream(record_data)
    except dtfabric_errors.MappingError as exception:
      raise errors.ParseError(
          f'Unable to parse record data with error: {exception!s}')

    if self._debug:
      if record_type == 0x0018:
        self._DebugPrintValue('Color', f'0x{record.color:04x}')

      elif record_type == 0x0025:
        stock_object_string = self._EMF_STOCK_OBJECT.GetName(
            record.object_identifier)

        if stock_object_string:
          value_string = (
              f'0x{record.object_identifier:08x} ({stock_object_string:s})')
        else:
          value_string = f'0x{record.object_identifier:08x}'

        self._DebugPrintValue('Object identifier', value_string)

      self._DebugPrintText('\n')

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

  FILE_TYPE = 'Windows Metafile'

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('wmf.yaml')

  # https://msdn.microsoft.com/en-us/library/cc250370.aspx

  # TODO: merge with YAML file
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

  _RECORD_TYPE = _FABRIC.CreateDataTypeMap('wmf_record_type')

  _WMF_PLACEABLE_SIGNATURE = b'\xd7\xcd\xc6\x9a'

  _MAP_MODE = _FABRIC.CreateDataTypeMap('wmf_map_mode')

  _STRETCH_MODE = _FABRIC.CreateDataTypeMap('wmf_stretch_mode')

  # record_size == ((record_type >> 8) + 3)
  # DIB: https://msdn.microsoft.com/en-us/library/cc250593.aspx

  # Here None represents that the record has no additional data.
  _WMF_RECORD_DATA_STRUCT_TYPES = {
      0x0000: None,
      0x001e: None,
      0x0103: _FABRIC.CreateDataTypeMap('wmf_setmapmode'),
      0x0107: _FABRIC.CreateDataTypeMap('wmf_setstretchbltmode'),
      0x0127: _FABRIC.CreateDataTypeMap('wmf_restoredc'),
      0x020b: _FABRIC.CreateDataTypeMap('wmf_setwindoworg'),
      0x020c: _FABRIC.CreateDataTypeMap('wmf_setwindowext'),
      0x0b41: _FABRIC.CreateDataTypeMap('wmf_dibstretchblt')}

  # Reverse Polish wmf_raster_operation_code
  _WMF_RASTER_OPERATIONS = {
      0x00000042: 'BLACKNESS',
      0x00010289: 'DPSOO',
      0x00020c89: 'DPSON',
      0x000300aa: 'PSO',
      0x00040c88: 'SDPON',
      0x000500a9: 'DPO',
      0x00060865: 'PDSXNO',
      0x000702c5: 'PDSAO',
      0x00080f08: 'SDPNA',
      0x00090245: 'PDSXO',
      0x000a0329: 'DPN',
      0x000b0b2a: 'PSDNAO',
      0x000c0324: 'SPN',
      0x000d0b25: 'PDSNAO',
      0x000e08a5: 'PDSONO',
      0x000f0001: 'P',
      0x00100c85: 'PDSON',
      0x001100a6: 'NOTSRCERAS',
      0x00120868: 'SDPXNO',
      0x001302c8: 'SDPAO',
      0x00140869: 'DPSXNO',
      0x001502c9: 'DPSAO',
      0x00165cca: 'PSDPSANAX',
      0x00171d54: 'SSPXDSXAX',
      0x00180d59: 'SPXPDX',
      0x00191cc8: 'SDPSANAX',
      0x001a06c5: 'PDSPAO',
      0x001b0768: 'SDPSXAX',
      0x001c06ca: 'PSDPAO',
      0x001d0766: 'DSPDXAX',
      0x001e01a5: 'PDSO',
      0x001f0385: 'PDSOA',
      0x00200f09: 'DPSNA',
      0x00210248: 'SDPXO',
      0x00220326: 'DSN',
      0x00230b24: 'SPDNAO',
      0x00240d55: 'SPXDSX',
      0x00251cc5: 'PDSPANAX',
      0x002606c8: 'SDPSAO',
      0x00271868: 'SDPSXNOX',
      0x00280369: 'DPSXA',
      0x002916ca: 'PSDPSAOXXN',
      0x002a0cc9: 'DPSANA',
      0x002b1d58: 'SSPXPDXAXN',
      0x002c0784: 'SPDSOAX',
      0x002d060a: 'PSDNOX',
      0x002e064a: 'PSDPXOX',
      0x002f0e2a: 'PSDNOAN',
      0x0030032a: 'PSNA',
      0x00310b28: 'SDPNAON',
      0x00320688: 'SDPSOOX',
      0x00330008: 'NOTSRCCOPY',
      0x003406c4: 'SPDSAOX',
      0x00351864: 'SPDSXNOX',
      0x003601a8: 'SDPOX',
      0x00370388: 'SDPOAN',
      0x0038078a: 'PSDPOAX',
      0x00390604: 'SPDNOX',
      0x003a0644: 'SPDSXOX',
      0x003b0e24: 'SPDNOAN',
      0x003c004a: 'PSX',
      0x003d18a4: 'SPDSONOX',
      0x003e1b24: 'SPDSNAOX',
      0x003f00ea: 'PSAN',
      0x00400f0a: 'PSDNAA',
      0x00410249: 'DPSXON',
      0x00420d5d: 'SDXPDXA',
      0x00431cc4: 'SPDSANAXN',
      0x00440328: 'SRCERASE',
      0x00450b29: 'DPSNAON',
      0x004606c6: 'DSPDAOX',
      0x0047076a: 'PSDPXAXN',
      0x00480368: 'SDPXA',
      0x004916c5: 'PDSPDAOXXN',
      0x004a0789: 'DPSDOAX',
      0x004b0605: 'PDSNOX',
      0x004c0cc8: 'SDPANA',
      0x004d1954: 'SSPXDSXOXN',
      0x004e0645: 'PDSPXOX',
      0x004f0e25: 'PDSNOAN',
      0x00500325: 'PDNA',
      0x00510b26: 'DSPNAON',
      0x005206c9: 'DPSDAOX',
      0x00530764: 'SPDSXAXN',
      0x005408a9: 'DPSONON',
      0x00550009: 'DSTINVERT',
      0x005601a9: 'DPSOX',
      0x00570389: 'DPSOAN',
      0x00580785: 'PDSPOAX',
      0x00590609: 'DPSNOX',
      0x005a0049: 'PATINVERT',
      0x005b18a9: 'DPSDONOX',
      0x005c0649: 'DPSDXOX',
      0x005d0e29: 'DPSNOAN',
      0x005e1b29: 'DPSDNAOX',
      0x005f00e9: 'DPAN',
      0x00600365: 'PDSXA',
      0x006116c6: 'DSPDSAOXXN',
      0x00620786: 'DSPDOAX',
      0x00630608: 'SDPNOX',
      0x00640788: 'SDPSOAX',
      0x00650606: 'DSPNOX',
      0x00660046: 'SRCINVERT',
      0x006718a8: 'SDPSONOX',
      0x006858a6: 'DSPDSONOXXN',
      0x00690145: 'PDSXXN',
      0x006a01e9: 'DPSAX',
      0x006b178a: 'PSDPSOAXXN',
      0x006c01e8: 'SDPAX',
      0x006d1785: 'PDSPDOAXXN',
      0x006e1e28: 'SDPSNOAX',
      0x006f0c65: 'PDXNAN',
      0x00700cc5: 'PDSANA',
      0x00711d5c: 'SSDXPDXAXN',
      0x00720648: 'SDPSXOX',
      0x00730e28: 'SDPNOAN',
      0x00740646: 'DSPDXOX',
      0x00750e26: 'DSPNOAN',
      0x00761b28: 'SDPSNAOX',
      0x007700e6: 'DSAN',
      0x007801e5: 'PDSAX',
      0x00791786: 'DSPDSOAXXN',
      0x007a1e29: 'DPSDNOAX',
      0x007b0c68: 'SDPXNAN',
      0x007c1e24: 'SPDSNOAX',
      0x007d0c69: 'DPSXNAN',
      0x007e0955: 'SPXDSXO',
      0x007f03c9: 'DPSAAN',
      0x008003e9: 'DPSAA',
      0x00810975: 'SPXDSXON',
      0x00820c49: 'DPSXNA',
      0x00831e04: 'SPDSNOAXN',
      0x00840c48: 'SDPXNA',
      0x00851e05: 'PDSPNOAXN',
      0x008617a6: 'DSPDSOAXX',
      0x008701c5: 'PDSAXN',
      0x008800c6: 'SRCAND',
      0x00891b08: 'SDPSNAOXN',
      0x008a0e06: 'DSPNOA',
      0x008b0666: 'DSPDXOXN',
      0x008c0e08: 'SDPNOA',
      0x008d0668: 'SDPSXOXN',
      0x008e1d7c: 'SSDXPDXAX',
      0x008f0ce5: 'PDSANAN',
      0x00900c45: 'PDSXNA',
      0x00911e08: 'SDPSNOAXN',
      0x009217a9: 'DPSDPOAXX',
      0x009301c4: 'SPDAXN',
      0x009417aa: 'PSDPSOAXX',
      0x009501c9: 'DPSAXN',
      0x00960169: 'DPSXX',
      0x0097588a: 'PSDPSONOXX',
      0x00981888: 'SDPSONOXN',
      0x00990066: 'DSXN',
      0x009a0709: 'DPSNAX',
      0x009b07a8: 'SDPSOAXN',
      0x009c0704: 'SPDNAX',
      0x009d07a6: 'DSPDOAXN',
      0x009e16e6: 'DSPDSAOXX',
      0x009f0345: 'PDSXAN',
      0x00a000c9: 'DPA',
      0x00a11b05: 'PDSPNAOXN',
      0x00a20e09: 'DPSNOA',
      0x00a30669: 'DPSDXOXN',
      0x00a41885: 'PDSPONOXN',
      0x00a50065: 'PDXN',
      0x00a60706: 'DSPNAX',
      0x00a707a5: 'PDSPOAXN',
      0x00a803a9: 'DPSOA',
      0x00a90189: 'DPSOXN',
      0x00aa0029: 'D',
      0x00ab0889: 'DPSONO',
      0x00ac0744: 'SPDSXAX',
      0x00ad06e9: 'DPSDAOXN',
      0x00ae0b06: 'DSPNAO',
      0x00af0229: 'DPNO',
      0x00b00e05: 'PDSNOA',
      0x00b10665: 'PDSPXOXN',
      0x00b21974: 'SSPXDSXOX',
      0x00b30ce8: 'SDPANAN',
      0x00b4070a: 'PSDNAX',
      0x00b507a9: 'DPSDOAXN',
      0x00b616e9: 'DPSDPAOXX',
      0x00b70348: 'SDPXAN',
      0x00b8074a: 'PSDPXAX',
      0x00b906e6: 'DSPDAOXN',
      0x00ba0b09: 'DPSNAO',
      0x00bb0226: 'MERGEPAINT',
      0x00bc1ce4: 'SPDSANAX',
      0x00bd0d7d: 'SDXPDXAN',
      0x00be0269: 'DPSXO',
      0x00bf08c9: 'DPSANO',
      0x00c000ca: 'MERGECOPY',
      0x00c11b04: 'SPDSNAOXN',
      0x00c21884: 'SPDSONOXN',
      0x00c3006a: 'PSXN',
      0x00c40e04: 'SPDNOA',
      0x00c50664: 'SPDSXOXN',
      0x00c60708: 'SDPNAX',
      0x00c707aa: 'PSDPOAXN',
      0x00c803a8: 'SDPOA',
      0x00c90184: 'SPDOXN',
      0x00ca0749: 'DPSDXAX',
      0x00cb06e4: 'SPDSAOXN',
      0x00cc0020: 'SRCCOPY',
      0x00cd0888: 'SDPONO',
      0x00ce0b08: 'SDPNAO',
      0x00cf0224: 'SPNO',
      0x00d00e0a: 'PSDNOA',
      0x00d1066a: 'PSDPXOXN',
      0x00d20705: 'PDSNAX',
      0x00d307a4: 'SPDSOAXN',
      0x00d41d78: 'SSPXPDXAX',
      0x00d50ce9: 'DPSANAN',
      0x00d616ea: 'PSDPSAOXX',
      0x00d70349: 'DPSXAN',
      0x00d80745: 'PDSPXAX',
      0x00d906e8: 'SDPSAOXN',
      0x00da1ce9: 'DPSDANAX',
      0x00db0d75: 'SPXDSXAN',
      0x00dc0b04: 'SPDNAO',
      0x00dd0228: 'SDNO',
      0x00de0268: 'SDPXO',
      0x00df08c8: 'SDPANO',
      0x00e003a5: 'PDSOA',
      0x00e10185: 'PDSOXN',
      0x00e20746: 'DSPDXAX',
      0x00e306ea: 'PSDPAOXN',
      0x00e40748: 'SDPSXAX',
      0x00e506e5: 'PDSPAOXN',
      0x00e61ce8: 'SDPSANAX',
      0x00e70d79: 'SPXPDXAN',
      0x00e81d74: 'SSPXDSXAX',
      0x00e95ce6: 'DSPDSANAXXN',
      0x00ea02e9: 'DPSAO',
      0x00eb0849: 'DPSXNO',
      0x00ec02e8: 'SDPAO',
      0x00ed0848: 'SDPXNO',
      0x00ee0086: 'SRCPAINT',
      0x00ef0a08: 'SDPNOO',
      0x00f00021: 'PATCOPY',
      0x00f10885: 'PDSONO',
      0x00f20b05: 'PDSNAO',
      0x00f3022a: 'PSNO',
      0x00f40b0a: 'PSDNAO',
      0x00f50225: 'PDNO',
      0x00f60265: 'PDSXO',
      0x00f708c5: 'PDSANO',
      0x00f802e5: 'PDSAO',
      0x00f90845: 'PDSXNO',
      0x00fa0089: 'DPO',
      0x00fb0a09: 'PATPAINT',
      0x00fc008a: 'PSO',
      0x00fd0a0a: 'PSDNOO',
      0x00fe02a9: 'DPSOO',
      0x00ff0062: 'WHITENESS'}

  def _DebugPrintHeader(self, file_header):
    """Prints header debug information.

    Args:
      file_header (wmf_header): file header.
    """
    self._DebugPrintValue('File type', f'0x{file_header.file_type:04x}')
    self._DebugPrintValue('Record size', f'{file_header.record_size:d}')
    self._DebugPrintValue('Format version', f'{file_header.format_version:d}')
    self._DebugPrintValue('File size lower', f'{file_header.file_size_lower:d}')
    self._DebugPrintValue('File size upper', f'{file_header.file_size_upper:d}')
    self._DebugPrintValue(
        'Maximum number of object',
        f'{file_header.maximum_number_of_objects:d}')
    self._DebugPrintValue(
        'Largest record size', f'{file_header.largest_record_size:d}')
    self._DebugPrintValue(
        'Number of records', f'{file_header.number_of_records:d}')
    self._DebugPrintText('\n')

  def _DebugPrintPlaceable(self, placeable):
    """Prints placeable debug information.

    Args:
      placeable (wmf_placeable): placeable.
    """
    self._DebugPrintValue('Signature', f'0x{placeable.signature:08x}')
    self._DebugPrintValue(
        'Resource handle', f'0x{placeable.resource_handle:04x}')
    self._DebugPrintData('Bounding box', placeable.bounding_box)
    self._DebugPrintValue(
        'Number of units per inch', f'{placeable.number_of_units_per_inch:d}')
    self._DebugPrintValue('Unknown1', f'0x{placeable.unknown1:08x}')
    self._DebugPrintValue('Checksum', f'0x{placeable.checksum:04x}')
    self._DebugPrintText('\n')

  def _DebugPrintRecordHeader(self, record_header):
    """Prints record header debug information.

    Args:
      record_header (wmf_record_header): record header.
    """
    number_of_bytes = record_header.record_size * 2
    self._DebugPrintValue('Record size', (
        f'{record_header.record_size:d} ({number_of_bytes:d} bytes)'))

    record_type_string = self._RECORD_TYPE.GetName(
        record_header.record_type) or 'UNKNOWN'
    self._DebugPrintValue('Record type', (
        f'0x{record_header.record_type:04x} ({record_type_string:s})'))

    self._DebugPrintText('\n')

  def _ReadHeader(self, file_object):
    """Reads a header.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the header cannot be read.
    """
    file_offset = file_object.tell()

    data_type_map = self._GetDataTypeMap('wmf_header')

    header, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'header')

    if self._debug:
      self._DebugPrintHeader(header)

    if header.file_type not in (1, 2):
      raise errors.ParseError(f'Unsupported file type: {header.file_type:d}')

    if header.record_size != 9:
      raise errors.ParseError(
          f'Unsupported record size: {header.record_size:d}')

  def _ReadPlaceable(self, file_object):
    """Reads a placeable.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the placeable cannot be read.
    """
    file_offset = file_object.tell()

    data_type_map = self._GetDataTypeMap('wmf_placeable')

    placeable, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'placeable')

    if self._debug:
      self._DebugPrintPlaceable(placeable)

  def _ReadRecord(self, file_object, file_offset):
    """Reads a record.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the data relative to the start of
          the file-like object.

    Returns:
      Record: a record.

    Raises:
      ParseError: if the record cannot be read.
    """
    data_type_map = self._GetDataTypeMap('wmf_record_header')

    record_header, data_offset = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'record header')

    if self._debug:
      self._DebugPrintRecordHeader(record_header)

    record_size = record_header.record_size * 2

    data_size = record_size - (data_offset - file_offset)

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
      self._DebugPrintData('Record data', record_data)

    # TODO: use lookup dict with callback.
    data_type_map = self._WMF_RECORD_DATA_STRUCT_TYPES.get(record_type, None)
    if not data_type_map:
      return

    try:
      record = data_type_map.MapByteStream(record_data)
    except dtfabric_errors.MappingError as exception:
      raise errors.ParseError(
          f'Unable to parse record data with error: {exception!s}')

    if self._debug:
      if record_type == 0x0103:
        map_mode_string = self._MAP_MODE.GetName(record.map_mode) or 'UNKNOWN'
        self._DebugPrintValue(
            'Map mode', f'0x{record.map_mode:04x} ({map_mode_string:s})')

      elif record_type == 0x0107:
        stretch_mode_string = self._MAP_MODE.GetName(
            record.stretch_mode) or 'UNKNOWN'
        self._DebugPrintValue('Stretch mode', (
            f'0x{record.stretch_mode:04x} ({stretch_mode_string:s})'))

      elif record_type == 0x0127:
        self._DebugPrintValue(
            'Number of saved device context',
            f'{record.number_of_saved_device_context:d}')

      elif record_type in (0x020b, 0x020c):
        self._DebugPrintValue('X coordinate', f'{record.x_coordinate:d}')

        self._DebugPrintValue('Y coordinate', f'{record.y_coordinate:d}')

      elif record_type == 0x0b41:
        raster_operation_string = self._WMF_RASTER_OPERATIONS.get(
            record.raster_operation, 'UNKNOWN')
        self._DebugPrintValue('Raster operation', (
            f'0x{record.raster_operation:08x} ({raster_operation_string:s})'))

        self._DebugPrintValue('Source height', f'{record.source_height:d}')

        self._DebugPrintValue('Source width', f'{record.source_width:d}')

        self._DebugPrintValue(
            'Source X coordinate', f'{record.source_x_coordinate:d}')

        self._DebugPrintValue(
            'Source Y coordinate', f'{record.source_y_coordinate:d}')

        self._DebugPrintValue(
            'Destination height', f'{record.destination_height:d}')

        self._DebugPrintValue(
            'Destination width', f'{record.destination_width:d}')

        self._DebugPrintValue(
            'Destination X coordinate', f'{record.destination_x_coordinate:d}')

        self._DebugPrintValue(
            'Destination Y coordinate', f'{record.destination_y_coordinate:d}')

      self._DebugPrintText('\n')

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
          f'Unable to read file signature with error: {exception!s}')

    if signature == self._WMF_PLACEABLE_SIGNATURE:
      self._ReadPlaceable(file_object)

    self._ReadHeader(file_object)

    file_offset = file_object.tell()
    while file_offset < self._file_size:
      record = self._ReadRecord(file_object, file_offset)

      file_offset += record.size
