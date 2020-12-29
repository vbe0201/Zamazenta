# -*- coding: utf-8 -*-
#
# A small Nintendo Shared Object file wrapper for use by other scripts.
#
# It does not actually verify data so it's only meant to be used with NSOs that
# are known to be valid (such as Pokémon Sword/Shield) instead of general-purpose
# NSO abstraction.
#

from enum import Enum
import struct

import lz4.block

MAGIC = b"NSO0"


class Permission(Enum):
    TEXT_COMPRESS = 1 << 0
    RO_COMPRESS = 1 << 1
    DATA_COMPRESS = 1 << 2
    TEXT_HASH = 1 << 3
    RO_HASH = 1 << 4
    DATA_HASH = 1 << 5


class Flags(int):
    def __contains__(self, item: Permission):
        return (self & item.value) == item.value


class Header(struct.Struct):
    def __init__(self):
        super().__init__("<4sI4xI12xI12xI12xI32sIII28x24x32s32s32s")

        self.magic = MAGIC
        self.version = 0
        self.flags = Flags(0)
        self.text_header = SegmentHeader()
        self.module_name_offset = 0
        self.ro_header = SegmentHeader()
        self.module_name_size = 0
        self.data_header = SegmentHeader()
        self.bss_size = 0
        self.module_id = b"\x00" * 0x20
        self.text_file_size = 0
        self.ro_file_size = 0
        self.data_file_size = 0
        self.api_info_header = SegmentHeaderRelative()
        self.dynstr_header = SegmentHeaderRelative()
        self.dynsym_header = SegmentHeaderRelative()
        self.text_hash = b"\x00" * 0x20
        self.ro_hash = b"\x00" * 0x20
        self.data_hash = b"\x00" * 0x20

    def load(self, data, offset=0):
        (self.magic,
         self.version,
         self.flags,
         self.module_name_offset,
         self.module_name_size,
         self.bss_size,
         self.module_id,
         self.text_file_size,
         self.ro_file_size,
         self.data_file_size,
         self.text_hash,
         self.ro_hash,
         self.data_hash) = self.unpack_from(data, offset)

        self.text_header.load(data, offset + 0x10)
        self.ro_header.load(data, offset + 0x20)
        self.data_header.load(data, offset + 0x30)
        self.api_info_header.load(data, offset + 0x88)
        self.dynstr_header.load(data, offset + 0x90)
        self.dynsym_header.load(data, offset + 0x98)


class SegmentHeader(struct.Struct):
    def __init__(self):
        super().__init__("<III")

        self.file_offset = 0
        self.memory_offset = 0
        self.decompressed_size = 0

    def load(self, data, offset):
        (self.file_offset,
         self.memory_offset,
         self.decompressed_size) = self.unpack_from(data, offset)

    def store(self):
        return self.pack(
            self.file_offset,
            self.memory_offset,
            self.decompressed_size
        )


class SegmentHeaderRelative(struct.Struct):
    def __init__(self):
        super().__init__("<II")

        self.offset = 0
        self.size = 0

    def load(self, data, offset):
        (self.offset, self.offset) = self.unpack_from(data, offset)

    def store(self):
        return self.pack(self.offset, self.size)


class NsoFile:
    def __init__(self, data):
        self.header = Header()
        self.header.load(data[:0x100], 0)

        self.text = NsoSegment(
            data[0x100:],
            self.header.text_header,
            Permission.TEXT_COMPRESS in self.header.flags
        )
        self.rodata = NsoSegment(
            data[0x100:],
            self.header.ro_header,
            Permission.RO_COMPRESS in self.header.flags
        )
        self.data = NsoSegment(
            data[0x100:],
            self.header.data_header,
            Permission.DATA_COMPRESS in self.header.flags
        )

        self.rodata.add_section("api_info", self.header.api_info_header)
        self.rodata.add_section("dynstr", self.header.dynstr_header)
        self.rodata.add_section("dynsym", self.header.dynsym_header)


class NsoSegment:
    def __init__(self, data, header, decompress=False):
        self.memory_address = header.memory_offset
        self.sections = {}
        if decompress:
            self.data = lz4.block.decompress(
                data[header.file_offset - 0x100:],
                header.decompressed_size,
                True
            )
        else:
            start = header.file_offset - 0x100
            self.data = data[start:start + header.decompressed_size]

    def add_section(self, name, header):
        self.sections[name] = self.data[header.offset:header.offset + header.size]
