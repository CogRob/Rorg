load("@pip_deps//:requirements.bzl", "requirement")

package(
  default_visibility = ["//visibility:public"],
)

py_binary(
  name = "create",
  srcs = [
    "create.py",
  ],
  deps = [
    requirement("absl-py"),
    requirement("grpcio"),
    "//cogrob/service_manager/proto:service_manager_rpc_py_proto",
    "//cogrob/service_manager/proto:service_options_py_proto",
    "//cogrob/service_manager/util:errors",
  ],
  data = [
    "//cogrob/service_manager/client:example_service",
  ],
)

py_binary(
  name = "query",
  srcs = [
    "query.py",
  ],
  deps = [
    requirement("absl-py"),
    requirement("grpcio"),
    "//cogrob/service_manager/model:service_id",
    "//cogrob/service_manager/proto:service_manager_rpc_py_proto",
    "//cogrob/service_manager/proto:service_options_py_proto",
    "//cogrob/service_manager/util:errors",
  ],
)


py_binary(
  name = "remove",
  srcs = [
    "remove.py",
  ],
  deps = [
    requirement("absl-py"),
    requirement("grpcio"),
    "//cogrob/service_manager/model:service_id",
    "//cogrob/service_manager/proto:service_manager_rpc_py_proto",
    "//cogrob/service_manager/proto:service_options_py_proto",
    "//cogrob/service_manager/util:errors",
  ],
)

py_binary(
  name = "request",
  srcs = [
    "request.py",
  ],
  deps = [
    requirement("absl-py"),
    requirement("grpcio"),
    "//cogrob/service_manager/model:service_id",
    "//cogrob/service_manager/proto:service_manager_rpc_py_proto",
    "//cogrob/service_manager/proto:service_options_py_proto",
    "//cogrob/service_manager/util:errors",
  ],
)

py_binary(
  name = "release",
  srcs = [
    "release.py",
  ],
  deps = [
    requirement("absl-py"),
    requirement("grpcio"),
    "//cogrob/service_manager/model:service_id",
    "//cogrob/service_manager/proto:service_manager_rpc_py_proto",
    "//cogrob/service_manager/proto:service_options_py_proto",
    "//cogrob/service_manager/util:errors",
  ],
)

py_binary(
  name = "test_multiple_actions",
  srcs = [
    "test_multiple_actions.py",
  ],
  deps = [
    requirement("absl-py"),
    requirement("grpcio"),
    "//cogrob/service_manager/model:docker_py",
    "//cogrob/service_manager/model:service_id",
    "//cogrob/service_manager/proto:service_manager_rpc_py_proto",
    "//cogrob/service_manager/proto:service_options_py_proto",
    "//cogrob/service_manager/util:errors",
  ],
  data = [
    "//cogrob/service_manager/client:example_service",
  ],
)

py_binary(
  name = "sync_with_rorg_server",
  srcs = [
    "sync_with_rorg_server.py",
  ],
  deps = [
    "//cogrob/service_manager/model:service_id",
    "//cogrob/service_manager/proto:service_manager_rpc_py_proto",
    "//cogrob/service_manager/proto:service_options_py_proto",
    "//cogrob/service_manager/proto:sync_helper_config_py_proto",
    "//third_party:python_absl",
    "//third_party:python_checksumdir",
    "//third_party:python_protobuf",
  ]
)

py_binary(
  name = "request_always_on",
  srcs = [
    "request_always_on.py",
  ],
  deps = [
    "//third_party:python_absl",
    "//third_party:python_grpc",
    "//third_party:python_protobuf",
    "//cogrob/service_manager/model:service_id",
    "//cogrob/service_manager/proto:service_manager_rpc_py_proto",
    "//cogrob/service_manager/proto:service_options_py_proto",
    "//cogrob/service_manager/util:errors",
  ],
)

py_binary(
  name = "release_always_on",
  srcs = [
    "release_always_on.py",
  ],
  deps = [
    "//third_party:python_absl",
    "//third_party:python_grpc",
    "//third_party:python_protobuf",
    "//cogrob/service_manager/model:service_id",
    "//cogrob/service_manager/proto:service_manager_rpc_py_proto",
    "//cogrob/service_manager/proto:service_options_py_proto",
    "//cogrob/service_manager/util:errors",
  ],
)
