

import struct
#import psyco
#psyco.full()

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
        self.read_bits = 0

    def peek(self, nbits):
        # Read enough bits into chunk so we have at least nbits available
        while nbits > self.bits_left:
            self.chunk = self.chunk << (self.size * 8)
            self.chunk |= struct.unpack_from(self.fc,
                                             self.packet,
                                             self.offset*self.size)[0]
            self.offset += 1
            self.bits_left += self.size * 8
        mask = 2**nbits-1
        mask = mask << (self.bits_left - nbits)
        res = self.chunk & mask
        res = res >> (self.bits_left - nbits)
        return res

    def read(self, nbits):
        # Read enough bits into chunk so we have at least nbits available
        while nbits > self.bits_left:
            self.chunk = self.chunk << (self.size * 8)
            self.chunk |= struct.unpack_from(self.fc,
                                             self.packet,
                                             self.offset*self.size)[0]
            self.offset += 1
            self.bits_left += self.size * 8
        # Get the first nbits bits from chunk (and remove them from chunk)
        mask = 2**nbits-1
        mask = mask << (self.bits_left - nbits)
        res = self.chunk & mask
        res = res >> (self.bits_left - nbits)
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

def get_mb(bitreader):
    mbc = bitreader.read(1)
    mbdesc = 0
    block = []
    if mbc == 0:
        mbdesc = bitreader.read(8)
        assert(mbdesc & 0b10000000)
        if mbdesc & 0b01000000:
            mbdiff = bitreader.read(2)
        y = [None, None, None, None]
        y[0] = decode_block(get_block(bitreader, (mbdesc >> 0) & 1))
        y[1] = decode_block(get_block(bitreader, (mbdesc >> 1) & 1))
        y[2] = decode_block(get_block(bitreader, (mbdesc >> 2) & 1))
        y[3] = decode_block(get_block(bitreader, (mbdesc >> 3) & 1))
        cb = decode_block(get_block(bitreader, (mbdesc >> 4) & 1))
        cr = decode_block(get_block(bitreader, (mbdesc >> 5) & 1))

        # ycbcr to rgb
        for j in range(4):
            if j == 0:
                offset = 0
            elif j == 1:
                offset = 4
            elif j == 2:
                offset = 32
            else:
                offset = 36
            i = 0
            for row in range(8):
                for col in range(8):
                    Y = y[j][i] - 16
                    B = cb[8*(row/2) + col/2 + offset] - 128
                    R = cr[8*(row/2) + col/2 + offset] - 128
                    r = (298 * Y           + 409 * R + 128) >> 8
                    g = (298 * Y - 100 * B - 208 * R + 128) >> 8
                    b = (298 * Y + 516 * B           + 128) >> 8
                    for v in r, g, b:
                        if v < 0:
                            v = 0
                        elif v > 255:
                            v = 255
                    block.append([r, g, b])
                    i += 1

    return block

def get_block(bitreader, has_coeff):
    # read the first 10 bits in a 16 bit datum
    out_list = []
    out_list.append(int(bitreader.read(10)))
    if not has_coeff:
        return out_list
    while 1:
        # count the zeros
        zerocount = 0
        while bitreader.read(1) == 0:
            zerocount += 1
        assert(zerocount <= 6)
        # get number of remaining bits to read
        toread = 0 if zerocount <= 1 else zerocount - 1
        additional = bitreader.read(toread)
        # add as many zeros to out_list as indicated by additional bits
        # if zerocount is 0, tmp = 0 else the 1 merged with additional bits
        tmp = 0 if zerocount == 0 else (1 << toread) + additional
        for i in range(tmp):
            out_list.append(0)

        # count the zeros
        zerocount = 0
        while bitreader.read(1) == 0:
            zerocount += 1
        assert(zerocount <= 7)
        # 01 == EOB
        if zerocount == 1:
            break
        # get number of remaining bits to read
        toread = 0 if zerocount == 0 else zerocount - 1
        additional = bitreader.read(toread)
        tmp = (1 << toread) + additional
        # get one more bit for the sign
        tmp = -tmp if bitreader.read(1) else tmp
        out_list.append(tmp)
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
        #print "b%i" % i,
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
    data = fh.read()
    fh.close()
    br = BitReader(data)
    read_picture(br)


if __name__ == '__main__':
    import cProfile
    #stats = cProfile.run('main()')
    main()
