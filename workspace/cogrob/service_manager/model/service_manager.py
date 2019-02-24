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
from cogrob.service_manager.model import meta_service
from cogrob.service_manager.model import docker_service
from cogrob.service_manager.model import group_service
from cogrob.service_manager.model import service_id
from cogrob.service_manager.proto import service_options_pb2
from cogrob.service_manager.proto import service_state_pb2
from cogrob.service_manager.util import errors
import concurrent.futures
import google.protobuf.text_format
import os.path
import threading
import time

flags.DEFINE_string(
    "service_manager_storage_base_path", "/tmp/RorgStorage",
    "Base path to store .service_state files.")
flags.DEFINE_integer(
    "refresh_stats_num_threads", 40,
    "Number of worker threads to refresh stats.")
flags.DEFINE_integer(
    "minimal_time_secs_between_refresh_stats", 1,
    "Minimal time gap between full refresh of stats.")
FLAGS = flags.FLAGS
ServiceId = service_id.ServiceId


class ServiceManager(object):

  def __init__(self):
    # TODO(shengye): We need to add mutex to the manager.
    self._managed_services = {}

    self._base_path = FLAGS.service_manager_storage_base_path
    self._service_state_extension = ".service_state"
    self._remove_extension = ".removed"

    self._docker_refresh_thread = None
    self._quit_docker_refresh_thread = False


  def _ServiceIdToFilePath(self, service_id):
    """Generate a file path from a service id."""
    filename = service_id.name + self._service_state_extension
    path = reduce(os.path.join,
        [self._base_path] + list(service_id.namespace) + [filename])
    return path


  def _ServiceFromPb(self, pb):
    if pb.type == service_options_pb2.SERVICE_TYPE_DOCKER:
      return docker_service.DockerService.RestoreFromProto(pb, self)
    elif pb.type == service_options_pb2.SERVICE_TYPE_DOCKER:
      return group_service.GroupService.RestoreFromProto(pb, self)
    elif pb.type == service_options_pb2.SERVICE_TYPE_META:
      return meta_service.MetaService.RestoreFromProto(pb, self)
    else:
      raise errors.ServiceTypeNotSupportedError()


  def CreateMetaOperatorService(self):
    """Returns true if created, otherwise (already exits) returns false"""
    if not ServiceId(["__builtin"], "__operator") in self._managed_services:
      options = service_options_pb2.ServiceOptions()
      options.id.namespace.extend(["__builtin"])
      options.id.name = "__operator"
      options.type = service_options_pb2.SERVICE_TYPE_META
      options.disable_deactivate = True
      options.enabled = True
      service = meta_service.MetaService.CreateFromServiceOptionsPb(
          options, self)
      self.AddService(service)
      return True
    else:
      return False


  def _GetAllManagedFiles(self):
    all_managed_files = []
    for dirpath, dirnames, filenames in os.walk(self._base_path):
      for filename in filenames:
        full_path = os.path.join(dirpath, filename)
        if full_path.endswith(self._service_state_extension):
          all_managed_files.append(full_path)
        else:
          logging.warn("Not a %s file: %s",
                       self._service_state_extension, full_path)
    return all_managed_files

  def LoadFromDisk(self):
    if not os.path.isdir(self._base_path):
      logging.error("Cannot load from disk: %s is not valid.",
                    self._base_path)
      return

    for managed_file in self._GetAllManagedFiles():
      logging.info("Loading %s", managed_file)
      with open(managed_file, "r") as fp:
        pbtxt = fp.read()
      pb = service_state_pb2.ServiceState()
      google.protobuf.text_format.Merge(pbtxt, pb)
      srv = self._ServiceFromPb(pb)
      self._managed_services[srv.GetServiceId()] = srv


  def WriteToDisk(self):
    """Write all the services to the disk."""
    # First, dump all the services we have.
    files_to_keep = []
    for service in self._managed_services.values():
      pb = service.ToProto()
      file_path = self._ServiceIdToFilePath(service.GetServiceId())
      pb_txt = google.protobuf.text_format.MessageToString(pb)
      dir_path = os.path.dirname(file_path)
      if not os.path.isdir(dir_path):
        os.makedirs(os.path.dirname(file_path))
      with open(file_path, "w") as fp:
        fp.write(pb_txt)
      files_to_keep.append(os.path.abspath(file_path))

    # Then, we scan all the files in self._base_path with
    # self._service_state_extension. We will append ".removed" to the
    # filename. If ".removed" already exist, we overwrite that file.
    files_with_correct_extension = [
        x for x in self._GetAllManagedFiles()
        if x.endswith(self._service_state_extension)]
    files_to_remove = [x for x in files_with_correct_extension
                       if x not in files_to_keep]
    for file_to_remove in files_to_remove:
      new_file_path = file_to_remove + self._remove_extension
      if os.path.isfile(new_file_path):
        os.remove(new_file_path)
      os.rename(file_to_remove, new_file_path)


  def AddService(self, service):
    """Add a service to the manager."""
    srv_id = service.GetServiceId()
    if srv_id in self._managed_services:
      raise errors.ServiceAlreadyExistError(
          "Service {} already exist in ServiceManager".format(str(srv_id)))
    else:
      self._managed_services[srv_id] = service
      service.SetManager(self)


  def GetService(self, service_id, no_raise=False):
    """Get a service from the manager."""
    if service_id in self._managed_services:
      return self._managed_services[service_id]
    else:
      if no_raise:
        return None
      else:
        raise errors.ServiceNotFoundError(
            "Service {} not found in ServiceManager".format(service_id))


  def RemoveService(self, service_id):
    """Remove a service from the manager."""

    if service_id in self._managed_services:
      self._managed_services[service_id].SetManager(None)
      self._managed_services.pop(service_id)
    else:
      raise errors.ServiceNotFoundError(
          "Service {} not found in ServiceManager".format(service_id))


  def RequestService(self, service_request):
    requester_service = self.GetService(ServiceId.FromProto(
        service_request.request_id.service_id))
    return requester_service.ActRequestService(service_request)


  def ReleaseService(self, service_request_id):
    requester_service = self.GetService(service_request_id.service_id)
    return requester_service.ActReleaseService(service_request_id)


  def GetAllManagedServiceIds(self):
    return self._managed_services.keys()


  def CollectAllServiceCpuUsage(self):
    result = 0
    for service in self._managed_services.values():
      cpu_usage = service.GetCpuUsage()
      if cpu_usage is not None:
        result += cpu_usage
    return result


  def CollectAllServiceMemoryUsage(self):
    result = 0
    for service in self._managed_services.values():
      memory_usage = service.GetMemoryUsage()
      if memory_usage is not None:
        result += memory_usage
    return result


  def DockerRefreshThread(self):
    pool = concurrent.futures.ThreadPoolExecutor(
        max_workers=FLAGS.refresh_stats_num_threads)

    while not self._quit_docker_refresh_thread:
      last_start_time = time.time()
      all_docker_services = [x for x in self._managed_services.values()
                             if isinstance(x, docker_service.DockerService)]
      pending_futures = []
      for service in all_docker_services:
        pending_futures.append(pool.submit(service.RefreshDockerStats))

      for pending_future in pending_futures:
        while not pending_future.done():
          if self._quit_docker_refresh_thread:
            pool.shutdown()
          time.sleep(0.25)

      logging.info("Refershed docker stats.")

      while (not self._quit_docker_refresh_thread) and (time.time() <
             last_start_time + FLAGS.minimal_time_secs_between_refresh_stats):
        time.sleep(0.25)


  def StartDockerRefreshThread(self):
    assert self._docker_refresh_thread is None
    self._docker_refresh_thread = threading.Thread(
        target=self.DockerRefreshThread)
    self._docker_refresh_thread.start()


  def StopDockerRefreshThread(self):
    # TODO(shengye): Race condition! Use a lock to protect
    # self._docker_refresh_thread
    if self._docker_refresh_thread is not None:
      self._quit_docker_refresh_thread = True
      self._docker_refresh_thread.join()
      self._docker_refresh_thread = None
