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

from cogrob.service_manager.proto import result_code_pb2

class ServiceManagerError(Exception):
  def __init__(self, message, result_code=result_code_pb2.RESULT_UNKNOWN):
    super(ServiceManagerError, self).__init__(message)
    self._result_code = result_code


  def GetResultCode(self):
    return self._result_code


class ServiceNotFoundError(ServiceManagerError):
  def __init__(self, message="Service not found."):
    super(ServiceNotFoundError, self).__init__(
        message, result_code_pb2.RESULT_SERVICE_NOT_FOUND)


class ServiceAlreadyExistError(ServiceManagerError):
  def __init__(self, message="Service already exist."):
    super(ServiceAlreadyExistError, self).__init__(
        message, result_code_pb2.RESULT_SERVICE_ALREADY_EXIST)


class ServiceTypeNotSupportedError(ServiceManagerError):
  def __init__(self, message="Service type is not supported."):
    super(ServiceTypeNotSupportedError, self).__init__(
        message, result_code_pb2.RESULT_SERVICE_TYPE_NOT_SUPPORTED)


class ServiceUnsupportedOptionsError(ServiceManagerError):
  def __init__(self, message="Service option is not supported."):
    super(ServiceUnsupportedOptionsError, self).__init__(
        message, result_code_pb2.RESULT_SERVICE_UNSUPPORTED_OPTIONS)


class InternalError(ServiceManagerError):
  def __init__(self, message="Internal error."):
    super(InternalError, self).__init__(
        message, result_code_pb2.RESULT_INTERNAL)


class ServiceRequestNotExistError(ServiceManagerError):
  def __init__(self, message="Service request not exist."):
    super(ServiceRequestNotExistError, self).__init__(
        message, result_code_pb2.RESULT_SERVICE_REQUEST_NOT_EXIST)


class InvalidServiceIdError(ServiceManagerError):
  def __init__(self, message="Invalid service id."):
    super(InvalidServiceIdError, self).__init__(
        message, result_code_pb2.RESULT_INVALID_SERVICE_ID)


class ServiceNotActiveError(ServiceManagerError):
  def __init__(self, message="Service not active."):
    super(ServiceNotActiveError, self).__init__(
        message, result_code_pb2.RESULT_SERVICE_NOT_ACTIVE)
