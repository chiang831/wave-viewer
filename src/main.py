#!/usr/bin/python
"""The main entry point."""

import logging
import os
import cStringIO
import subprocess

from data import data

def show_basic_function():
  logging.basicConfig(level=logging.INFO)
  src_folder = os.path.dirname(os.path.realpath(__file__))
  input_file = os.path.join(src_folder, '..', 'test_data', '1hz.raw')
  raw_data = read_raw_data(input_file)

  width, height = get_window_size()
  down_samples = get_down_sample(raw_data, width)
  canvas = draw_down_sample(down_samples, height, 1<<16)
  print_canvas(canvas)


def get_window_size():
  # Must leave space for user prompt
  width = int(subprocess.check_output(['tput', 'cols']).strip()) - 30
  height = int(subprocess.check_output(['tput', 'lines']).strip()) - 5
  logging.info('width, height = %r, %r', width, height)
  return width, height


def read_raw_data(input_file):
  content = None
  with open(input_file) as f:
    content = f.read()
  data_format = data.DataFormat(
      num_channels=1,
      length_bits=16,
      sampling_rate=48000)
  return data.RawData(content, data_format)


def get_down_sample(raw_data, num_of_points):
  time_duration_secs = (raw_data.num_of_samples /
                        raw_data.data_format.sampling_rate)
  logging.info('time: 0 ~ %r s', time_duration_secs)
  num_of_samples = raw_data.num_of_samples
  down_sample_number = num_of_samples / num_of_points
  down_sample_values = raw_data.channel_data[0][::down_sample_number]
  logging.debug('Down sample length: %s', len(down_sample_values))
  return down_sample_values


def draw_down_sample(samples, height, full_range):
  canvas = [[' '] * len(samples) for _ in xrange(height)]

  logging.debug('canvas size: width: %r, height: %r',
                len(canvas[0]), len(canvas))
  half_height = height >> 1
  canvas[half_height] = ['-'] * len(samples)
  scale_factor = full_range / height
  logging.info('full_range: %r ~ %r', 0 - full_range / 2, full_range / 2)
  logging.debug('full_range = %r, height = %r, scale_factor = %r',
                full_range, height, scale_factor)
  for index, value in enumerate(samples):
    logging.debug('index, value = %r, %r', index, value)
    scaled_value = value / scale_factor
    canvas_y = scaled_value + half_height
    if canvas_y >= height or canvas_y < 0:
      continue
    canvas_x = index
    logging.debug('x, y = %r, %r', canvas_x, canvas_y)
    canvas[canvas_y][canvas_x] = '*'
  return canvas


def print_canvas(canvas):
  output = cStringIO.StringIO()
  num_rows = len(canvas)
  num_cols = len(canvas[0])
  for row in xrange(num_rows - 1, -1, -1):
    for col in xrange(num_cols):
      output.write(canvas[row][col])
    output.write('\n')
  print output.getvalue()


def main():
  print 'Hello'

  show_basic_function()


if __name__ == '__main__':
  main()
