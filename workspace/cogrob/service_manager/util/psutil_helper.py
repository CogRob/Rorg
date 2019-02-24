# Copyright (c) 2019, The Regents of the University of California
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# * Neither the name of the University of California nor the
#   names of its contributors may be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OF THE UNIVERSITY OF CALIFORNIA
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import psutil
import threading
import time


def _GetPsUtilCpuUsage(sample_interval=1.0):
  cpu_percents = psutil.cpu_percent(interval=sample_interval, percpu=True)
  return sum(map(lambda x: x/100.0, cpu_percents))


def _GetPsUtilMemoryUsage():
  return psutil.virtual_memory().used


class PsUtilHelperWithCache(object):

  def __init__(self, sample_interval=1.0):
    self._cpu_usage = 0
    self._memory_usage = 0
    self._sample_interval = sample_interval
    self._stop_loop_thread = False
    self._thread = None


  def _LoopThread(self):
    while not self._stop_loop_thread:
      start_time = time.time()
      self._cpu_usage = _GetPsUtilCpuUsage(
          sample_interval=self._sample_interval)
      self._memory_usage = _GetPsUtilMemoryUsage()
      if time.time() - start_time < 0.9 * self._sample_interval:
        # Fail safe, in case psutil is not doing the delay, we do this to
        # prevent using 100% of CPU.
        time.sleep(self._sample_interval)


  def StartLoopingThread(self):
    if self._thread is None:
      self._stop_loop_thread = False
      self._thread = threading.Thread(target=self._LoopThread)
      self._thread.start()


  def StopLoopingThread(self):
    self._stop_loop_thread = True
    if self._thread is not None:
      self._thread.join()
      self._thread = None


  def GetCpuUsage(self):
    return self._cpu_usage


  def GetMemoryUsage(self):
    return self._memory_usage


if __name__ == "__main__":
  print "CPU Usage: {}".format(_GetPsUtilCpuUsage())
  print "Memory Usage: {}".format(_GetPsUtilMemoryUsage())
