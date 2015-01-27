"""Create a view from a waveform."""

import logging


class WaveViewError(Exception):
  """Error in WaveView."""


class WaveView(object):  # pylint:disable=R0903
  """A wave view contains part of the waveform to be shown in a view.

  A view is composed by a rectangle of fixed width and height.
  The height of a view is an odd number.

  The element of the rectangle is either ' ' or '*'.
  The content is determined by the starting point of wave view.

  The job of WaveView object is to fill the content of view according to
  samples and the starting point.

  Sample coordinate:

        |           - - - - -
        |          | * *     |
        |   (5, 2) -         |
        |          |         |
        |           - - - - -
 (0, 0) |___________________________________
        |
        |
        |
        |
        |

  (5, 2) is the starting point of the view in sample coordinate.

  View coordinate:

  |--------|--------|--------|--------|
  | (0, 3) | (1, 3) | (2, 3) | (3, 3) |
  |--------|--------|--------|--------|
  | (0, 2) |*(1, 2) |*(2, 2) | (3, 2) |
  |--------|--------|--------|--------|
  | (0, 1) | (1, 1) | (2, 1) | (3, 1) |
  |--------|--------|--------|--------|
  | (0, 0) | (1, 0) | (2, 0) | (3, 0) |
  |--------|--------|--------|--------|
  | (0,-1) | (1,-1) | (2,-1) | (3,-1) |
  |--------|--------|--------|--------|
  | (0,-2) | (1,-2) | (2,-2) | (3,-2) |
  |--------|--------|--------|--------|
  | (0,-3) | (1,-3) | (2,-3) | (3,-3) |
  |--------|--------|--------|--------|

  """
  def __init__(self, samples, width, height):
    """Initialize a WaveView.

    @param samples: A list containing samples. Each element in the list
                    should be an integer.
    @width: The width of the view.
    @height: The height of the view. It should be an odd number.
    """
    if not height & 1:
      raise WaveViewError('height %r should be an odd number' % height)

    logging.debug('Create a view of width %r, height %r', width, height)

    self._view_content = ViewContent(width, height)
    self._samples = samples
    self._width = width
    self._height = height
    self._half_height = height >> 1
    self._samples_length = len(samples)


  def _draw_point(self, view_x, view_y):
    """Draws a point at (view_x, view_y) in view coordinate.

    @param view_x: x coordinate in view coordinate.
    @param view_y: y coordinate in view coordinate.
    """
    self._view_content.set(view_x, view_y, '*')


  def draw_view(self, start_x, start_y):
    """Draws the view starting from (start_x, start_y) in sample coordinate.

    @param start_x: x coordinate in start coordinate.
    @param start_y: y coordinate in start coordinate.
    """
    logging.debug('Draw view at (%r, %r) in sample coordinate',
                  start_x, start_y)
    self._view_content.clear()
    for view_x in xrange(self._width):
      sample_x = view_x + start_x

      # No sample to show at this point.
      if sample_x < 0:
        continue

      # No sample to show after this point.
      if sample_x >= self._samples_length:
        break

      view_y = self._samples[sample_x] - start_y
      # Too high or too low so the point is not in the view.
      if abs(view_y) > self._half_height:
        continue

      self._draw_point(view_x, view_y)


  def get_view(self):
    """Gets a 2D array with view content.

    A 2D array[height][width] containing the contents in the view using storage
    coordinate as in the docstring of ViewContent.

    """
    return self._view_content.get_all()


class ViewContentError(Exception):
  """Error in ViewContent."""


class ViewContent(object):
  """Provide getter and setter of view coordinate.

  Given a height and width, View content will create a 2D array
  storage[height][width] to store the data. User can get/set
  content using the view coordinate.

  View coordinate:

  |--------|--------|--------|--------|
  | (0, 3) | (1, 3) | (2, 3) | (3, 3) |
  |--------|--------|--------|--------|
  | (0, 2) | (1, 2) | (2, 2) | (3, 2) |
  |--------|--------|--------|--------|
  | (0, 1) | (1, 1) | (2, 1) | (3, 1) |
  |--------|--------|--------|--------|
  | (0, 0) | (1, 0) | (2, 0) | (3, 0) |
  |--------|--------|--------|--------|
  | (0,-1) | (1,-1) | (2,-1) | (3,-1) |
  |--------|--------|--------|--------|
  | (0,-2) | (1,-2) | (2,-2) | (3,-2) |
  |--------|--------|--------|--------|
  | (0,-3) | (1,-3) | (2,-3) | (3,-3) |
  |--------|--------|--------|--------|

  This view is stored in a 2D array storage[height][width].

  Storage coordinate:

  |--------|--------|--------|--------|
  | (0, 0) | (0, 1) | (0, 2) | (0, 3) |
  |--------|--------|--------|--------|
  | (1, 0) | (1, 1) | (1, 2) | (1, 3) |
  |--------|--------|--------|--------|
  | (2, 0) | (2, 1) | (2, 2) | (2, 3) |
  |--------|--------|--------|--------|
  | (3, 0) | (3, 1) | (3, 2) | (3, 3) |
  |--------|--------|--------|--------|
  | (4, 0) | (4, 1) | (4, 2) | (4, 3) |
  |--------|--------|--------|--------|
  | (5, 0) | (5, 1) | (5, 2) | (5, 3) |
  |--------|--------|--------|--------|
  | (6, 0) | (6, 1) | (6, 2) | (6, 3) |
  |--------|--------|--------|--------|

  User can use set and get method to set content at view coordinate.
  ViewContent will handle the coordinate transform and storage.
  """
  def __init__(self, width, height):
    """Creates a ViewContent of size width by height.

    @param width: The width of the storage.
    @param widht: The height of the storage. It should be an odd number.
    """
    if not height & 1:
      raise ViewContentError('height %r should be an odd number' % height)

    self._height = height
    self._half_height = height >> 1
    self._width = width
    self._storage = None
    self.clear()


  def clear(self):
    """Clears the storage."""
    self._storage = [[' '] * self._width for _ in xrange(self._height)]


  def set(self, view_x, view_y, value):
    """Sets the content at (view_x, view_y) in view_coordinate.

    @param view_x: x coordinate in view coordinate.
    @param view_y: y coordinate in view coordinate.
    @param value: The value to set. It should be one character, e.g. '*'.
    """
    row, col = self._view_to_storage(view_x, view_y)
    self._storage[row][col] = value


  def get(self, view_x, view_y):
    """Gets the content at (view_x, view_y) in view_coordinate.

    @param view_x: x coordinate in view coordinate.
    @param view_y: y coordinate in view coordinate.

    @returns: The content at (view_x, view_y) in view_coordinate.
    """
    row, col = self._view_to_storage(view_x, view_y)
    return self._storage[row][col]


  def _view_to_storage(self, view_x, view_y):
    """Transform the coordinate from view to storage.

    @param view_x: x coordinate in view coordinate.
    @param view_y: y coordinate in view coordinate.

    @returns: A tuple (storage_row, storage_col) in storage coordinate.
    """
    return self._half_height - view_y, view_x


  def get_all(self):
    """Gets all contents.

    @returns: A 2D array containing all the contens in the view.
    """
    return self._storage
