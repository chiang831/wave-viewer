"""The module to control content on the sreen."""

import logging

from waveform import waveform
from waveview import waveview


class ScaleDirection(object):
  """Scale direction."""
  UP = 'UP'
  DOWN = 'DOWN'


class Direction(object):
  """Directions."""
  LEFT = 'LEFT'
  RIGHT = 'RIGHT'
  UP = 'UP'
  DOWN = 'DOWN'


def get_next(current_x, current_y, direction):
  """Gets the next location given the current point and direction.

  @param current_x: The x coordinate in sample coordinate.
  @param current_y: The y coordinate in sample coordinate.
  @param direction: A direcition defined in Direction.

  @returns: The new (x, y) in sample coordinate.

  """
  if direction == Direction.LEFT:
    current_x -= 1
  elif direction == Direction.RIGHT:
    current_x += 1
  elif direction == Direction.UP:
    current_y += 1
  elif direction == Direction.DOWN:
    current_y -= 1
  else:
    raise WaveViewDisplayError('Not a valid direction: %r' % direction)

  return current_x, current_y


def format_value(value, width):
  """Format the value into a string of length width.

  @param value: The value.
  @param width: The width of returned string.

  @returns: A strnig of length width representing the number.

  """
  full_string = '%s' % value
  dot_index = full_string.find('.')
  error = False
  # 1234.56 can not be shown in 3 digits.
  if dot_index > width:
    error = True
  # 1234 can not be shown show in 3 digits.
  elif dot_index == -1:
    if len(full_string) > width:
      error = True
  else:
    pass
  if error:
    logging.error('width %r is not long enough for value %r',
                  width, value)
  if len(full_string) < width:
    return ' ' * (width - len(full_string)) + full_string
  else:
    return full_string[0:width]


class Screen(object):
  """Screen controls a data view and a menu.

   ----------------------------------------
  |                                        |
  |               Data view                |
  |                                        |
  |                                        |
  |                                        |
  |                                        |
  |                                        |
  |                                        |
  |                                        |
  |----------------------------------------|
  |   Menu                                 |
  |                                        |
  |                                        |
   ----------------------------------------

  Screen object controls a window object to control
  overall content in the termimal.
  MenuDisplay and DataViewDisplay are two Display Object.
  Display object uses subwindow to draw the content.

  Note that window coordinate use (row, col) where (0, 0) is the
  top left corner of the window.

  """
  _MENU_HEIGHT = 8
  def __init__(self, window, raw_data):
    """Create a Screen object.

    @param window: A curses.window object.
    @param raw_data: A data.OneChannelRawData object.

    """
    window.clear()
    window_height, window_width = window.getmaxyx()
    logging.debug('window_height, window_width = %r, %r',
                  window_height, window_width)

    self._window = window

    subwindow_menu = self._window.subwin(
        self._MENU_HEIGHT, window_width, window_height - self._MENU_HEIGHT, 0)
    subwindow_data = self._window.subwin(
        window_height - self._MENU_HEIGHT, window_width, 0, 0)

    self._menu_display = MenuDisplay(subwindow_menu)
    self._data_display = DataViewDisplay(subwindow_data, raw_data)


  def clear(self):
    """Clears the window."""
    self._window.clear()


  def init_display(self):
    """Display initial menu and data view."""
    self._menu_display.init_display()
    self._data_display.init_display()
    self._window.refresh()


  def wave_view_move(self, direction):
    """Move curser in the data view window.

    Asks DataViewDisplay to handle a curser move event.

    @param direction: A direction defined in Direction

    """
    self._data_display.move(direction)
    self._window.refresh()


  def wave_view_change_time_level(self, direction):
    """Change wave view time level.

    @param direction: ScaleDirection.UP or ScaleDirection.DOWN
    """
    self._data_display.change_time_level(direction)
    self._window.refresh()


  def wave_view_change_value_level(self, direction):
    """Change wave view value level.

    @param direction: ScaleDirection.UP or ScaleDirection.DOWN
    """
    self._data_display.change_value_level(direction)
    self._window.refresh()


  def wave_view_reset(self):
    """Change wave view to default time and value scale and position."""
    self._data_display.init_display()
    self._window.refresh()


