#!/usr/bin/env python

# Copyright (c) 2011 Bastian Venthur
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import array
import cProfile
import datetime
import struct
import sys
import psyco
#psyco.full()


# from zig-zag back to normal
ZIG_ZAG_POSITIONS = array.array('B', ( 0,  1,  8, 16,  9,  2, 3, 10,
                     17, 24, 32, 25, 18, 11, 4,  5,
                     12, 19, 26, 33, 40, 48, 41, 34,
                     27, 20, 13,  6,  7, 14, 21, 28,
                     35, 42, 49, 56, 57, 50, 43, 36,
                     29, 22, 15, 23, 30, 37, 44, 51,
                     58, 59, 52, 45, 38, 31, 39, 46,
                     53, 60, 61, 54, 47, 55, 62, 63))

# int16_t
IQUANT_TAB = array.array('B', ( 3,  5,  7,  9, 11, 13, 15, 17,
               5,  7,  9, 11, 13, 15, 17, 19,
               7,  9, 11, 13, 15, 17, 19, 21,
               9, 11, 13, 15, 17, 19, 21, 23,
              11, 13, 15, 17, 19, 21, 23, 25,
              13, 15, 17, 19, 21, 23, 25, 27,
              15, 17, 19, 21, 23, 25, 27, 29,
              17, 19, 21, 23, 25, 27, 29, 31))

# Used for upscaling the 8x8 b- and r-blocks to 16x16
SCALE_TAB = array.array('B', ( 0,  0,  1,  1,  2,  2,  3,  3,
             0,  0,  1,  1,  2,  2,  3,  3,
             8,  8,  9,  9, 10, 10, 11, 11,
             8,  8,  9,  9, 10, 10, 11, 11,
            16, 16, 17, 17, 18, 18, 19, 19,
            16, 16, 17, 17, 18, 18, 19, 19,
            24, 24, 25, 25, 26, 26, 27, 27,
            24, 24, 25, 25, 26, 26, 27, 27,

             4,  4,  5,  5,  6,  6,  7,  7,
             4,  4,  5,  5,  6,  6,  7,  7,
            12, 12, 13, 13, 14, 14, 15, 15,
            12, 12, 13, 13, 14, 14, 15, 15,
            20, 20, 21, 21, 22, 22, 23, 23,
            20, 20, 21, 21, 22, 22, 23, 23,
            28, 28, 29, 29, 30, 30, 31, 31,
            28, 28, 29, 29, 30, 30, 31, 31,

            32, 32, 33, 33, 34, 34, 35, 35,
            32, 32, 33, 33, 34, 34, 35, 35,
            40, 40, 41, 41, 42, 42, 43, 43,
            40, 40, 41, 41, 42, 42, 43, 43,
            48, 48, 49, 49, 50, 50, 51, 51,
            48, 48, 49, 49, 50, 50, 51, 51,
            56, 56, 57, 57, 58, 58, 59, 59,
            56, 56, 57, 57, 58, 58, 59, 59,

            36, 36, 37, 37, 38, 38, 39, 39,
            36, 36, 37, 37, 38, 38, 39, 39,
            44, 44, 45, 45, 46, 46, 47, 47,
            44, 44, 45, 45, 46, 46, 47, 47,
            52, 52, 53, 53, 54, 54, 55, 55,
            52, 52, 53, 53, 54, 54, 55, 55,
            60, 60, 61, 61, 62, 62, 63, 63,
            60, 60, 61, 61, 62, 62, 63, 63))

CLZLUT = array.array('B', (8, 7, 6, 6, 5, 5, 5, 5, 4, 4, 4, 4, 4,
          4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2,
          2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
          2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
          1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
          1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
          1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))

