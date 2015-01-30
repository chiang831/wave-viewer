# wave-viewer
This is a tool to view waveform in command line.

Currently only basic waveform viewing is implemented.

Usage:
./wave_view to demonstrate basic waveform vieweing.

Use arrow key to scroll.

O and o to scale in time.

P and p to scale in value.

Q to quit.

./wave_view FILE to view a file.

./wave_view --help for help.

=================================================

For developer:
./src/utils/run_pylint.py to run pylint on all files.
./src/utils/run_pylint.py -E to output error only.
./src/utils/run_pylint.py [file1] [file2] to run pylint on files.
