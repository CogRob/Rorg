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

from absl import logging
from cogrob.service_manager.model import docker_interface
import docker

class DockerContainer(docker_interface.DockerContainerInterface):

  def __init__(self, docker_py_container):
    assert docker_py_container is not None
    self._docker_py_container = docker_py_container


  def Start(self, *args, **kwargs):
    return self._docker_py_container.start(*args, **kwargs)


  def Stop(self, *args, **kwargs):
    return self._docker_py_container.stop(*args, **kwargs)


  def Restart(self, *args, **kwargs):
    return self._docker_py_container.restart(*args, **kwargs)


  def Remove(self, *args, **kwargs):
    return self._docker_py_container.remove(*args, **kwargs)


  def Stats(self, *args, **kwargs):
    return self._docker_py_container.stats(*args, **kwargs)


class DockerClient(docker_interface.DockerClientInterface):

  def __init__(self):
    # TODO(shengye): Accepts a docker-py client as an argument.
    self._docker_py_client = docker.from_env()


  def GetContainer(self, *args, **kwargs):
    return DockerContainer(
        self._docker_py_client.containers.get(*args, **kwargs))


  def CreateContainer(self, *args, **kwargs):
    if "image" in kwargs:
      self.TestOrPullImage(kwargs["image"])
    else:
      logging.fatal("Missing image field in CreateContainer")

    return DockerContainer(
        self._docker_py_client.containers.create(*args, **kwargs))


  def TestOrPullImage(self, image_tag, force_pull=True):
    if ":" not in image_tag:
      image_tag += ":latest"

    need_pull = False
    if force_pull:
      need_pull = True
    else:
      try:
        self._docker_py_client.images.get(image_tag)
      except docker.errors.ImageNotFound:
        need_pull = True

    if need_pull:
      logging.info("Start to pull image: %s", image_tag)
      self._docker_py_client.images.pull(image_tag)
      logging.info("Pulled image: %s", image_tag)


def GetGlobalDockerClient():
  if not hasattr(GetGlobalDockerClient, "_inst"):
    GetGlobalDockerClient._inst = DockerClient()
  return GetGlobalDockerClient._inst
