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


class GroupService(base_service.BaseService):

  def __init__(self, manager):
    super(GroupService, self).__init__(manager=manager)


  @staticmethod
  def RestoreFromProto(service_state_pb, manager):
    result = GroupService(manager=manager)
    new_pb = ServiceStatePb()
    new_pb.CopyFrom(service_state_pb)
    result.SetStateProto(new_pb)
    return result


  def _GetServiceRequestId(self):
    return service_request.ServiceRequestId(self.GetServiceId(), "")


  def _GetServiceRequest(self):
    implied_service_ids = [
        ServiceId.FromProto(x) for x
        in self.GetStateProto().options.implied_services]
    grouped_service_ids = [
        ServiceId.FromProto(x) for x
        in self.GetStateProto().options.group_service_options.grouped_services]
    return service_request.ServiceRequest(
        self._GetServiceRequestId(), implied_service_ids + grouped_service_ids)


  @staticmethod
  def CreateFromServiceOptionsPb(pb_service_option, manager):
    assert pb_service_option.type == service_options_pb2.SERVICE_TYPE_GROUP

    pb_service_state = ServiceStatePb()
    pb_service_state.id.CopyFrom(pb_service_option.id)
    pb_service_state.type = pb_service_option.type
    pb_service_state.options.CopyFrom(pb_service_option)
    pb_service_state.status = ServiceStatePb.STATUS_STOPPED

    result = GroupService(manager=manager)
    result.SetStateProto(pb_service_state)

    return result


  def Update(self, new_options):
    raise NotImplementedError("Cannot update a GroupService at this moment.")
    # TODO(shengye): When we decide to implement this Update function,
    # we should: compare old and new actions. Call release on those no longer
    # belongs to this group, and request those added to this group.


  def Remove(self):
    # Here we cancel all the requests this service sent and remove self from the
    # manager.
    self.DeactivateSelf(force=True)
    self._manager.RemoveService(self.GetServiceId())


  def ActivateSelf(self):
    # If current state is stopped, set it to active and generate a request, and
    # send to all related services.
    if self.IsActive():
      logging.info("No need to activate service: %s, already active",
                   str(self.GetServiceId()))
      return []

    all_delayed_actions = []

    self.GetStateProto().requests_by_self.ClearFields()
    self.GetStateProto().requests_by_self.append(self._GetServiceRequest())
    self.GetStateProto().status = ServiceStatePb.STATUS_ACTIVE

    for srv_id in self.GetStateProto().options.grouped_services:
      grouped_service = self._manager.GetService(
          ServiceId.FromProto(srv_id))
      all_delayed_actions += grouped_service.HandleRequestService(
          self._GetServiceRequest())

    # Reactivate all implied requests.
    all_delayed_actions += self.ActRequestService(
        self.GetImpliedServiceRequest())

    # Only after this service activates all grouped services could it claim
    # it can start the countdown.
    if self.GetStateProto().options.ready_detection_method.HasField(
        "wait_fixed_time"):
      all_delayed_actions.append(
          delayed_action.WaitUntilTimestamp(time.time() +
          self.GetStateProto().options.ready_detection_method.wait_fixed_time))
    elif self.GetStateProto().options.ready_detection_method.HasField(
        "wait_for_prober"):
      raise errors.ServiceUnsupportedOptionsError(
          "{} has an unsupported wait_for_prober ReadyDetectionMethod".format(
          self.GetServiceId()))

    return all_delayed_actions


  def DeactivateSelf(self, force=False):
    if not self.IsActive():
      logging.info("No need to deactivate service: %s, not active",
                   str(self.GetServiceId()))
      return []

    if not force and self.GetStateProto().options.disable_deactivate:
      raise errors.InternalError(
          "Cannot deactivate {}, disable_deactivate is true.".format(
              self.GetServiceId()))

    if not force and self.GetStateProto().requested_by_others:
      raise errors.InternalError(
          "Cannot deactivate {}, requested by services: {}.".format(
              self.GetServiceId(),
              ", ".join(map(str, self.GetStateProto().requested_by_others))))
    all_delayed_actions = []
    for srv_id in self.GetStateProto().options.grouped_services:
      grouped_service = self._manager.GetService(
          ServiceId.FromProto(srv_id))
      all_delayed_actions += grouped_service.HandleReleaseService(
          self._GetServiceRequest())
    self.GetStateProto().requests_by_self.ClearFields()
    self.GetStateProto().status = ServiceStatePb.STATUS_STOPPED

    # all_delayed_actions will always be [], which is OK for now.
    return all_delayed_actions


  def HandleRequestService(self, request):
    return self.HandleRequestServiceBasic(request)


  def HandleReleaseService(self, service_request_id):
    return self.HandleReleaseServiceBasic(service_request_id)


  def ForceRestart(self):
    raise errors.InternalError(
        "Cannot force-restart a GroupService. Please find the groupped "
        "services and restart them individually.")


  def ActRequestService(self, service_request):
    return self.ActRequestServiceBasic(service_request)


  def ActReleaseService(self, service_request_id):
    return self.ActReleaseServiceBasic(service_request_id)
