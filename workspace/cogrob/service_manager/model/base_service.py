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
from cogrob.service_manager.model import service_request
from cogrob.service_manager.proto import service_state_pb2
from cogrob.service_manager.proto import service_options_pb2
from cogrob.service_manager.util import errors

ServiceId = service_id.ServiceId
ServiceOptions = service_options_pb2.ServiceOptions
ServiceStatePb = service_state_pb2.ServiceState
ServiceRequest = service_request.ServiceRequest
ServiceRequestId = service_request.ServiceRequestId

class BaseService(object):
  """
  BaseService the common base of a service. It defines the interfaces.


  Create:
    [RPC handler] call FromServiceOptionsPb through a router factory function.
                  FromServiceOptionsPb will prepare the service (create docker
                  container, etc.) and register with the service manager.
  Update:
    By default, delete then create. Otherwise if supported, do a partial update.

  Activate:
    [RPC handler] Find the service and call ActRequestService.
                  ActRequestService will call HandleRequestService on other
                  services. Failures may happen, and error message will be
                  returned.
  """

  def __init__(self, manager):
    # _manager is service_manager.ServiceManager
    self._manager = manager

    # _service_state is service_state_pb2.ServiceState
    # _service_state should include all the current state. i.e. it
    # alone is sufficient to construct self.
    self._service_state = None


  @staticmethod
  def RestoreFromProto(service_state_pb, manager):
    """Restore from a service_state_pb2.ServiceState."""
    raise NotImplementedError(
        "RestoreFromProto in ServiceBase must be override by derived class")


  @staticmethod
  def CreateFromServiceOptionsPb(service_options_pb, manager):
    """Create a service given options from the client."""
    raise NotImplementedError(
        "FromServiceOptionsPb in ServiceBase must be override by derived class")


  def SetManager(self, manager):
    self._manager = manager


  def Update(self, new_options):
    """Update a service."""
    raise NotImplementedError(
        "Update in ServiceBase must be override by derived class")


  def Remove(self):
    """Remove a service."""
    raise NotImplementedError(
        "Update in ServiceBase must be override by derived class")


  def HandleRequestService(self, service_request):
    """Handle a request of this service (called by other services)."""
    raise NotImplementedError(
        "HandleRequestService in ServiceBase must be override by derived class")


  def HandleReleaseService(self, service_request_id):
    """Handle a request release of this service (called by other services)."""
    raise NotImplementedError(
        "HandleReleaseService in ServiceBase must be override by derived class")


  def ActivateSelf(self, new_options):
    """Activate self service."""
    raise NotImplementedError(
        "ActivateSelf in ServiceBase must be override by derived class")


  def DeactivateSelf(self, new_options):
    """Deactivate self service."""
    raise NotImplementedError(
        "DeactivateSelf in ServiceBase must be override by derived class")


  def Remove(self):
    """Remove a service."""
    raise NotImplementedError(
        "Update in ServiceBase must be override by derived class")


  def ForceRestart(self):
    """Force restart the current service. """
    # Some service is stateful: if roscore restarts, all other services will
    # need to restart.
    # TODO(shengye): Carefully design the usage of this interface.
    raise NotImplementedError(
        "ForceRestart in ServiceBase must be override by derived class")


  def ActRequestService(self, service_request):
    """Bringup some services on behalf of self."""
    raise NotImplementedError(
        "ActRequestService in ServiceBase must be override by derived class")


  def ActReleaseService(self, service_request_id):
    """Revert a previous service request on behalf of self."""
    # TODO(shengye): add an immediate shutdown field.
    raise NotImplementedError(
        "ActReleaseService in ServiceBase must be override by derived class")


  def ToProto(self):
    """Convert self to service_state_pb2.ServiceState"""
    result = service_state_pb2.ServiceState()
    result.CopyFrom(self._service_state)
    return result


  def GetServiceId(self):
    """Get service id."""
    return ServiceId.FromProto(self._service_state.id)


  def GetStateProto(self):
    """For derived classes, get self._service_state"""
    return self._service_state


  def SetStateProto(self, pb):
    """For derived classes, set self._service_state"""
    self._service_state = pb


  def ActRequestServiceBasic(self, request):
    # Returns List[DelayedAction]
    if self.GetStateProto().status != ServiceStatePb.STATUS_ACTIVE:
      raise errors.ServiceNotActiveError(
          "Service {} is not active.".format(self.GetServiceId()))

    filtered_requests_by_self = [
        x for x in self.GetStateProto().requests_by_self if
        ServiceRequestId.FromProto(x.request_id) != request.request_id]
    self.GetStateProto().ClearField("requests_by_self")
    self.GetStateProto().requests_by_self.extend(filtered_requests_by_self)
    self.GetStateProto().requests_by_self.extend([request.ToProto()])

    # The HandleRequestService will return a list of DelayedAction. They are
    # non-blocking. The call handler will either wait for these actions to
    # finish, or let the client know the situation.
    all_delayed_actions = []
    for requested_service in request.requested_services:
      delayed_actions = (self._manager.GetService(requested_service)
                         .HandleRequestService(request))
      all_delayed_actions.extend(delayed_actions)
    return all_delayed_actions


  def ActReleaseServiceBasic(self, service_request_id):
    if (self.GetStateProto().status != ServiceStatePb.STATUS_ACTIVE and
        self.GetStateProto().status != ServiceStatePb.STATUS_TO_BE_STOPPED):
      raise errors.ServiceNotActiveError(
          "Service {} is not active.".format(self.GetServiceId()))

    filtered_requests_by_self = [
        x for x in self.GetStateProto().requests_by_self
        if ServiceRequestId.FromProto(x.request_id) != service_request_id]
    if (len(filtered_requests_by_self)
        == len(self.GetStateProto().requests_by_self)):
      raise errors.ServiceRequestNotExistError(
          "Cannot find service request: {}".format(str(service_request_id)))

    service_request = ServiceRequest.FromProto(
        [x for x in self.GetStateProto().requests_by_self
         if ServiceRequestId.FromProto(x.request_id) == service_request_id][0])

    self.GetStateProto().ClearField("requests_by_self")
    self.GetStateProto().requests_by_self.extend(filtered_requests_by_self)

    all_delayed_actions = []
    for requested_service in service_request.requested_services:
      delayed_actions = (self._manager.GetService(requested_service)
                         .HandleReleaseService(service_request.request_id))
      all_delayed_actions.extend(delayed_actions)
    return all_delayed_actions


  def HandleRequestServiceBasic(self, request):
    # TODO(shengye): We should check if self.GetServiceId() is in request.
    # First, record the request, but not to duplicate the request.
    filtered_service_req_id = [
        x for x in self.GetStateProto().requested_by_others
        if ServiceRequestId.FromProto(x) != request.request_id]
    self.GetStateProto().ClearField("requested_by_others")
    self.GetStateProto().requested_by_others.extend(filtered_service_req_id)
    self.GetStateProto().requested_by_others.extend([
        request.request_id.ToProto()])
    return self.ActivateSelf()


  def HandleReleaseServiceBasic(self, service_request_id):
    # First, remove service_request_id from requested_by_others.
    filtered_service_req_id = [
        x for x in self.GetStateProto().requested_by_others
        if ServiceRequestId.FromProto(x) != service_request_id]
    if (len(filtered_service_req_id) >=
        len(self.GetStateProto().requested_by_others)):
      raise errors.ServiceRequestNotExistError(
          "{} does not exist in {}.".format(service_request_id,
                                            self.GetServiceId()))
    self.GetStateProto().ClearField("requested_by_others")
    self.GetStateProto().requested_by_others.extend(filtered_service_req_id)

    if not self.GetStateProto().requested_by_others:
      # We can now turn from active to inactive and cancel our request.
      return self.DeactivateSelf()
    else:
      return []


  def GetImpliedServiceRequest(self):
    implied_service_ids = [
        ServiceId.FromProto(x) for x
        in self.GetStateProto().options.implied_dependencies]
    return service_request.ServiceRequest(
        service_request.ServiceRequestId(self.GetServiceId(), "__IMPLIED"),
        implied_service_ids)


  def IsInSimulation(self):
    if (self.GetStateProto().options.run_mode
        == service_options_pb2.RUN_MODE_SIMULATION):
      return True
    return False


  def GetCpuUsage(self):
    """Get the CPU usage of this service (direct, e.g. CPU usage for
    GroupService should not include this children processes, so that's
    nearly zero). Returns None if not available."""

    return None


  def GetMemoryUsage(self):
    """Get the memory usage of this service (direct, e.g. memory usage for
    GroupService should not include this children processes, so that's
    nearly zero). Returns None if not available."""

    return None


  def IsActive(self):
    return self.GetStateProto().status == ServiceStatePb.STATUS_ACTIVE
