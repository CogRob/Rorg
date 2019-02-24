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

from absl import flags
from cogrob.service_manager.model import base_service
from cogrob.service_manager.model import service_id
from cogrob.service_manager.model import service_request
from cogrob.service_manager.proto import service_options_pb2
from cogrob.service_manager.proto import service_state_pb2
from cogrob.service_manager.util import errors

FLAGS = flags.FLAGS

ServiceId = service_id.ServiceId
ServiceOptions = service_options_pb2.ServiceOptions
ServiceRequest = service_request.ServiceRequest
ServiceRequestId = service_request.ServiceRequestId
ServiceStatePb = service_state_pb2.ServiceState


class MetaService(base_service.BaseService):

  def __init__(self, manager):
    super(MetaService, self).__init__(manager=manager)


  @staticmethod
  def RestoreFromProto(service_state_pb, manager):
    result = MetaService(manager=manager)
    new_pb = ServiceStatePb()
    new_pb.CopyFrom(service_state_pb)
    result.SetStateProto(new_pb)
    return result


  @staticmethod
  def CreateFromServiceOptionsPb(pb_service_option, manager):
    assert pb_service_option.type == service_options_pb2.SERVICE_TYPE_META

    pb_service_state = ServiceStatePb()
    pb_service_state.id.CopyFrom(pb_service_option.id)
    pb_service_state.type = pb_service_option.type
    pb_service_state.options.CopyFrom(pb_service_option)
    pb_service_state.status = ServiceStatePb.STATUS_ACTIVE

    result = MetaService(manager=manager)
    result.SetStateProto(pb_service_state)

    return result


  def Update(self, new_options):
    raise errors.InternalError("Cannot update a MetaService.")


  def Remove(self):
    raise errors.InternalError("Cannot remove a MetaService.")


  def HandleRequestService(self, request):
    del request
    raise errors.InternalError("Cannot request a MetaService")


  def HandleReleaseService(self, service_request_id):
    del request
    raise errors.InternalError("Cannot release a MetaService")


  def ForceRestart(self):
    raise errors.InternalError("Cannot force-restart a MetaService.")


  def ActRequestService(self, service_request):
    return self.ActRequestServiceBasic(service_request)


  def ActReleaseService(self, service_request_id):
    return self.ActReleaseServiceBasic(service_request_id)
