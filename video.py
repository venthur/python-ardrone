
import sys
import struct
import psyco
psyco.full()

# from zig-zag back to normal
ZIG_ZAG_POSITIONS = [ 0,  1,  8, 16,  9,  2, 3, 10,
                     17, 24, 32, 25, 18, 11, 4,  5,
                     12, 19, 26, 33, 40, 48, 41, 34,
                     27, 20, 13,  6,  7, 14, 21, 28,
                     35, 42, 49, 56, 57, 50, 43, 36,
                     29, 22, 15, 23, 30, 37, 44, 51,
                     58, 59, 52, 45, 38, 31, 39, 46,
                     53, 60, 61, 54, 47, 55, 62, 63]

# int16_t
iquant_tab = [ 3,  5,  7,  9, 11, 13, 15, 17,
               5,  7,  9, 11, 13, 15, 17, 19,
               7,  9, 11, 13, 15, 17, 19, 21,
               9, 11, 13, 15, 17, 19, 21, 23,
              11, 13, 15, 17, 19, 21, 23, 25,
              13, 15, 17, 19, 21, 23, 25, 27,
              15, 17, 19, 21, 23, 25, 27, 29,
              17, 19, 21, 23, 25, 27, 29, 31]

# Used for upscaling the 8x8 b- and r-blocks to 16x16
scalemap = [ 0,  0,  1,  1,  2,  2,  3,  3,
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
            60, 60, 61, 61, 62, 62, 63, 63]