# Map from pixels from four 8x8 blocks to one 16x16
MB_TO_GOB_MAP = array.array('B', [0, 1, 2, 3, 4, 5, 6, 7, 16, 17, 18, 19, 20, 21, 22, 23, 32,
        33, 34, 35, 36, 37, 38, 39, 48, 49, 50, 51, 52, 53, 54, 55, 64, 65, 66,
        67, 68, 69, 70, 71, 80, 81, 82, 83, 84, 85, 86, 87, 96, 97, 98, 99,
        100, 101, 102, 103, 112, 113, 114, 115, 116, 117, 118, 119, 8, 9, 10,
        11, 12, 13, 14, 15, 24, 25, 26, 27, 28, 29, 30, 31, 40, 41, 42, 43, 44,
        45, 46, 47, 56, 57, 58, 59, 60, 61, 62, 63, 72, 73, 74, 75, 76, 77, 78,
        79, 88, 89, 90, 91, 92, 93, 94, 95, 104, 105, 106, 107, 108, 109, 110,
        111, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132,
        133, 134, 135, 144, 145, 146, 147, 148, 149, 150, 151, 160, 161, 162,
        163, 164, 165, 166, 167, 176, 177, 178, 179, 180, 181, 182, 183, 192,
        193, 194, 195, 196, 197, 198, 199, 208, 209, 210, 211, 212, 213, 214,
        215, 224, 225, 226, 227, 228, 229, 230, 231, 240, 241, 242, 243, 244,
        245, 246, 247, 136, 137, 138, 139, 140, 141, 142, 143, 152, 153, 154,
        155, 156, 157, 158, 159, 168, 169, 170, 171, 172, 173, 174, 175, 184,
        185, 186, 187, 188, 189, 190, 191, 200, 201, 202, 203, 204, 205, 206,
        207, 216, 217, 218, 219, 220, 221, 222, 223, 232, 233, 234, 235, 236,
        237, 238, 239, 248, 249, 250, 251, 252, 253, 254, 255])

MB_ROW_MAP = array.array('B', [i / 16 for i in MB_TO_GOB_MAP])
MB_COL_MAP = array.array('B', [i % 16 for i in MB_TO_GOB_MAP])

MB_ROW_COL_MAP = [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [0, 7],
        [1, 0], [1, 1], [1, 2], [1, 3], [1, 4], [1, 5], [1, 6], [1, 7], [2, 0],
        [2, 1], [2, 2], [2, 3], [2, 4], [2, 5], [2, 6], [2, 7], [3, 0], [3, 1],
        [3, 2], [3, 3], [3, 4], [3, 5], [3, 6], [3, 7], [4, 0], [4, 1], [4, 2],
        [4, 3], [4, 4], [4, 5], [4, 6], [4, 7], [5, 0], [5, 1], [5, 2], [5, 3],
        [5, 4], [5, 5], [5, 6], [5, 7], [6, 0], [6, 1], [6, 2], [6, 3], [6, 4],
        [6, 5], [6, 6], [6, 7], [7, 0], [7, 1], [7, 2], [7, 3], [7, 4], [7, 5],
        [7, 6], [7, 7], [0, 8], [0, 9], [0, 10], [0, 11], [0, 12], [0, 13], [0, 14], 
        [0, 15], [1, 8], [1, 9], [1, 10], [1, 11], [1, 12], [1, 13],
        [1, 14], [1, 15], [2, 8], [2, 9], [2, 10], [2, 11], [2, 12], [2, 13],
        [2, 14], [2, 15], [3, 8], [3, 9], [3, 10], [3, 11], [3, 12], [3, 13],
        [3, 14], [3, 15], [4, 8], [4, 9], [4, 10], [4, 11], [4, 12], [4, 13],
        [4, 14], [4, 15], [5, 8], [5, 9], [5, 10], [5, 11], [5, 12], [5, 13],
        [5, 14], [5, 15], [6, 8], [6, 9], [6, 10], [6, 11], [6, 12], [6, 13],
        [6, 14], [6, 15], [7, 8], [7, 9], [7, 10], [7, 11], [7, 12], [7, 13],
        [7, 14], [7, 15], [8, 0], [8, 1], [8, 2], [8, 3], [8, 4], [8, 5], [8, 6],
        [8, 7], [9, 0], [9, 1], [9, 2], [9, 3], [9, 4], [9, 5], [9, 6],
        [9, 7], [10, 0], [10, 1], [10, 2], [10, 3], [10, 4], [10, 5], [10, 6],
        [10, 7], [11, 0], [11, 1], [11, 2], [11, 3], [11, 4], [11, 5], [11, 6],
        [11, 7], [12, 0], [12, 1], [12, 2], [12, 3], [12, 4], [12, 5], [12, 6],
        [12, 7], [13, 0], [13, 1], [13, 2], [13, 3], [13, 4], [13, 5], [13, 6],
        [13, 7], [14, 0], [14, 1], [14, 2], [14, 3], [14, 4], [14, 5], [14, 6],
        [14, 7], [15, 0], [15, 1], [15, 2], [15, 3], [15, 4], [15, 5], [15, 6],
        [15, 7], [8, 8], [8, 9], [8, 10], [8, 11], [8, 12], [8, 13], [8, 14],
        [8, 15], [9, 8], [9, 9], [9, 10], [9, 11], [9, 12], [9, 13], [9, 14],
        [9, 15], [10, 8], [10, 9], [10, 10], [10, 11], [10, 12], [10, 13], [10, 14],
        [10, 15], [11, 8], [11, 9], [11, 10], [11, 11], [11, 12], [11, 13], 
        [11, 14], [11, 15], [12, 8], [12, 9], [12, 10], [12, 11], [12, 12],
        [12, 13], [12, 14], [12, 15], [13, 8], [13, 9], [13, 10], [13, 11],
        [13, 12], [13, 13], [13, 14], [13, 15], [14, 8], [14, 9], [14, 10],
        [14, 11], [14, 12], [14, 13], [14, 14], [14, 15], [15, 8], [15, 9],
        [15, 10], [15, 11], [15, 12], [15, 13], [15, 14], [15, 15]]


