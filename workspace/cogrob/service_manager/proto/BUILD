load("@org_pubref_rules_protobuf//cpp:rules.bzl", "cc_proto_library")
load("@org_pubref_rules_protobuf//python:rules.bzl", "py_proto_compile")
load("@pip_deps//:requirements.bzl", "requirement")

package(
  default_visibility = ["//visibility:public"],
)

cc_proto_library(
  name = "result_code_cc_proto",
  protos = ["result_code.proto"],
)

py_proto_compile(
  name = "result_code_py_proto_only",
  protos = ["result_code.proto"],
)

py_library(
  name = "result_code_py_proto",
  srcs = ["result_code_py_proto_only"],
  deps = [
    "//third_party:python_protobuf"
  ],
)

cc_proto_library(
  name = "docker_options_cc_proto",
  protos = ["docker_options.proto"],
)

py_proto_compile(
  name = "docker_options_py_proto_only",
  protos = ["docker_options.proto"],
)

py_library(
  name = "docker_options_py_proto",
  srcs = ["docker_options_py_proto_only"],
  deps = [
    "//third_party:python_protobuf"
  ],
)

cc_proto_library(
  name = "service_options_cc_proto",
  protos = ["service_options.proto"],
  proto_deps = [
    ":docker_options_cc_proto",
  ],
)

py_proto_compile(
  name = "service_options_py_proto_only",
  protos = ["service_options.proto"],
  deps = [
    ":docker_options_py_proto_only",
  ],
)

py_library(
  name = "service_options_py_proto",
  srcs = ["service_options_py_proto_only"],
  deps = [
    ":docker_options_py_proto",
    "//third_party:python_protobuf"
  ],
)

cc_proto_library(
  name = "service_state_cc_proto",
  protos = ["service_state.proto"],
  proto_deps = [
    ":service_options_cc_proto",
    ":service_request_cc_proto",
  ],
)

py_proto_compile(
  name = "service_state_py_proto_only",
  protos = ["service_state.proto"],
  deps = [
    ":service_options_py_proto_only",
    ":service_request_py_proto_only",
  ],
)

py_library(
  name = "service_state_py_proto",
  srcs = ["service_state_py_proto_only"],
  deps = [
    ":service_options_py_proto",
    ":service_request_py_proto",
    "//third_party:python_protobuf"
  ],
)

cc_proto_library(
  name = "service_request_cc_proto",
  protos = ["service_request.proto"],
  proto_deps = [
    ":service_options_cc_proto",
  ],
)

py_proto_compile(
  name = "service_request_py_proto_only",
  protos = ["service_request.proto"],
  deps = [
    ":service_options_py_proto_only",
  ],
)

py_library(
  name = "service_request_py_proto",
  srcs = ["service_request_py_proto_only"],
  deps = [
    ":service_options_py_proto",
    "//third_party:python_protobuf"
  ],
)

cc_proto_library(
  name = "service_manager_rpc_cc_proto",
  protos = ["service_manager_rpc.proto"],
  proto_deps = [
    ":delayed_action_cc_proto",
    ":result_code_cc_proto",
    ":service_options_cc_proto",
    ":service_request_cc_proto",
    ":service_state_cc_proto",
  ],
  with_grpc = True,
)

py_proto_compile(
  name = "service_manager_rpc_py_proto_only",
  protos = ["service_manager_rpc.proto"],
  deps = [
    ":delayed_action_py_proto_only",
    ":result_code_py_proto_only",
    ":service_options_py_proto_only",
    ":service_request_py_proto_only",
    ":service_state_py_proto_only",
  ],
  with_grpc = True,
)

py_library(
  name = "service_manager_rpc_py_proto",
  srcs = ["service_manager_rpc_py_proto_only"],
  deps = [
    ":delayed_action_py_proto",
    ":result_code_py_proto",
    ":service_options_py_proto",
    ":service_request_py_proto",
    ":service_state_py_proto",
    "//third_party:python_grpc"
  ],
)

cc_proto_library(
  name = "simulation_cc_proto",
  protos = ["simulation.proto"],
  proto_deps = [
    ":service_manager_rpc_cc_proto",
    ":service_options_cc_proto",
  ],
)

py_proto_compile(
  name = "simulation_py_proto_only",
  protos = ["simulation.proto"],
  deps = [
    ":service_manager_rpc_py_proto_only",
    ":service_options_py_proto_only",
  ],
)

py_library(
  name = "simulation_py_proto",
  srcs = [":simulation_py_proto_only"],
  deps = [
    ":service_manager_rpc_py_proto",
    ":service_options_py_proto",
    "//third_party:python_protobuf"
  ],
)

cc_proto_library(
  name = "delayed_action_cc_proto",
  protos = ["delayed_action.proto"],
  proto_deps = [
    ":service_options_cc_proto",
    "//util/proto:timestamp_cc_proto",
  ],
)

py_proto_compile(
  name = "delayed_action_py_proto_only",
  protos = ["delayed_action.proto"],
  deps = [
    ":service_options_py_proto_only",
    "//util/proto:timestamp_py_proto_only",
  ],
)

py_library(
  name = "delayed_action_py_proto",
  srcs = [":delayed_action_py_proto_only"],
  deps = [
    ":service_options_py_proto",
    "//util/proto:timestamp_py_proto",
    "//third_party:python_protobuf"
  ],
)

cc_proto_library(
  name = "sync_helper_config_cc_proto",
  protos = ["sync_helper_config.proto"],
)

py_proto_compile(
  name = "sync_helper_config_py_proto_only",
  protos = ["sync_helper_config.proto"],
)

py_library(
  name = "sync_helper_config_py_proto",
  srcs = [":sync_helper_config_py_proto_only"],
  deps = [
    "//third_party:python_protobuf"
  ],
)
