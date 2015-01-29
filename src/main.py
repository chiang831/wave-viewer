#!/usr/bin/python
"""The main entry point."""

import argparse
import curses
import logging
import os

from data import data
from screen import screen


LOG_FILE = '/tmp/wave-view.log'


def wave_view(stdscr, input_file):
  """View wave form."""
  raw_data = read_raw_data(input_file)
  one_channel_raw_data = data.OneChannelRawData(raw_data, 0)

  top_screen = screen.Screen(stdscr, one_channel_raw_data)
  top_screen.clear()
  top_screen.init_display()

  # TODO: constraint cursor in view window.
  # TODO: show time stamp and value at cursor.

  while True:
    input_char = stdscr.getch()
    logging.debug('input char = %r', input_char)
    direction = None
    time_level_direction = None
    if 0 < input_char < 256:
      python_char = chr(input_char)
      if python_char in 'Qq':
        break
      elif python_char in 'Oo':
        time_level_direction = screen.ScaleDirection.UP
      elif python_char in 'Pp':
        time_level_direction = screen.ScaleDirection.DOWN
      # Ignore incorrect keys
      else:
        pass
    elif input_char == curses.KEY_UP:
      direction = screen.Direction.UP
    elif input_char == curses.KEY_DOWN:
      direction = screen.Direction.DOWN
    elif input_char == curses.KEY_LEFT:
      direction = screen.Direction.LEFT
    elif input_char == curses.KEY_RIGHT:
      direction = screen.Direction.RIGHT
    else:
      # Ignore incorrect keys
      pass

    if direction:
      # Move view.
      top_screen.wave_view_move(direction)
    elif time_level_direction:
      top_screen.wave_view_change_time_level(time_level_direction)


#TODO: Set format from command line.
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


def parse_args():
  """Parse command line arguments.

  @returns: populated namespace containing parsed arguments.
  """
  parser = argparse.ArgumentParser(
      description='Interactive waveform viewer.\n'
                  'The log is in %s.' % LOG_FILE,
      formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument('--debug', '-d', action='store_true', default=False,
                      help='Print debug messages.')
  parser.add_argument('input_file', action='store', default=None, nargs='?',
                      help='Raw data to view. It must be a little-endian\n'
                           'signed 16-bit, 48000 sampling rate, 1-channel\n'
                           'raw data. Default file is a 5 seconds 1Hz\n'
                           'sine wave.')

  args = parser.parse_args()
  level = logging.DEBUG if args.debug else logging.INFO
  logging.basicConfig(filename=LOG_FILE, level=level)
  return args


def get_input_file(args):
  """Gets input file from args, or use default test data."""
  if args.input_file:
    return args.input_file
  else:
    src_folder = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(src_folder, '..', 'test_data', '1hz.raw')


def main():
  """Main entry point."""
  args = parse_args()
  input_file = get_input_file(args)
  curses.wrapper(wave_view, input_file)

if __name__ == '__main__':
  main()
