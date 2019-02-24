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

class DockerClientInterface(object):
  # Interface of a docker-py client. Returns a DockerContainerInterface
  # instance.

  def GetContainer(self, *args, **kwargs):
    raise NotImplementedError(
        "GetContainer in DockerClientInterface not implemented in {}",
        str(type(self)))


  def CreateContainer(self, *args, **kwargs):
    raise NotImplementedError(
        "Create in DockerClientInterface not implemented in {}",
        str(type(self)))


class DockerContainerInterface(object):
  # Can be a real one (backed by docker-py) or a mocked instance.

  def Start(self, *args, **kwargs):
    raise NotImplementedError(
        "Start in DockerInterface not implemented in {}", str(type(self)))


  def Stop(self, *args, **kwargs):
    raise NotImplementedError(
        "Stop in DockerInterface not implemented in {}", str(type(self)))


  def Restart(self, *args, **kwargs):
    raise NotImplementedError(
        "Restart in DockerInterface not implemented in {}", str(type(self)))


  def Remove(self, *args, **kwargs):
    raise NotImplementedError(
        "Remove in DockerInterface not implemented in {}", str(type(self)))


# TODO(shengye): Maybe add "try-except" wrappers to the derived classes and
# capture the exceptions from docker-py and replace them with our own exceptions
