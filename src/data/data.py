"""Read and parse data"""

import contextlib
import logging
import struct
import StringIO


class IntFormat(object):
  def __init__(self):
    pass

  SIGNED = 'Signed'
  UNSIGNED = 'Unsigned' 


class Endian(object):
  def __init__(self):
    pass

  LITTLE_ENDIAN = 'Little Endian'
  BIG_ENDIAN = 'Big Endian'


_STRUCT_UNPACK_FORMAT = {
    (16, IntFormat.SIGNED, Endian.LITTLE_ENDIAN): '<h',
    (32, IntFormat.SIGNED, Endian.LITTLE_ENDIAN): '<i',
}


class DataFormat(object):
  def __init__(self, num_channels, length_bits, sampling_rate):
    self.num_channels = num_channels
    self.length_bits = length_bits
    self.sampling_rate = sampling_rate
    self.struct_format = _STRUCT_UNPACK_FORMAT[
        (length_bits, IntFormat.SIGNED, Endian.LITTLE_ENDIAN)]


  @property
  def data_range(self):
    """The min and max of sample value range.

    @returns: A tuple containing (min, max) of sample value range.

    """
    half_length_bits = self.length_bits - 1
    logging.debug('half length of bits = %r', half_length_bits)
    return (-(1 << half_length_bits), (1 << half_length_bits) - 1)


class RawData(object): # pylint:disable=R0903
  """The abstraction of raw data.

  @property channel_data: A list of lists containing samples in each channel.
                          E.g., The third sample in the second channel is
                          channel_data[1][2].
  @property data_format: A DataFormat.
  @property num_of_samples: The number of samples in a channel.
  """
  def __init__(self, binary, data_format):
    """Initializes a RawData.

    @param binary: A string containing binary data.
    @param data_format: A DataFormat object.
    """
    self.data_format = data_format
    self.channel_data = [[] for _ in xrange(self.data_format.num_channels)]
    self._read_binary(binary)
    self.num_of_samples = len(self.channel_data[0])


  def _read_one_sample(self, handle):
    """Reads one sample from handle.

    @param handle: A handle that supports read() method.

    @return: A number read from file handle based on sample format.
             None if there is no data to read.
    """
    data = handle.read(self.data_format.length_bits >> 3)
    if data == '':
      return None
    number, = struct.unpack(self.data_format.struct_format, data)
    return number


  def _read_binary(self, binary):
    """Reads samples from binary and fills channel_data.

    Reads one sample for each channel and repeats until the end of
    binary.

    @param binary: A string containing binary data.
    """
    channel_index = 0
    with contextlib.closing(StringIO.StringIO(binary)) as f:
      number = self._read_one_sample(f)
      while number is not None:
        self.channel_data[channel_index].append(number)
        channel_index = ((channel_index + 1) %
                         self.data_format.num_channels)
        number = self._read_one_sample(f)


class OneChannelRawData(object): # pylint:disable=R0903
  """A 1-channel raw data."""
  def __init__(self, raw_data, channel_index):
    """Creates a OneChannelRawData from RawData.

    @param raw_data: A RawData object.
    @channel_index: The selected channel. 0 for the first channel.

    """
    self.samples = raw_data.channel_data[channel_index]
    self.sampling_rate = raw_data.data_format.sampling_rate
    self.data_range = raw_data.data_format.data_range