ZEROS = array.array('i', [0 for i in range(256)])

FIX_0_298631336 = 2446
FIX_0_390180644 = 3196
FIX_0_541196100 = 4433
FIX_0_765366865 = 6270
FIX_0_899976223 = 7373
FIX_1_175875602 = 9633
FIX_1_501321110 = 12299
FIX_1_847759065 = 15137
FIX_1_961570560 = 16069
FIX_2_053119869 = 16819
FIX_2_562915447 = 20995
FIX_3_072711026 = 25172

CONST_BITS = 13
PASS1_BITS = 1
F1 = CONST_BITS - PASS1_BITS - 1
F2 = CONST_BITS - PASS1_BITS
F3 = CONST_BITS + PASS1_BITS + 3


class BitReader(object):

    def __init__(self, packet):
        self.packet = packet
        self.offset = 0
        self.bits_left = 0
        self.chunk = 0
        self.read_bits = 0

    def read(self, nbits, consume=True):
        # Read enough bits into chunk so we have at least nbits available
        while nbits > self.bits_left:
            try:
                self.chunk = (self.chunk << 32) | struct.unpack_from('<I', self.packet, self.offset)[0]
            except:
                self.chunk <<= 32
            self.offset += 4
            self.bits_left += 32
        # Get the first nbits bits from chunk (and remove them from chunk)
        shift = self.bits_left - nbits
        res = self.chunk >> shift
        if consume:
            self.chunk -= res << shift
            self.bits_left -= nbits
            self.read_bits += nbits
        return res

    def align(self):
        shift = (8 - self.read_bits) % 8
        self.read(shift)


def get_pheader(bitreader):
    bitreader.align()
    psc = bitreader.read(22)
    assert(psc == 0b0000000000000000100000)
    pformat = bitreader.read(2)
    assert(pformat != 0b00)
    if pformat == 1:
        # CIF
        width, height = 88, 72
    else:
        # VGA
        width, height = 160, 120
    presolution = bitreader.read(3)
    assert(presolution != 0b000)
    # double resolution presolution-1 times
    width = width << presolution - 1
    height = height << presolution - 1
    #print "width/height:", width, height
    ptype = bitreader.read(3)
    pquant = bitreader.read(5)
    pframe = bitreader.read(32)
    return width, height


