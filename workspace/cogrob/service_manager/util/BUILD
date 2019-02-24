load("@pip_deps//:requirements.bzl", "requirement")

package(
  default_visibility = ["//visibility:public"],
)

py_library(
  name = "docker_options_pb_to_py",
  srcs = [
    "docker_options_pb_to_py.py",
  ],
  deps = [
    "//cogrob/service_manager/proto:docker_options_py_proto",
  ]
)

py_test(
  name = "docker_options_pb_to_py_test",
  srcs = [
    "docker_options_pb_to_py_test.py",
  ],
  deps = [
    requirement("absl-py"),
    requirement("protobuf"),
    ":docker_options_pb_to_py",
    "//cogrob/service_manager/proto:docker_options_py_proto",
  ],
  data = [
    "//cogrob/service_manager/util:testdata",
  ],
)

py_library(
  name = "errors",
  srcs = [
    "errors.py",
  ],
  deps = [
    "//cogrob/service_manager/proto:result_code_py_proto",
  ]
)

py_library(
  name = "psutil_helper",
  srcs = [
    "psutil_helper.py",
  ],
  deps = [
    requirement("psutil"),
  ]
)

py_test(
  name = "errors_test",
  srcs = [
    "errors_test.py",
  ],
  deps = [
    requirement("absl-py"),
    ":errors",
    "//cogrob/service_manager/proto:result_code_py_proto",
  ],
)

py_test(
  name = "psutil_helper_test",
  srcs = [
    "psutil_helper_test.py",
  ],
  deps = [
    ":psutil_helper",
  ]
)
