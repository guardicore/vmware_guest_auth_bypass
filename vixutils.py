import time
import shlex
from collections import defaultdict
import logging
from enum import IntEnum  # USE enum34 PACKAGE FOR THIS
import ctypes
import vixlib


class OperatingSystem(IntEnum):
    Unknown = 0
    Windows = 1
    Linux = 2
    HTTP = 3
    SMBLure = 4


OperatingSystemStringToEnum = defaultdict(lambda: OperatingSystem.Unknown)
OperatingSystemStringToEnum["windows"] = OperatingSystem.Windows
OperatingSystemStringToEnum["linux"] = OperatingSystem.Linux


class VixException(object):
    def __init__(self, msg, err_code, *args):
        msg = ("[%d] " % (err_code,)) + msg
        # super(VixException, self).__init__(msg, *args)

        self.err_code = err_code


VIX_VMWARE_WORKSTATION = vixlib.VIX_SERVICEPROVIDER_VMWARE_WORKSTATION
VIX_VMWARE_PLAYER = vixlib.VIX_SERVICEPROVIDER_VMWARE_PLAYER

SUPPORTS_NESTED_VIRT_VMX = 1
SUPPORTS_NESTED_VIRT_EPT = 2

NETWORK_NAT = "__nat__"
NETWORK_HOST_ONLY = "__host_only__"


def get_vix_host_type():
    return vixlib.VIX_SERVICEPROVIDER_DEFAULT


def _check_job_err_code(err):
    if err:
        msg = vixlib.Vix_GetErrorText(err, None)
        raise Exception(msg + str(err))


_host_type = None


