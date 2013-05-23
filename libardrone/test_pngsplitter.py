import paveparser
import mock
import pngsplitter
import os


def test_pngsplitter():
    listener = mock.Mock()
    splitter = pngsplitter.PNGSplitter(listener)
    example_png_stream = open(os.path.join(os.path.dirname(__file__), 'pngstream.example'))
    while True:
        data = example_png_stream.read(1000)
        if len(data) == 0:
            break
        splitter.write(data)

    assert listener.image_ready.call_count > 60
