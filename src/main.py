#!/usr/bin/python
"""The main entry point."""

import argparse
import curses
import logging
import os

from data import data
from screen import screen


LOG_FILE = '/tmp/wave-view.log'

def show_basic_function(stdscr):
  """Show basic function with test data."""
  src_folder = os.path.dirname(os.path.realpath(__file__))
  input_file = os.path.join(src_folder, '..', 'test_data', '1hz.raw')
  raw_data = read_raw_data(input_file)
  one_channel_raw_data = data.OneChannelRawData(raw_data, 0)

  top_screen = screen.Screen(stdscr, one_channel_raw_data, 5)
  top_screen.clear()
  top_screen.init_display()

  # TODO: constraint cursor in view window.
  # TODO: show time stamp and value at cursor.

  while True:
    input_char = stdscr.getch()
    logging.debug('input char = %r', input_char)
    if 0 < input_char < 256:
      python_char = chr(input_char)
      if python_char in 'Qq':
        break
      else:
        # Ignore incorrect keys
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

    # Move view.
    top_screen.wave_view_move(direction)


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

  args = parser.parse_args()
  level = logging.DEBUG if args.debug else logging.INFO
  logging.basicConfig(filename=LOG_FILE, level=level)
  return args


def main():
  """Main entry point."""
  parse_args()
  curses.wrapper(show_basic_function)

if __name__ == '__main__':
  main()
