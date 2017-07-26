import argparse
import getpass
import pickle
from collections import defaultdict, namedtuple

from prettytable import PrettyTable
from pyVmomi import vim, SoapAdapter

from vsphere_client import VSphereClient

BUILTIN_ROLES = ['NoAccess', 'Anonymous', 'View', 'ReadOnly', 'Admin',
                 'VirtualMachinePowerUser', 'VirtualMachineUser',
                 'ResourcePoolAdministrator', 'VMwareConsolidatedBackupUser',
                 'DatastoreConsumer', 'NetworkConsumer']

BUILTIN_USERS_AND_GROUPS = ['vpxuser/VSPHERE.LOCAL', 'root',
                            'krbtgt/VSPHERE.LOCAL', 'K/M'
                                                    'Administrator',
                            'Administrators',
                            'admin'  # on vSphere 5.1
                            "Users", 'DCAdmins',
                            'SolutionUsers',
                            'ExternalIDPUsers'
                            ]

VM_ADVANCED_CONFIG_PRIVILEGE = "VirtualMachine.Config.AdvancedConfig"
VM_GUEST_CONTROL_PRIVILEGE = "VirtualMachine.Interact.GuestControl"
HOST_CONFIG_PRIVILEGE = "Host.Config.AdvancedConfig"
INSTALL_VM_TOOLS_PRIVILEGE = "VirtualMachine.Interact.ToolsInstall"

privilege_strings = namedtuple('privilege_strings', ['title', 'value_if_set', 'value_if_not_available'])
PRIVILEGES = {VM_ADVANCED_CONFIG_PRIVILEGE: privilege_strings("Advanced Config Privilege", "", "N/A"),
              VM_GUEST_CONTROL_PRIVILEGE: privilege_strings("Guest Control Privilege", "", "N/A"),
              HOST_CONFIG_PRIVILEGE: privilege_strings("Set RefCount", "Already set", "N/A"),
              INSTALL_VM_TOOLS_PRIVILEGE: privilege_strings("", "", "")
              }

SECURE_VM_TOOLS_VERSION = 10272  # anything lower than this is vulnerable in some fashion

SHARED_POLICY_REF_COUNT_SETTING = 'Config.GlobalSettings.guest.commands.sharedPolicyRefCount'


class VsphereObject(object):
    def __init__(self, obj_id, name, parent, permission):
        self.obj_id = obj_id
        self.name = name
        self.parent = parent
        self.permission = permission

    @classmethod
    def generate_from_vim(cls, vsphere_object):
        return cls(VsphereObject.get_vim_obj_id(vsphere_object),
                   VsphereObject.safe_getattr(vsphere_object, 'name'),
                   VsphereObject.get_vim_obj_id(VsphereObject.safe_getattr(vsphere_object, 'parent')),
                   VsphereObject.safe_getattr(vsphere_object, 'permission', []))

    @staticmethod
    def get_vim_obj_id(obj):
        return obj._moId if obj else None

    @staticmethod
    def safe_getattr(vsphere_object, attr_name, default=None):
        try:
            return getattr(vsphere_object, attr_name, default)
        except vim.fault.NoPermission:
            print("WARNING: No permissions to read %s of %s" % (attr_name, vsphere_object))
        except Exception, e:
            print("ERROR: Failed to read %s of %s" % (attr_name, vsphere_object))
            print(e)
        return default

    @classmethod
    def generate_objects_dict(cls, objects):
        objects_dict = {}
        parents = set()
        for obj in objects:
            objects_dict[cls.get_vim_obj_id(obj)] = cls.generate_from_vim(obj)
            if obj.parent:
                parents.add(obj.parent)
        return objects_dict, parents