class VixVM(object):
    def __init__(self, vm_handle):
        self._vm_handle = vm_handle
        self._vmx_path = None
        self._vmtools_waited = False
        self._vm_name = None
        self._guest_os_str = None
        self._guest_os = None

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        if self._vm_handle:
            vixlib.Vix_ReleaseHandle(self._vm_handle)
            self._vm_handle = None

    @property
    def name(self):
        if not self._vm_name:
            vm_name = ctypes.c_char_p()
            err = vixlib.Vix_GetProperties(self._vm_handle,
                                           vixlib.VIX_PROPERTY_VM_NAME,
                                           ctypes.byref(vm_name),
                                           vixlib.VIX_PROPERTY_NONE)
            _check_job_err_code(err)

            self._vm_name = vm_name.value
            vixlib.Vix_FreeBuffer(vm_name)

        return self._vm_name

    @property
    def guest_os_str(self):
        if self._guest_os_str is None:
            guest_os = ctypes.c_char_p()
            err = vixlib.Vix_GetProperties(self._vm_handle,
                                           vixlib.VIX_PROPERTY_VM_GUESTOS,
                                           ctypes.byref(guest_os),
                                           vixlib.VIX_PROPERTY_NONE)
            _check_job_err_code(err)
            self._guest_os_str = guest_os.value
            vixlib.Vix_FreeBuffer(guest_os)

        return self._guest_os_str

    @property
    def guest_os(self):
        if self._guest_os is None:
            os_str = self.guest_os_str

            if os_str in ["ubuntu64Guest", "ubuntu32Guest",
                          "centos32Guest", "centos64Guest",
                          "sles11_64Guest", "sles11_32Guest",
                          "otherLinux64Guest", "otherLinux32Guest"]:
                self._guest_os = OperatingSystem.Linux
            elif os_str in ["winNetEnterpriseGuest",
                            "windows7_64Guest", "windows7_32Guest",
                            "windows7Server64Guest", "windows7Server32Guest",
                            "windows8_64Guest", "windows8_32Guest",
                            "windows8Server64Guest", "windows8Server32Guest",
                            "windows10_64Guest", "windows10_32Guest",
                            "windows10Server64Guest", "windows10Server32Guest"]:
                self._guest_os = OperatingSystem.Windows
            elif os_str in ["otherGuest", "otherGuest64"]:
                self._guest_os = OperatingSystem.Unknown
            else:
                self._guest_os = OperatingSystem.Unknown

            if OperatingSystem.Unknown == self._guest_os:
                logging.warning("Unknown OS version '%s' for VM '%s'", os_str, self.name)

        return self._guest_os

    @property
    def is_running(self):
        is_running = ctypes.c_int()
        err = vixlib.Vix_GetProperties(self._vm_handle,
                                       vixlib.VIX_PROPERTY_VM_IS_RUNNING,
                                       ctypes.byref(is_running),
                                       vixlib.VIX_PROPERTY_NONE)
        _check_job_err_code(err)
        return bool(is_running.value)

    @property
    def power_state(self):
        power_state = ctypes.c_int()
        err = vixlib.Vix_GetProperties(self._vm_handle,
                                       vixlib.VIX_PROPERTY_VM_POWER_STATE,
                                       ctypes.byref(power_state),
                                       vixlib.VIX_PROPERTY_NONE)
        _check_job_err_code(err)
        return power_state.value

    @property
    def tools_state(self):
        tools_state = ctypes.c_int()
        err = vixlib.Vix_GetProperties(self._vm_handle,
                                       vixlib.VIX_PROPERTY_VM_TOOLS_STATE,
                                       ctypes.byref(tools_state),
                                       vixlib.VIX_PROPERTY_NONE)
        _check_job_err_code(err)
        return tools_state.value

    def power_on(self, show_gui=True):
        if show_gui:
            options = vixlib.VIX_VMPOWEROP_LAUNCH_GUI
        else:
            options = vixlib.VIX_VMPOWEROP_NORMAL

        job_handle = vixlib.VixVM_PowerOn(self._vm_handle,
                                          options,
                                          vixlib.VIX_INVALID_HANDLE,
                                          None, None)
        err = vixlib.VixJob_Wait(job_handle, vixlib.VIX_PROPERTY_NONE)
        vixlib.Vix_ReleaseHandle(job_handle)
        _check_job_err_code(err)

    def pause(self):
        job_handle = vixlib.VixVM_Pause(self._vm_handle,
                                        0, vixlib.VIX_INVALID_HANDLE,
                                        None, None)
        err = vixlib.VixJob_Wait(job_handle, vixlib.VIX_PROPERTY_NONE)
        vixlib.Vix_ReleaseHandle(job_handle)
        _check_job_err_code(err)

    def unpause(self):
        job_handle = vixlib.VixVM_Unpause(self._vm_handle,
                                          0, vixlib.VIX_INVALID_HANDLE,
                                          None, None)
        err = vixlib.VixJob_Wait(job_handle, vixlib.VIX_PROPERTY_NONE)
        vixlib.Vix_ReleaseHandle(job_handle)
        _check_job_err_code(err)

    def suspend(self):
        job_handle = vixlib.VixVM_Suspend(self._vm_handle,
                                          0, None, None)
        err = vixlib.VixJob_Wait(job_handle, vixlib.VIX_PROPERTY_NONE)
        vixlib.Vix_ReleaseHandle(job_handle)
        _check_job_err_code(err)

    def reboot(self, soft=False):
        if soft:
            power_op = vixlib.VIX_VMPOWEROP_FROM_GUEST
        else:
            power_op = vixlib.VIX_VMPOWEROP_NORMAL

        job_handle = vixlib.VixVM_Reset(self._vm_handle, power_op,
                                        None, None)
        err = vixlib.VixJob_Wait(job_handle, vixlib.VIX_PROPERTY_NONE)
        vixlib.Vix_ReleaseHandle(job_handle)
        _check_job_err_code(err)

    def power_off(self, soft=False):
        if soft:
            power_op = vixlib.VIX_VMPOWEROP_FROM_GUEST
        else:
            power_op = vixlib.VIX_VMPOWEROP_NORMAL

        job_handle = vixlib.VixVM_PowerOff(self._vm_handle, power_op,
                                           None, None)
        err = vixlib.VixJob_Wait(job_handle, vixlib.VIX_PROPERTY_NONE)
        vixlib.Vix_ReleaseHandle(job_handle)
        _check_job_err_code(err)

    def wait_for_tools_in_guest(self, timeout=600):
        if self._vmtools_waited:
            return

        job_handle = vixlib.VixVM_WaitForToolsInGuest(self._vm_handle,
                                                      timeout,
                                                      None, None)
        err = vixlib.VixJob_Wait(job_handle, vixlib.VIX_PROPERTY_NONE)
        vixlib.Vix_ReleaseHandle(job_handle)
        _check_job_err_code(err)
        self._vmtools_waited = True

    def login_guest(self, username, password, options):
        job_handle = vixlib.VixVM_LoginInGuest(self._vm_handle,
                                               username,
                                               password,
                                               options,
                                               None,
                                               None)
        err = vixlib.VixJob_Wait(job_handle,
                                 vixlib.VIX_PROPERTY_NONE)
        _check_job_err_code(err)

    def call_guest(self, args, shell=False):
        if shell:
            if self.guest_os == OperatingSystem.Linux:

                cmd = "/bin/bash"
                if type(args) in (list, tuple):
                    args = '-c "%s"' % (" ".join(args),)
                else:
                    args = '-c "%s"' % (args,)
            elif self.guest_os == OperatingSystem.Windows:
                cmd = "cmd.exe"
                if type(args) in (list, tuple):
                    args = '/C "%s"' % (" ".join(args),)
                else:
                    args = '/C "%s"' % (args,)
            else:
                raise NotImplementedError()
        else:
            if type(args) not in (list, tuple):
                args = shlex.split(args)

            cmd = args[0]
            args = " ".join(args[1:])

        return self.run_cmd_on_guest(cmd=cmd, args=args)

    def run_cmd_on_guest(self, cmd, args="", timeout=30):
        self.wait_for_tools_in_guest(timeout)

        pl_handle = vixlib.VixHandle()

        err = vixlib.VixPropertyList_AllocPropertyList(self._vm_handle,
                                                       ctypes.byref(pl_handle),
                                                       vixlib.VIX_PROPERTY_NONE)
        _check_job_err_code(err)

        job_handle = vixlib.VixVM_RunProgramInGuest(self._vm_handle,
                                                    cmd,
                                                    args,
                                                    0,
                                                    pl_handle,
                                                    None,
                                                    None)

        pid = ctypes.c_uint32()
        exit_code = ctypes.c_uint32()

        err = vixlib.VixJob_Wait(job_handle,
                                 vixlib.VIX_PROPERTY_JOB_RESULT_PROCESS_ID,
                                 ctypes.byref(pid),
                                 vixlib.VIX_PROPERTY_JOB_RESULT_GUEST_PROGRAM_EXIT_CODE,
                                 ctypes.byref(exit_code),
                                 vixlib.VIX_PROPERTY_NONE)
        vixlib.Vix_ReleaseHandle(job_handle)
        vixlib.Vix_ReleaseHandle(pl_handle)
        _check_job_err_code(err)

        return pid.value, exit_code.value

    def upload_file_to_guest(self, local_file_path, guest_file_path):
        job_handle = vixlib.VixVM_CopyFileFromHostToGuest(self._vm_handle,
                                                          local_file_path,
                                                          guest_file_path,
                                                          0,  # options
                                                          vixlib.VIX_INVALID_HANDLE,  # prop list
                                                          None,  # callback
                                                          None)  # client data
        err = vixlib.VixJob_Wait(job_handle,
                                 vixlib.VIX_PROPERTY_NONE)
        vixlib.Vix_ReleaseHandle(job_handle)
        _check_job_err_code(err)

    def download_file_from_guest(self, guest_file_path, local_file_path):
        job_handle = vixlib.VixVM_CopyFileFromGuestToHost(self._vm_handle,
                                                          guest_file_path,
                                                          local_file_path,
                                                          0,  # options
                                                          vixlib.VIX_INVALID_HANDLE,  # prop list
                                                          None,  # callback
                                                          None)  # client data
        err = vixlib.VixJob_Wait(job_handle,
                                 vixlib.VIX_PROPERTY_NONE)
        vixlib.Vix_ReleaseHandle(job_handle)
        _check_job_err_code(err)

    def is_file_exists_in_guest(self, guest_file_path):
        is_exists = ctypes.c_bool()

        job_handle = vixlib.VixVM_DirectoryExistsInGuest(self._vm_handle,
                                                         guest_file_path,
                                                         None,  # callback
                                                         None)  # client data
        err = vixlib.VixJob_Wait(job_handle,
                                 vixlib.VIX_PROPERTY_JOB_RESULT_GUEST_OBJECT_EXISTS,
                                 ctypes.byref(is_exists),
                                 vixlib.VIX_PROPERTY_NONE)
        vixlib.Vix_ReleaseHandle(job_handle)
        _check_job_err_code(err)

        return is_exists.value

    def is_folder_exists_in_guest(self, guest_folder_path):
        is_exists = ctypes.c_bool()

        job_handle = vixlib.VixVM_DirectoryExistsInGuest(self._vm_handle,
                                                         guest_folder_path,
                                                         None,  # callback
                                                         None)  # client data
        err = vixlib.VixJob_Wait(job_handle,
                                 vixlib.VIX_PROPERTY_JOB_RESULT_GUEST_OBJECT_EXISTS,
                                 ctypes.byref(is_exists),
                                 vixlib.VIX_PROPERTY_NONE)
        vixlib.Vix_ReleaseHandle(job_handle)
        _check_job_err_code(err)

        return is_exists.value

    def delete_file_in_guest(self, guest_file_path):
        job_handle = vixlib.VixVM_DeleteFileInGuest(self._vm_handle,
                                                    guest_file_path,
                                                    None,  # callback
                                                    None)  # client data
        err = vixlib.VixJob_Wait(job_handle,
                                 vixlib.VIX_PROPERTY_NONE)
        vixlib.Vix_ReleaseHandle(job_handle)
        _check_job_err_code(err)

    def delete_folder_in_guest(self, guest_folder_path):
        job_handle = vixlib.VixVM_DeleteDirectoryInGuest(self._vm_handle,
                                                         guest_folder_path,
                                                         0,  # options- must be 0
                                                         None,  # callback
                                                         None)  # client data
        err = vixlib.VixJob_Wait(job_handle,
                                 vixlib.VIX_PROPERTY_NONE)
        vixlib.Vix_ReleaseHandle(job_handle)
        _check_job_err_code(err)

    def list_guest_processes(self):
        job_handle = vixlib.VixVM_ListProcessesInGuest(self._vm_handle, 0, None, None)
        err = vixlib.VixJob_Wait(job_handle,
                                 vixlib.VIX_PROPERTY_NONE)

        try:
            _check_job_err_code(err)

            process_count = vixlib.VixJob_GetNumProperties(job_handle, vixlib.VIX_PROPERTY_JOB_RESULT_ITEM_NAME)
            processes = []
            for i in range(process_count):
                process_name = ctypes.c_char_p()
                owner = ctypes.c_char_p()
                cmdline = ctypes.c_char_p()
                pid = ctypes.c_uint64()
                is_debugged = ctypes.c_bool()
                start_time = ctypes.c_int()

                err = vixlib.VixJob_GetNthProperties(job_handle, i,
                                                     vixlib.VIX_PROPERTY_JOB_RESULT_ITEM_NAME,
                                                     ctypes.byref(process_name),
                                                     vixlib.VIX_PROPERTY_JOB_RESULT_PROCESS_ID,
                                                     ctypes.byref(pid),
                                                     vixlib.VIX_PROPERTY_JOB_RESULT_PROCESS_OWNER,
                                                     ctypes.byref(owner),
                                                     vixlib.VIX_PROPERTY_JOB_RESULT_PROCESS_COMMAND,
                                                     ctypes.byref(cmdline),
                                                     vixlib.VIX_PROPERTY_JOB_RESULT_PROCESS_BEING_DEBUGGED,
                                                     ctypes.byref(is_debugged),
                                                     vixlib.VIX_PROPERTY_JOB_RESULT_PROCESS_START_TIME,
                                                     ctypes.byref(start_time),
                                                     vixlib.VIX_PROPERTY_NONE)

                processes.append(dict(pid=pid.value,
                                      name=process_name.value,
                                      owner=owner.value,
                                      cmdline=cmdline.value,
                                      is_debugged=is_debugged.value,
                                      start_time=start_time.value))

                vixlib.Vix_FreeBuffer(process_name)
                vixlib.Vix_FreeBuffer(owner)
                vixlib.Vix_FreeBuffer(cmdline)
        finally:
            vixlib.Vix_ReleaseHandle(job_handle)

        return processes

    def capture_guest_screenshot(self, screenshot_path):
        data_blob = ctypes.c_void_p()
        data_size = ctypes.c_size_t()

        job_handle = vixlib.VixVM_CaptureScreenImage(self._vm_handle,
                                                     vixlib.VIX_CAPTURESCREENFORMAT_PNG,
                                                     vixlib.VIX_INVALID_HANDLE,
                                                     None,  # callback
                                                     None)  # client data
        err = vixlib.VixJob_Wait(job_handle,
                                 vixlib.VIX_PROPERTY_JOB_RESULT_SCREEN_IMAGE_DATA,
                                 ctypes.byref(data_size),
                                 ctypes.byref(data_blob),
                                 vixlib.VIX_PROPERTY_NONE)
        vixlib.Vix_ReleaseHandle(job_handle)
        _check_job_err_code(err)

        try:
            buff = (ctypes.c_char * data_size.value).from_address(data_blob.value)
            with open(screenshot_path, "wb")as fp:
                fp.write(buff)
        finally:
            vixlib.Vix_FreeBuffer(data_blob)

        return screenshot_path, data_size

    def get_guest_ip_address(self, timeout=30):
        ip_address = None
        while not ip_address:
            ip_address = self.read_guest_variable_str("ip", timeout=timeout)
            if not ip_address or ip_address.startswith('169.254.'):
                time.sleep(2)
                ip_address = None

        return ip_address

    def get_physical_interfaces(self):
        ifaces = []
        for i in range(32):
            eth_name = "ethernet%d" % (i,)
            mac_addr = self.read_guest_variable_str("%s.generatedAddress" % (eth_name,),
                                                    variable_type=vixlib.VIX_VM_CONFIG_RUNTIME_ONLY)
            if not mac_addr:
                break

            present = ("TRUE" == self.read_guest_variable_str("%s.present" % (eth_name,),
                                                              variable_type=vixlib.VIX_VM_CONFIG_RUNTIME_ONLY).strip(
                ' "'))

            ifaces.append(dict(eth_addr=mac_addr,
                               eth_name=eth_name,
                               present=present))

        return ifaces

    def write_guest_variable_str(self, variable_name, variable_value, variable_type=vixlib.VIX_VM_GUEST_VARIABLE,
                                 timeout=30):
        if variable_type in (vixlib.VIX_VM_GUEST_VARIABLE, vixlib.VIX_GUEST_ENVIRONMENT_VARIABLE):
            self.wait_for_tools_in_guest(timeout)

        job_handle = vixlib.VixVM_WriteVariable(self._vm_handle,
                                                variable_type,
                                                variable_name,
                                                ctypes.c_char_p(variable_value),
                                                0,
                                                None,
                                                None)
        err = vixlib.VixJob_Wait(job_handle,
                                 vixlib.VIX_PROPERTY_NONE)
        _check_job_err_code(err)

    def read_guest_variable_str(self, variable_name, variable_type=vixlib.VIX_VM_GUEST_VARIABLE, timeout=30):
        if variable_type in (vixlib.VIX_VM_GUEST_VARIABLE, vixlib.VIX_GUEST_ENVIRONMENT_VARIABLE):
            self.wait_for_tools_in_guest(timeout)

        job_handle = vixlib.VixVM_ReadVariable(self._vm_handle,
                                               variable_type,
                                               variable_name,
                                               0,
                                               None,
                                               None)
        read_value = ctypes.c_char_p()
        err = vixlib.VixJob_Wait(job_handle,
                                 vixlib.VIX_PROPERTY_JOB_RESULT_VM_VARIABLE_STRING,
                                 ctypes.byref(read_value),
                                 vixlib.VIX_PROPERTY_NONE)
        vixlib.Vix_ReleaseHandle(job_handle)
        _check_job_err_code(err)

        value = read_value.value
        vixlib.Vix_FreeBuffer(read_value)

        return value

    def delete(self, delete_disk_files=True):
        if delete_disk_files:
            delete_options = vixlib.VIX_VMDELETE_DISK_FILES
        else:
            delete_options = 0

        job_handle = vixlib.VixVM_Delete(self._vm_handle, delete_options,
                                         None, None)
        err = vixlib.VixJob_Wait(job_handle, vixlib.VIX_PROPERTY_NONE)
        vixlib.Vix_ReleaseHandle(job_handle)
        _check_job_err_code(err)

        self.close()

    def create_snapshot(self, include_memory=False, name=None,
                        description=None):
        if include_memory:
            options = vixlib.VIX_SNAPSHOT_INCLUDE_MEMORY
        else:
            options = 0

        job_handle = vixlib.VixVM_CreateSnapshot(self._vm_handle,
                                                 name, description, options,
                                                 vixlib.VIX_INVALID_HANDLE,
                                                 None, None)
        snapshot_handle = vixlib.VixHandle()
        err = vixlib.VixJob_Wait(job_handle,
                                 vixlib.VIX_PROPERTY_JOB_RESULT_HANDLE,
                                 ctypes.byref(snapshot_handle),
                                 vixlib.VIX_PROPERTY_NONE)
        vixlib.Vix_ReleaseHandle(job_handle)
        _check_job_err_code(err)

        return VixSnapshot(snapshot_handle)

    def remove_snapshot(self, snapshot):
        job_handle = vixlib.VixVM_RemoveSnapshot(self._vm_handle,
                                                 snapshot._snapshot_handle,
                                                 0, None, None)
        err = vixlib.VixJob_Wait(job_handle, vixlib.VIX_PROPERTY_NONE)
        _check_job_err_code(err)

        snapshot.close()

    def get_vmx_path(self):
        if not self._vmx_path:
            vmx_path = ctypes.c_char_p()
            err = vixlib.Vix_GetProperties(self._vm_handle,
                                           vixlib.VIX_PROPERTY_VM_VMX_PATHNAME,
                                           ctypes.byref(vmx_path),
                                           vixlib.VIX_PROPERTY_NONE)
            _check_job_err_code(err)

            self._vmx_path = vmx_path.value
            vixlib.Vix_FreeBuffer(vmx_path)

        return self._vmx_path

    def get_vmteam_path(self):
        vmx_path = ctypes.c_char_p()

        try:
            err = vixlib.Vix_GetProperties(self._vm_handle,
                                           vixlib.VIX_PROPERTY_VM_VMTEAM_PATHNAME,
                                           ctypes.byref(vmx_path),
                                           vixlib.VIX_PROPERTY_NONE)
            _check_job_err_code(err)

            return vmx_path.value
        finally:
            vixlib.Vix_FreeBuffer(vmx_path)


