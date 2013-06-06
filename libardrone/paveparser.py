# -*- coding: utf-8 -*-
# Copyright (c) 2013 Adrian Taylor
# Inspired by equivalent node.js code by Felix Geisendörfer
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

import struct

"""
The AR Drone 2.0 allows a tcp client to receive H264 (MPEG4.10 AVC) video
from the drone. However, the frames are wrapped by Parrot Video
Encapsulation (PaVE), which this class parses.
"""

"""
Usage: Pass in an output file object into the constructor, then call write on this.
"""
class PaVEParser(object):

    HEADER_SIZE_SHORT = 64; # sometimes header is longer

    def __init__(self, outfileobject):
        self.buffer = ""
        self.state = self.handle_header
        self.outfileobject = outfileobject
        self.misaligned_frames = 0
        self.payloads = 0

    def write(self, data):
        self.buffer += data

        while True:
            made_progress = self.state()
            if not made_progress:
                return

    def handle_header(self):
        if self.fewer_remaining_than(self.HEADER_SIZE_SHORT):
            return False
        (signature, version, video_codec, header_size, self.payload_size, encoded_stream_width, encoded_stream_height, display_width, display_height, frame_number, timestamp, total_chunks, chunk_index, frame_type, control, stream_byte_position_lw, stream_byte_position_uw, stream_id, total_slices, slice_index, header1_size, header2_size, reserved2, advertised_size, reserved3) = struct.unpack("<4sBBHIHHHHIIBBBBIIHBBBB2sI12s", self.buffer[0:self.HEADER_SIZE_SHORT])
        if signature != "PaVE":
            self.state = self.handle_misalignment
            return True
        self.buffer = self.buffer[header_size:]
        self.state = self.handle_payload
        return True

    def handle_misalignment(self):
        """Sometimes we start of in the middle of frame - look for the PaVE header."""
        index = self.buffer.find('PaVE')
        if index == -1:
            return False
        self.misaligned_frames += 1
        self.buffer = self.buffer[index:]
        self.state = self.handle_header
        return True

    def handle_payload(self):
        if self.fewer_remaining_than(self.payload_size):
             return False
        self.state = self.handle_header
        self.outfileobject.write(self.buffer[0:self.payload_size])
        self.buffer = self.buffer[self.payload_size:]
        self.payloads += 1
        return True

    def fewer_remaining_than(self, desired_size):
        return len(self.buffer) < desired_size