class MenuDisplay(object):
  """This class controls a subwindow for menu."""
  def __init__(self, window):
    """Creates a MenuDisplay object.

    @param window: A subwindow.

    """
    self._window = window
    self._height, self._width = self._window.getmaxyx()
    logging.debug('Menu height, width = %r, %r', self._height, self._width)

  def init_display(self):
    """Initializes a menu."""
    self.clear()
    self._window.addstr(1, 2, 'Menu')
    self._window.addstr(2, 2, 'Arrow key to move around.')
    self._window.addstr(3, 2, 'Q to quit.')
    self._window.addstr(4, 2, 'O to scale larger in time.')
    self._window.addstr(5, 2, 'o to scale smaller in time.')
    self._window.addstr(6, 2, 'P to scale larger in value.')
    self._window.addstr(7, 2, 'p to scale smaller in value.')
    self._window.refresh()


  def clear(self):
    """Clears the window."""
    for row in xrange(self._height):
      self._window.move(row, 0)
      self._window.clrtoeol()


class DataViewDisplay(object):
  """DataViewDisplay controls 3 displays.

   ----------------------------------------
  |   |                                    |
  |   |             Wave view              |
  |   |                                    |
  |val|                                    |
  |   |                                    |
  |   |                                    |
  |   |                                    |
  |   |                                    |
  |---|------------------------------------|
  |   |  time                              |
  |----------------------------------------|

  """
  _VALUE_WIDTH = 10
  _TIME_HEIGHT = 2

  def __init__(self, window, raw_data):
    """Creates a DataViewDisplay object.

    @param window: A subwindow.
    @param raw_data: A data.OneChannelRawData object.

    """
    self._window = window
    self._raw_data = raw_data
    self._height, self._width = self._window.getmaxyx()

    subwindow_value = self._window.subwin(
        self._height - self._TIME_HEIGHT, self._VALUE_WIDTH, 0, 0)
    subwindow_wave = self._window.subwin(
        self._height - self._TIME_HEIGHT, self._width - self._VALUE_WIDTH,
        0, self._VALUE_WIDTH)
    subwindow_time = self._window.subwin(
        self._TIME_HEIGHT, self._width - self._VALUE_WIDTH,
        self._height - self._TIME_HEIGHT, self._VALUE_WIDTH)

    self._wave_display = WaveViewDisplay(subwindow_wave, self._raw_data)
    wave_height, wave_width = self._wave_display.draw_size
    self._value_display = ValueDisplay(subwindow_value, wave_height)
    self._time_display = TimeDisplay(subwindow_time, wave_width)


  def init_display(self):
    """Initializes display."""
    self._wave_display.init_display()
    self._update_time_value()


  def _update_time_value(self):
    """Updates time and value."""
    value_range = self._wave_display.get_value_range()
    time_range = self._wave_display.get_time_range()
    self._value_display.update(value_range)
    self._time_display.update(time_range)


  def move(self, direction):
    """Move view toward a direction. Also update time and value.

    @param direction: A direcition defined in Direction.

    """
    self._wave_display.move(direction)
    self._update_time_value()


  def change_time_level(self, direction):
    """Change wave view time level.

    @param direction: ScaleDirection.UP or ScaleDirection.DOWN
    """
    self._wave_display.change_time_level(direction)
    self._update_time_value()


  def change_value_level(self, direction):
    """Change wave view value level.

    @param direction: ScaleDirection.UP or ScaleDirection.DOWN
    """
    self._wave_display.change_value_level(direction)
    self._update_time_value()


class ValueDisplayError(Exception):
  """Error in WaveViewDisplay."""
  pass


class ValueDisplay(object):
  """Value display controls display for value.

 ------------------------------
 | Maximum value in this view.| --> 0
 |                            |
 |                            |
 |                            |
 |                            |
 |                            |
 |                            |
 | Minimum value in this view.| --> wave_height - 1
 |                            |
 -----------------------------

  """
  _VALUE_LENGTH = 8
  def __init__(self, window, wave_height):
    """Creates a ValueDisplay object.

    @param window: A subwindow.
    @param wave_height: The height of wave view.

    """
    self._window = window
    self._height, self._width = self._window.getmaxyx()
    self._wave_height = wave_height
    logging.debug('Value display height, width = %r, %r',
                  self._height, self._width)
    logging.debug('wave height: %r', wave_height)
    if self._width < self._VALUE_LENGTH + 1:
      raise ValueDisplayError('Width %r is not long enough' % self._width)


  def update(self, value_range):
    """Updates the display with new value range.

    @param value_range: (min_value, max_value).

    """
    min_value, max_value = value_range
    min_value_str = format_value(min_value, self._VALUE_LENGTH)
    max_value_str = format_value(max_value, self._VALUE_LENGTH)

    self.clear()
    self._window.addstr(0, 0, max_value_str)
    self._window.addstr(self._wave_height - 1, 0, min_value_str)
    self._window.refresh()


  def clear(self):
    """Clears the window."""
    for row in xrange(self._height):
      self._window.move(row, 0)
      self._window.clrtoeol()


class TimeDisplayError(Exception):
  """Error in WaveViewDisplay."""
  pass


