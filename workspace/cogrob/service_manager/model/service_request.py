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
from cogrob.service_manager.proto import service_request_pb2
import collections


class ServiceRequestId(object):

  @staticmethod
  def FromProto(proto):
    assert isinstance(proto, service_request_pb2.ServiceRequestId), (
        "proto must be a ServiceRequestId")
    return ServiceRequestId(
        srv_id=service_id.ServiceId.FromProto(proto.service_id),
        request_uuid=proto.request_uuid)


  def __init__(self, srv_id, request_uuid):
    assert isinstance(srv_id, service_id.ServiceId), (
        "srv_id must be a ServiceId")
    assert isinstance(request_uuid, basestring), (
        "request_uuid must be a string")
    self._service_id = srv_id
    self._request_uuid = request_uuid


  def ToProto(self):
    result = service_request_pb2.ServiceRequestId(
        service_id=self._service_id.ToProto(), request_uuid=self._request_uuid)
    return result


  @property
  def service_id(self):
    return self._service_id


  @property
  def request_uuid(self):
    return self._request_uuid


  def __hash__(self):
    return hash((self._service_id, self._request_uuid))


  def __eq__(self, other):
    assert isinstance(other, ServiceRequestId), (
        "other must be a ServiceRequestId")
    return ((self._service_id, self._request_uuid)
            == (other._service_id, other._request_uuid))


  def __ne__(self, other):
    return not self == other


  def __str__(self):
    return "{}[{}]".format(self._service_id, self._request_uuid)


class ServiceRequest(object):

  @staticmethod
  def FromProto(proto):
    assert isinstance(proto, service_request_pb2.ServiceRequest), (
        "proto must be a ServiceRequest")

    return ServiceRequest(
        request_id=ServiceRequestId.FromProto(proto.request_id),
        requested_services=tuple(
            map(service_id.ServiceId.FromProto,
                proto.requested_services)))


  def __init__(self, request_id, requested_services):
    assert isinstance(request_id, ServiceRequestId), (
        "request_id must be a ServiceRequestId")
    assert isinstance(requested_services, collections.Iterable), (
        "requested_services must be iterable.")
    for requested_service_id in requested_services:
      assert isinstance(requested_service_id, service_id.ServiceId), (
          "requested_services can only contain ServiceId.")
    self._request_id = request_id
    self._requested_services = tuple(requested_services)


  def ToProto(self):
    result = service_request_pb2.ServiceRequest()
    result.request_id.CopyFrom(self._request_id.ToProto())
    result.requested_services.extend(
        [x.ToProto() for x in self._requested_services])
    return result


  @property
  def request_id(self):
    return self._request_id


  @property
  def requested_services(self):
    return self._requested_services
