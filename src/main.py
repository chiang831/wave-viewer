#!/usr/bin/python
"""The main entry point."""

import argparse
import cStringIO
import logging
import os
import subprocess

from data import data
from waveform import waveform
from waveview import waveview


def show_basic_function():
  """Show basic function with test data."""
  src_folder = os.path.dirname(os.path.realpath(__file__))
  input_file = os.path.join(src_folder, '..', 'test_data', '1hz.raw')
  raw_data = read_raw_data(input_file)
  one_channel_raw_data = data.OneChannelRawData(raw_data, 0)
  width, height = get_window_size()
  if not height & 1:
    logging.debug('Modify height %r to %r', height, height - 1)
    height = height - 1
  wave = waveform.Waveform(one_channel_raw_data, width, height)
  view = waveview.WaveView(wave.wave_samples, width, height)
  view.draw_view(0, 0)
  canvas = view.get_view()
  print_canvas(canvas)


def get_window_size():
  """Gets window size.

  @returns: A tuple (width, height).
  """
  # Must leave space for user prompt
  width = int(subprocess.check_output(['tput', 'cols']).strip()) - 30
  height = int(subprocess.check_output(['tput', 'lines']).strip()) - 8
  logging.info('width, height = %r, %r', width, height)
  return width, height


#TODO Set format from command line.
def read_raw_data(input_file):
  """Read a file.

  The file data format is fixed to 1 channel, 16 bit signed int,
  48000 Hz sampling rate.

  @param input_file: The path to the input raw data file.

  @returns: A RawData object.
  """
  content = None
  with open(input_file) as handle:
    content = handle.read()
  data_format = data.DataFormat(
      num_channels=1,
      length_bits=16,
      sampling_rate=48000)
  return data.RawData(content, data_format)


#TODO abstract this to a new class ViewPrinter.
def print_canvas(canvas):
  """Print canvas to command line.

  @args canvas: A 2D array containing the content to print with (0,0) =
  in the top left corner and the dimension is (row, col).

  """
  output = cStringIO.StringIO()
  num_rows = len(canvas)
  num_cols = len(canvas[0])
  for row in xrange(num_rows):
    for col in xrange(num_cols):
      output.write(canvas[row][col])
    output.write('\n')
  print output.getvalue()


def parse_args():
  """Parse command line arguments.

  @returns: populated namespace containing parsed arguments.
  """
  parser = argparse.ArgumentParser(description='Interactive waveform viewer')
  parser.add_argument('--debug', '-d', action='store_true', default=False,
                      help='Print debug messages.')

  args = parser.parse_args()
  level = logging.DEBUG if args.debug else logging.INFO
  logging.basicConfig(level=level)
  return args


def main():
  """Main entry point."""
  parse_args()
  show_basic_function()


if __name__ == '__main__':
  main()
