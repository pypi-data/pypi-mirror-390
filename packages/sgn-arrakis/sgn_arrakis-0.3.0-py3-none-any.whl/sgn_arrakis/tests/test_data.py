import numpy
from sgnts.base import SeriesBuffer

from sgn_arrakis.sink import buffers_to_masked_array


def test_frame_to_masked_array():
    buf0 = SeriesBuffer(
        offset=0,
        sample_rate=16384,
        data=numpy.zeros(10),
    )
    buf1 = SeriesBuffer(
        offset=10,
        sample_rate=16384,
        data=None,
        shape=(10,),
    )
    buf2 = SeriesBuffer(
        offset=20,
        sample_rate=16384,
        data=numpy.ones(10),
    )
    buffers = [buf0, buf1, buf2]
    marray = buffers_to_masked_array(buffers, buf0.data.dtype)
    assert len(marray) == 30
    assert numpy.array_equal(marray[:10], buf0.data)
    assert numpy.all(marray.mask[10:20])
    assert numpy.array_equal(marray[20:], buf2.data)
