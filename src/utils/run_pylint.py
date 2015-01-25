#!/usr/bin/python
"""Pylint runner."""

import argparse
import logging
import os
import pprint

from pylint.lint import Run


class PylintRunnerError(Exception):
  """Error in run_pylint."""
  pass


def parse_args():
  """Parse command line arguments.

  @returns: The populated namespace.
  """
  parser = argparse.ArgumentParser(description='Pylint runner')
  parser.add_argument('files', action='store', default=None, nargs='*',
                      help='Run pylint on files. Default is all python files.')

  parser.add_argument('--debug', '-d', action='store_true', default=False,
                      help='Print debug messages.')

  parser.add_argument('--error', '-E', action='store_true', default=False,
                      help='Neglect rc file and output error only.')

  args = parser.parse_args()
  level = logging.DEBUG if args.debug else logging.INFO
  logging.basicConfig(level=level)
  return args


def get_src_path():
  """Gets src directory path.

  @returns: The path to src directory.
  """
  src_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../')
  logging.debug('src directory = %r', src_path)
  return src_path


def find_all_py_files(src_path):
  """Finds all python files under a path.

  @param src_path: A path to src directory.

  @returns: A list containing paths to all python files under a path.

  """
  python_files = [os.path.join(dirpath, f)
      for dirpath, _, files in os.walk(src_path)
      for f in files if f.endswith('.py')]

  logging.debug('find python files  %s', pprint.pformat(python_files))

  return python_files


def find_rc_path(src_path):
  """Finds the rcfile used by pylint.

  @param src_path: A path to src directory.

  @return: The path to pylint file.

  @raises: PylintRunnerError if rcfile can not be found.
  """
  rc_path = os.path.join(src_path, '.pylintrc')
  if not os.path.exists(rc_path):
    raise PylintRunnerError('pylintrc %r does not exist!' % rc_path)
  return rc_path


def run_pylint(rc_path, files, error):
  """Run pylint using rcfile on files.

  @param rc_path: The path to rc file.
  @param files: The files to run pylint.
  @param error: Output error only.
  """
  logging.debug('run pylint on %s with rcfile %s', pprint.pformat(files),
                rc_path)
  arguments = []
  if error:
    arguments = ['-E']
  else:
    arguments = ['--rcfile', rc_path]
  arguments += files
  Run(arguments)


def main():
  """The main entry point."""
  args = parse_args()
  src_path = get_src_path()
  files = args.files if args.files else find_all_py_files(src_path)
  rc_path = find_rc_path(src_path)
  run_pylint(rc_path, files, args.error)


if __name__ == '__main__':
  main()