def inverse_dct(block):
    workspace = ZEROS[0:64]
    data = ZEROS[0:64]

    for pointer in range(8):

        if (block[pointer + 8] == 0 and block[pointer + 16] == 0 and
            block[pointer + 24] == 0 and block[pointer + 32] == 0 and
            block[pointer + 40] == 0 and block[pointer + 48] == 0 and
            block[pointer + 56] == 0):
            dcval = block[pointer] << PASS1_BITS
            for i in range(8):
                workspace[pointer + i*8] = dcval
            continue

        z2 = block[pointer + 16]
        z3 = block[pointer + 48]

        z1 = (z2 + z3) * FIX_0_541196100
        tmp2 = z1 + z3 * -FIX_1_847759065
        tmp3 = z1 + z2 * FIX_0_765366865

        z2 = block[pointer]
        z3 = block[pointer + 32]

        tmp0 = (z2 + z3) << CONST_BITS
        tmp1 = (z2 - z3) << CONST_BITS

        tmp10 = tmp0 + tmp3
        tmp13 = tmp0 - tmp3
        tmp11 = tmp1 + tmp2
        tmp12 = tmp1 - tmp2

        tmp0 = block[pointer + 56]
        tmp1 = block[pointer + 40]
        tmp2 = block[pointer + 24]
        tmp3 = block[pointer + 8]

        z1 = tmp0 + tmp3
        z2 = tmp1 + tmp2
        z3 = tmp0 + tmp2
        z4 = tmp1 + tmp3
        z5 = (z3 + z4) * FIX_1_175875602

        tmp0 *= FIX_0_298631336
        tmp1 *= FIX_2_053119869
        tmp2 *= FIX_3_072711026
        tmp3 *= FIX_1_501321110
        z1 *= -FIX_0_899976223
        z2 *= -FIX_2_562915447
        z3 *= -FIX_1_961570560
        z4 *= -FIX_0_390180644

        z3 += z5
        z4 += z5

        tmp0 += z1 + z3
        tmp1 += z2 + z4
        tmp2 += z2 + z3
        tmp3 += z1 + z4

        workspace[pointer + 0] = ((tmp10 + tmp3 + (1 << F1)) >> F2)
        workspace[pointer + 56] = ((tmp10 - tmp3 + (1 << F1)) >> F2)
        workspace[pointer + 8] = ((tmp11 + tmp2 + (1 << F1)) >> F2)
        workspace[pointer + 48] = ((tmp11 - tmp2 + (1 << F1)) >> F2)
        workspace[pointer + 16] = ((tmp12 + tmp1 + (1 << F1)) >> F2)
        workspace[pointer + 40] = ((tmp12 - tmp1 + (1 << F1)) >> F2)
        workspace[pointer + 24] = ((tmp13 + tmp0 + (1 << F1)) >> F2)
        workspace[pointer + 32] = ((tmp13 - tmp0 + (1 << F1)) >> F2)

    for pointer in range(0, 64, 8):

        z2 = workspace[pointer + 2]
        z3 = workspace[pointer + 6]

        z1 = (z2 + z3) * FIX_0_541196100
        tmp2 = z1 + z3 * -FIX_1_847759065
        tmp3 = z1 + z2 * FIX_0_765366865

        tmp0 = (workspace[pointer] + workspace[pointer + 4]) << CONST_BITS
        tmp1 = (workspace[pointer] - workspace[pointer + 4]) << CONST_BITS

        tmp10 = tmp0 + tmp3
        tmp13 = tmp0 - tmp3
        tmp11 = tmp1 + tmp2
        tmp12 = tmp1 - tmp2

        tmp0 = workspace[pointer + 7]
        tmp1 = workspace[pointer + 5]
        tmp2 = workspace[pointer + 3]
        tmp3 = workspace[pointer + 1]

        z1 = tmp0 + tmp3
        z2 = tmp1 + tmp2
        z3 = tmp0 + tmp2
        z4 = tmp1 + tmp3

        z5 = (z3 + z4) * FIX_1_175875602

        tmp0 *= FIX_0_298631336
        tmp1 *= FIX_2_053119869
        tmp2 *= FIX_3_072711026
        tmp3 *= FIX_1_501321110
        z1 *= -FIX_0_899976223
        z2 *= -FIX_2_562915447
        z3 *= -FIX_1_961570560
        z4 *= -FIX_0_390180644

        z3 += z5
        z4 += z5

        tmp0 += z1 + z3
        tmp1 += z2 + z4
        tmp2 += z2 + z3
        tmp3 += z1 + z4

        data[pointer + 0] = (tmp10 + tmp3) >> F3
        data[pointer + 7] = (tmp10 - tmp3) >> F3
        data[pointer + 1] = (tmp11 + tmp2) >> F3
        data[pointer + 6] = (tmp11 - tmp2) >> F3
        data[pointer + 2] = (tmp12 + tmp1) >> F3
        data[pointer + 5] = (tmp12 - tmp1) >> F3
        data[pointer + 3] = (tmp13 + tmp0) >> F3
        data[pointer + 4] = (tmp13 - tmp0) >> F3

    return data