class Host(VsphereObject):
    def __init__(self, obj_id, name, parent, permission, config, vm, version=None, ref_count=None):
        super(Host, self).__init__(obj_id, name, parent, permission)
        self.config = config
        self.vm = vm

        self.version = self.config.product.version if version is None else version
        self.ref_count = self._get_ref_count() if ref_count is None else ref_count

    @classmethod
    def generate_from_vim(cls, host):
        return cls(cls.get_vim_obj_id(host),
                   VsphereObject.safe_getattr(host, 'name'),
                   cls.get_vim_obj_id(VsphereObject.safe_getattr(host, 'parent')),
                   VsphereObject.safe_getattr(host, 'permission', []),
                   VsphereObject.safe_getattr(host, 'config'),
                   [cls.get_vim_obj_id(vm) for vm in VsphereObject.safe_getattr(host, 'vm', [])])

    def _get_ref_count(self):
        if not self.config:
            print("ERROR: Config data is missing for %s (%s)" % (self.name, self.obj_id))
            return 0

        ref_count = [opt.value for opt in self.config.option
                     if opt.key == SHARED_POLICY_REF_COUNT_SETTING]
        if not ref_count:
            ref_count = [opt.optionType.defaultValue for opt in self.config.optionDef
                         if opt.key == SHARED_POLICY_REF_COUNT_SETTING]
            return ref_count[0] if ref_count else 0

        return ref_count[0]

    def is_vulnerable_host(self):
        return self.version.startswith("5.5")


class VirtualMachine(VsphereObject):
    def __init__(self, obj_id, name, parent, permission, guest, config, datastore, summary, runtime, toolsVersion=None,
                 toolsStatus=None):
        super(VirtualMachine, self).__init__(obj_id, name, parent, permission)
        self.guest = guest
        self.config = config
        self.datastore = datastore
        self.summary = summary
        self.runtime = runtime
        self.toolsStatus = guest.toolsStatus if toolsStatus is None else toolsStatus
        self.toolsVersion = self.config.tools.toolsVersion if toolsVersion is None else toolsVersion

    @classmethod
    def generate_from_vim(cls, vm):
        return cls(cls.get_vim_obj_id(vm),
                   VsphereObject.safe_getattr(vm, 'name'),
                   cls.get_vim_obj_id(VsphereObject.safe_getattr(vm, 'parent')),
                   VsphereObject.safe_getattr(vm, 'permission', []),
                   VsphereObject.safe_getattr(vm, 'guest'),
                   VsphereObject.safe_getattr(vm, 'config'),
                   VsphereObject.safe_getattr(vm, 'datastore'),
                   VsphereObject.safe_getattr(vm, 'summary'),
                   VsphereObject.safe_getattr(vm, 'runtime'))

    def is_vmtools_installed(self):
        if not self.toolsStatus:
            print("ERROR: Tools Status data is missing for %s (%s)" % (self.name, self.obj_id))
            return False
        return self.guest.toolsStatus != 'toolsNotInstalled'

    def is_vmtools_vulnerable(self):
        if not self.is_vmtools_installed():
            return False
        if not self.toolsVersion:
            print("ERROR: Tools Version data is missing for %s (%s)" % (self.name, self.obj_id))
            return False
        return self.toolsVersion < SECURE_VM_TOOLS_VERSION


class VsphereData(object):
    def __init__(self, roles, vm_uuids, host_uuids, objects_tree):
        self._vm_permission_cache = dict()

        self.roles = roles
        self.vm_uuids = vm_uuids
        self.host_uuids = host_uuids
        self.objects_tree = objects_tree

    @classmethod
    def collect_data(cls, vsphere_client):
        if vsphere_client is None:
            raise Exception('Not connected to vsphere')
        print("Fetch roles...")
        roles = {role.roleId: role for role in vsphere_client.roles}
        vm_uuids, host_uuids, obj_tree = VsphereData._build_objects_tree(vsphere_client)
        return cls(roles, vm_uuids, host_uuids, obj_tree)

    @staticmethod
    def _build_objects_tree(vsphere_client):
        print("Fetch VMs information...")
        vms, vm_parents = VirtualMachine.generate_objects_dict(vsphere_client.list_vms())
        print("Fetch Hosts information...")
        hosts, host_parents = Host.generate_objects_dict(vsphere_client.list_hosts())
        vm_uuids = vms.keys()
        host_uuids = hosts.keys()

        objects_tree = dict()
        objects_tree.update(vms)
        objects_tree.update(hosts)

        print("Fetch objects tree...")
        objects_to_iter = vm_parents.union(host_parents)
        while 0 < len(objects_to_iter):
            vsphere_objects, objects_to_iter = VsphereObject.generate_objects_dict(objects_to_iter)
            objects_tree.update(vsphere_objects)

        return vm_uuids, host_uuids, objects_tree

    def get_vms_permission(self):
        return {vm_uuid: self.get_obj_permission(vm_uuid) for vm_uuid in self.vm_uuids}

    def get_hosts_permission(self):
        return {host_uuid: self.get_obj_permission(host_uuid) for host_uuid in self.host_uuids}

    def get_obj_permission(self, obj_uuid):
        if obj_uuid in self._vm_permission_cache:
            return self._vm_permission_cache[obj_uuid]

        if self.objects_tree[obj_uuid].parent is None:
            self._vm_permission_cache[obj_uuid] = self.objects_tree[obj_uuid].permission
            return self.objects_tree[obj_uuid].permission

        obj_permission = self.objects_tree[obj_uuid].permission
        parent_permission = self.get_obj_permission(self.objects_tree[obj_uuid].parent)
        for permission in parent_permission:
            if permission.propagate:
                obj_permission.append(permission)
        self._vm_permission_cache[obj_uuid] = obj_permission
        return obj_permission