class TimeDisplay(object):
  """Time display controls display for time.

  ----------------------------------------------------------
 | Minimum time in this view.    Maximum time in this view.|
 |                                                          |
  ----------------------------------------------------------

  """
  _TIME_LENGTH = 8
  def __init__(self, window, wave_width):
    """Creates a TimeDisplay object.

    @param window: A subwindow.
    @param wave_width: The width of wave view.

    """
    self._window = window
    self._height, self._width = self._window.getmaxyx()
    self._wave_width = wave_width
    logging.debug('Time display height, width = %r, %r',
                  self._height, self._width)
    if self._width < 2 * (self._TIME_LENGTH + 1):
      raise TimeDisplayError('Width %r is not long enough' % self._width)


  def update(self, time_range):
    """Updates the display with new time range.

    @param time_range: (min_time, max_time).

    """
    min_time, max_time = time_range
    min_time_str = format_value(min_time, self._TIME_LENGTH)
    max_time_str = format_value(max_time, self._TIME_LENGTH)

    self.clear()
    self._window.addstr(0, 0, min_time_str)
    # Do not write to the last point
    self._window.addstr(0, self._wave_width - self._TIME_LENGTH - 2,
                        max_time_str)
    self._window.refresh()


  def clear(self):
    """Clears the window."""
    for row in xrange(self._height):
      self._window.move(row, 0)
      self._window.clrtoeol()


class WaveViewDisplayError(Exception):
  """Error in WaveViewDisplay."""
  pass