def get_mb(bitreader, picture, width, offset):
    mbc = bitreader.read(1)

    if mbc == 0:
        mbdesc = bitreader.read(8)
        assert(mbdesc >> 7 & 1)
        if mbdesc >> 6 & 1:
            mbdiff = bitreader.read(2)

        y = get_block(bitreader, mbdesc & 1)
        y.extend(get_block(bitreader, mbdesc >> 1 & 1))
        y.extend(get_block(bitreader, mbdesc >> 2 & 1))
        y.extend(get_block(bitreader, mbdesc >> 3 & 1))

        cb = get_block(bitreader, mbdesc >> 4 & 1)
        cr = get_block(bitreader, mbdesc >> 5 & 1)

        # ycbcr to rgb
        for i in range(256):
            j = SCALE_TAB[i]
            Y = y[i] - 16
            B = cb[j] - 128
            R = cr[j] - 128
            r = (298 * Y           + 409 * R + 128) >> 8
            g = (298 * Y - 100 * B - 208 * R + 128) >> 8
            b = (298 * Y + 516 * B           + 128) >> 8
            r = 0 if r < 0 else r
            r = 255 if r > 255 else r
            g = 0 if g < 0 else g
            g = 255 if g > 255 else g
            b = 0 if b < 0 else b
            b = 255 if b > 255 else b
            # re-order the pixels
            row = MB_ROW_MAP[i]
            col = MB_COL_MAP[i]
            picture[offset + row*width + col] = ''.join((chr(r), chr(g), chr(b)))
    else:
        print "mbc was not zero"


def _first_half(data):
    # data has to be 12 bits wide
    streamlen = 0
    # count the zeros
    zerocount = CLZLUT[data >> 4];
    data = (data << (zerocount + 1)) & 0b111111111111
    streamlen += zerocount + 1
    # get number of remaining bits to read
    toread = 0 if zerocount <= 1 else zerocount - 1
    additional = data >> (12 - toread)
    data = (data << toread) & 0b111111111111
    streamlen += toread
    # add as many zeros to out_list as indicated by additional bits
    # if zerocount is 0, tmp = 0 else the 1 merged with additional bits
    tmp = 0 if zerocount == 0 else (1 << toread) | additional
    return [streamlen, tmp]