def serialize(obj):
    obj_cls = obj.__class__
    if obj_cls is dict:
        res = {k: serialize(v) for k, v in obj.items()}
    elif obj_cls is list:
        res = [serialize(val) for val in obj]
    elif issubclass(obj_cls, (VsphereObject, VsphereData)):
        res = {k: serialize(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
    else:
        try:
            res = SoapAdapter.Serialize(obj)
        except UnicodeEncodeError:
            print("WARNING: Failed to serialize %s data" % type(obj))
            return None, None
        obj_cls = None
    return obj_cls, res


def deserialize(clazz, data):
    if clazz is None:
        return SoapAdapter.Deserialize(data) if data else None
    elif clazz is list:
        return [deserialize(*elem) for elem in data]
    #elif issubclass(clazz, (VsphereObject, VsphereData, dict)):
    else:
        return clazz(**{k: deserialize(*v) for k, v in data.items()})


def print_logo():
    print("****************************************************")
    print("GuardiCore VMware auth bypass discovery tool")
    print("Written By Guardicore Labs")
    print("Contact us at: support@guardicore.com")
    print("****************************************************")


def get_args():
    parser = argparse.ArgumentParser()

    host_arg = parser.add_argument('-c', '--host',
                                   required=False,
                                   action='store',
                                   help='Remote host to connect to')

    parser.add_argument('-o', '--port',
                        required=False,
                        action='store',
                        help="Port to use, default 443", default=443)

    user_arg = parser.add_argument('-u', '--user',
                                   required=False,
                                   action='store',
                                   help='Administrator user name to use when connecting to host')

    parser.add_argument('-p', '--password',
                        required=False,
                        action='store',
                        help='Password to use when connecting to host')

    parser.add_argument('-s', '--save-query',
                        required=False,
                        action='store',
                        help='Save vsphere query results to file')

    parser.add_argument('-l', '--load-query',
                        required=False,
                        action='store',
                        help='Load vsphere query results from file')

    parser.add_argument('-i', '--include-builtin',
                        required=False,
                        action='store_false',
                        help='Include builtin roles')

    args = parser.parse_args()

    if args.load_query:
        return args

    if not args.host:
        parser.error('argument %s is required' % "/".join(host_arg.option_strings))

    if not args.user:
        parser.error('argument %s is required' % "/".join(user_arg.option_strings))

    if args.password is None:
        args.password = getpass.getpass(
            prompt='Enter password for host %s and user %s: ' %
                   (args.host, args.user))

    return args


def get_roles_by_privileges(roles, privileges, is_builtin_roles_included):
    if is_builtin_roles_included:
        roles = [x for x in roles if x.name not in BUILTIN_ROLES]
    roles_by_priv = defaultdict(list)
    [roles_by_priv[priv].append(role.roleId) for role in roles for priv in role.privilege if priv in privileges]
    return roles_by_priv


def get_vsphere_data(args):
    if args.load_query is None:
        vsphere_client = VSphereClient(admin_user=args.user,
                                       admin_password=args.password,
                                       auth_host=args.host,
                                       auth_port=args.port)
        print("Connecting to VSphere...")
        vsphere_client.connect()
        vsphere_data = VsphereData.collect_data(vsphere_client)
        if args.save_query is not None:
            print("Dump vsphere data to %s" % args.save_query)
            with open(args.save_query, 'wb') as f:
                pickle.dump(serialize(vsphere_data), f)
        return vsphere_data
    else:
        print("Load VSphere data from %s" % args.load_query)
        with open(args.load_query, 'r') as f:
            data = pickle.load(f)
        return deserialize(*data)


def get_vms_at_risk(vms_state):
    vms_at_risk = []
    for vm_uuid, state in vms_state.items():
        is_at_risk = True
        for priv in PRIVILEGES:
            if not state[priv][0] and not state[priv][1]:
                is_at_risk = False
                break
        if is_at_risk:
            vms_at_risk.append(vm_uuid)
    return vms_at_risk


def print_vms_state(vms_state, vms_at_risk, vsphere_data, is_only_at_risk=True):
    def state_to_print_format(state):
        to_print = {}
        for priv_name, priv_state in state.items():
            if priv_state[0]:
                to_print[priv_name] = PRIVILEGES[priv_name].value_if_set
            elif priv_state[1]:
                to_print[priv_name] = "\n".join({"%s (%s)" % (permission.principal,
                                                              vsphere_data.roles[permission.roleId].name)
                                                 for permission in priv_state[1]})
            else:
                to_print[priv_name] = PRIVILEGES[priv_name].value_if_not_available
        return to_print

    t = PrettyTable(['Name'] + [priv.title for priv in PRIVILEGES.values() if priv.title != ""])
    vms_to_print = vms_at_risk if is_only_at_risk else vms_state
    for vm_uuid in vms_to_print:
        state = state_to_print_format(vms_state[vm_uuid])
        t.add_row([vsphere_data.objects_tree[vm_uuid].name] + [state[k] for k in PRIVILEGES
                                                               if k != INSTALL_VM_TOOLS_PRIVILEGE])

    if vms_to_print:
        print("High Risk:")
        print(t)
    else:
        print("No high risk VMs!\n")


def main():
    print_logo()
    args = get_args()
    vsphere_data = get_vsphere_data(args)

    roles_by_priv = get_roles_by_privileges(vsphere_data.roles.values(), PRIVILEGES.keys(), args.include_builtin)
    vms_permission = vsphere_data.get_vms_permission()
    hosts_permission = vsphere_data.get_hosts_permission()

    vms_state = defaultdict(dict)

    for host_uuid in vsphere_data.host_uuids:
        host_config_roles = set()
        # Get host permissions
        for permission in hosts_permission[host_uuid]:
            if permission.roleId in roles_by_priv[HOST_CONFIG_PRIVILEGE]:
                host_config_roles.add(permission)

        host = vsphere_data.objects_tree[host_uuid]
        is_set = host.ref_count > 0
        is_host_vulnerable = host.is_vulnerable_host()
        for vm_id in host.vm:
            vms_state[vm_id][HOST_CONFIG_PRIVILEGE] = (is_set, host_config_roles)
            vms_state[vm_id][INSTALL_VM_TOOLS_PRIVILEGE] = (vsphere_data.objects_tree[vm_id].is_vmtools_vulnerable() or
                                                            (vsphere_data.objects_tree[vm_id].is_vmtools_installed() and
                                                             is_host_vulnerable),
                                                            [])

    for vm_id in vsphere_data.vm_uuids:
        roles = defaultdict(set)
        for permission in vms_permission[vm_id]:
            if permission.roleId in roles_by_priv[INSTALL_VM_TOOLS_PRIVILEGE]:
                roles[INSTALL_VM_TOOLS_PRIVILEGE].add(permission)
            if permission.roleId in roles_by_priv[VM_ADVANCED_CONFIG_PRIVILEGE]:
                roles[VM_ADVANCED_CONFIG_PRIVILEGE].add(permission)
            if permission.roleId in roles_by_priv[VM_GUEST_CONTROL_PRIVILEGE]:
                roles[VM_GUEST_CONTROL_PRIVILEGE].add(permission)

        vms_state[vm_id][VM_ADVANCED_CONFIG_PRIVILEGE] = (False, roles[VM_ADVANCED_CONFIG_PRIVILEGE])
        vms_state[vm_id][VM_GUEST_CONTROL_PRIVILEGE] = (False, roles[VM_GUEST_CONTROL_PRIVILEGE])

    # Find all vms with True OR list of roles != []
    vms_at_risk = get_vms_at_risk(vms_state)

    print_vms_state(vms_state, vms_at_risk, vsphere_data)


if __name__ == "__main__":
    main()
