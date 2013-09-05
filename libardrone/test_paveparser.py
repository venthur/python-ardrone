import paveparser
import mock
import os


def test_misalignment():
    outfile = mock.Mock()
    p = paveparser.PaVEParser(outfile)
    example_video_stream = open(os.path.join(os.path.dirname(__file__), 'ardrone2_video_example.capture'))
    while True:
        data = example_video_stream.read(1000000)
        if len(data) == 0:
            break
        p.write(data)

    assert outfile.write.called
    assert p.misaligned_frames < 3

if __name__ == "__main__":
    test_misalignment()