class WaveViewDisplay(object):
  """This class controls a subwindow for waveview display.

   ----------------------------------------
  |                                        |
  |                 Wave view              |
  |                                        |
  |                                        |
  |                                        |
  |                                        |
  |                                        |
  |                                        |
  |                                        |
  |                                        |
  |----------------------------------------|


  """
  def __init__(self, window, raw_data):
    """Creates a WaveViewDisplay object.

    @param window: A subwindow.
    @param raw_data: A data.OneChannelRawData object.

    """
    self._window = window
    self._raw_data = raw_data
    self._wave = None
    self._view = None
    self._start_x, self._start_y = None, None
    self._width, self._height = None, None
    self._setup_valid_size()
    # Time level is an integer to control sample length.
    # Level 0 means the sample length is the width of this view.
    # Level 1 means to enlarge the wave view horizontally, that is, increase
    # the sample length by certain amount. The scale corresponds to each
    # level is defined in _get_time_scale.
    self._time_level = None
    self._sample_length = None

    # Value level is an integer to control number of quantize levels.
    # Level 0 means the number of quantize levels is the height of this view.
    # Level 1 means to enlarge the wave view vertically that is, increase
    # the number of quantize levels by certain amount. The scale corresponds
    # to each value level is defined in _get_value_scale.
    self._value_level = None
    self._quantize_levels = None

  @property
  def draw_size(self):
    """Return the (height, width) that is used to draw the wave view.

    @returns: (height, width)

    """
    return (self._height, self._width)


  def clear(self):
    """Clears the window."""
    for row in xrange(self._height):
      self._window.move(row, 0)
      self._window.clrtoeol()


  def _setup_valid_size(self):
    """Sets up valid view size according to window size."""
    self._height, self._width = self._window.getmaxyx()
    # Avoid using the last point to prevent scroll.
    self._height -= 1
    # Adjust height to an odd number.
    if not self._height & 1:
      self._height -= 1
    self._width -= 1


  def init_display(self):
    """Initializes the display of a wave view.

    Use full waveform scale and display at (0, 0) in sample coordinate.

    """
    # Set time level to 0 and sample length to the width of this view.
    # In default view, full data can be displayed in this view.
    self._time_level = 0
    self._sample_length = self._width

    # Set value level to 0 and quantize levels to the height of this view.
    # In default view, full data can be displayed in this view.
    self._value_level = 0
    self._quantize_levels = self._height

    self._wave = waveform.Waveform(self._raw_data, self._sample_length,
                                   self._quantize_levels)
    self._view = waveview.WaveView(self._wave.wave_samples, self._width,
                                   self._height)
    self._start_x, self._start_y = 0, 0
    self._display()


  def move(self, direction):
    """Move view toward a direction.

    @param direction: A direcition defined in Direction.

    """
    logging.debug('Move direction: %r', direction)

    self._start_x, self._start_y = get_next(self._start_x, self._start_y,
                                            direction)
    self._display()


  def _display(self):
    """Display wave view at using current start point in sample coordinate."""
    self._view.draw_view(self._start_x, self._start_y)
    self._draw_content(self._view.get_view())


  def _draw_char(self, row, col, python_char):
    """Draws a python character at (row, col) in window coordinate.

    @param row: row in window coordinate.
    @param col: col in window coordinate.
    @python python_char: a python character, which is a one-length string.

    """
    # Enable this logging if want to debug to detail.
    #logging.debug('Draw %r and (row, col) = (%r, %r)',
    #              python_char, row, col)
    self._window.addch(row, col, ord(python_char))


  def _draw_content(self, content):
    """Draws the content starting from (0, 0) of window.

    @param content: A 2D array where each element is a python char.

    """
    for row in xrange(self._height):
      for col in xrange(self._width):
        self._draw_char(row, col, content[row][col])

    self._window.refresh()


  def get_value_range(self):
    """Get current value range in the view.

    @return (min_value, max_value)

    """
    min_level, max_level = self._view.get_level_range(self._start_y)
    scale = self._wave.quantization_factor
    value_range = (min_level * scale, max_level * scale)
    return value_range


  def get_time_range(self):
    """Get current value range in the view.

    @return (min_time, max_time)

    """
    min_time_index, max_time_index = self._view.get_time_index_range(
            self._start_x)
    scale = self._wave.down_sample_factor
    min_sample_index, max_sample_index = (min_time_index * scale,
                                          max_time_index * scale)
    time_range = (
            float(min_sample_index) / self._raw_data.sampling_rate,
            float(max_sample_index) / self._raw_data.sampling_rate)

    return time_range


  def change_time_level(self, scale_direction):
    """Change time level by change it UP or DOWN.

    @param scale_direction: ScaleDirection.UP or ScaleDirection.DOWN to
                            change time level up or down.

    """
    logging.debug('Scale time level %r', scale_direction)

    if scale_direction == ScaleDirection.UP:
      new_time_level = self._time_level + 1
    else:
      if self._time_level == 0:
        logging.warning('Lowest time level already.')
        return
      else:
        new_time_level = self._time_level - 1
    current_time_scale = self._get_time_scale(self._time_level)
    new_time_scale = self._get_time_scale(new_time_level)

    new_sample_length = int(new_time_scale * self._width)
    if new_sample_length > len(self._raw_data.samples):
      logging.warning('Highest time level already.')
      return

    # Update time level, sample length, and start x at new time level.
    self._time_level = new_time_level
    self._sample_length = new_sample_length
    self._start_x = int(self._start_x / current_time_scale * new_time_scale)

    logging.debug('After scale, new time level: %r, new sample length: %r, '
                  'new start_x: %r',
                  self._time_level, self._sample_length, self._start_x)

    # Update wave form and wave view and display it.
    self._wave = waveform.Waveform(self._raw_data, self._sample_length,
                                   self._quantize_levels)
    self._view = waveview.WaveView(self._wave.wave_samples, self._width,
                                   self._height)
    self._display()


  def _get_time_scale(self, level):
    """Return a scale value based on scale_level.

    @param level: An integer. 0 means the view contains full data range.
                  1 means the width of waveform is 1.1 times the width at
                  level 0.
                  2 means the width of waveform is 1.2 times the width at
                  level 0.
    """
    return 1 + level * 0.1


  def change_value_level(self, scale_direction):
    """Change value level by change it UP or DOWN.

    @param scale_direction: ScaleDirection.UP or ScaleDirection.DOWN to
                            change value level up or down.

    """
    logging.debug('Scale value level %r', scale_direction)

    if scale_direction == ScaleDirection.UP:
      new_value_level = self._value_level + 1
    else:
      if self._value_level == 0:
        logging.warning('Lowest value level already.')
        return
      else:
        new_value_level = self._value_level - 1
    current_value_scale = self._get_value_scale(self._value_level)
    new_value_scale = self._get_value_scale(new_value_level)
    new_quantize_levels = int(new_value_scale * self._height)

    # Update value level, quantize levels, and start y at new value level.
    self._value_level = new_value_level
    self._quantize_levels = new_quantize_levels
    self._start_y = int(self._start_y / current_value_scale * new_value_scale)

    logging.debug('After scale, new value level: %r, new quantize levels: %r, '
                  'new start_y: %r',
                  self._value_level, self._quantize_levels, self._start_y)

    # Update wave form and wave view and display it.
    self._wave = waveform.Waveform(self._raw_data, self._sample_length,
                                   self._quantize_levels)
    self._view = waveview.WaveView(self._wave.wave_samples, self._width,
                                   self._height)
    self._display()


  def _get_value_scale(self, level):
    """Return a scale value based on scale_level.

    @param level: An integer. 0 means the view contains full data range.
                  1 means the number of levels is 1.1 times the number of
                  levels at level 0.
                  2 means the number of levels is 1.2 times the number of
                  levels at level 0.
    """
    return 1 + level * 0.1
