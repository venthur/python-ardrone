

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
    _pp('psc', bitreader.read(22))
    _pp('pformat', bitreader.read(2))
    # vga: 160x120
    # civ: 88x72
    _pp('presolution', bitreader.read(3))
    _pp('ptype', bitreader.read(3))
    _pp('pquant', bitreader.read(5))
    _pp('pframe', bitreader.read(32))

def get_mb(bitreader):
    #_pp('mbc', bitreader.read(1))
    #_pp('mbdesc', bitreader.read(8))
    #_pp('mbdiff', bitreader.read(2))
    # his:
    mbc = bitreader.read(1)
    if not (mbc & 1):
        mbdesc = bitreader.read(8)
        if not (mbdesc & 0b10000000):
            print "wrong mbdesc!"
            return False
        else:
            print "correct mbdesc"
        if mbdesc & 0b01000000:
            mbdiff = bitreader.read(2)
        for i in range(6):
            if (mbdesc >> i) & 1:
                get_block(bitreader)
    return True

def get_block(bitreader):
    # read the first 10 bits in a 16 bit datum
    out_list = []
    _ = 0b111111 << 10
    _ += bitreader.read(10)
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

def get_gob(bitreader):
    bitreader.align()
    #_pp('gobsc', bitreader.read(22))
    #_pp('gobquant', bitreader.read(5))
    gobsc = bitreader.read(22)
    if gobsc == 0b0000000000000000111111:
        print "weeeee"
        return False
    elif not (gobsc & 0b0000000000000000100000):
        print "Got wrong GOBSC, aborting."
        return False
    print gobsc & 0b11111
    _ = bitreader.read(5)
    for i in range(10):
        if not get_mb(bitreader):
            return False
    return True

def read_picture(bitreader):
    get_pheader(bitreader)
    for i in range(10):
        get_mb(bitreader)
    while get_gob(bitreader):
        print '.',
        pass
    print "\nEND OF PICTURE\n"

def _pp(name, value):
    #return
    print "%s\t\t%s\t%s" % (name, str(bin(value)), str(value))

if __name__ == '__main__':
    fh = open('videoframe.raw', 'r')
    data = fh.read()
    fh.close()
    br = BitReader(data)
    read_picture(br)

