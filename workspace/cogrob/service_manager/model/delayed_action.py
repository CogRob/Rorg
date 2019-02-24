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

from cogrob.service_manager.model import service_id
from cogrob.service_manager.proto import delayed_action_pb2
import math
import time

class DelayedAction(object):

  def Wait(self):
    raise NotImplementedError(
        "Wait in DelayedAction must be override by derived class")


  def ToProto(self):
    raise NotImplementedError(
        "ToProto in DelayedAction must be override by derived class")


class WaitForServiceHeartbeat(DelayedAction):

  def __init__(self, srv_id):
    assert(isinstance(srv_id, service_id.ServiceId))
    self._service_id = srv_id


  def GetServiceId(self):
    return self._service_id


  def ToProto(self):
    result = delayed_action_pb2.DelayedAction()
    result.service_to_wait.CopyFrom(self._service_id)
    return result


class WaitUntilTimestamp(DelayedAction):

  def __init__(self, timestamp):
    self._timestamp = timestamp


  def GetTimestamp(self):
    return self._timestamp


  def Wait(self):
    if time.time() < self._timestamp:
      time.sleep(0.25)


  def ToProto(self):
    result = delayed_action_pb2.DelayedAction()
    result.wait_timestamp.timestamp.seconds = int(math.floor(self._timestamp))
    result.wait_timestamp.timestamp.nanos = int(
        (self._timestamp - result.wait_timestamp.timestamp.seconds) * 1e9)
    return result
