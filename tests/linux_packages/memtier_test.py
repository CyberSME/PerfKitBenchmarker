"""Tests for perfkitbenchmarker.linux_packages.memtier."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import unittest
from perfkitbenchmarker import sample
from perfkitbenchmarker import test_util
from perfkitbenchmarker.linux_packages import memtier

TEST_OUTPUT = """
  4         Threads
  50        Connections per thread
  20        Seconds
  Type        Ops/sec     Hits/sec   Misses/sec      Latency       KB/sec
  ------------------------------------------------------------------------
  Sets        4005.50          ---          ---      4.50600       308.00
  Gets       40001.05         0.00     40001.05      4.54300      1519.00
  Totals     44006.55         0.00     40001.05      4.54000      1828.00

  Request Latency Distribution
Type        <= msec      Percent
------------------------------------------------------------------------
SET               0         5.00
SET               1        10.00
SET               2        15.00
SET               3        30.00
SET               4        50.00
SET               5        70.00
SET               6        90.00
SET               7        95.00
SET               8        99.00
SET               9       100.00
---
GET               0         50.0
GET               2       100.00
"""

METADATA = {'test': 'foobar'}


class MemtierTestCase(unittest.TestCase, test_util.SamplesTestMixin):

  def testParseResults(self):
    get_metadata = {
        'histogram': json.dumps([
            {'count': 4500, 'millisec': 0},
            {'count': 4500, 'millisec': 2}])}
    get_metadata.update(METADATA)
    set_metadata = {
        'histogram': json.dumps([
            {'count': 50, 'millisec': 0},
            {'count': 50, 'millisec': 1},
            {'count': 50, 'millisec': 2},
            {'count': 150, 'millisec': 3},
            {'count': 200, 'millisec': 4},
            {'count': 200, 'millisec': 5},
            {'count': 200, 'millisec': 6},
            {'count': 50, 'millisec': 7},
            {'count': 40, 'millisec': 8},
            {'count': 10, 'millisec': 9}])}
    set_metadata.update(METADATA)
    expected_result = [
        sample.Sample(
            metric='Ops Throughput',
            value=44006.55, unit='ops/s',
            metadata=METADATA),
        sample.Sample(
            metric='KB Throughput',
            value=1828.0,
            unit='KB/s',
            metadata=METADATA),
        sample.Sample(
            metric='get latency histogram',
            value=0,
            unit='',
            metadata=get_metadata),
        sample.Sample(
            metric='set latency histogram',
            value=0,
            unit='',
            metadata=set_metadata),
    ]
    samples = []
    samples.extend(memtier.ParseResults(TEST_OUTPUT, METADATA))
    self.assertSampleListsEqualUpToTimestamp(samples, expected_result)
