"""Transform raw data to waveform."""

import logging


class WaveformError(Exception):
  """Error in Waveform."""
  pass


class Waveform(object): # pylint:disable=R0903
  """Waveform is a 1-channel raw data processed by down-sample and quantization.

  A waveform is defined by a 1-channel raw data, number of subsamples, and
  number of value levels.

  Down sample and quantize the original raw data to obtain a waveform.

  The number of subsamples determines the down-sample factor.
  The selected subsamples are at multiple of down-sample factor, with no more
  than number of desird number of subsamples.
  E.g., There are 12 samples [0, 1,..., 11] in the original raw data.
  The number of subsamples is 4. The down-sample factor is then 12 / 4 = 3.
  The selected subsamples are [0, 3, 6, 9].

  The number of levels determines the quantization factor.
  Note that for symmetry, number of levels will be adjusted to an odd number.

  E.g., if number of levels is 5. The original value range is -10 ~ 10.

  Original       Quantized

  +10 ------------- +2

  +5  ------------- +1

   0  -------------  0

  -5  ------------- -1

  -10 ------------- -2

  There will be 4 intervals, and 5 levels. The quantization factor is computed
  as full range divided by number of intervals, that is, 20 / 4 = 5.
  The quantized value is the original value divided by quantization factor
  and rounded to the nearest integer.
  """
  def __init__(self, one_channel_raw_data, number_of_subsamples,
               number_of_levels):
    """Creates a Waveform object from OneChannelRawData object.


    @param one_channel_raw_data: A OneChannelRawData object.
    @param number_of_subsamples: Number of subsamples.
    @param number_of_levels: Number of levels.
    """
    self._raw_data = one_channel_raw_data
    self._number_of_subsamples = None
    self._number_of_levels = None
    self._down_sample_factor = None
    self._quantization_factor = None
    self._subsamples = None
    self._quantized_subsamples = None

    self._set_number_of_subsamples(number_of_subsamples)
    self._set_number_of_levels(number_of_levels)
    self._compute_quantized_subsamples()


  @property
  def wave_samples(self):
    """Returns the down-sampled and quantized subsamples."""
    return self._quantized_subsamples


  @property
  def _number_of_samples(self):
    """Returns the number of samples in the original data."""
    return len(self._raw_data.samples)


  @property
  def _full_value_range(self):
    """Returns the full value range in the original data."""
    min_value, max_value = self._raw_data.data_range
    return max_value - min_value


  @property
  def _number_of_intervals(self):
    """Returns the number of intervals."""
    return self._number_of_levels - 1


  def _set_number_of_subsamples(self, number_of_subsamples):
    """Sets the number of subsamples and computes down-sample factor.

    @param number_of_subsamples: The number of subsamples.

    """
    self._number_of_subsamples = number_of_subsamples
    self._compute_down_sample_factor()


  def _set_number_of_levels(self, number_of_levels):
    """Sets the number of levels and computes the level factor.

    @param number_of_levels: The number of levels.

    """
    if not number_of_levels & 1:
      number_of_levels -= 1
      logging.warning('Set number of levels to an odd number %r',
                       number_of_levels)

    self._number_of_levels = number_of_levels
    self._compute_quantization_factor()


  def _compute_down_sample_factor(self):
    """Computes the down-sample factor."""
    self._down_sample_factor = int(self._number_of_samples /
                                   self._number_of_subsamples)
    logging.debug(
        'number of samples: %r, number of subsamples: %r',
        self._number_of_samples, self._number_of_subsamples)
    logging.debug('down-sample factor: %r', self._down_sample_factor)


  def _compute_quantization_factor(self):
    """Computes the level factor."""
    self._quantization_factor = (float(self._full_value_range) /
                                 self._number_of_intervals)
    logging.debug(
        'full value range: %r, number of intervals: %r',
        self._full_value_range, self._number_of_intervals)
    logging.debug('quantization factor: %r', self._quantization_factor)


  def _compute_quantized_subsamples(self):
    """Computes the quantized subsamples."""
    self._down_sample()
    self._quantize()


  def _down_sample(self):
    """Down-samples original samples using down-sample factor."""
    self._subsamples = self._raw_data.samples[::self._down_sample_factor]
    # Neglects the last one subsample if any.
    if len(self._subsamples) == self._number_of_subsamples + 1:
      self._subsamples = self._subsamples[:-1]
    if not len(self._subsamples) == self._number_of_subsamples:
      raise WaveformError(
          'Number of subsample is %r, while %r is expected' % (
              len(self._subsamples), self._number_of_subsamples))
    logging.debug('down-samples: %r', self._subsamples)


  def _quantize(self):
    """Quantizes the down-sampled subsamples."""
    self._quantized_subsamples = [0] * self._number_of_subsamples
    for index, value in enumerate(self._subsamples):
      self._quantized_subsamples[index] = self._quantize_one_value(value)
    logging.debug('quantized down-samples: %r', self._quantized_subsamples)


  def _quantize_one_value(self, value):
    """Quantizes one sample value using quantization factor.

    @param value: The original value.

    @returns: An integer. The quantizaed result.

    """
    add = 0.5 if value > 0 else -0.5
    return int(value / self._quantization_factor + add)
