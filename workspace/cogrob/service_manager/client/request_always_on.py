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
import google.protobuf.text_format
import grpc
import sys

FLAGS = flags.FLAGS
flags.DEFINE_string("service_manager_grpc_server", "localhost:7016",
                    "gRPC server address for service manager.")
flags.DEFINE_string(
    "request_pbtxt_path",
    "/home/common/mission_control_fetch33/always_on_request.pbtxt",
    "File path of the request.")


def main(argv):
  FLAGS.verbosity = logging.INFO
  FLAGS(argv)

  with grpc.insecure_channel(FLAGS.service_manager_grpc_server) as channel:
    stub = service_manager_rpc_pb2_grpc.ServiceManagerStub(channel)

    request_request = service_manager_rpc_pb2.RequestServiceRequest()
    with open(FLAGS.request_pbtxt_path, "r") as fp:
      pbtxt_content = fp.read()
      google.protobuf.text_format.Merge(pbtxt_content, request_request)

    logging.info("Request to send: \n%s", str(request_request))
    request_response = stub.RequestService(request_request)
    logging.info("Response: \n%s", str(request_response))


if __name__ == "__main__":
  main(sys.argv)
