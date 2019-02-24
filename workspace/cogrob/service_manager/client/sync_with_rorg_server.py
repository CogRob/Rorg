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
from cogrob.service_manager.model import service_id
from cogrob.service_manager.proto import service_manager_rpc_pb2
from cogrob.service_manager.proto import service_manager_rpc_pb2_grpc
from cogrob.service_manager.proto import service_options_pb2
from cogrob.service_manager.proto import sync_helper_config_pb2
import checksumdir
import google.protobuf.text_format
import grpc
import sys

FLAGS = flags.FLAGS
flags.DEFINE_string("service_manager_grpc_server", "localhost:7016",
                    "gRPC server address for service manager.")

# TODO(shengye): This should be automatic, default should be
# /home/common/mission_control_XXX/rorg_sync_config.pbtxt
flags.DEFINE_string(
    "config_path",
    "/home/common/mission_control_fetch33/rorg_sync_config.pbtxt",
    "Configuration file for this script.")


class RorgSyncScriptHelper(object):

  def __init__(self):
    channel = grpc.insecure_channel(FLAGS.service_manager_grpc_server)
    self._rorg_stub = service_manager_rpc_pb2_grpc.ServiceManagerStub(channel)
    self._sync_helper_config = None


  def _LoadFromConfigFile(self):
    self._sync_helper_config = sync_helper_config_pb2.SyncHelperConfig()
    with open(FLAGS.config_path, "r") as fp:
      file_content = fp.read()
      try:
        google.protobuf.text_format.Merge(file_content,
                                          self._sync_helper_config)
      except Exception as e:
        logging.error("Error parsing %s: %s", filename, str(e))


  def _WriteBackHelperConfig(self):
    with open(FLAGS.config_path, "w") as fp:
      pbtxt_out = google.protobuf.text_format.MessageToString(
          self._sync_helper_config)
      fp.write(pbtxt_out)


  def _GetAllManagedNamespaces(self):
    result = []
    for managed_namepsace in self._sync_helper_config.managed_namepsaces:
      result.append(tuple(managed_namepsace.namespace))
    return result


  def Run(self):
    self._LoadFromConfigFile()
    self._RemoveRemovedServices()
    self._CreateNewServices()
    self._UpdateUpdatedServices()


  def _ParseServiceOptionsPb(self, filename):
    pb_constructed = service_options_pb2.ServiceOptions()
    with open(filename, "r") as fp:
      file_content = fp.read()
      try:
        google.protobuf.text_format.Merge(file_content, pb_constructed)
      except Exception as e:
        logging.error("Error parsing %s: %s", filename, str(e))
    return pb_constructed


  def _CreateNewServices(self):
    # Create new services that do not exist in Rorg server but in the base
    # directory.
    list_request = service_manager_rpc_pb2.ListServicesRequest()
    list_response = self._rorg_stub.ListServices(list_request)
    all_existing_services = set([service_id.ServiceId.FromProto(x)
                                 for x in list_response.services])

    need_write_back_helper_config = False
    for managed_service in self._sync_helper_config.managed_services:
      pb = self._ParseServiceOptionsPb(managed_service.configuration_file)

      if not service_id.ServiceId.FromProto(pb.id) in all_existing_services:
        if tuple(pb.id.namespace) not in self._GetAllManagedNamespaces():
          raise ValueError(str(service_id) + " has non-managed namespace.")

        logging.info("Will new service for %s",
                     managed_service.configuration_file)
        create_request = service_manager_rpc_pb2.CreateServiceRequest()
        create_request.options.CopyFrom(pb)
        create_response = self._rorg_stub.CreateService(create_request)
        logging.info("Created new service with response: %s",
                     str(create_response))

        managed_service.ClearField("additional_configuration_hashes")
        for i in range(
            len(managed_service.additional_configuration_directories)):
          config_dir = managed_service.additional_configuration_directories[i]
          checksum_dir = checksumdir.dirhash(config_dir)
          managed_service.additional_configuration_hashes.extend([checksum_dir])

        need_write_back_helper_config = True

    if need_write_back_helper_config:
      self._WriteBackHelperConfig()


  def _RemoveRemovedServices(self):
    # Remove services that are no longer in the base directory.
    # TODO(shengye): ask for confirmation, and use --yes to skip that.
    # TODO(shengye): Add a dryrun flag.
    list_request = service_manager_rpc_pb2.ListServicesRequest()
    list_response = self._rorg_stub.ListServices(list_request)

    removed_services = set([service_id.ServiceId.FromProto(x)
                                 for x in list_response.services])

    for managed_service in self._sync_helper_config.managed_services:
      pb = self._ParseServiceOptionsPb(managed_service.configuration_file)
      if service_id.ServiceId.FromProto(pb.id) in removed_services:
        removed_services.remove(service_id.ServiceId.FromProto(pb.id))

    for removed_service_id in removed_services:
      if tuple(removed_service_id.namespace) in self._GetAllManagedNamespaces():
        remove_request = service_manager_rpc_pb2.RemoveServiceRequest()
        remove_request.id.CopyFrom(removed_service_id.ToProto())
        remove_response = self._rorg_stub.RemoveService(remove_request)
        logging.info("Removed existing service with response: \n%s",
                     str(remove_response))


  def _UpdateUpdatedServices(self):
    # For each service, get its options from the server, if not the same,
    # update the service.
    # TODO(shengye): After the update, write back the latest configuration to
    # the disk.
    # In fact, if we update a service -- and we restart it, it should also lose
    # all of the requests (we do need to track if some one is requesting it)
    # Do this in the server.

    need_write_back_helper_config = False
    for managed_service in self._sync_helper_config.managed_services:
      pb = self._ParseServiceOptionsPb(managed_service.configuration_file)
      if tuple(pb.id.namespace) not in self._GetAllManagedNamespaces():
        raise ValueError(str(pb.id) + " has non-managed namespace.")
      query_request = service_manager_rpc_pb2.QueryServiceRequest()
      query_request.id.CopyFrom(pb.id)
      query_response = self._rorg_stub.QueryService(query_request)

      need_update = False
      # TODO(shengye): Will need a better comparison method.
      if (query_response.service_status.options.SerializeToString()
          != pb.SerializeToString()):
        need_update = True
      else:
        if (len(managed_service.additional_configuration_directories) !=
            len(managed_service.additional_configuration_hashes)):
          need_update = True
        else:
          for i in range(
              len(managed_service.additional_configuration_directories)):
            config_dir = managed_service.additional_configuration_directories[i]
            checksum_dir = checksumdir.dirhash(config_dir)
            if (checksum_dir !=
                  managed_service.additional_configuration_hashes[i]):
              need_update = True


      if need_update:
        update_request = service_manager_rpc_pb2.UpdateServiceRequest()
        update_request.options.CopyFrom(pb)
        update_response = self._rorg_stub.UpdateService(update_request)
        logging.info("Updated existing service with response: \n%s",
                     str(update_response))

        query_response = self._rorg_stub.QueryService(query_request)
        pbtxt_out = google.protobuf.text_format.MessageToString(
            query_response.service_status.options)
        with open(managed_service.configuration_file, "w") as fp:
          fp.write(pbtxt_out)
          logging.info("Wrote back the options from Rorg server to disk: %s",
                       managed_service.configuration_file)

        managed_service.ClearField("additional_configuration_hashes")
        for i in range(
            len(managed_service.additional_configuration_directories)):
          config_dir = managed_service.additional_configuration_directories[i]
          checksum_dir = checksumdir.dirhash(config_dir)
          managed_service.additional_configuration_hashes.extend([checksum_dir])

        need_write_back_helper_config = True

    if need_write_back_helper_config:
      self._WriteBackHelperConfig()


def main(argv):
  FLAGS.verbosity = logging.INFO
  FLAGS(argv)

  helper = RorgSyncScriptHelper()
  helper.Run()


if __name__ == "__main__":
  main(sys.argv)
