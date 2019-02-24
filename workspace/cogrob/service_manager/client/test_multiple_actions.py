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
import docker
import google.protobuf.text_format
import grpc
import sys

FLAGS = flags.FLAGS
flags.DEFINE_string("service_manager_grpc_server", "localhost:7016",
                    "gRPC server address for service manager.")
flags.DEFINE_string(
    "roscore_options_pbtxt",
    "cogrob/service_manager/client/example_service/roscore.pbtxt",
    "Options to create the roscore service.")
flags.DEFINE_string(
    "ros_trigger_ui_options_pbtxt",
    "cogrob/service_manager/client/example_service/ros_trigger_ui.pbtxt",
    "Options to create the roscore service.")
flags.DEFINE_string(
    "docker_container_name_prefix", "rorg__",
    "Name prefix for docker containers.")
flags.DEFINE_bool(
    "docker_rm_before_start", False,
    "Whether to remove containers before start.")


def ServiceIdToContainerName(srv_id):
  return (FLAGS.docker_container_name_prefix +
          "__".join(srv_id.namespace) + "_" + srv_id.name)


def ReadServiceOptions(file_path):
  with open(file_path, "r") as fp:
    pbtxt = fp.read()
    pb_service_options = service_options_pb2.ServiceOptions()
    google.protobuf.text_format.Merge(pbtxt, pb_service_options)
    return pb_service_options


def RemoveExistingDockerContainerById(srv_id):
  assert isinstance(srv_id, service_options_pb2.ServiceId)
  container_name = ServiceIdToContainerName(srv_id)

  docker_py_client = docker.from_env()
  try:
    container = docker_py_client.containers.get(container_name)
  except Exception as e:
    # TODO(shengye): Only filter certain exceptions.
    return
  container.remove(force=True)


def RorgCreateService(stub, pb_service_options):
  create_request = service_manager_rpc_pb2.CreateServiceRequest()
  create_request.options.CopyFrom(pb_service_options)
  logging.info("CreateService Request to send: \n%s", str(create_request))
  create_response = stub.CreateService(create_request)
  logging.info("CreateService Response: \n%s", str(create_response))


def RorgQueryService(stub, srv_id):
  query_request = service_manager_rpc_pb2.QueryServiceRequest()
  query_request.id.CopyFrom(srv_id)
  logging.info("QueryService Request to send: \n%s", str(query_request))
  query_response = stub.QueryService(query_request)
  logging.info("QueryService Response: \n%s", str(query_response))


def RorgRemoveService(stub, srv_id):
  remove_request = service_manager_rpc_pb2.RemoveServiceRequest()
  remove_request.id.CopyFrom(srv_id)
  logging.info("RemoveService Request to send: \n%s", str(remove_request))
  remove_response = stub.RemoveService(remove_request)
  logging.info("RemoveService Response: \n%s", str(remove_response))


def RorgRequestService(stub, srv_id, srv_id_requestor=None, request_uuid=None):
  if srv_id_requestor is None:
    srv_id_requestor = service_id.ServiceId.FromString(
        "__builtin:__operator").ToProto()
  if request_uuid is None:
    request_uuid = str(srv_id)

  request_request = service_manager_rpc_pb2.RequestServiceRequest()
  request_request.request.request_id.service_id.CopyFrom(srv_id_requestor)
  request_request.request.request_id.request_uuid = request_uuid
  request_request.request.requested_services.extend([srv_id])
  logging.info("RequestService Request to send: \n%s", str(request_request))
  request_response = stub.RequestService(request_request)
  logging.info("RequestService Response: \n%s", str(request_response))


def RorgReleaseService(
    stub, srv_id_releasor=None, request_uuid=None, srv_id=None):
  if srv_id_releasor is None:
    srv_id_releasor = service_id.ServiceId.FromString(
        "__builtin:__operator").ToProto()
  if request_uuid is None:
    if srv_id is not None:
      request_uuid = str(srv_id)
    else:
      raise ValueError("request uuid and srv id are both None.")

  release_request = service_manager_rpc_pb2.ReleaseServiceRequest()
  release_request.request_id.service_id.CopyFrom(srv_id_releasor)
  release_request.request_id.request_uuid = request_uuid
  logging.info("ReleaseService Request to send: \n%s", str(release_request))
  release_response = stub.ReleaseService(release_request)
  logging.info("ReleaseService Response: \n%s", str(release_response))


def main(argv):
  FLAGS.verbosity = logging.INFO
  FLAGS(argv)

  with grpc.insecure_channel(FLAGS.service_manager_grpc_server) as channel:
    stub = service_manager_rpc_pb2_grpc.ServiceManagerStub(channel)

    roscore_options = ReadServiceOptions(FLAGS.roscore_options_pbtxt)
    ros_trigger_ui_options = ReadServiceOptions(
        FLAGS.ros_trigger_ui_options_pbtxt)

    if FLAGS.docker_rm_before_start:
      RemoveExistingDockerContainerById(roscore_options.id)
      RemoveExistingDockerContainerById(ros_trigger_ui_options.id)

    RorgCreateService(stub, roscore_options)
    RorgCreateService(stub, ros_trigger_ui_options)

    RorgQueryService(stub, roscore_options.id)
    RorgQueryService(stub, ros_trigger_ui_options.id)

    RorgRequestService(stub, srv_id=ros_trigger_ui_options.id)

    RorgQueryService(stub, roscore_options.id)
    RorgQueryService(stub, ros_trigger_ui_options.id)


if __name__ == "__main__":
  main(sys.argv)
