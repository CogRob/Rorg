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
from concurrent import futures
from cogrob.service_manager.model import meta_service
from cogrob.service_manager.model import docker_service
from cogrob.service_manager.model import group_service
from cogrob.service_manager.model import service_id
from cogrob.service_manager.model import service_manager
from cogrob.service_manager.model import service_request
from cogrob.service_manager.proto import result_code_pb2
from cogrob.service_manager.proto import service_manager_rpc_pb2
from cogrob.service_manager.proto import service_manager_rpc_pb2_grpc
from cogrob.service_manager.proto import service_options_pb2
from cogrob.service_manager.util import errors
from cogrob.service_manager.util import psutil_helper
import grpc
import sys
import time
import threading


FLAGS = flags.FLAGS
_ONE_DAY_IN_SECONDS = 60 * 60 * 24
ServiceId = service_id.ServiceId


class ServiceManagerServicer(
    service_manager_rpc_pb2_grpc.ServiceManagerServicer):

  def __init__(self, service_manager, psutil_with_cache):
    self._service_manager = service_manager
    self._psutil_with_cache = psutil_with_cache
    self._lock = threading.Lock()


  def CreateService(self, request, context):
    with self._lock:
      srv_id = ServiceId.FromProto(request.options.id)
      logging.info("Received create request: %s", str(srv_id))

      options = request.options
      response = service_manager_rpc_pb2.CreateServiceResponse()
      try:
        if self._service_manager.GetService(srv_id, no_raise=True) is not None:
          raise errors.ServiceAlreadyExistError(
              "Service {} already exist in ServiceManager".format(srv_id))

        if options.type == service_options_pb2.SERVICE_TYPE_DOCKER:
          service = docker_service.DockerService.CreateFromServiceOptionsPb(
              options, self._service_manager)
        elif options.type == service_options_pb2.SERVICE_TYPE_DOCKER:
          service = group_service.GroupService.CreateFromServiceOptionsPb(
              options, self._service_manager)
        elif options.type == service_options_pb2.SERVICE_TYPE_META:
          service = meta_service.MetaService.CreateFromServiceOptionsPb(
              options, self._service_manager)
        else:
          raise errors.ServiceTypeNotSupportedError()
        self._service_manager.AddService(service)
        response.result = result_code_pb2.RESULT_OK
      except errors.ServiceManagerError as e:
        response.result = e.GetResultCode()
        response.error_message = str(e)
      self._service_manager.WriteToDisk()
      return response


  def QueryService(self, request, context):
    with self._lock:
      response = service_manager_rpc_pb2.QueryServiceResponse()
      try:
        srv_id = ServiceId.FromProto(request.id)
        logging.info("Received query request: %s", str(srv_id))
        service = self._service_manager.GetService(srv_id)
        response.service_status.CopyFrom(service.ToProto())
        response.result = result_code_pb2.RESULT_OK
      except errors.ServiceManagerError as e:
        response.result = e.GetResultCode()
        response.error_message = str(e)
      self._service_manager.WriteToDisk()
      return response


  def UpdateService(self, request, context):
    with self._lock:
      response = service_manager_rpc_pb2.UpdateServiceResponse()
      try:
        service = self._service_manager.GetService(
            ServiceId.FromProto(request.options.id))
        service.Update(request.options)
        response.result = result_code_pb2.RESULT_OK
      except errors.ServiceManagerError as e:
        response.result = e.GetResultCode()
        response.error_message = str(e)
      self._service_manager.WriteToDisk()
      return response


  def RemoveService(self, request, context):
    with self._lock:
      response = service_manager_rpc_pb2.RemoveServiceResponse()
      try:
        srv_id = ServiceId.FromProto(request.id)
        logging.info("Received remove request: %s", str(srv_id))
        service = self._service_manager.GetService(srv_id)
        logging.info("Found service: %s", str(srv_id))
        service.Remove()
        logging.info("Removed service: %s", str(srv_id))
        response.result = result_code_pb2.RESULT_OK
      except errors.ServiceManagerError as e:
        response.result = e.GetResultCode()
        response.error_message = str(e)
      self._service_manager.WriteToDisk()
      return response


  def RequestService(self, request, context):
    with self._lock:
      response = service_manager_rpc_pb2.RequestServiceResponse()
      try:
        delayed_actions = self._service_manager.RequestService(
            service_request.ServiceRequest.FromProto(request.request))
        assert delayed_actions is not None
        if request.wait_for_ready:
          for delayed_action in delayed_actions:
            delayed_action.Wait()
        else:
          response.delayed_actions.extend(
              map(lambda x: x.ToProto(), delayed_actions))
        response.result = result_code_pb2.RESULT_OK
      except errors.ServiceManagerError as e:
        response.result = e.GetResultCode()
        response.error_message = str(e)
      self._service_manager.WriteToDisk()
      return response


  def ListServices(self, request, context):
    with self._lock:
      del request
      response = service_manager_rpc_pb2.ListServicesResponse()
      response.services.extend([
          x.ToProto() for x in self._service_manager.GetAllManagedServiceIds()])
      return response


  def ReleaseService(self, request, context):
    with self._lock:
      response = service_manager_rpc_pb2.ReleaseServiceResponse()
      try:
        self._service_manager.ReleaseService(
            service_request.ServiceRequestId.FromProto(request.request_id))
        response.result = result_code_pb2.RESULT_OK
      except errors.ServiceManagerError as e:
        response.result = e.GetResultCode()
        response.error_message = str(e)
      self._service_manager.WriteToDisk()
      return response


  def QueryServiceResourceUsage(self, request, context):
    with self._lock:
      response = service_manager_rpc_pb2.QueryServiceResourceUsageResponse()
      try:
        srv_id = ServiceId.FromProto(request.id)
        logging.info("Received query resource request: %s", str(srv_id))
        service = self._service_manager.GetService(srv_id)
        cpu_usage = service.GetCpuUsage()
        memory_usage = service.GetMemoryUsage()
        if cpu_usage is not None:
          response.cpu_usage = cpu_usage
        if memory_usage is not None:
          response.memory_usage = memory_usage
        response.result = result_code_pb2.RESULT_OK
      except errors.ServiceManagerError as e:
        response.result = e.GetResultCode()
        response.error_message = str(e)
      return response


  def QueryTotalResourceUsage(self, request, context):
    with self._lock:
      response = service_manager_rpc_pb2.QueryTotalResourceUsageResponse()
      try:
        if request.collect_method == (
            service_manager_rpc_pb2.QueryTotalResourceUsageRequest
            .COLLECT_METHOD_SUM_INDIVIDUAL):
          response.cpu_usage = self._service_manager.CollectAllServiceCpuUsage()
          response.memory_usage = (
              self._service_manager.CollectAllServiceMemoryUsage())
          response.result = result_code_pb2.RESULT_OK
        elif request.collect_method == (
            service_manager_rpc_pb2.QueryTotalResourceUsageRequest
            .COLLECT_METHOD_PSUTIL):
          response.cpu_usage = self._psutil_with_cache.GetCpuUsage()
          response.memory_usage = self._psutil_with_cache.GetMemoryUsage()
          response.result = result_code_pb2.RESULT_OK
      except errors.ServiceManagerError as e:
        response.result = e.GetResultCode()
        response.error_message = str(e)
      return response



def main(argv):
  FLAGS.verbosity = logging.INFO
  FLAGS(argv)

  psutil_with_cache = psutil_helper.PsUtilHelperWithCache()
  psutil_with_cache.StartLoopingThread()

  manager = service_manager.ServiceManager()
  manager.LoadFromDisk()
  manager.CreateMetaOperatorService()
  manager.StartDockerRefreshThread()

  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  service_manager_rpc_pb2_grpc.add_ServiceManagerServicer_to_server(
    ServiceManagerServicer(manager, psutil_with_cache), server)
  server.add_insecure_port("[::]:7016")
  server.start()
  logging.info("Server started.")
  try:
    while True:
      time.sleep(_ONE_DAY_IN_SECONDS)
  except:
    logging.error("The main thread in being killed.")
    server.stop(0)
    psutil_with_cache.StopLoopingThread()
    manager.StopDockerRefreshThread()


if __name__ == "__main__":
  main(sys.argv)
