#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script to decodes a NSKeyedArchiver encoded plist."""

import argparse
import base64
import json
import plistlib
import sys
import uuid


class NSKeyedArchiverDecoder(object):
  """Decodes a NSKeyedArchiver encoded plist."""

  # TODO: add support for NSAttributedString
  # TODO: add support for NSData
  # TODO: add support for NSDate
  # TODO: add support for NSMutableAttributedString
  # TODO: add support for NSMutableData
  # TODO: add support for NSMutableString
  # TODO: add support for NSValue
  # TODO: add support for SFLListItem

  _CALLBACKS = {
      'BackgroundItemContainer': '_DecodeComposite',
      'BackgroundItems': '_DecodeComposite',
      'BackgroundLoginItem': '_DecodeComposite',
      'Bookmark': '_DecodeComposite',
      'BTMUserSettings': '_DecodeComposite',
      'ItemRecord': '_DecodeComposite',
      'NSArray': '_DecodeNSArray',
      'NSDictionary': '_DecodeNSDictionary',
      'NSHashTable': '_DecodeNSHashTable',
      'NSMutableArray': '_DecodeNSArray',
      'NSMutableDictionary': '_DecodeNSDictionary',
      'NSMutableSet': '_DecodeNSSet',
      'NSSet': '_DecodeNSSet',
      'NSURL': '_DecodeNSURL',
      'NSUUID': '_DecodeNSUUID',
      'Storage': '_DecodeComposite'}

  def _DecodeComposite(self, encoded_object, objects_list):
    """Decodes a composite object.

    Args:
      encoded_object (object): encoded object.
      list[object]: $objects list.

    Returns:
      object: decoded object.
    """
    decoded_dict = {}

    for key in encoded_object:
      if key == '$class':
        continue

      encoded_value = encoded_object.get(key, None)
      if encoded_value:
        decoded_value = self._DecodeObject(encoded_value, objects_list)

        decoded_dict[key] = decoded_value

    return decoded_dict

  def _DecodeContainer(self, encoded_object, objects_list):
    """Decodes a container object.

    Args:
      encoded_object (object): encoded object.
      list[object]: $objects list.

    Returns:
      object: decoded object.
    """
    decoded_dict = {}

    for key in encoded_object:
      if key in ('$class', 'container'):
        continue

      encoded_value = encoded_object.get(key, None)
      if encoded_value:
        decoded_value = self._DecodeObject(encoded_value, objects_list)

        decoded_dict[key] = decoded_value

    return decoded_dict

  def _DecodeNSArray(self, encoded_object, objects_list):
    """Decodes a NSArray.

    Args:
      encoded_object (object): encoded object.
      list[object]: $objects list.

    Returns:
      object: decoded object.
    """
    if 'NS.objects' not in encoded_object:
      raise RuntimeError('Missing NS.objects')

    return [self._DecodeObject(element, objects_list)
            for element in encoded_object['NS.objects']]

  def _DecodeNSDictionary(self, encoded_object, objects_list):
    """Decodes a NSDictionary.

    Args:
      encoded_object (object): encoded object.
      list[object]: $objects list.

    Returns:
      object: decoded object.
    """
    if 'NS.keys' not in encoded_object or 'NS.objects' not in encoded_object:
      raise RuntimeError('Missing NS.keys or NS.objects')

    ns_keys = encoded_object['NS.keys']
    ns_objects = encoded_object['NS.objects']

    if len(ns_keys) != len(ns_objects):
      raise RuntimeError('Mismatch between number of NS.keys and NS.objects')

    decoded_dict = {}

    for index, encoded_key in enumerate(ns_keys):
      decoded_key = self._DecodeObject(encoded_key, objects_list)

      encoded_value = ns_objects[index]
      decoded_value = self._DecodeObject(encoded_value, objects_list)

      decoded_dict[decoded_key] = decoded_value

    return decoded_dict

  def _DecodeNSHashTable(self, encoded_object, objects_list):
    """Decodes a NSHashTable.

    Args:
      encoded_object (object): encoded object.
      list[object]: $objects list.

    Returns:
      object: decoded object.
    """
    if '$1' not in encoded_object:
      raise RuntimeError('Missing $1')

    value_object = encoded_object['$1']

    plist_uid = self._GetPlistUID(value_object)
    if plist_uid is None:
      encoded_object_type = type(value_object)
      raise RuntimeError(
          f'Unsupported encoded object $1 type: {encoded_object_type!s}')

    referenced_object = objects_list[plist_uid]

    # TODO: what about value $0? It seems to indicate the number of elements
    # in the hash table.
    # TODO: what about value $2?

    return self._DecodeContainer(referenced_object, objects_list)

  def _DecodeNSSet(self, encoded_object, objects_list):
    """Decodes a NSSet.

    Args:
      encoded_object (object): encoded object.
      list[object]: $objects list.

    Returns:
      object: decoded object.
    """
    if 'NS.objects' not in encoded_object:
      raise RuntimeError('Missing NS.objects')

    decoded_list = []

    for value_object in encoded_object['NS.objects']:
      plist_uid = self._GetPlistUID(value_object)
      referenced_object = objects_list[plist_uid]

      decoded_element = self._DecodeContainer(referenced_object, objects_list)

      decoded_list.append(decoded_element)

    return decoded_element

  def _DecodeNSURL(self, encoded_object, objects_list):
    """Decodes a NSURL.

    Args:
      encoded_object (object): encoded object.
      list[object]: $objects list.

    Returns:
      object: decoded object.
    """
    if 'NS.base' not in encoded_object or 'NS.relative' not in encoded_object:
      raise RuntimeError('Missing NS.base or NS.relative')

    decoded_base = self._DecodeObject(encoded_object['NS.base'], objects_list)

    decoded_relative = self._DecodeObject(
        encoded_object['NS.relative'], objects_list)

    if decoded_base:
      decoded_url = '/'.join([decoded_base, decoded_relative])
    else:
      decoded_url = decoded_relative

    return decoded_url

  # pylint: disable=unused-argument
  def _DecodeNSUUID(self, encoded_object, objects_list):
    """Decodes a NSUUID.

    Args:
      encoded_object (object): encoded object.
      list[object]: $objects list.

    Returns:
      object: decoded object.
    """
    if 'NS.uuidbytes' not in encoded_object:
      raise RuntimeError('Missing NS.uuidbytes')

    ns_uuidbytes = encoded_object['NS.uuidbytes']
    if len(ns_uuidbytes) != 16:
      raise RuntimeError('Unsupported NS.uuidbytes size')

    return str(uuid.UUID(bytes=ns_uuidbytes))

  def _DecodeObject(self, encoded_object, objects_list):
    """Decodes an object.

    Args:
      encoded_object (object): encoded object.
      list[object]: $objects list.

    Returns:
      object: decoded object.
    """
    # Due to how plist UID are stored in an XML plsit we need to test for it
    # before testing for a dict.

    plist_uid = self._GetPlistUID(encoded_object)
    if plist_uid is not None:
      referenced_object = objects_list[plist_uid]
      return self._DecodeObject(referenced_object, objects_list)

    if (encoded_object is None or
        isinstance(encoded_object, (bool, int, float))):
      return encoded_object

    if isinstance(encoded_object, bytes):
      return str(base64.urlsafe_b64encode(encoded_object))[2:-1]

    if isinstance(encoded_object, str):
      if encoded_object == '$null':
        return None

      return encoded_object

    if isinstance(encoded_object, dict):
      encoded_class = encoded_object.get('$class', None)
      if not encoded_class:
        return encoded_object

      decoded_class = self._DecodeObject(encoded_class, objects_list)
      class_name = decoded_class.get('$classname', None)
      if not class_name:
        return encoded_object

      callback_method = self._CALLBACKS.get(class_name, None)
      if not callback_method:
        raise RuntimeError(f'Missing callback for class: {class_name:s}')

      callback = getattr(self, callback_method, None)
      return callback(encoded_object, objects_list)

    if isinstance(encoded_object, list):
      return [self._DecodeObject(element, objects_list)
              for element in encoded_object]

    encoded_object_type = type(encoded_object)
    raise RuntimeError(
        f'Unsupported encoded object type: {encoded_object_type!s}')

  def _GetPlistUID(self, encoded_object):
    """Retrieves a plist UID.

    Args:
      encoded_object (object): encoded object.

    Returns:
      int: plist UID or None if not available.
    """
    if isinstance(encoded_object, plistlib.UID):
      return encoded_object.data

    if (isinstance(encoded_object, dict) and 'CF$UID' in encoded_object and
        len(encoded_object) == 1):
      return encoded_object['CF$UID']

    return None

  def DecodePlistFile(self, path):
    """Decodes a NSKeyedArchiver encoded plist file.

    Args:
      path (str): path of the plist file.

    Returns:
      dict[str, object]: unarchived plist.
    """
    with open(path, 'rb') as file_object:
      encoded_plist = plistlib.load(file_object)

    archiver = encoded_plist.get('$archiver')
    version = encoded_plist.get('$version')
    if archiver != 'NSKeyedArchiver' or version != 100000:
      raise RuntimeError(f'Unsupported plist: {archiver!s} {version!s}')

    decoded_plist = {}

    objects_list = encoded_plist.get('$objects') or []

    for name, value in encoded_plist.get('$top', {}).items():
      plist_uid = self._GetPlistUID(value)
      if plist_uid is not None:
        encoded_object = objects_list[plist_uid]

        value = self._DecodeObject(encoded_object, objects_list)

      decoded_plist[name] = value

    return decoded_plist


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Decodes NSKeyedArchiver encoded plist files.'))

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH', default=None,
      help='path of the NSKeyedArchiver encoded plist file.')

  options = argument_parser.parse_args()

  if not options.source:
    print('Source file missing.')
    print('')
    argument_parser.print_help()
    print('')
    return False

  decoder = NSKeyedArchiverDecoder()
  plist = decoder.DecodePlistFile(options.source)

  print(json.dumps(plist))

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
