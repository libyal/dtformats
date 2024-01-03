# -*- coding: utf-8 -*-
"""IndexedDB database files."""

from dtformats import leveldb


class IndexedDBDatabaseEntry(object):
  """IndexedDB entry.

  Attributes:
    key_segments (list[int|str]): key segments.
    sequence_number (int): sequence number.
    value (bytes): value.
    value_type (int): value type.
  """

  def __init__(self, key_segments, sequence_number, value_type, value):
    """Initializes a IndexedDB table entry.

    Args:
      key_segments (list[int|str]): key segments.
      sequence_number (int): sequence number.
      value_type (int): value type.
      value (bytes): value.
    """
    super(IndexedDBDatabaseEntry, self).__init__()
    self.key_segments = key_segments
    self.sequence_number = sequence_number
    self.value_type = value_type
    self.value = value


class IndexedDBDatabaseTableFile(leveldb.LevelDBDatabaseTableFile):
  """IndexedDB database sorted tables (.ldb) file."""

  def _ReadKeyPrefix(self, data):
    """Reads a key prefix.

    Args:
      data (bytes): data.

    Returns:
      tuple[tuple[int, int, int], int]: key prefix and number of bytes read.
    """
    byte_value = data[0]
    bytes_read = 1

    database_identifier = 0
    object_store_identifier = 0
    index_identifier = 0

    bit_shift = 0
    for _ in range((byte_value >> 5) + 1):
      database_identifier |= data[bytes_read] << bit_shift
      bytes_read += 1
      bit_shift += 8

    bit_shift = 0
    for _ in range(((byte_value & 0x1f) >> 2) + 1):
      object_store_identifier |= data[bytes_read] << bit_shift
      bytes_read += 1
      bit_shift += 8

    bit_shift = 0
    for _ in range((byte_value & 0x03) + 1):
      index_identifier |= data[bytes_read] << bit_shift
      bytes_read += 1
      bit_shift += 8

    key_prefix = (
        database_identifier, object_store_identifier, index_identifier)

    return key_prefix, bytes_read

  def ReadEntries(self):
    """Reads the table entries.

    Yields:
      IndexedDBDatabaseEntry: entry.

    Raises:
      ParseError: if the entries cannot be read.
    """
    table_entries_iterator = super(
        IndexedDBDatabaseTableFile, self).ReadTableEntries()

    for table_entry in table_entries_iterator:
      key_prefix, bytes_read = self._ReadKeyPrefix(table_entry.key)

      key_segments = [f'{value:d}' for value in key_prefix]

      if key_prefix == (0, 0, 0):
        metadata_type = int(table_entry.key[bytes_read])
        bytes_read += 1

        key_segments.append(f'{metadata_type:d}')

      # Represent the reamaining key as a string without leading b
      if bytes_read < len(table_entry.key):
        remaining_key = repr(table_entry.key[bytes_read:])[1:]
        key_segments.append(remaining_key)

      yield IndexedDBDatabaseEntry(
          key_segments, table_entry.sequence_number, table_entry.value_type,
          table_entry.value)
