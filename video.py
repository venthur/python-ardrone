

import struct


class BitReader(object):

    def __init__(self, packet):
        self.packet = packet
        self.offset = 0
        self.bits_left = 0
        self.chunk = 0
        self.fc = '<I'
        self.read_bits = 0

    def peek(self, nbits):
        # Read enough bits into chunk so we have at least nbits available
        while nbits > self.bits_left:
            self.chunk = self.chunk << (struct.calcsize(self.fc) * 8)
            self.chunk |= struct.unpack_from(self.fc,
                                             self.packet,
                                             self.offset*struct.calcsize(self.fc))[0]
            self.offset += 1
            self.bits_left += struct.calcsize(self.fc) * 8
        mask = 2**nbits-1
        mask = mask << (self.bits_left - nbits)
        res = self.chunk & mask
        res = res >> (self.bits_left - nbits)
        return res

    def read(self, nbits):
        # Read enough bits into chunk so we have at least nbits available
        while nbits > self.bits_left:
            self.chunk = self.chunk << (struct.calcsize(self.fc) * 8)
            self.chunk |= struct.unpack_from(self.fc,
                                             self.packet,
                                             self.offset*struct.calcsize(self.fc))[0]
            self.offset += 1
            self.bits_left += struct.calcsize(self.fc) * 8
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
    # double resolution presolution times
    width = width << presolution - 1
    height = height << presolution - 1
    print "width/height:", width, height
    ptype = bitreader.read(3)
    pquant = bitreader.read(5)
    pframe = bitreader.read(32)
    return width, height

def get_mb(bitreader):
    mbc = bitreader.read(1)
    mbdesc = 0
    if not (mbc & 1):
        mbdesc = bitreader.read(8)
        print bin(mbdesc)
        assert(mbdesc & 0b10000000)
        if mbdesc & 0b01000000:
            mbdiff = bitreader.read(2)
        for i in range(6):
            get_block(bitreader, (mbdesc >> i) & 1)
    return True

def get_block(bitreader, has_coeff):
    # read the first 10 bits in a 16 bit datum
    out_list = []
    _ = 0b111111 << 10
    _ += bitreader.read(10)
    if not has_coeff:
        return
    out_list.append(_)
    while 1:
        zerocount = 0
        while bitreader.read(1) == 0:
            zerocount += 1
        toread = 0 if zerocount <= 1 else zerocount - 1
        additional = bitreader.read(toread)
        if zerocount > 0:
            tmp = (1 << zerocount) + additional
            for i in range(tmp):
                out_list.append(0)

        zerocount = 0
        while bitreader.read(1) == 0:
            zerocount += 1
        if zerocount == 1:
            break
        else:
            tmp = (1 << zerocount)
            if zerocount > 1:
                tmp += bitreader.read(zerocount - 1)
            tmp = -tmp if bitreader.read(1) else tmp
            out_list.append(tmp)

def get_gob(bitreader, blocks):
    bitreader.align()
    gobsc = bitreader.read(22)
    if gobsc == 0b0000000000000000111111:
        print "weeeee"
        return False
    elif (not (gobsc & 0b0000000000000000100000) or
         (gobsc & 0b1111111111111111000000)):
        print "Got wrong GOBSC, aborting.", bin(gobsc)
        return False
    print 'GOBSC:', gobsc & 0b11111
    _ = bitreader.read(5)
    for i in range(blocks):
        print "b%i" % i,
        get_mb(bitreader)
    print
    return True

def read_picture(bitreader):
    width, height = get_pheader(bitreader)
    slices = height / 16
    blocks = width / 16
    # this is already the first slice
    for i in range(blocks):
        get_mb(bitreader)
    # those are the remaining ones
    for i in range(1, slices):
        print "Getting Slice", i, slices
        get_gob(bitreader, blocks)
    print "\nEND OF PICTURE\n"

def _pp(name, value):
    #return
    print "%s\t\t%s\t%s" % (name, str(bin(value)), str(value))

if __name__ == '__main__':
    fh = open('video.raw', 'r')
    data = fh.read()
    fh.close()
    br = BitReader(data)
    read_picture(br)

