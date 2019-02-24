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
from absl import logging
from cogrob.service_manager.model import base_service
from cogrob.service_manager.model import delayed_action
from cogrob.service_manager.model import docker_py
from cogrob.service_manager.model import fake_docker_py
from cogrob.service_manager.model import service_id
from cogrob.service_manager.model import service_request
from cogrob.service_manager.proto import service_options_pb2
from cogrob.service_manager.proto import service_state_pb2
from cogrob.service_manager.util import docker_options_pb_to_py
from cogrob.service_manager.util import errors
import datetime
import dateutil.parser
import docker
import random
import threading
import time

flags.DEFINE_string(
    "docker_container_name_prefix", "rorg__",
    "Name prefix for docker containers.")
flags.DEFINE_float(
    "docker_stats_valid_time", 5.0,
    "Time (in seconds) that one docker stats read will be valid.")
FLAGS = flags.FLAGS

ServiceId = service_id.ServiceId
ServiceOptions = service_options_pb2.ServiceOptions
ServiceStatePb = service_state_pb2.ServiceState
ServiceRequest = service_request.ServiceRequest
ServiceRequestId = service_request.ServiceRequestId

class DockerService(base_service.BaseService):

  def __init__(self, manager):
    super(DockerService, self).__init__(manager=manager)
    self._docker_py_client = None
    self._docker_py_inst = None
    self._docker_stats = None


  @staticmethod
  def RestoreFromProto(service_state_pb, manager):
    result = DockerService(manager=manager)
    new_pb = ServiceStatePb()
    new_pb.CopyFrom(service_state_pb)
    result.SetStateProto(new_pb)

    if result.IsInSimulation():
      result._docker_py_client = fake_docker_py.GetGlobalFakeDockerClient()
    else:
      result._docker_py_client = docker_py.GetGlobalDockerClient()

    result._docker_py_inst = result._docker_py_client.GetContainer(
        result._GetContainerName())
    return result


  def _GetContainerName(self):
    return (FLAGS.docker_container_name_prefix +
            "__".join(self.GetServiceId().namespace)
            + "_" + self.GetServiceId().name)


  @staticmethod
  def _CheckServiceOption(pb_service_option):
    assert pb_service_option.type == service_options_pb2.SERVICE_TYPE_DOCKER
    docker_options = pb_service_option.docker_service_options

    if docker_options.HasField("auto_remove") and docker_options.auto_remove:
      raise errors.ServiceUnsupportedOptionsError(
          "DockerService: auto_remove cannot be true.")

    if docker_options.HasField("remove") and docker_options.remove:
      raise errors.ServiceUnsupportedOptionsError(
          "DockerService: remove cannot be true.")


  @staticmethod
  def CreateFromServiceOptionsPb(pb_service_option, manager):
    assert pb_service_option.type == service_options_pb2.SERVICE_TYPE_DOCKER

    pb_service_state = ServiceStatePb()
    pb_service_state.id.CopyFrom(pb_service_option.id)
    pb_service_state.type = pb_service_option.type
    pb_service_state.options.CopyFrom(pb_service_option)
    pb_service_state.status = ServiceStatePb.STATUS_STOPPED

    result = DockerService(manager=manager)
    result.SetStateProto(pb_service_state)

    # TODO(shengye): Check the parameters and fill in the default parameters.

    docker_py_args = docker_options_pb_to_py.DockerOptionsPbToDict(
        result.GetStateProto().options.docker_service_options.container_options)
    docker_py_args["name"] = result._GetContainerName()
    # TODO(shengye): Some parameter need to be converted to docker-py structures

    options_to_remove = ["stdout", "stderr", "remove"]
    for opt_to_rm_name in options_to_remove:
      if opt_to_rm_name in docker_py_args:
        docker_py_args.pop(opt_to_rm_name)

    if result.IsInSimulation():
      result._docker_py_client = fake_docker_py.GetGlobalFakeDockerClient()
    else:
      result._docker_py_client = docker_py.GetGlobalDockerClient()

    # FIXME(shengye): Pull image from registry.
    result._docker_py_inst = result._docker_py_client.CreateContainer(
        **docker_py_args)

    return result


  def Update(self, new_options):
    # TODO(shengye): When we decide to implement this Update function,
    # we should check and only update those parameters that can be updated
    # online
    # TODO(shengye): We can also have a flag that only recreates the underlying
    # docker-py object, without touch anything else.

    previous_status = self.GetStateProto().status
    self.DeactivateSelf(force=True)
    self._RemoveContainer()

    self.GetStateProto().options.CopyFrom(new_options)

    docker_py_args = docker_options_pb_to_py.DockerOptionsPbToDict(
        self.GetStateProto().options.docker_service_options.container_options)
    docker_py_args["name"] = self._GetContainerName()
    # TODO(shengye): Some parameter need to be converted to docker-py structures

    options_to_remove = ["stdout", "stderr", "remove"]
    for opt_to_rm_name in options_to_remove:
      if opt_to_rm_name in docker_py_args:
        docker_py_args.pop(opt_to_rm_name)

    if self.IsInSimulation():
      self._docker_py_client = fake_docker_py.GetGlobalFakeDockerClient()
    else:
      self._docker_py_client = docker_py.GetGlobalDockerClient()

    # FIXME(shengye): Pull image from registry.
    self._docker_py_inst = self._docker_py_client.CreateContainer(
        **docker_py_args)

    if previous_status == ServiceStatePb.STATUS_ACTIVE:
      self.ActivateSelf()


  def Remove(self):
    # Here we cancel all the requests this service sent and remove self from the
    # manager.
    self.DeactivateSelf(force=True)
    self._RemoveContainer()
    self._manager.RemoveService(self.GetServiceId())


  def ActivateSelf(self):
    # If current state is stopped, set it to active and generate a request, and
    # send to all related services.
    if self.IsActive():
      logging.info("No need to activate service: %s, already active",
                   str(self.GetServiceId()))
      return []

    logging.info("Activating service: %s", str(self.GetServiceId()))
    self._docker_py_inst.Start()
    self.GetStateProto().status = ServiceStatePb.STATUS_ACTIVE
    self.GetStateProto().docker_service_state.status = (
        service_state_pb2.DockerServiceState.DOCKER_STATUS_ACTIVE)

    all_delayed_actions = []

    # Reactivate all implied requests.
    all_delayed_actions += (
        self.ActRequestService(self.GetImpliedServiceRequest()))

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

    self.GetStateProto().status = ServiceStatePb.STATUS_TO_BE_STOPPED

    if not force and self.GetStateProto().options.disable_deactivate:
      raise errors.InternalError(
          "Cannot deactivate {}, disable_deactivate is true.".format(
              self.GetServiceId()))

    if not force and self.GetStateProto().requested_by_others:
      raise errors.InternalError(
          "Cannot deactivate {}, requested by services: {}.".format(
              self.GetServiceId(),
              ", ".join(map(str, self.GetStateProto().requested_by_others))))

    logging.info("Deactivating service (releasing requests): %s",
                 str(self.GetServiceId()))
    requests_by_self = [ServiceRequest.FromProto(x) for x
                        in self.GetStateProto().requests_by_self]

    all_delayed_actions = []
    for request_by_self in requests_by_self:
      # TODO(shengye): If it is pause, we can save these to somewhere else.
      all_delayed_actions += self.ActReleaseService(request_by_self.request_id)

    logging.info("Deactivating service (stopping docker): %s",
                 str(self.GetServiceId()))
    self._docker_py_inst.Stop()
    self.GetStateProto().docker_service_state.status = (
        service_state_pb2.DockerServiceState.DOCKER_STATUS_STOPPED)

    logging.info("Deactivated service: %s", str(self.GetServiceId()))
    self.GetStateProto().status = ServiceStatePb.STATUS_STOPPED

    # all_delayed_actions will always be [], which is OK for now.
    return all_delayed_actions


  def _RemoveContainer(self, force=True):
    self._docker_py_inst.Remove(force=force)


  def HandleRequestService(self, request):
    return self.HandleRequestServiceBasic(request)


  def HandleReleaseService(self, service_request_id):
    return self.HandleReleaseServiceBasic(service_request_id)


  def ForceRestart(self):
    self._docker_py_inst.Restart()


  def ActRequestService(self, service_request):
    return self.ActRequestServiceBasic(service_request)


  def ActReleaseService(self, service_request_id):
    return self.ActReleaseServiceBasic(service_request_id)


  def RefreshDockerStats(self):
    if self.IsInSimulation():
      return None
    self._docker_stats = self._docker_py_inst.Stats(stream=False, decode=True)
    return self._docker_stats


  def GetDockerStats(self):
    stats_dict = self._docker_stats
    need_requery = False

    if stats_dict is None:
      need_requery = True
    else:
      read_time = dateutil.parser.parse(stats_dict["read"])
      read_timestamp = (read_time - datetime.datetime(
          1970, 1, 1, tzinfo=read_time.tzinfo)).total_seconds()
      if time.time() - read_timestamp > FLAGS.docker_stats_valid_time:
        need_requery = True

    if need_requery:
      self.RefreshDockerStats()
      stats_dict = self._docker_stats

    return stats_dict


  def GetCpuUsage(self):
    if not self.IsInSimulation():
      # Query CPU usage from Docker, CPU usage is counted as number of logical
      # cores. (Number can be greater than 1.)
      # TODO(shengye): This read takes a lot of time, it should be asychronized
      try:
        stats_dict = self.GetDockerStats()
        if "percpu_usage" in stats_dict["cpu_stats"]["cpu_usage"]:
          cpu_count = len(stats_dict["cpu_stats"]["cpu_usage"]["percpu_usage"])
          cpu_usage = (float(
              stats_dict["cpu_stats"]["cpu_usage"]["total_usage"] -
              stats_dict["precpu_stats"]["cpu_usage"]["total_usage"]) /
              (stats_dict["cpu_stats"]["system_cpu_usage"] -
              stats_dict["precpu_stats"]["system_cpu_usage"])) * cpu_count
          return cpu_usage
        else:
          return 0
      except docker.errors.DockerException as e:
        raise errors.InternalError("Docker error: %s", str(e))
        logging.error("Docker error: %s", str(e))
    else:
      if not self.IsActive():
        return 0
      cpu_usage_pb = (
          self.GetStateProto().options.simulation_parameters.cpu_usage)
      if cpu_usage_pb.HasField("guassian"):
        return random.gauss(cpu_usage_pb.guassian.mean,
                            math.sqrt(cpu_usage_pb.guassian.variance))
      elif cpu_usage_pb.HasField("fixed_value"):
        return cpu_usage_pb.fixed_value
      else:
        return None


  def GetMemoryUsage(self):
    if not self.IsInSimulation():
      # Query memory usage from Docker, memory usage is counted in bytes.
      # TODO(shengye): This read takes a lot of time, it should be asychronized.
      try:
        stats_dict = self.GetDockerStats()
        if ("memory_stats" in stats_dict
            and "usage" in stats_dict["memory_stats"]):
          return stats_dict["memory_stats"]["usage"]
        return 0
      except docker.errors.DockerException as e:
        raise errors.InternalError("Docker error: %s", str(e))
        logging.error("Docker error: %s", str(e))
    else:
      if not self.IsActive():
        return 0
      memory_usage_pb = (
          self.GetStateProto().options.simulation_parameters.memory_usage)
      if memory_usage_pb.HasField("guassian"):
        return random.gauss(memory_usage_pb.guassian.mean,
                            math.sqrt(memory_usage_pb.guassian.variance))
      elif memory_usage_pb.HasField("fixed_value"):
        return memory_usage_pb.fixed_value
      else:
        return None
