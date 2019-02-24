load("@pip_deps//:requirements.bzl", "requirement")

package(
  default_visibility = ["//visibility:public"],
)

py_library(
  name = "service_id",
  srcs = [
    "service_id.py",
  ],
  deps = [
    "//cogrob/service_manager/proto:service_options_py_proto",
    "//cogrob/service_manager/util:errors",
  ]
)

py_test(
  name = "service_id_test",
  srcs = [
    "service_id_test.py",
  ],
  deps = [
    requirement("absl-py"),
    ":service_id",
    "//cogrob/service_manager/proto:service_options_py_proto",
  ],
)

py_library(
  name = "service_request",
  srcs = [
    "service_request.py",
  ],
  deps = [
    ":service_id",
    "//cogrob/service_manager/proto:service_options_py_proto",
    "//cogrob/service_manager/proto:service_request_py_proto",
  ]
)

py_library(
  name = "service",
  srcs = [
    "base_service.py",
    "meta_service.py",
    "docker_service.py",
    "group_service.py",
  ],
  deps = [
    requirement("absl-py"),
    requirement("backports.ssl_match_hostname"),
    requirement("docker"),
    requirement("docker-pycreds"),
    requirement("ipaddress"),
    requirement("requests"),
    requirement("six"),
    requirement("websocket"),
    requirement("python-dateutil"),
    ":delayed_action",
    ":docker_py",
    ":fake_docker_py",
    ":service_id",
    ":service_request",
    "//cogrob/service_manager/proto:service_state_py_proto",
    "//cogrob/service_manager/proto:service_options_py_proto",
    "//cogrob/service_manager/util:docker_options_pb_to_py",
    "//cogrob/service_manager/util:errors",
  ]
)

py_library(
  name = "service_manager",
  srcs = [
    "service_manager.py",
  ],
  deps = [
    requirement("absl-py"),
    requirement("protobuf"),
    ":service",
    ":service_id",
    ":service_request",
    "//cogrob/service_manager/proto:service_state_py_proto",
    "//cogrob/service_manager/proto:service_options_py_proto",
    "//cogrob/service_manager/util:errors",
  ]
)

py_library(
  name = "docker_py",
  srcs = [
    "docker_py.py",
    "docker_interface.py",
  ],
  deps = [
    requirement("absl-py"),
    requirement("backports.ssl_match_hostname"),
    requirement("docker"),
    requirement("docker-pycreds"),
    requirement("ipaddress"),
    requirement("requests"),
    requirement("six"),
    requirement("websocket"),
  ]
)

py_library(
  name = "fake_docker_py",
  srcs = [
    "fake_docker_py.py",
    "docker_interface.py",
  ],
  deps = [
    requirement("absl-py"),
  ]
)

py_library(
  name = "delayed_action",
  srcs = [
    "delayed_action.py",
  ],
  deps = [
    ":service_id",
  ]
)