clzlut = [8, 7, 6, 6, 5, 5, 5, 5, 4, 4, 4, 4, 4,
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
          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

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
        self.fc = '<I'
        self.size = struct.calcsize(self.fc)
        self.size_bits = self.size * 8
        self.read_bits = 0

    def peek(self, nbits):
        # Read enough bits into chunk so we have at least nbits available
        return self.read(nbits, False)

    def read(self, nbits, consume=True):
        # Read enough bits into chunk so we have at least nbits available
        while nbits > self.bits_left:
            self.chunk <<= self.size_bits
            self.chunk |= struct.unpack_from(self.fc,
                                             self.packet,
                                             self.offset*self.size)[0]
            self.offset += 1
            self.bits_left += self.size_bits
        # Get the first nbits bits from chunk (and remove them from chunk)
        shift = self.bits_left - nbits
        res = self.chunk >> shift
        if consume:
            mask = (2**nbits-1) << shift
            self.chunk = self.chunk & ~mask
            self.bits_left -= nbits
            self.read_bits += nbits
        return res

    def align(self):
        shift = (8 - self.read_bits) % 8
        #print "shifting: ", shift
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
    print "width/height:", width, height
    ptype = bitreader.read(3)
    pquant = bitreader.read(5)
    pframe = bitreader.read(32)
    return width, height



def inverse_dct(block):

    workspace = [0 for i in range(64)]
    data = [0 for i in range(64)]
    for pointer in range(8):
        if (block[pointer + 8] == 0 and block[pointer + 16] == 0 and
            block[pointer + 24] == 0 and block[pointer + 32] == 0 and
            block[pointer + 40] == 0 and block[pointer + 48] == 0 and
            block[pointer + 56] == 0):
            dcval = block[pointer] << PASS1_BITS
            for i in range(8):
                workspace[pointer + 8*i] = dcval
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


    for pointer in range(0, 8*8, 8):
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


def decode_block(block):
    # de-zic-zag
    tmp = [0 for i in range(64)]
    for i in range(len(block)):
        tmp[ZIG_ZAG_POSITIONS[i]] = block[i]
    # de-quant
    for i in range(64):
        tmp[i] *= iquant_tab[i]
    tmp = inverse_dct(tmp)
    return tmp



def scale_block(b):
    """Scale an 8x8 block up to 4 8x8 blocks."""
    br = [0 for i in range(4*8*8)]
    for i in range(4*8*8):
        br[i] = b[scalemap[i]]
    return br

def get_mb(bitreader):
    mbc = bitreader.read(1)
    block = [0 for i in range(8*8*4)]
    if mbc == 0:
        mbdesc = bitreader.read(8)
        assert(mbdesc & 0b10000000)
        if mbdesc & 0b01000000:
            mbdiff = bitreader.read(2)
        y = []
        y.extend(decode_block(get_block(bitreader, (mbdesc >> 0) & 1)))
        y.extend(decode_block(get_block(bitreader, (mbdesc >> 1) & 1)))
        y.extend(decode_block(get_block(bitreader, (mbdesc >> 2) & 1)))
        y.extend(decode_block(get_block(bitreader, (mbdesc >> 3) & 1)))
        cb = decode_block(get_block(bitreader, (mbdesc >> 4) & 1))
        cr = decode_block(get_block(bitreader, (mbdesc >> 5) & 1))
        # upscale cb and cr to make calculations below more efficient
        cb = scale_block(cb)
        cr = scale_block(cr)
        # ycbcr to rgb
        for i in range(8*8*4):
            Y = y[i] - 16
            B = cb[i] - 128
            R = cr[i] - 128
            r = (298 * Y           + 409 * R + 128) >> 8
            g = (298 * Y - 100 * B - 208 * R + 128) >> 8
            b = (298 * Y + 516 * B           + 128) >> 8
            r = 0 if r < 0 else r
            r = 255 if r > 255 else r
            g = 0 if g < 0 else g
            g = 255 if g > 0 else g
            b = 0 if b < 0 else b
            b = 255 if b > 255 else b
            block[i] = [r, g, b]
    return block


def get_block(bitreader, has_coeff):
    # read the first 10 bits in a 16 bit datum
    out_list = []
    out_list.append(int(bitreader.read(10)))
    if not has_coeff:
        return out_list
    while 1:
        streamlen = 0
        data = bitreader.peek(32)
        # count the zeros
        #zerocount = cout_leading_zeros(data)
        zerocount = clzlut[data >> 24];
        if zerocount == 8:
            zerocount += clzlut[(data >> 16) & 0xFF];
        if zerocount == 16:
            zerocount += clzlut[(data >> 8) & 0xFF];
        if zerocount == 24:
            zerocount += clzlut[data & 0xFF];
        data = (data << (zerocount + 1)) & 0xffffffff
        streamlen += zerocount + 1
        assert(zerocount <= 6)
        # get number of remaining bits to read
        toread = 0 if zerocount <= 1 else zerocount - 1
        additional = data >> (32 - toread)
        data = (data << toread) & 0xffffffff
        streamlen += toread
        # add as many zeros to out_list as indicated by additional bits
        # if zerocount is 0, tmp = 0 else the 1 merged with additional bits
        tmp = 0 if zerocount == 0 else (1 << toread) | additional
        for i in range(tmp):
            out_list.append(0)

        # count the zeros
        #zerocount = cout_leading_zeros(data)
        zerocount = clzlut[data >> 24];
        if zerocount == 8:
            zerocount += clzlut[(data >> 16) & 0xFF];
        if zerocount == 16:
            zerocount += clzlut[(data >> 8) & 0xFF];
        if zerocount == 24:
            zerocount += clzlut[data & 0xFF];
        data = (data << (zerocount + 1)) & 0xffffffff
        streamlen += zerocount + 1
        assert(zerocount <= 7)
        # 01 == EOB
        if zerocount == 1:
            bitreader.read(streamlen)
            break
        # get number of remaining bits to read
        toread = 0 if zerocount == 0 else zerocount - 1
        additional = data >> (32 - toread)
        data = (data << toread) & 0xffffffff
        streamlen += toread
        tmp = (1 << toread) | additional
        # get one more bit for the sign
        tmp = -tmp if data >> (32 - 1) else tmp
        streamlen += 1
        out_list.append(tmp)
        bitreader.read(streamlen)
    assert(len(out_list) <= 64)
    out_list = map(int, out_list)
    return out_list

def get_gob(bitreader, blocks):
    block = []
    bitreader.align()
    gobsc = bitreader.read(22)
    if gobsc == 0b0000000000000000111111:
        print "weeeee"
        return False
    elif (not (gobsc & 0b0000000000000000100000) or
         (gobsc & 0b1111111111111111000000)):
        print "Got wrong GOBSC, aborting.", bin(gobsc)
        return False
    #print 'GOBSC:', gobsc & 0b11111
    _ = bitreader.read(5)
    for i in range(blocks):
        #print "b%i" % i
        block.extend(get_mb(bitreader))
    return block

def read_picture(bitreader):
    import datetime
    t = datetime.datetime.now()
    block = []
    width, height = get_pheader(bitreader)
    slices = height / 16
    blocks = width / 16
    # this is already the first slice
    for i in range(blocks):
        block.extend(get_mb(bitreader))
    # those are the remaining ones
    for i in range(1, slices):
        #print "Getting Slice", i, slices
        block.extend(get_gob(bitreader, blocks))
    bitreader.align()
    eos = bitreader.read(22)
    assert(eos == 0b0000000000000000111111)
    print "\nEND OF PICTURE\n"
    print slices, blocks
    print len(block)
    print 'time', datetime.datetime.now() - t
    # print the image
    #from PIL import Image
    #im = Image.new("RGBA", (blocks*16, slices*16))
    #i = 0
    #for sl in range(slices):
    #    for bl in range(blocks):
    #        for j in range(4):
    #            for y in range(8):
    #                for x in range(8):
    #                    r, g, b = block[i]
    #                    if j == 0:
    #                        im.putpixel((bl*16+x, sl*16+y), (r, g, b))
    #                    if j == 1:
    #                       im.putpixel((bl*16+x+8, sl*16+y), (r, g, b))
    #                    if j == 2:
    #                       im.putpixel((bl*16+x, sl*16+y+8), (r, g, b))
    #                    if j == 3:
    #                       im.putpixel((bl*16+x+8, sl*16+y+8), (r, g, b))
    #                    i += 1
    #im.show()


def _pp(name, value):
    #return
    print "%s\t\t%s\t%s" % (name, str(bin(value)), str(value))


def main():
    fh = open('videoframe.raw', 'r')
    #fh = open('video.raw', 'r')
    data = fh.read()
    fh.close()
    br = BitReader(data)
    read_picture(br)

if __name__ == '__main__':
    if 'profile' in sys.argv:
        import cProfile
        cProfile.run('main()')
    else:
        main()

