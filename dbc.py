# Copyright 2015 shiro <shiro@worldofcorecraft.com>
# This file is part of SSI.

# SSI is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# SSI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with SSI.  If not, see <http://www.gnu.org/licenses/>.

import struct

class Mapping:
    def __init__(self, index, type, id, count = 1, post_process = None):
        """
            index: index in DBC
            type:  python type to cast bytes to
            id:    attribute name to map to
            count: make list of these many consecutive items under same id
        """
        self.index = index
        self.type = type
        self.identifier = id
        self.count = count
        self.post_process = post_process

class DbcEntry:
    pass

class Dbc:
    def __init__(self, filename, mappings, index, type=DbcEntry,
        custom_size = False):
        """DBC file is assumed to be little-endian encoded"""
        """Note: most dbcs have all fields as 4 byte, but not all do. If you set
        custom_size to true it indicates you know the size is wonky, and you can
        open and parse one of said DBCs with care"""
        f = open(filename, 'rb')
        self.mappings = mappings
        self.index = index
        self.type = type
        self.custom_size = custom_size
        try:
            self._parse(f)
        finally:
            f.close()

    def _parse(self, f):
        if (f.read(1) != b'W' or f.read(1) != b'D' or f.read(1) != b'B'  or
            f.read(1) != b'C'):
            raise RuntimeError
        rows = struct.unpack('<I', f.read(4))[0]
        cols = struct.unpack('<I', f.read(4))[0]
        row_size = struct.unpack('<I', f.read(4))[0]
        string_size = struct.unpack('<I', f.read(4))[0]

        if not self.custom_size and row_size / 4 != cols:
            raise RuntimeError('row_size: ' + str(row_size) + ' cols: ' +
                str(cols))

        # Read table as binary blob
        bin_blob = [None] * rows
        for i in range(0, rows):
            bin_blob[i] = f.read(row_size)

        # Read string table
        string_table = f.read(string_size)

        # Create table from provided mapping
        self.table = {}
        for i in range(0, rows):
            item = self._map_single(bin_blob[i], string_table)
            self.table[getattr(item, self.index)] = item

    def _map_single(self, raw, string_table):
        entry = self.type()
        for mapping in self.mappings:
            l = []
            for i in range(mapping.count):
                index = i + mapping.index
                if mapping.type == 'str':
                    index = struct.unpack_from('<I', raw, index * 4)[0]
                    bstr = []
                    while True:
                        if string_table[index] == 0:
                            break
                        bstr.append(string_table[index])
                        index += 1
                    # TODO: Are strings actually utf-8 encoded?
                    v = bytes(bstr).decode('utf-8')
                elif mapping.type == 'int':
                    v = struct.unpack_from('<I', raw, index * 4)[0]
                elif mapping.type == 'sint':
                    v = struct.unpack_from('<i', raw, index * 4)[0]
                elif mapping.type == 'long':
                    v = struct.unpack_from('<Q', raw, index * 4)[0]
                elif mapping.type == 'float':
                    v = struct.unpack_from('<f', raw, index * 4)[0]
                else:
                    raise RuntimeError(str(mapping.type) + ' not a valid map type')
                if mapping.post_process != None:
                    v = mapping.post_process(v, entry)
                l.append(v)
            if len(l) <= 1:
                setattr(entry, mapping.identifier, l[0])
            else:
                setattr(entry, mapping.identifier, l)
        return entry
