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

from cogrob.service_manager.proto import docker_options_pb2

DockerOptions = docker_options_pb2.DockerOptions

def DockerOptionsPbToDict(pb):

  assert isinstance(pb, DockerOptions)
  result = {}

  if pb.HasField("image"):
    result["image"] = pb.image

  if pb.command.HasField("exec_form"):
    result["command"] = list(pb.command.exec_form.elements)
  elif pb.command.HasField("shell_form"):
    result["command"] = pb.command.shell_form

  if pb.HasField("auto_remove"):
    result["auto_remove"] = pb.auto_remove

  if pb.blkio_weight_device:
    result["blkio_weight_device"] = []
    for blkio_weight_device in pb.blkio_weight_device:
      result["blkio_weight_device"].append(
          {"Path": blkio_weight_device.path,
           "Weight": int(blkio_weight_device.weight)})

  if pb.HasField("blkio_weight"):
    result["blkio_weight"] = int(pb.blkio_weight)

  if pb.cap_add:
    result["cap_add"] = []
    for cap_add in pb.cap_add:
      if cap_add == DockerOptions.CAP_UNKNOWN:
        raise ValueError("cap_add has CAP_UNKNOWN")
      cap_add_new = DockerOptions.Capability.Name(cap_add)
      assert cap_add_new.startswith("CAP_")
      cap_add_new = cap_add_new[len("CAP_"):]
      result["cap_add"].append(cap_add_new)

  if pb.cap_drop:
    result["cap_drop"] = []
    for cap_drop in pb.cap_drop:
      if cap_drop == DockerOptions.CAP_UNKNOWN:
        raise ValueError("cap_drop has CAP_UNKNOWN")
      cap_drop_new = DockerOptions.Capability.Name(cap_drop)
      assert cap_drop_new.startswith("CAP_")
      cap_drop_new = cap_drop_new[len("CAP_"):]
      result["cap_drop"].append(cap_drop_new)

  if pb.HasField("cpu_count"):
    result["cpu_count"] = int(pb.cpu_count)

  if pb.HasField("cpu_percent"):
    result["cpu_percent"] = int(pb.cpu_percent)

  if pb.HasField("cpu_period"):
    result["cpu_period"] = int(pb.cpu_period)

  if pb.HasField("cpu_quota"):
    result["cpu_quota"] = int(pb.cpu_quota)

  if pb.HasField("cpu_shares"):
    result["cpu_shares"] = int(pb.cpu_shares)

  if pb.cpuset_cpus:
    result["cpuset_cpus"] = ",".join(map(str, pb.cpuset_cpus))

  if pb.cpuset_mems:
    result["cpuset_mems"] = ",".join(map(str, pb.cpuset_mems))

  if pb.HasField("detach"):
    result["detach"] = pb.detach

  if pb.device_cgroup_rules:
    result["device_cgroup_rules"] = list(pb.device_cgroup_rules)

  if pb.device_read_bps:
    result["device_read_bps"] = []
    for device_read_bps in pb.device_read_bps:
      result["device_read_bps"].append(
          {"Path": device_read_bps.path,
           "Rate": int(device_read_bps.rate_bps)})

  if pb.device_read_iops:
    result["device_read_iops"] = []
    for device_read_iops in pb.device_read_iops:
      result["device_read_iops"].append(
          {"Path": device_read_iops.path,
           "Rate": int(device_read_iops.rate_iops)})

  if pb.device_write_bps:
    result["device_write_bps"] = []
    for device_write_bps in pb.device_write_bps:
      result["device_write_bps"].append(
          {"Path": device_write_bps.path,
           "Rate": int(device_write_bps.rate_bps)})

  if pb.device_write_iops:
    result["device_write_iops"] = []
    for device_write_iops in pb.device_write_iops:
      result["device_write_iops"].append(
          {"Path": device_write_iops.path,
           "Rate": int(device_write_iops.rate_iops)})

  if pb.devices:
    result["devices"] = []
    for device in pb.devices:
      result["devices"].append("{}:{}:{}".format(device.path_on_host,
                                                 device.path_in_container,
                                                 device.cgroup_permissions))

  if pb.dns:
    result["dns"] = list(pb.dns)

  if pb.dns_opt:
    result["dns_opt"] = list(pb.dns_opt)

  if pb.dns_search:
    result["dns_search"] = list(pb.dns_search)

  if pb.domainname:
    result["domainname"] = list(pb.domainname)

  if pb.entrypoint.HasField("exec_form"):
    result["entrypoint"] = list(pb.entrypoint.exec_form.elements)
  elif pb.entrypoint.HasField("shell_form"):
    result["entrypoint"] = pb.entrypoint.shell_form

  if pb.environment:
    result["environment"] = {k : v for k, v in pb.environment.items()}

  if pb.extra_hosts:
    result["extra_hosts"] = {k : v for k, v in pb.extra_hosts.items()}

  if pb.group_add:
    result["group_add"] = []
    for group_add in pb.group_add:
      if group_add.HasField("name"):
        result["group_add"].append(group_add.name)
      if group_add.HasField("id"):
        result["group_add"].append(int(group_add.id))

  if pb.HasField("healthcheck"):
    result["healthcheck"] = {
        "test": pb.healthcheck.test,
        "interval": int(pb.healthcheck.interval),
        "timeout": int(pb.healthcheck.timeout),
        "retries": int(pb.healthcheck.retries),
        "start_period": int(pb.healthcheck.start_period),
    }

  if pb.HasField("hostname"):
    result["hostname"] = pb.hostname

  if pb.HasField("init"):
    result["init"] = pb.init

  if pb.HasField("init_path"):
    result["init_path"] = pb.init_path

  if pb.HasField("ipc_mode"):
    if pb.ipc_mode.type == DockerOptions.IpcMode.IPC_MODE_NONE:
      result["ipc_mode"] = "none"
    elif pb.ipc_mode.type == DockerOptions.IpcMode.IPC_MODE_PRIVATE:
      result["ipc_mode"] = "private"
    elif pb.ipc_mode.type == DockerOptions.IpcMode.IPC_MODE_SHAREABLE:
      result["ipc_mode"] = "shareable"
    elif pb.ipc_mode.type == DockerOptions.IpcMode.IPC_MODE_HOST:
      result["ipc_mode"] = "host"
    elif pb.ipc_mode.type == DockerOptions.IpcMode.IPC_MODE_CONTAINER:
      result["ipc_mode"] = "container:{}".format(pb.ipc_mode.join_container)

  if pb.isolation != DockerOptions.ISOLATION_DEFAULT:
    if pb.isolation == DockerOptions.ISOLATION_PROCESS:
      result["isolation"] = "process"
    elif pb.isolation == DockerOptions.ISOLATION_HYPERV:
      result["isolation"] = "hyperv"

  if pb.labels:
    result["labels"] = {k : v for k, v in pb.labels.items()}

  if pb.links:
    result["links"] = {k : v for k, v in pb.links.items()}

  if pb.HasField("log_config"):
    result["log_config"] = {
        "type": pb.log_config.type,
        "config": {k : v for k, v in pb.log_config.config.items()},
    }

  if pb.HasField("mac_address"):
    result["mac_address"] = pb.mac_address

  if pb.HasField("mem_limit"):
    result["mem_limit"] = int(pb.mem_limit)

  if pb.HasField("mem_swappiness"):
    result["mem_swappiness"] = int(pb.mem_swappiness)

  if pb.HasField("memswap_limit"):
    result["memswap_limit"] = int(pb.memswap_limit)

  if pb.mounts:
    result["mounts"] = []
    for mount in pb.mounts:
      new_mount = {}
      new_mount["target"] = mount.target

      new_mount["source"] = mount.source

      if mount.type == DockerOptions.Mount.MOUNT_TYPE_BIND:
        new_mount["type"] = "bind"
      elif mount.type == DockerOptions.Mount.MOUNT_TYPE_VOLUME:
        new_mount["type"] = "volume"
      elif mount.type == DockerOptions.Mount.MOUNT_TYPE_TMPFS:
        new_mount["type"] = "tmpfs"
      elif mount.type == DockerOptions.Mount.MOUNT_TYPE_NPIPE:
        new_mount["type"] = "npipe"

      if mount.HasField("read_only"):
        new_mount["read_only"] = mount.read_only

      if (mount.consistency
          == DockerOptions.Mount.MOUNT_CONSISTENCY_CONSISTENT):
        new_mount["consistency"] = "consistent"
      elif (mount.consistency ==
            DockerOptions.Mount.MOUNT_CONSISTENCY_CACHED):
        new_mount["consistency"] = "cached"
      elif (mount.consistency ==
            DockerOptions.Mount.MOUNT_CONSISTENCY_DELEGATED):
        new_mount["consistency"] = "delegated"

      if mount.propagation == DockerOptions.Mount.MOUNT_PROPAGATION_PRIVATE:
        new_mount["propagation"] = "private"
      elif mount.propagation == DockerOptions.Mount.MOUNT_PROPAGATION_SHARED:
        new_mount["propagation"] = "shared"
      elif mount.propagation == DockerOptions.Mount.MOUNT_PROPAGATION_SLAVE:
        new_mount["propagation"] = "slave"
      elif (mount.propagation
            == DockerOptions.Mount.MOUNT_PROPAGATION_RPRIVATE):
        new_mount["propagation"] = "rprivate"
      elif (mount.propagation
            == DockerOptions.Mount.MOUNT_PROPAGATION_RSHARED):
        new_mount["propagation"] = "rshared"
      elif mount.propagation == DockerOptions.Mount.MOUNT_PROPAGATION_RSLAVE:
        new_mount["propagation"] = "rslave"

      if mount.HasField("no_copy"):
        new_mount["no_copy"] = mount.no_copy

      if mount.labels:
        new_mount["labels"] = {k : v for k, v in mount.labels.items()}

      if mount.HasField("driver_config"):
        new_mount["driver_config"] = {"name": mount.driver_config.name}
        if mount.driver_config.options:
          new_mount["driver_config"]["options"] = {
              k : v for k, v in mount.driver_config.options.items()}

      if mount.HasField("tmpfs_size"):
        new_mount["tmpfs_size"] = int(mount.tmpfs_size)

      if mount.HasField("tmpfs_mode"):
        new_mount["tmpfs_mode"] = int(mount.tmpfs_mode)

      result["mounts"].append(new_mount)

  if pb.HasField("name"):
    result["name"] = pb.name

  if pb.HasField("nano_cpus"):
    result["nano_cpus"] = int(pb.nano_cpus)

  if pb.HasField("network"):
    result["network"] = pb.network

  if pb.HasField("network_disabled"):
    result["network_disabled"] = pb.network_disabled

  if pb.HasField("network_mode"):
    if (pb.network_mode.type
        == DockerOptions.NetworkMode.NETWORK_MODE_BRIDGE):
      result["network_mode"] = "bridge"
    elif (pb.network_mode.type
          == DockerOptions.NetworkMode.NETWORK_MODE_NONE):
      result["network_mode"] = "none"
    elif (pb.network_mode.type
          == DockerOptions.NetworkMode.NETWORK_MODE_HOST):
      result["network_mode"] = "host"
    elif (pb.network_mode.type
          == DockerOptions.NetworkMode.NETWORK_MODE_CONTAINER):
      result["network_mode"] = "container:{}".format(
          pb.network_mode.join_container)

  if pb.HasField("oom_kill_disable"):
    result["oom_kill_disable"] = pb.oom_kill_disable

  if pb.HasField("oom_score_adj"):
    result["oom_score_adj"] = int(pb.oom_score_adj)

  if pb.HasField("pid_mode"):
    if pb.pid_mode.type == DockerOptions.PidMode.PID_MODE_HOST:
      result["pid_mode"] = "host"
    elif pb.pid_mode.type == DockerOptions.PidMode.PID_MODE_CONTAINER:
      result["pid_mode"] = "container:{}".format(pb.pid_mode.join_container)

  if pb.HasField("pids_limit"):
    result["pids_limit"] = int(pb.pids_limit)

  if pb.HasField("platform"):
    result["platform"] = pb.platform

  if pb.ports:
    result["ports"] = {}
    for port in pb.ports:
      if port.protocol == DockerOptions.Port.PORT_PROTOCOL_TCP:
        key = "{}/tcp".format(port.container_port)
      elif port.protocol == DockerOptions.Port.PORT_PROTOCOL_UDP:
        key = "{}/udp".format(port.container_port)
      else:
        key = int(port.container_port)

      if port.HasField("single_host_port"):
        value = int(port.single_host_port)
      elif port.HasField("any_host_port"):
        if not port.any_host_port:
          raise ValueError("any_host_port is set, but not set to true.")
        value = None
      elif port.HasField("host_interface_and_port"):
        value = (port.host_interface_and_port.interface_address,
                 port.host_interface_and_port.port)
      elif port.HasField("multiple_host_ports"):
        value = map(int, port.multiple_host_ports.ports)
      result["ports"][key] = value

  if pb.HasField("privileged"):
    result["privileged"] = pb.privileged

  if pb.HasField("publish_all_ports"):
    result["publish_all_ports"] = pb.publish_all_ports

  if pb.HasField("read_only"):
    result["read_only"] = pb.read_only

  if pb.HasField("remove"):
    result["remove"] = pb.remove

  if pb.HasField("restart_policy"):
    result["restart_policy"] = {
        "MaximumRetryCount": int(pb.restart_policy.maximum_retry_count)}
    if (pb.restart_policy.type ==
        DockerOptions.RestartPolicy.RESTART_POLICY_ALWAYS):
      result["restart_policy"]["Name"] = "always"
    elif (pb.restart_policy.type ==
          DockerOptions.RestartPolicy.RESTART_POLICY_ON_FAILURE):
      result["restart_policy"]["Name"] = "on-failure"

  if pb.security_opt:
    result["security_opt"] = list(pb.security_opt)

  if pb.HasField("shm_size"):
    result["shm_size"] = int(pb.shm_size)

  if pb.HasField("stdin_open"):
    result["stdin_open"] = pb.stdin_open

  if pb.HasField("stdout"):
    result["stdout"] = pb.stdout

  if pb.HasField("stderr"):
    result["stderr"] = pb.stderr

  if pb.stop_signal != DockerOptions.STOP_SIG_DEFAULT:
    stop_signal_name = DockerOptions.StopSignal.Name(pb.stop_signal)
    assert stop_signal_name.startswith("STOP_")
    result["stop_signal"] = stop_signal_name[len("STOP_"):]

  if pb.storage_opt:
    result["storage_opt"] = {k : v for k, v in pb.storage_opt.items()}

  if pb.HasField("stream"):
    result["stream"] = pb.stream

  if pb.sysctls:
    result["sysctls"] = {k : v for k, v in pb.sysctls.items()}

  if pb.tmpfs:
    result["tmpfs"] = {k : v for k, v in pb.tmpfs.items()}

  if pb.HasField("tty"):
    result["tty"] = pb.tty

  if pb.ulimits:
    result["ulimits"] = []
    for ulimit in pb.ulimits:
      new_ulimit = {"Name" : ulimit.name}
      if ulimit.HasField("soft"):
        new_ulimit["Soft"] = int(ulimit.soft)
      if ulimit.HasField("hard"):
        new_ulimit["Hard"] = int(ulimit.hard)
      result["ulimits"].append(new_ulimit)

  if pb.HasField("user"):
    if pb.user.HasField("name"):
      result["user"] = pb.user.name
    if pb.user.HasField("id"):
      result["user"] = pb.user.id

  if pb.HasField("userns_mode"):
    if pb.userns_mode.type == DockerOptions.UserNsMode.USER_NS_MODE_HOST:
      result["userns_mode"] = "host"

  if pb.HasField("volume_driver"):
    result["volume_driver"] = pb.volume_driver

  if pb.volumes:
    result["volumes"] = {}
    for volume in pb.volumes:
      new_volume = {}
      if not volume.container_path:
        raise ValueError("Volume does not have a container path set.")

      new_volume["bind"] = volume.container_path

      # Current default will has no mode field,
      # docker container will be configured as 'rw'.
      if volume.mode == DockerOptions.Volume.VOLUME_MODE_READ_ONLY:
        new_volume["mode"] = "ro"
      elif volume.mode == DockerOptions.Volume.VOLUME_MODE_READ_WRITE:
        new_volume["mode"] = "rw"
      else:
        raise ValueError(
            "Volume '{}' does not have a access mode set.".format(
            volume.container_path))

      if volume.HasField("host_path"):
        result["volumes"][volume.host_path] = new_volume
      elif volume.HasField("volume_name"):
        result["volumes"][volume.volume_name] = new_volume
      else:
        raise ValueError(
            "Volume '{}' has neither host_path nor volume_name.".format(
            volume.container_path))


  if pb.volumes_from:
    result["volumes_from"] = list(pb.volumes_from)

  if pb.HasField("working_dir"):
    result["working_dir"] = pb.working_dir

  if pb.HasField("runtime"):
    result["runtime"] = pb.runtime

  return result
