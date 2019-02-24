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

from cogrob.service_manager.proto import service_options_pb2
from cogrob.service_manager.util import errors
import collections
import re

ServiceIdPb = service_options_pb2.ServiceId


class ServiceId(object):

  @staticmethod
  def FromProto(proto):
    return ServiceId(namespace=proto.namespace, name=proto.name)

  @staticmethod
  def FromString(id_str):
    id_pattern = r"((?:\w+/)*(?:\w+)):(\w+)$"
    regex_match = re.match(id_pattern, id_str)
    if not regex_match:
      raise errors.InvalidServiceIdError(
          "{} is not a valid service id.".format(id_str))
    namespace = regex_match.group(1).split("/")
    name = regex_match.group(2)
    return ServiceId(namespace, name)


  def __init__(self, namespace, name):
    """Construct from namespace (iterable of string) and a name (string)."""
    assert isinstance(namespace, collections.Iterable), (
        "Namespace must be iterable.")
    assert not isinstance(namespace, basestring), (
        "Namespace cannot be a string, did you forget []?")
    for ns_component in namespace:
      assert isinstance(ns_component, basestring), (
          "Namespace can only contain string: {}".format(str(namespace)))
      # TODO(shengye): we should check namespace is only [a-zA-Z_-]
    assert isinstance(name, basestring), "Name must be a string."

    self._namespace = tuple(namespace)
    self._name = name


  def ToProto(self):
    """Converts to Proto."""
    result = ServiceIdPb(namespace=self._namespace, name=self._name)
    return result


  @property
  def name(self):
    return self._name


  @property
  def namespace(self):
    return self._namespace


  def __hash__(self):
    return hash((self._namespace, self._name))


  def __eq__(self, other):
    return (self._namespace, self._name) == (other._namespace, other._name)


  def __ne__(self, other):
    return not self == other


  def __str__(self):
    return "/".join(self._namespace) + ":" + self._name
