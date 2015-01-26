"""The module to control content on the sreen."""

import logging

from waveform import waveform
from waveview import waveview


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


class Screen(object):
  """Screen controls a wave view and a menu.

   ----------------------------------------
  |                                        |
  |               Wave view                |
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
  MenuDisplay and WaveViewDisplay are two Display Object.
  Display object uses subwindow to draw the content.

  Note that window coordinate use (row, col) where (0, 0) is the
  top left corner of the window.

  """
  def __init__(self, window, raw_data, menu_height):
    """Create a Screen object.

    @param window: A curses.window object.
    @param raw_data: A data.OneChannelRawData object.
    @param menu_height: A number for height of menu

    """
    window.clear()
    window_height, window_width = window.getmaxyx()
    logging.debug('window_height, window_width = %r, %r',
                  window_height, window_width)

    self._window = window

    subwindow_menu = self._window.subwin(
        menu_height, window_width, window_height - menu_height, 0)
    subwindow_wave = self._window.subwin(
        window_height - menu_height, window_width, 0, 0)

    self._menu_display = MenuDisplay(subwindow_menu)
    self._wave_display = WaveViewDisplay(subwindow_wave, raw_data)


  def clear(self):
    """Clears the window."""
    self._window.clear()


  def init_display(self):
    """Display initial menu and wave view."""
    self._menu_display.init_display()
    self._wave_display.init_display()
    self._window.refresh()


  def wave_view_move(self, direction):
    """Move curser in the view window.

    Asks WaveViewDisplay to handle a curser move event.

    @param direction: A direction defined in Direction

    """
    self._wave_display.move(direction)
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
  """This class controls a subwindow for waveview display."""
  def __init__(self, window, raw_data):
    """Creates a WaveViewDisplay object.

    @param window: A subwindow.
    @param raw_data: A data.OneChannelRawData object.

    """
    self._window = window
    self._raw_data = raw_data
    self._view = None
    self._start_x, self._start_y = None, None
    self._width, self._height = None, None
    self._setup_valid_size()

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
    wave = waveform.Waveform(self._raw_data, self._width, self._height)
    self._view = waveview.WaveView(wave.wave_samples, self._width,
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
    logging.debug('Draw %r and (row, col) = (%r, %r)',
                  python_char, row, col)
    self._window.addch(row, col, ord(python_char))


  def _draw_content(self, content):
    """Draws the content starting from (0, 0) of window.

    @param content: A 2D array where each element is a python char.

    """
    for row in xrange(self._height):
      for col in xrange(self._width):
        self._draw_char(row, col, content[row][col])

    self._window.refresh()
