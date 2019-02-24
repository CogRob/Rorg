load("@pip_deps//:requirements.bzl", "requirement")

package(
  default_visibility = ["//visibility:public"],
)

py_binary(
  name = "service_manager_server_main",
  srcs = [
    "service_manager_server_main.py",
  ],
  deps = [
    requirement("absl-py"),
    requirement("grpcio"),
    requirement("futures"),
    "//cogrob/service_manager/model:service",
    "//cogrob/service_manager/model:service_id",
    "//cogrob/service_manager/model:service_manager",
    "//cogrob/service_manager/model:service_request",
    "//cogrob/service_manager/proto:service_manager_rpc_py_proto",
    "//cogrob/service_manager/proto:service_options_py_proto",
    "//cogrob/service_manager/util:errors",
    "//cogrob/service_manager/util:psutil_helper",
  ]
)
