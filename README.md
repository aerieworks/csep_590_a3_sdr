# CSEP 590 Assignment 3: Software Defined Radio
Annabelle Richard <richanna@u.washington.edu>

The remote_control.py file reads a float stream from a file or stdin and detects remote control keypresses in the stream.  The signal_to_stdout.grc file is a GNU Radio project that listens on the remote control's frequency and streams the signal samples to stdout, making it available for redirection.  The signal_to_stdout.py file is the generated output of that project.

Note that GNU Radio spits out 94 bytes of text content onto stdout, which must be skipped when streaming data using signal_to_stdout.py.  This can easily be accomplished with dd, albeit with additional redirection and added latency:

  python signal_to_stdout.py | dd ifs=94 skip=1 | python remote_control.py


