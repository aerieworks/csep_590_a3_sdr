#!/usr/bin/python

import argparse
from os import stat
from struct import unpack
from sys import stderr, stdin
from time import sleep

class SignalProcessor:

  HIGH_THRESHOLD = 0.5
  READ_CHUNK_SIZE = 2048
  LABEL_LONG = 'L'
  LABEL_SHORT = 'S'

  messages = {
    'LS.LLSS.LLSS.LLSS.LLSS.LLSS.LLSS.LLSS.LLSLSLSS.LS.LS.LS.LS.LS.LS': 'Button A pressed.',
    'LS.LLSS.LLSS.LLSS.LLSS.LLSS.LLSS.LLSS.LLSS.LS.LLSLSS.LS.LS.LS.LS': 'Button B pressed.',
    'LS.LLSS.LLSS.LLSS.LLSS.LLSS.LLSS.LLSS.LLSS.LS.LS.LS.LLSLSS.LS.LS': 'Button C pressed.',
    'LS.LLSS.LLSS.LLSS.LLSS.LLSS.LLSS.LLSS.LLSS.LS.LS.LS.LS.LS.LLSLSS': 'Button D pressed.'
  }

  def __init__(self, noise_threshold, print_values, print_counts, print_letters, print_words, continuous):
    self.signal_count = 0
    self.noise_count = 0
    self.current_message = []
    self.current_word = []
    self.noise_threshold = noise_threshold
    self.print_values = print_values
    self.print_counts = print_counts
    self.print_letters = print_letters
    self.print_words = print_words
    self.is_continuous = continuous

  def process(self, source):
      sample_count = 0
      float_bytes = source.read(SignalProcessor.READ_CHUNK_SIZE)
      while len(float_bytes) >= 4:
        float_count = len(float_bytes) / 4
        unpack_format = str(float_count) + 'f'
        values = unpack(unpack_format, float_bytes)

        remainder_count = len(float_bytes) % 4
        if remainder_count > 0:
          remainder_bytes = float_bytes[-remainder_count:]
        else:
          remainder_bytes = ''

        for value in values:
          if self.print_values:
            print value
          self.handle_value(value)
        sample_count += len(values)

        float_bytes = remainder_bytes + source.read(SignalProcessor.READ_CHUNK_SIZE)

      return sample_count

  def handle_value(self, value):
    if value < SignalProcessor.HIGH_THRESHOLD:
      self.handle_low_value()
    else:
      self.handle_high_value()

  def handle_low_value(self):
    self.noise_count += 1
    if self.noise_count == self.noise_threshold:
      self.detect_letter(1, self.signal_count)
      self.signal_count = 0
    if self.noise_count == 500:
      word = ''.join(self.current_word)
      self.current_word = []
      if self.print_words:
        print 'Chunk:', word
      self.current_message.append(word)
      self.detect_message()
      if self.print_letters:
        print '\t',
    elif self.noise_count == 2000:
      self.current_message = []
      if self.print_letters:
        print

  def handle_high_value(self):
    if self.noise_count < self.noise_threshold:
      self.signal_count += self.noise_count
    else:
      self.detect_letter(0, self.noise_count)
    self.signal_count += 1
    self.noise_count = 0

  def detect_letter(self, value, count):
    if count > self.noise_threshold:
      if self.print_counts:
        print '%d x %d' % (value, count)
      if count < 500:
        self.current_word.append(SignalProcessor.LABEL_SHORT)
        if self.print_letters:
          print SignalProcessor.LABEL_SHORT,
      else:
        self.current_word.append(SignalProcessor.LABEL_LONG)
        if self.print_letters:
          print SignalProcessor.LABEL_LONG,

  def detect_message(self):
    if len(self.current_message) == 15:
      message = '.'.join(self.current_message)
      if SignalProcessor.messages.has_key(message):
        print SignalProcessor.messages[message]
        self.current_message = []
      else:
        self.current_message.pop(0)


parser = argparse.ArgumentParser(description = 'Parse a signal from some floaty noise.')
parser.add_argument('-f', '--file', nargs=1, dest='filename', type=str, help='The file from which to read floats.')
parser.add_argument('-n', '--noise-threshold', dest='noise_threshold', nargs=1, type=int, default=[50], help='The number of consecutive data points required to treat a value as signal and not noise.')
parser.add_argument('-a', '--values', action='store_true', dest='print_values', help='Print raw values as we detect them.')
parser.add_argument('-c', '--counts', action='store_true', dest='print_counts', help='Print consecutive counts of 0, 1 as we detect them.')
parser.add_argument('-l', '--letters', action='store_true', dest='print_letters', help='Print long, short letters as we detect them.')
parser.add_argument('-w', '--words', action='store_true', dest='print_words', help='Print words as we detect them.')
parser.add_argument('-C', '--continuous', action='store_true', dest='continuous', help='Continue to watch the file for new input.')

args = parser.parse_args()
processor = SignalProcessor(args.noise_threshold[0], args.print_values, args.print_counts, args.print_letters, args.print_words, args.continuous)

if args.filename == None:
  processor.process(stdin)
else:
  keep_going = True
  while keep_going:
    skip_count = 0
    with open(args.filename[0], 'r') as source:
      if skip_count > 0:
        print >> stderr, 'Skipping %d bytes...' % (skip_count,)
        source.seek(skip_count)

      skip_count = processor.process(source)

    keep_going = args.continuous