def _second_half(data):
    # data has to be 15 bits wide
    streamlen = 0
    zerocount = CLZLUT[data >> 7];
    data = (data << (zerocount + 1)) & 0b111111111111111
    streamlen += zerocount + 1
    # 01 == EOB
    eob = False
    if zerocount == 1:
        eob = True
        return [streamlen, None, eob]
    # get number of remaining bits to read
    toread = 0 if zerocount == 0 else zerocount - 1
    additional = data >> (15 - toread)
    data = (data << toread) & 0b111111111111111
    streamlen += toread
    tmp = (1 << toread) | additional
    # get one more bit for the sign
    tmp = -tmp if data >> (15 - 1) else tmp
    tmp = int(tmp)
    streamlen += 1
    return [streamlen, tmp, eob]

FH = [_first_half(i) for i in range(2**12)]
SH = [_second_half(i) for i in range(2**15)]

TRIES = 16
MASK = 2**(TRIES*32)-1
SHIFT = 32*(TRIES-1)

def get_block(bitreader, has_coeff):
    # read the first 10 bits in a 16 bit datum
    out_list = ZEROS[0:64]
    out_list[0] = int(bitreader.read(10)) * IQUANT_TAB[0]
    if not has_coeff:
        return inverse_dct(out_list)
    i = 1
    while 1:
        _ = bitreader.read(32*TRIES, False)
        streamlen = 0
        #######################################################################
        for j in range(TRIES):
            data = (_ << streamlen) & MASK
            data >>= SHIFT

            l, tmp = FH[data >> 20]
            streamlen += l
            data = (data << l) & 0xffffffff
            i += tmp

            l, tmp, eob = SH[data >> 17]
            streamlen += l
            if eob:
                bitreader.read(streamlen)
                return inverse_dct(out_list)
            j = ZIG_ZAG_POSITIONS[i]
            out_list[j] = tmp*IQUANT_TAB[j]
            i += 1
        #######################################################################
        bitreader.read(streamlen)
    return inverse_dct(out_list)



def get_gob(bitreader, picture, slicenr, width):
    # the first gob has a special header
    if slicenr > 0:
        bitreader.align()
        gobsc = bitreader.read(22)
        if gobsc == 0b0000000000000000111111:
            print "weeeee"
            return False
        elif (not (gobsc & 0b0000000000000000100000) or
             (gobsc & 0b1111111111111111000000)):
            print "Got wrong GOBSC, aborting.", bin(gobsc)
            return False
        _ = bitreader.read(5)
    offset = slicenr*16*width
    for i in range(width / 16):
        get_mb(bitreader, picture, width, offset+16*i)


def read_picture(bitreader):
    t = datetime.datetime.now()
    width, height = get_pheader(bitreader)
    slices = height / 16
    blocks = width / 16
    image = [0 for i in range(width*height)]
    for i in range(0, slices):
        get_gob(bitreader, image, i, width)
    bitreader.align()
    eos = bitreader.read(22)
    assert(eos == 0b0000000000000000111111)
    t2 = datetime.datetime.now()
    return width, height, ''.join(image), (t2 - t).microseconds / 1000000.

psyco.bind(BitReader)
psyco.bind(get_block)
psyco.bind(get_gob)
psyco.bind(get_mb)
psyco.bind(inverse_dct)
psyco.bind(read_picture)

#import pygame
#pygame.init()
#W, H = 320, 240
#screen = pygame.display.set_mode((W, H))
#surface = pygame.Surface((W, H))
#
#
#def show_image(image, width, height):
#    surface = pygame.image.fromstring(image, (width, height), 'RGB')
#    screen.blit(surface, (0, 0))
#    pygame.display.flip()
#

def main():
    fh = open('framewireshark.raw', 'r')
    #fh = open('videoframe.raw', 'r')
    data = fh.read()
    fh.close()
    runs = 20
    t = 0
    for i in range(runs):
        print '.',
        br = BitReader(data)
        width, height, image, ti = read_picture(br)
        show_image(image, width, height)
        t += ti
    print
    print 'avg time:\t', t / runs, 'sec'
    print 'avg fps:\t', 1 / (t / runs), 'fps'

if __name__ == '__main__':
    if 'profile' in sys.argv:
        cProfile.run('main()')
    else:
        main()