class VixSnapshot(object):
    def __init__(self, snapshot_handle):
        self._snapshot_handle = snapshot_handle

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        if self._snapshot_handle:
            vixlib.Vix_ReleaseHandle(self._snapshot_handle)
            self._snapshot_handle = None


class VixConnection(object):
    def __init__(self):
        self._host_handle = None
        self._software_version = None
        self._host_type = None
        self._host = None

    def __repr__(self):
        return "<VixConnection %s%s>" % (self._host, " Connected" if self.connected else "")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, type, value, traceback):
        self.disconnect()

    @property
    def connected(self):
        return self._host_handle is not None

    def connect(self, host=None, host_port=0, username=None, password=None, host_type=None):
        assert not self.connected, "VixConnection already connected"
        if (host_type is None) or (host is None):
            host_type = get_vix_host_type()

        job_handle = vixlib.VixHost_Connect(vixlib.VIX_API_VERSION,  # API version
                                            host_type,  # host connection type
                                            host,  # host address/URL
                                            host_port,  # host port
                                            username,  # username
                                            password,  # password
                                            0,  # options
                                            vixlib.VIX_INVALID_HANDLE,  # properties list
                                            None,  # callback
                                            None)  # user data

        host_handle = vixlib.VixHandle()
        err = vixlib.VixJob_Wait(job_handle,
                                 vixlib.VIX_PROPERTY_JOB_RESULT_HANDLE,
                                 ctypes.byref(host_handle),
                                 vixlib.VIX_PROPERTY_NONE)
        vixlib.Vix_ReleaseHandle(job_handle)
        _check_job_err_code(err)

        self._host = host
        self._host_handle = host_handle

    def open_vm(self, vmx_path, timeout=4):
        assert self.connected, "VixConnection not connected"

        start_time = time.time()
        job_handle = vixlib.VixVM_Open(self._host_handle, vmx_path, None, None)
        vm_handle = vixlib.VixHandle()

        job_completed = ctypes.c_byte(0)
        while not job_completed.value:
            err = vixlib.VixJob_CheckCompletion(job_handle, ctypes.byref(job_completed))
            _check_job_err_code(err)

            if timeout and timeout < (time.time() - start_time):
                raise VixException("Timeout (%d seconds) waiting to open VM by VMX '%s'", 0, timeout, vmx_path)

        err = vixlib.Vix_GetProperties(job_handle,
                                       vixlib.VIX_PROPERTY_JOB_RESULT_HANDLE,
                                       ctypes.byref(vm_handle),
                                       vixlib.VIX_PROPERTY_NONE)
        vixlib.Vix_ReleaseHandle(job_handle)
        _check_job_err_code(err)

        return VixVM(vm_handle)

    def disconnect(self):
        if self._host_handle:
            vixlib.VixHost_Disconnect(self._host_handle)
            self._host_handle = None

    def list_running_vms(self):
        assert self.connected, "VixConnection not connected"
        vmx_paths = []

        def callback(jobHandle, eventType, moreEventInfo, clientData):
            if vixlib.VIX_EVENTTYPE_FIND_ITEM != eventType:
                return

            url = ctypes.c_char_p()
            err = vixlib.Vix_GetProperties(
                moreEventInfo,
                vixlib.VIX_PROPERTY_FOUND_ITEM_LOCATION,
                ctypes.byref(url),
                vixlib.VIX_PROPERTY_NONE)

            vmx_paths.append(url.value)

            vixlib.Vix_FreeBuffer(url)
            _check_job_err_code(err)

        cb = vixlib.VixEventProc(callback)
        job_handle = vixlib.VixHost_FindItems(self._host_handle,
                                              vixlib.VIX_FIND_RUNNING_VMS,
                                              vixlib.VIX_INVALID_HANDLE,
                                              -1, cb, None)
        err = vixlib.VixJob_Wait(job_handle, vixlib.VIX_PROPERTY_NONE)
        vixlib.Vix_ReleaseHandle(job_handle)
        _check_job_err_code(err)

        return vmx_paths

    def get_software_version(self):
        assert self.connected, "VixConnection not connected"

        if not self._software_version:
            version = ctypes.c_char_p()
            err = vixlib.Vix_GetProperties(self._host_handle,
                                           vixlib.VIX_PROPERTY_HOST_SOFTWARE_VERSION,
                                           ctypes.byref(version),
                                           vixlib.VIX_PROPERTY_NONE)
            _check_job_err_code(err)

            self._software_version = version.value
            vixlib.Vix_FreeBuffer(version)

        return self._software_version

    def get_host_type(self):
        assert self.connected, "VixConnection not connected"

        if not self._host_type:
            host_type = ctypes.c_int()
            err = vixlib.Vix_GetProperties(self._host_handle,
                                           vixlib.VIX_PROPERTY_HOST_HOSTTYPE,
                                           ctypes.byref(host_type),
                                           vixlib.VIX_PROPERTY_NONE)
            _check_job_err_code(err)

            self._host_type = host_type.value

        return self._host_type
