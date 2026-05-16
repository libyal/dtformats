"""Tests for Safari Cookies (Cookies.binarycookies) files."""

import io
import os
import unittest

from dtformats import errors
from dtformats import safari_cookies

from tests import test_lib


class BinaryCookiesFileTest(test_lib.BaseTestCase):
    """Safari Cookies (Cookies.binarycookies) file tests."""

    # pylint: disable=protected-access

    _FILE_HEADER_DATA = bytes(
        bytearray(
            [
                0x63,
                0x6F,
                0x6F,
                0x6B,
                0x00,
                0x00,
                0x00,
                0x1D,
                0x00,
                0x00,
                0x00,
                0x76,
                0x00,
                0x00,
                0x00,
                0x95,
                0x00,
                0x00,
                0x00,
                0x80,
                0x00,
                0x00,
                0x01,
                0x31,
                0x00,
                0x00,
                0x00,
                0xCD,
                0x00,
                0x00,
                0x06,
                0xC9,
                0x00,
                0x00,
                0x02,
                0x34,
                0x00,
                0x00,
                0x01,
                0x2C,
                0x00,
                0x00,
                0x02,
                0x08,
                0x00,
                0x00,
                0x03,
                0x3D,
                0x00,
                0x00,
                0x00,
                0xA2,
                0x00,
                0x00,
                0x04,
                0x08,
                0x00,
                0x00,
                0x03,
                0x58,
                0x00,
                0x00,
                0x02,
                0x4E,
                0x00,
                0x00,
                0x02,
                0x88,
                0x00,
                0x00,
                0x05,
                0x6E,
                0x00,
                0x00,
                0x01,
                0x05,
                0x00,
                0x00,
                0x01,
                0x20,
                0x00,
                0x00,
                0x00,
                0xD3,
                0x00,
                0x00,
                0x00,
                0x76,
                0x00,
                0x00,
                0x01,
                0x8D,
                0x00,
                0x00,
                0x00,
                0xF4,
                0x00,
                0x00,
                0x01,
                0x95,
                0x00,
                0x00,
                0x00,
                0x6A,
                0x00,
                0x00,
                0x00,
                0x77,
                0x00,
                0x00,
                0x00,
                0xED,
                0x00,
                0x00,
                0x00,
                0xA6,
                0x00,
                0x00,
                0x00,
                0xA3,
                0x00,
                0x00,
                0x00,
                0x76,
            ]
        )
    )

    _FILE_HEADER_DATA_BAD_SIGNATURE = bytes(
        bytearray(
            [
                0xFF,
                0xFF,
                0xFF,
                0xFF,
                0x00,
                0x00,
                0x00,
                0x1D,
                0x00,
                0x00,
                0x00,
                0x76,
                0x00,
                0x00,
                0x00,
                0x95,
                0x00,
                0x00,
                0x00,
                0x80,
                0x00,
                0x00,
                0x01,
                0x31,
                0x00,
                0x00,
                0x00,
                0xCD,
                0x00,
                0x00,
                0x06,
                0xC9,
                0x00,
                0x00,
                0x02,
                0x34,
                0x00,
                0x00,
                0x01,
                0x2C,
                0x00,
                0x00,
                0x02,
                0x08,
                0x00,
                0x00,
                0x03,
                0x3D,
                0x00,
                0x00,
                0x00,
                0xA2,
                0x00,
                0x00,
                0x04,
                0x08,
                0x00,
                0x00,
                0x03,
                0x58,
                0x00,
                0x00,
                0x02,
                0x4E,
                0x00,
                0x00,
                0x02,
                0x88,
                0x00,
                0x00,
                0x05,
                0x6E,
                0x00,
                0x00,
                0x01,
                0x05,
                0x00,
                0x00,
                0x01,
                0x20,
                0x00,
                0x00,
                0x00,
                0xD3,
                0x00,
                0x00,
                0x00,
                0x76,
                0x00,
                0x00,
                0x01,
                0x8D,
                0x00,
                0x00,
                0x00,
                0xF4,
                0x00,
                0x00,
                0x01,
                0x95,
                0x00,
                0x00,
                0x00,
                0x6A,
                0x00,
                0x00,
                0x00,
                0x77,
                0x00,
                0x00,
                0x00,
                0xED,
                0x00,
                0x00,
                0x00,
                0xA6,
                0x00,
                0x00,
                0x00,
                0xA3,
                0x00,
                0x00,
                0x00,
                0x76,
            ]
        )
    )

    _PAGE_DATA = bytes(
        bytearray(
            [
                0x6C,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x62,
                0x00,
                0x00,
                0x00,
                0x38,
                0x00,
                0x00,
                0x00,
                0x6A,
                0x00,
                0x00,
                0x00,
                0x3D,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x80,
                0x77,
                0xE5,
                0x94,
                0xCE,
                0x41,
                0x00,
                0x00,
                0x00,
                0x70,
                0x2D,
                0x8B,
                0xB7,
                0x41,
                0x53,
                0x57,
                0x49,
                0x44,
                0x00,
                0x43,
                0x42,
                0x45,
                0x43,
                0x37,
                0x46,
                0x30,
                0x42,
                0x2D,
                0x43,
                0x36,
                0x34,
                0x45,
                0x2D,
                0x34,
                0x32,
                0x39,
                0x30,
                0x2D,
                0x38,
                0x37,
                0x33,
                0x45,
                0x2D,
                0x31,
                0x42,
                0x31,
                0x38,
                0x33,
                0x30,
                0x33,
                0x31,
                0x33,
                0x39,
                0x35,
                0x44,
                0x00,
                0x2E,
                0x67,
                0x6F,
                0x2E,
                0x63,
                0x6F,
                0x6D,
                0x00,
                0x2F,
                0x00,
            ]
        )
    )

    def testDebugPrintFileHeader(self):
        """Tests the _DebugPrintFileHeader function."""
        output_writer = test_lib.TestOutputWriter()
        test_file = safari_cookies.BinaryCookiesFile(output_writer=output_writer)

        data_type_map = test_file._GetDataTypeMap("binarycookies_file_header")

        file_header = data_type_map.CreateStructureValues(
            number_of_pages=1, signature=b"cook"
        )

        test_file._DebugPrintFileHeader(file_header)

    def testDebugPrintRecordHeader(self):
        """Tests the _DebugPrintRecordHeader function."""
        output_writer = test_lib.TestOutputWriter()
        test_file = safari_cookies.BinaryCookiesFile(output_writer=output_writer)

        data_type_map = test_file._GetDataTypeMap("binarycookies_record_header")

        record_header = data_type_map.CreateStructureValues(
            creation_time=0,
            expiration_time=1,
            flags=2,
            name_offset=3,
            path_offset=4,
            size=5,
            unknown1=6,
            unknown2=7,
            unknown3=8,
            url_offset=9,
            value_offset=10,
        )

        test_file._DebugPrintRecordHeader(record_header)

    def testReadCString(self):
        """Tests the _ReadCString function."""
        output_writer = test_lib.TestOutputWriter()
        test_file = safari_cookies.BinaryCookiesFile(output_writer=output_writer)

        page_data = b"string\x00"

        cstring = test_file._ReadCString(page_data, 0)
        self.assertEqual(cstring, "string")

        with self.assertRaises(errors.ParseError):
            test_file._ReadCString(page_data[:-1], 0)

    def testReadFileFooter(self):
        """Tests the _ReadFileFooter function."""
        output_writer = test_lib.TestOutputWriter()
        test_file = safari_cookies.BinaryCookiesFile(output_writer=output_writer)

        test_file_path = self._GetTestFilePath(["Cookies.binarycookies"])
        self._SkipIfPathNotExists(test_file_path)

        with open(test_file_path, "rb") as file_object:
            file_object.seek(-8, os.SEEK_END)
            test_file._ReadFileFooter(file_object)

    def testReadFileHeader(self):
        """Tests the _ReadFileHeader function."""
        output_writer = test_lib.TestOutputWriter()
        test_file = safari_cookies.BinaryCookiesFile(output_writer=output_writer)

        file_object = io.BytesIO(self._FILE_HEADER_DATA)

        test_file._ReadFileHeader(file_object)

        file_object = io.BytesIO(self._FILE_HEADER_DATA_BAD_SIGNATURE)

        with self.assertRaises(errors.ParseError):
            test_file._ReadFileHeader(file_object)

        file_object = io.BytesIO(self._FILE_HEADER_DATA[:-1])

        with self.assertRaises(errors.ParseError):
            test_file._ReadFileHeader(file_object)

    def testReadPage(self):
        """Tests the _ReadPage function."""
        output_writer = test_lib.TestOutputWriter()
        test_file = safari_cookies.BinaryCookiesFile(output_writer=output_writer)

        test_file_path = self._GetTestFilePath(["Cookies.binarycookies"])
        self._SkipIfPathNotExists(test_file_path)

        with open(test_file_path, "rb") as file_object:
            test_file._ReadFileHeader(file_object)
            test_file._ReadPage(
                file_object, file_object.tell(), test_file._page_sizes[0]
            )

        # TODO: test errors.ParseError exception being raised.

    def testReadPages(self):
        """Tests the _ReadPages function."""
        output_writer = test_lib.TestOutputWriter()
        test_file = safari_cookies.BinaryCookiesFile(output_writer=output_writer)

        test_file_path = self._GetTestFilePath(["Cookies.binarycookies"])
        self._SkipIfPathNotExists(test_file_path)

        with open(test_file_path, "rb") as file_object:
            test_file._ReadFileHeader(file_object)
            test_file._ReadPages(file_object)

    def testReadRecord(self):
        """Tests the _ReadRecord function."""
        output_writer = test_lib.TestOutputWriter()
        test_file = safari_cookies.BinaryCookiesFile(output_writer=output_writer)

        test_file._ReadRecord(self._PAGE_DATA, 0)

        with self.assertRaises(errors.ParseError):
            test_file._ReadRecord(self._PAGE_DATA[:-1], 0)

    def testReadFileObject(self):
        """Tests the ReadFileObject function."""
        output_writer = test_lib.TestOutputWriter()
        test_file = safari_cookies.BinaryCookiesFile(
            debug=True, output_writer=output_writer
        )

        test_file_path = self._GetTestFilePath(["Cookies.binarycookies"])
        self._SkipIfPathNotExists(test_file_path)

        test_file.Open(test_file_path)


if __name__ == "__main__":
    unittest.main()
