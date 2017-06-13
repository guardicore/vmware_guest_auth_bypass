# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 Cloudbase Solutions Srl
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
import ctypes

VMWR_CONFIG_FILE = "/etc/vmware/config"


def _find_vix_lib():
    if os.path.isfile(VMWR_CONFIG_FILE):
        for config_line in open(VMWR_CONFIG_FILE, "rb"):
            if config_line.startswith("vix.libdir"):
                vix_libdir = config_line.strip().split("=", 2)[1]
                return os.path.join(vix_libdir.strip().strip('"'), "libvixAllProducts.so")

    return r"vix.dll"

vixpath = _find_vix_lib()

try:
    vix = ctypes.CDLL(vixpath)
except Exception:
    raise IOError('Cannot load Vix: %s' % vixpath)

VixHandle = ctypes.c_int
VixHandleType = ctypes.c_int
VixError = ctypes.c_uint64
VixPropertyType = ctypes.c_int
VixPropertyID = ctypes.c_int
VixEventType = ctypes.c_int
VixHostOptions = ctypes.c_int
VixServiceProvider = ctypes.c_int
VixFindItemType = ctypes.c_int
VixVMOpenOptions = ctypes.c_int
VixPumpEventsOptions = ctypes.c_int
VixVMPowerOpOptions = ctypes.c_int
VixVMDeleteOptions = ctypes.c_int
VixPowerState = ctypes.c_int
VixToolsState = ctypes.c_int
VixRunProgramOptions = ctypes.c_int
VixRemoveSnapshotOptions = ctypes.c_int
VixCreateSnapshotOptions = ctypes.c_int
VixMsgSharedFolderOptions = ctypes.c_int
VixCloneType = ctypes.c_int
VixEventProc = ctypes.CFUNCTYPE(
    None,
    VixHandle,
    VixEventType,
    VixHandle,
    ctypes.c_void_p)

VIX_INVALID_HANDLE = 0
VIX_HANDLETYPE_NONE = 0
VIX_HANDLETYPE_HOST = 2
VIX_HANDLETYPE_VM = 3
VIX_HANDLETYPE_NETWORK = 5
VIX_HANDLETYPE_JOB = 6
VIX_HANDLETYPE_SNAPSHOT = 7
VIX_HANDLETYPE_PROPERTY_LIST = 9
VIX_HANDLETYPE_METADATA_CONTAINER = 11
VIX_OK = 0
VIX_E_FAIL = 1
VIX_E_OUT_OF_MEMORY = 2
VIX_E_INVALID_ARG = 3
VIX_E_FILE_NOT_FOUND = 4
VIX_E_OBJECT_IS_BUSY = 5
VIX_E_NOT_SUPPORTED = 6
VIX_E_FILE_ERROR = 7
VIX_E_DISK_FULL = 8
VIX_E_INCORRECT_FILE_TYPE = 9
VIX_E_CANCELLED = 10
VIX_E_FILE_READ_ONLY = 11
VIX_E_FILE_ALREADY_EXISTS = 12
VIX_E_FILE_ACCESS_ERROR = 13
VIX_E_REQUIRES_LARGE_FILES = 14
VIX_E_FILE_ALREADY_LOCKED = 15
VIX_E_VMDB = 16
VIX_E_NOT_SUPPORTED_ON_REMOTE_OBJECT = 20
VIX_E_FILE_TOO_BIG = 21
VIX_E_FILE_NAME_INVALID = 22
VIX_E_ALREADY_EXISTS = 23
VIX_E_BUFFER_TOOSMALL = 24
VIX_E_OBJECT_NOT_FOUND = 25
VIX_E_HOST_NOT_CONNECTED = 26
VIX_E_INVALID_UTF8_STRING = 27
VIX_E_OPERATION_ALREADY_IN_PROGRESS = 31
VIX_E_UNFINISHED_JOB = 29
VIX_E_NEED_KEY = 30
VIX_E_LICENSE = 32
VIX_E_VM_HOST_DISCONNECTED = 34
VIX_E_AUTHENTICATION_FAIL = 35
VIX_E_HOST_CONNECTION_LOST = 36
VIX_E_DUPLICATE_NAME = 41
VIX_E_INVALID_HANDLE = 1000
VIX_E_NOT_SUPPORTED_ON_HANDLE_TYPE = 1001
VIX_E_TOO_MANY_HANDLES = 1002
VIX_E_NOT_FOUND = 2000
VIX_E_TYPE_MISMATCH = 2001
VIX_E_INVALID_XML = 2002
VIX_E_TIMEOUT_WAITING_FOR_TOOLS = 3000
VIX_E_UNRECOGNIZED_COMMAND = 3001
VIX_E_OP_NOT_SUPPORTED_ON_GUEST = 3003
VIX_E_PROGRAM_NOT_STARTED = 3004
VIX_E_CANNOT_START_READ_ONLY_VM = 3005
VIX_E_VM_NOT_RUNNING = 3006
VIX_E_VM_IS_RUNNING = 3007
VIX_E_CANNOT_CONNECT_TO_VM = 3008
VIX_E_POWEROP_SCRIPTS_NOT_AVAILABLE = 3009
VIX_E_NO_GUEST_OS_INSTALLED = 3010
VIX_E_VM_INSUFFICIENT_HOST_MEMORY = 3011
VIX_E_SUSPEND_ERROR = 3012
VIX_E_VM_NOT_ENOUGH_CPUS = 3013
VIX_E_HOST_USER_PERMISSIONS = 3014
VIX_E_GUEST_USER_PERMISSIONS = 3015
VIX_E_TOOLS_NOT_RUNNING = 3016
VIX_E_GUEST_OPERATIONS_PROHIBITED = 3017
VIX_E_ANON_GUEST_OPERATIONS_PROHIBITED = 3018
VIX_E_ROOT_GUEST_OPERATIONS_PROHIBITED = 3019
VIX_E_MISSING_ANON_GUEST_ACCOUNT = 3023
VIX_E_CANNOT_AUTHENTICATE_WITH_GUEST = 3024
VIX_E_UNRECOGNIZED_COMMAND_IN_GUEST = 3025
VIX_E_CONSOLE_GUEST_OPERATIONS_PROHIBITED = 3026
VIX_E_MUST_BE_CONSOLE_USER = 3027
VIX_E_VMX_MSG_DIALOG_AND_NO_UI = 3028
VIX_E_NOT_ALLOWED_DURING_VM_RECORDING = 3029
VIX_E_NOT_ALLOWED_DURING_VM_REPLAY = 3030
VIX_E_OPERATION_NOT_ALLOWED_FOR_LOGIN_TYPE = 3031
VIX_E_LOGIN_TYPE_NOT_SUPPORTED = 3032
VIX_E_EMPTY_PASSWORD_NOT_ALLOWED_IN_GUEST = 3033
VIX_E_INTERACTIVE_SESSION_NOT_PRESENT = 3034
VIX_E_INTERACTIVE_SESSION_USER_MISMATCH = 3035
VIX_E_UNABLE_TO_REPLAY_VM = 3039
VIX_E_CANNOT_POWER_ON_VM = 3041
VIX_E_NO_DISPLAY_SERVER = 3043
VIX_E_VM_NOT_RECORDING = 3044
VIX_E_VM_NOT_REPLAYING = 3045
VIX_E_VM_NOT_FOUND = 4000
VIX_E_NOT_SUPPORTED_FOR_VM_VERSION = 4001
VIX_E_CANNOT_READ_VM_CONFIG = 4002
VIX_E_TEMPLATE_VM = 4003
VIX_E_VM_ALREADY_LOADED = 4004
VIX_E_VM_ALREADY_UP_TO_DATE = 4006
VIX_E_VM_UNSUPPORTED_GUEST = 4011
VIX_E_UNRECOGNIZED_PROPERTY = 6000
VIX_E_INVALID_PROPERTY_VALUE = 6001
VIX_E_READ_ONLY_PROPERTY = 6002
VIX_E_MISSING_REQUIRED_PROPERTY = 6003
VIX_E_INVALID_SERIALIZED_DATA = 6004
VIX_E_PROPERTY_TYPE_MISMATCH = 6005
VIX_E_BAD_VM_INDEX = 8000
VIX_E_INVALID_MESSAGE_HEADER = 10000
VIX_E_INVALID_MESSAGE_BODY = 10001
VIX_E_SNAPSHOT_INVAL = 13000
VIX_E_SNAPSHOT_DUMPER = 13001
VIX_E_SNAPSHOT_DISKLIB = 13002
VIX_E_SNAPSHOT_NOTFOUND = 13003
VIX_E_SNAPSHOT_EXISTS = 13004
VIX_E_SNAPSHOT_VERSION = 13005
VIX_E_SNAPSHOT_NOPERM = 13006
VIX_E_SNAPSHOT_CONFIG = 13007
VIX_E_SNAPSHOT_NOCHANGE = 13008
VIX_E_SNAPSHOT_CHECKPOINT = 13009
VIX_E_SNAPSHOT_LOCKED = 13010
VIX_E_SNAPSHOT_INCONSISTENT = 13011
VIX_E_SNAPSHOT_NAMETOOLONG = 13012
VIX_E_SNAPSHOT_VIXFILE = 13013
VIX_E_SNAPSHOT_DISKLOCKED = 13014
VIX_E_SNAPSHOT_DUPLICATEDDISK = 13015
VIX_E_SNAPSHOT_INDEPENDENTDISK = 13016
VIX_E_SNAPSHOT_NONUNIQUE_NAME = 13017
VIX_E_SNAPSHOT_MEMORY_ON_INDEPENDENT_DISK = 13018
VIX_E_SNAPSHOT_MAXSNAPSHOTS = 13019
VIX_E_SNAPSHOT_MIN_FREE_SPACE = 13020
VIX_E_SNAPSHOT_HIERARCHY_TOODEEP = 13021
VIX_E_HOST_DISK_INVALID_VALUE = 14003
VIX_E_HOST_DISK_SECTORSIZE = 14004
VIX_E_HOST_FILE_ERROR_EOF = 14005
VIX_E_HOST_NETBLKDEV_HANDSHAKE = 14006
VIX_E_HOST_SOCKET_CREATION_ERROR = 14007
VIX_E_HOST_SERVER_NOT_FOUND = 14008
VIX_E_HOST_NETWORK_CONN_REFUSED = 14009
VIX_E_HOST_TCP_SOCKET_ERROR = 14010
VIX_E_HOST_TCP_CONN_LOST = 14011
VIX_E_HOST_NBD_HASHFILE_VOLUME = 14012
VIX_E_HOST_NBD_HASHFILE_INIT = 14013
VIX_E_DISK_INVAL = 16000
VIX_E_DISK_NOINIT = 16001
VIX_E_DISK_NOIO = 16002
VIX_E_DISK_PARTIALCHAIN = 16003
VIX_E_DISK_NEEDSREPAIR = 16006
VIX_E_DISK_OUTOFRANGE = 16007
VIX_E_DISK_CID_MISMATCH = 16008
VIX_E_DISK_CANTSHRINK = 16009
VIX_E_DISK_PARTMISMATCH = 16010
VIX_E_DISK_UNSUPPORTEDDISKVERSION = 16011
VIX_E_DISK_OPENPARENT = 16012
VIX_E_DISK_NOTSUPPORTED = 16013
VIX_E_DISK_NEEDKEY = 16014
VIX_E_DISK_NOKEYOVERRIDE = 16015
VIX_E_DISK_NOTENCRYPTED = 16016
VIX_E_DISK_NOKEY = 16017
VIX_E_DISK_INVALIDPARTITIONTABLE = 16018
VIX_E_DISK_NOTNORMAL = 16019
VIX_E_DISK_NOTENCDESC = 16020
VIX_E_DISK_NEEDVMFS = 16022
VIX_E_DISK_RAWTOOBIG = 16024
VIX_E_DISK_TOOMANYOPENFILES = 16027
VIX_E_DISK_TOOMANYREDO = 16028
VIX_E_DISK_RAWTOOSMALL = 16029
VIX_E_DISK_INVALIDCHAIN = 16030
VIX_E_DISK_KEY_NOTFOUND = 16052
VIX_E_DISK_SUBSYSTEM_INIT_FAIL = 16053
VIX_E_DISK_INVALID_CONNECTION = 16054
VIX_E_DISK_ENCODING = 16061
VIX_E_DISK_CANTREPAIR = 16062
VIX_E_DISK_INVALIDDISK = 16063
VIX_E_DISK_NOLICENSE = 16064
VIX_E_DISK_NODEVICE = 16065
VIX_E_DISK_UNSUPPORTEDDEVICE = 16066
VIX_E_CRYPTO_UNKNOWN_ALGORITHM = 17000
VIX_E_CRYPTO_BAD_BUFFER_SIZE = 17001
VIX_E_CRYPTO_INVALID_OPERATION = 17002
VIX_E_CRYPTO_RANDOM_DEVICE = 17003
VIX_E_CRYPTO_NEED_PASSWORD = 17004
VIX_E_CRYPTO_BAD_PASSWORD = 17005
VIX_E_CRYPTO_NOT_IN_DICTIONARY = 17006
VIX_E_CRYPTO_NO_CRYPTO = 17007
VIX_E_CRYPTO_ERROR = 17008
VIX_E_CRYPTO_BAD_FORMAT = 17009
VIX_E_CRYPTO_LOCKED = 17010
VIX_E_CRYPTO_EMPTY = 17011
VIX_E_CRYPTO_KEYSAFE_LOCATOR = 17012
VIX_E_CANNOT_CONNECT_TO_HOST = 18000
VIX_E_NOT_FOR_REMOTE_HOST = 18001
VIX_E_INVALID_HOSTNAME_SPECIFICATION = 18002
VIX_E_SCREEN_CAPTURE_ERROR = 19000
VIX_E_SCREEN_CAPTURE_BAD_FORMAT = 19001
VIX_E_SCREEN_CAPTURE_COMPRESSION_FAIL = 19002
VIX_E_SCREEN_CAPTURE_LARGE_DATA = 19003
VIX_E_GUEST_VOLUMES_NOT_FROZEN = 20000
VIX_E_NOT_A_FILE = 20001
VIX_E_NOT_A_DIRECTORY = 20002
VIX_E_NO_SUCH_PROCESS = 20003
VIX_E_FILE_NAME_TOO_LONG = 20004
VIX_E_TOOLS_INSTALL_NO_IMAGE = 21000
VIX_E_TOOLS_INSTALL_IMAGE_INACCESIBLE = 21001
VIX_E_TOOLS_INSTALL_NO_DEVICE = 21002
VIX_E_TOOLS_INSTALL_DEVICE_NOT_CONNECTED = 21003
VIX_E_TOOLS_INSTALL_CANCELLED = 21004
VIX_E_TOOLS_INSTALL_INIT_FAILED = 21005
VIX_E_TOOLS_INSTALL_AUTO_NOT_SUPPORTED = 21006
VIX_E_TOOLS_INSTALL_GUEST_NOT_READY = 21007
VIX_E_TOOLS_INSTALL_SIG_CHECK_FAILED = 21008
VIX_E_TOOLS_INSTALL_ERROR = 21009
VIX_E_TOOLS_INSTALL_ALREADY_UP_TO_DATE = 21010
VIX_E_TOOLS_INSTALL_IN_PROGRESS = 21011
VIX_E_WRAPPER_WORKSTATION_NOT_INSTALLED = 22001
VIX_E_WRAPPER_VERSION_NOT_FOUND = 22002
VIX_E_WRAPPER_SERVICEPROVIDER_NOT_FOUND = 22003
VIX_E_WRAPPER_PLAYER_NOT_INSTALLED = 22004
VIX_E_WRAPPER_RUNTIME_NOT_INSTALLED = 22005
VIX_E_WRAPPER_MULTIPLE_SERVICEPROVIDERS = 22006
VIX_E_MNTAPI_MOUNTPT_NOT_FOUND = 24000
VIX_E_MNTAPI_MOUNTPT_IN_USE = 24001
VIX_E_MNTAPI_DISK_NOT_FOUND = 24002
VIX_E_MNTAPI_DISK_NOT_MOUNTED = 24003
VIX_E_MNTAPI_DISK_IS_MOUNTED = 24004
VIX_E_MNTAPI_DISK_NOT_SAFE = 24005
VIX_E_MNTAPI_DISK_CANT_OPEN = 24006
VIX_E_MNTAPI_CANT_READ_PARTS = 24007
VIX_E_MNTAPI_UMOUNT_APP_NOT_FOUND = 24008
VIX_E_MNTAPI_UMOUNT = 24009
VIX_E_MNTAPI_NO_MOUNTABLE_PARTITONS = 24010
VIX_E_MNTAPI_PARTITION_RANGE = 24011
VIX_E_MNTAPI_PERM = 24012
VIX_E_MNTAPI_DICT = 24013
VIX_E_MNTAPI_DICT_LOCKED = 24014
VIX_E_MNTAPI_OPEN_HANDLES = 24015
VIX_E_MNTAPI_CANT_MAKE_VAR_DIR = 24016
VIX_E_MNTAPI_NO_ROOT = 24017
VIX_E_MNTAPI_LOOP_FAILED = 24018
VIX_E_MNTAPI_DAEMON = 24019
VIX_E_MNTAPI_INTERNAL = 24020
VIX_E_MNTAPI_SYSTEM = 24021
VIX_E_MNTAPI_NO_CONNECTION_DETAILS = 24022
VIX_E_MNTAPI_INCOMPATIBLE_VERSION = 24300
VIX_E_MNTAPI_OS_ERROR = 24301
VIX_E_MNTAPI_DRIVE_LETTER_IN_USE = 24302
VIX_E_MNTAPI_DRIVE_LETTER_ALREADY_ASSIGNED = 24303
VIX_E_MNTAPI_VOLUME_NOT_MOUNTED = 24304
VIX_E_MNTAPI_VOLUME_ALREADY_MOUNTED = 24305
VIX_E_MNTAPI_FORMAT_FAILURE = 24306
VIX_E_MNTAPI_NO_DRIVER = 24307
VIX_E_MNTAPI_ALREADY_OPENED = 24308
VIX_E_MNTAPI_ITEM_NOT_FOUND = 24309
VIX_E_MNTAPI_UNSUPPROTED_BOOT_LOADER = 24310
VIX_E_MNTAPI_UNSUPPROTED_OS = 24311
VIX_E_MNTAPI_CODECONVERSION = 24312
VIX_E_MNTAPI_REGWRITE_ERROR = 24313
VIX_E_MNTAPI_UNSUPPORTED_FT_VOLUME = 24314
VIX_E_MNTAPI_PARTITION_NOT_FOUND = 24315
VIX_E_MNTAPI_PUTFILE_ERROR = 24316
VIX_E_MNTAPI_GETFILE_ERROR = 24317
VIX_E_MNTAPI_REG_NOT_OPENED = 24318
VIX_E_MNTAPI_REGDELKEY_ERROR = 24319
VIX_E_MNTAPI_CREATE_PARTITIONTABLE_ERROR = 24320
VIX_E_MNTAPI_OPEN_FAILURE = 24321
VIX_E_MNTAPI_VOLUME_NOT_WRITABLE = 24322
VIX_E_NET_HTTP_UNSUPPORTED_PROTOCOL = 30001
VIX_E_NET_HTTP_URL_MALFORMAT = 30003
VIX_E_NET_HTTP_COULDNT_RESOLVE_PROXY = 30005
VIX_E_NET_HTTP_COULDNT_RESOLVE_HOST = 30006
VIX_E_NET_HTTP_COULDNT_CONNECT = 30007
VIX_E_NET_HTTP_HTTP_RETURNED_ERROR = 30022
VIX_E_NET_HTTP_OPERATION_TIMEDOUT = 30028
VIX_E_NET_HTTP_SSL_CONNECT_ERROR = 30035
VIX_E_NET_HTTP_TOO_MANY_REDIRECTS = 30047
VIX_E_NET_HTTP_TRANSFER = 30200
VIX_E_NET_HTTP_SSL_SECURITY = 30201
VIX_E_NET_HTTP_GENERIC = 30202
VIX_PROPERTYTYPE_ANY = 0
VIX_PROPERTYTYPE_INTEGER = 1
VIX_PROPERTYTYPE_STRING = 2
VIX_PROPERTYTYPE_BOOL = 3
VIX_PROPERTYTYPE_HANDLE = 4
VIX_PROPERTYTYPE_INT64 = 5
VIX_PROPERTYTYPE_BLOB = 6
VIX_PROPERTY_NONE = 0
VIX_PROPERTY_META_DATA_CONTAINER = 2
VIX_PROPERTY_HOST_HOSTTYPE = 50
VIX_PROPERTY_HOST_API_VERSION = 51
VIX_PROPERTY_HOST_SOFTWARE_VERSION = 52
VIX_PROPERTY_VM_NUM_VCPUS = 101
VIX_PROPERTY_VM_VMX_PATHNAME = 103
VIX_PROPERTY_VM_VMTEAM_PATHNAME = 105
VIX_PROPERTY_VM_MEMORY_SIZE = 106
VIX_PROPERTY_VM_READ_ONLY = 107
VIX_PROPERTY_VM_NAME = 108
VIX_PROPERTY_VM_GUESTOS = 109
VIX_PROPERTY_VM_IN_VMTEAM = 128
VIX_PROPERTY_VM_POWER_STATE = 129
VIX_PROPERTY_VM_TOOLS_STATE = 152
VIX_PROPERTY_VM_IS_RUNNING = 196
VIX_PROPERTY_VM_SUPPORTED_FEATURES = 197
VIX_PROPERTY_VM_IS_RECORDING = 236
VIX_PROPERTY_VM_IS_REPLAYING = 237
VIX_PROPERTY_JOB_RESULT_ERROR_CODE = 3000
VIX_PROPERTY_JOB_RESULT_VM_IN_GROUP = 3001
VIX_PROPERTY_JOB_RESULT_USER_MESSAGE = 3002
VIX_PROPERTY_JOB_RESULT_EXIT_CODE = 3004
VIX_PROPERTY_JOB_RESULT_COMMAND_OUTPUT = 3005
VIX_PROPERTY_JOB_RESULT_HANDLE = 3010
VIX_PROPERTY_JOB_RESULT_GUEST_OBJECT_EXISTS = 3011
VIX_PROPERTY_JOB_RESULT_GUEST_PROGRAM_ELAPSED_TIME = 3017
VIX_PROPERTY_JOB_RESULT_GUEST_PROGRAM_EXIT_CODE = 3018
VIX_PROPERTY_JOB_RESULT_ITEM_NAME = 3035
VIX_PROPERTY_JOB_RESULT_FOUND_ITEM_DESCRIPTION = 3036
VIX_PROPERTY_JOB_RESULT_SHARED_FOLDER_COUNT = 3046
VIX_PROPERTY_JOB_RESULT_SHARED_FOLDER_HOST = 3048
VIX_PROPERTY_JOB_RESULT_SHARED_FOLDER_FLAGS = 3049
VIX_PROPERTY_JOB_RESULT_PROCESS_ID = 3051
VIX_PROPERTY_JOB_RESULT_PROCESS_OWNER = 3052
VIX_PROPERTY_JOB_RESULT_PROCESS_COMMAND = 3053
VIX_PROPERTY_JOB_RESULT_FILE_FLAGS = 3054
VIX_PROPERTY_JOB_RESULT_PROCESS_START_TIME = 3055
VIX_PROPERTY_JOB_RESULT_VM_VARIABLE_STRING = 3056
VIX_PROPERTY_JOB_RESULT_PROCESS_BEING_DEBUGGED = 3057
VIX_PROPERTY_JOB_RESULT_SCREEN_IMAGE_SIZE = 3058
VIX_PROPERTY_JOB_RESULT_SCREEN_IMAGE_DATA = 3059
VIX_PROPERTY_JOB_RESULT_FILE_SIZE = 3061
VIX_PROPERTY_JOB_RESULT_FILE_MOD_TIME = 3062
VIX_PROPERTY_JOB_RESULT_EXTRA_ERROR_INFO = 3084
VIX_PROPERTY_FOUND_ITEM_LOCATION = 4010
VIX_PROPERTY_SNAPSHOT_DISPLAYNAME = 4200
VIX_PROPERTY_SNAPSHOT_DESCRIPTION = 4201
VIX_PROPERTY_SNAPSHOT_POWERSTATE = 4205
VIX_PROPERTY_SNAPSHOT_IS_REPLAYABLE = 4207
VIX_PROPERTY_GUEST_SHAREDFOLDERS_SHARES_PATH = 4525
VIX_PROPERTY_VM_ENCRYPTION_PASSWORD = 7001
VIX_EVENTTYPE_JOB_COMPLETED = 2
VIX_EVENTTYPE_JOB_PROGRESS = 3
VIX_EVENTTYPE_FIND_ITEM = 8
VIX_EVENTTYPE_CALLBACK_SIGNALLED = 2
VIX_FILE_ATTRIBUTES_DIRECTORY = 0x0001
VIX_FILE_ATTRIBUTES_SYMLINK = 0x0002
VIX_HOSTOPTION_USE_EVENT_PUMP = 0x0008
VIX_SERVICEPROVIDER_DEFAULT = 1
VIX_SERVICEPROVIDER_VMWARE_SERVER = 2
VIX_SERVICEPROVIDER_VMWARE_WORKSTATION = 3
VIX_SERVICEPROVIDER_VMWARE_PLAYER = 4
VIX_SERVICEPROVIDER_VMWARE_VI_SERVER = 10
VIX_API_VERSION = -1
VIX_FIND_RUNNING_VMS = 1
VIX_FIND_REGISTERED_VMS = 4
VIX_VMOPEN_NORMAL = 0x0
VIX_PUMPEVENTOPTION_NONE = 0
VIX_VMPOWEROP_NORMAL = 0
VIX_VMPOWEROP_FROM_GUEST = 0x0004
VIX_VMPOWEROP_SUPPRESS_SNAPSHOT_POWERON = 0x0080
VIX_VMPOWEROP_LAUNCH_GUI = 0x0200
VIX_VMPOWEROP_START_VM_PAUSED = 0x1000
VIX_VMDELETE_DISK_FILES = 0x0002
VIX_POWERSTATE_POWERING_OFF = 0x0001
VIX_POWERSTATE_POWERED_OFF = 0x0002
VIX_POWERSTATE_POWERING_ON = 0x0004
VIX_POWERSTATE_POWERED_ON = 0x0008
VIX_POWERSTATE_SUSPENDING = 0x0010
VIX_POWERSTATE_SUSPENDED = 0x0020
VIX_POWERSTATE_TOOLS_RUNNING = 0x0040
VIX_POWERSTATE_RESETTING = 0x0080
VIX_POWERSTATE_BLOCKED_ON_MSG = 0x0100
VIX_POWERSTATE_PAUSED = 0x0200
VIX_POWERSTATE_RESUMING = 0x0800
VIX_TOOLSSTATE_UNKNOWN = 0x0001
VIX_TOOLSSTATE_RUNNING = 0x0002
VIX_TOOLSSTATE_NOT_INSTALLED = 0x0004
VIX_VM_SUPPORT_SHARED_FOLDERS = 0x0001
VIX_VM_SUPPORT_MULTIPLE_SNAPSHOTS = 0x0002
VIX_VM_SUPPORT_TOOLS_INSTALL = 0x0004
VIX_VM_SUPPORT_HARDWARE_UPGRADE = 0x0008
VIX_LOGIN_IN_GUEST_REQUIRE_INTERACTIVE_ENVIRONMENT = 0x08
VIX_RUNPROGRAM_RETURN_IMMEDIATELY = 0x0001
VIX_RUNPROGRAM_ACTIVATE_WINDOW = 0x0002
VIX_VM_GUEST_VARIABLE = 1
VIX_VM_CONFIG_RUNTIME_ONLY = 2
VIX_GUEST_ENVIRONMENT_VARIABLE = 3
VIX_SNAPSHOT_REMOVE_CHILDREN = 0x0001
VIX_SNAPSHOT_INCLUDE_MEMORY = 0x0002
VIX_SHAREDFOLDER_WRITE_ACCESS = 0x04
VIX_CAPTURESCREENFORMAT_PNG = 0x01
VIX_CAPTURESCREENFORMAT_PNG_NOCOMPRESS = 0x02
VIX_CLONETYPE_FULL = 0
VIX_CLONETYPE_LINKED = 1
VIX_INSTALLTOOLS_MOUNT_TOOLS_INSTALLER = 0x00
VIX_INSTALLTOOLS_AUTO_UPGRADE = 0x01
VIX_INSTALLTOOLS_RETURN_IMMEDIATELY = 0x02

vix.Vix_GetErrorText.restype = ctypes.c_char_p
vix.Vix_GetErrorText.argtypes = [VixError, ctypes.c_char_p]
Vix_GetErrorText = vix.Vix_GetErrorText

vix.Vix_ReleaseHandle.restype = None
vix.Vix_ReleaseHandle.argtypes = [VixHandle]
Vix_ReleaseHandle = vix.Vix_ReleaseHandle

vix.Vix_AddRefHandle.restype = None
vix.Vix_AddRefHandle.argtypes = [VixHandle]
Vix_AddRefHandle = vix.Vix_AddRefHandle

vix.Vix_GetHandleType.restype = VixHandleType
vix.Vix_GetHandleType.argtypes = [VixHandle]
vix.Vix_GetProperties.restype = VixError

vix.Vix_GetProperties.argtypes = [VixHandle, VixPropertyID]
vix.Vix_GetPropertyType.restype = VixError
Vix_GetProperties = vix.Vix_GetProperties

vix.Vix_GetPropertyType.argtypes = [VixHandle, VixPropertyID,
                                    ctypes.POINTER(VixPropertyType)]
vix.Vix_FreeBuffer.restype = None
vix.Vix_FreeBuffer.argtypes = [ctypes.c_void_p]
Vix_FreeBuffer = vix.Vix_FreeBuffer

vix.VixHost_Connect.restype = VixHandle
vix.VixHost_Connect.argtypes = [ctypes.c_int, VixServiceProvider,
                                ctypes.c_char_p, ctypes.c_int,
                                ctypes.c_char_p, ctypes.c_char_p,
                                VixHostOptions, VixHandle,
                                ctypes.POINTER(VixEventProc),
                                ctypes.c_void_p]
VixHost_Connect = vix.VixHost_Connect

vix.VixHost_Disconnect.restype = None
vix.VixHost_Disconnect.argtypes = [VixHandle]
VixHost_Disconnect = vix.VixHost_Disconnect

vix.VixHost_RegisterVM.restype = VixHandle
vix.VixHost_RegisterVM.argtypes = [VixHandle, ctypes.c_char_p,
                                   ctypes.POINTER(VixEventProc),
                                   ctypes.c_void_p]
VixHost_RegisterVM = vix.VixHost_RegisterVM

vix.VixHost_UnregisterVM.restype = VixHandle
vix.VixHost_UnregisterVM.argtypes = [VixHandle, ctypes.c_char_p,
                                     ctypes.POINTER(VixEventProc),
                                     ctypes.c_void_p]
VixHost_UnregisterVM = vix.VixHost_UnregisterVM

vix.VixHost_FindItems.restype = VixHandle
vix.VixHost_FindItems.argtypes = [VixHandle, VixFindItemType, VixHandle,
                                  ctypes.c_int32, VixEventProc,
                                  ctypes.c_void_p]
VixHost_FindItems = vix.VixHost_FindItems

vix.VixHost_OpenVM.restype = VixHandle
vix.VixHost_OpenVM.argtypes = [VixHandle, ctypes.c_char_p, VixVMOpenOptions,
                               VixHandle, ctypes.POINTER(VixEventProc),
                               ctypes.c_void_p]

vix.VixPropertyList_AllocPropertyList.restype = VixError
vix.VixPropertyList_AllocPropertyList.argtypes = [VixHandle,
                                                  ctypes.POINTER(VixHandle),
                                                  ctypes.c_int]
VixPropertyList_AllocPropertyList = vix.VixPropertyList_AllocPropertyList

vix.VixVM_Open.restype = VixHandle
vix.VixVM_Open.argtypes = [VixHandle, ctypes.c_char_p,
                           ctypes.POINTER(VixEventProc), ctypes.c_void_p]
VixVM_Open = vix.VixVM_Open

vix.VixVM_PowerOn.restype = VixHandle
vix.VixVM_PowerOn.argtypes = [VixHandle, VixVMPowerOpOptions,
                              VixHandle, ctypes.POINTER(VixEventProc),
                              ctypes.c_void_p]
VixVM_PowerOn = vix.VixVM_PowerOn

vix.VixVM_PowerOff.restype = VixHandle
vix.VixVM_PowerOff.argtypes = [VixHandle, VixVMPowerOpOptions,
                               ctypes.POINTER(VixEventProc),
                               ctypes.c_void_p]
VixVM_PowerOff = vix.VixVM_PowerOff

vix.VixVM_Reset.restype = VixHandle
vix.VixVM_Reset.argtypes = [VixHandle, VixVMPowerOpOptions,
                            ctypes.POINTER(VixEventProc),
                            ctypes.c_void_p]
VixVM_Reset = vix.VixVM_Reset

vix.VixVM_Suspend.restype = VixHandle
vix.VixVM_Suspend.argtypes = [VixHandle, VixVMPowerOpOptions,
                              ctypes.POINTER(VixEventProc),
                              ctypes.c_void_p]
VixVM_Suspend = vix.VixVM_Suspend

vix.VixVM_Pause.restype = VixHandle
vix.VixVM_Pause.argtypes = [VixHandle, ctypes.c_int, VixHandle,
                            ctypes.POINTER(VixEventProc),
                            ctypes.c_void_p]
VixVM_Pause = vix.VixVM_Pause

vix.VixVM_Unpause.restype = VixHandle
vix.VixVM_Unpause.argtypes = [VixHandle, ctypes.c_int,
                              VixHandle, ctypes.POINTER(VixEventProc),
                              ctypes.c_void_p]
VixVM_Unpause = vix.VixVM_Unpause

vix.VixVM_Delete.restype = VixHandle
vix.VixVM_Delete.argtypes = [VixHandle, VixVMDeleteOptions,
                             ctypes.POINTER(VixEventProc),
                             ctypes.c_void_p]
VixVM_Delete = vix.VixVM_Delete

#vix.VixVM_BeginRecording.restype = VixHandle
#vix.VixVM_BeginRecording.argtypes = [VixHandle, ctypes.c_char_p,
#                                     ctypes.c_char_p, ctypes.c_int,
#                                     VixHandle, ctypes.POINTER(VixEventProc),
#                                     ctypes.c_void_p]

#vix.VixVM_EndRecording.restype = VixHandle
#vix.VixVM_EndRecording.argtypes = [VixHandle, ctypes.c_int,
#                                   VixHandle, ctypes.POINTER(VixEventProc),
#                                   ctypes.c_void_p]

#vix.VixVM_BeginReplay.restype = VixHandle
#vix.VixVM_BeginReplay.argtypes = [VixHandle, VixHandle, ctypes.c_int,
#                                  VixHandle, ctypes.POINTER(VixEventProc),
#                                  ctypes.c_void_p]

#vix.VixVM_EndReplay.restype = VixHandle
#vix.VixVM_EndReplay.argtypes = [VixHandle, ctypes.c_int,
#                                VixHandle, ctypes.POINTER(VixEventProc),
#                                ctypes.c_void_p]

vix.VixVM_WaitForToolsInGuest.restype = VixHandle
vix.VixVM_WaitForToolsInGuest.argtypes = [VixHandle, ctypes.c_int,
                                          ctypes.POINTER(VixEventProc),
                                          ctypes.c_void_p]
VixVM_WaitForToolsInGuest = vix.VixVM_WaitForToolsInGuest

vix.VixVM_LoginInGuest.restype = VixHandle
vix.VixVM_LoginInGuest.argtypes = [VixHandle, ctypes.c_char_p,
                                   ctypes.c_char_p, ctypes.c_int,
                                   ctypes.POINTER(VixEventProc),
                                   ctypes.c_void_p]
VixVM_LoginInGuest = vix.VixVM_LoginInGuest

vix.VixVM_LogoutFromGuest.restype = VixHandle
vix.VixVM_LogoutFromGuest.argtypes = [VixHandle, ctypes.POINTER(VixEventProc),
                                      ctypes.c_void_p]

vix.VixVM_RunProgramInGuest.restype = VixHandle
vix.VixVM_RunProgramInGuest.argtypes = [VixHandle, ctypes.c_char_p,
                                        ctypes.c_char_p, VixRunProgramOptions,
                                        VixHandle,
                                        ctypes.POINTER(VixEventProc),
                                        ctypes.c_void_p]
VixVM_RunProgramInGuest = vix.VixVM_RunProgramInGuest

vix.VixVM_ListProcessesInGuest.restype = VixHandle
vix.VixVM_ListProcessesInGuest.argtypes = [VixHandle, ctypes.c_int,
                                           ctypes.POINTER(VixEventProc),
                                           ctypes.c_void_p]
VixVM_ListProcessesInGuest = vix.VixVM_ListProcessesInGuest

vix.VixVM_KillProcessInGuest.restype = VixHandle
vix.VixVM_KillProcessInGuest.argtypes = [VixHandle, ctypes.c_uint64,
                                         ctypes.c_int,
                                         ctypes.POINTER(VixEventProc),
                                         ctypes.c_void_p]

vix.VixVM_RunScriptInGuest.restype = VixHandle
vix.VixVM_RunScriptInGuest.argtypes = [VixHandle, ctypes.c_char_p,
                                       ctypes.c_char_p, VixRunProgramOptions,
                                       VixHandle, ctypes.POINTER(VixEventProc),
                                       ctypes.c_void_p]

vix.VixVM_CopyFileFromHostToGuest.restype = VixHandle
vix.VixVM_CopyFileFromHostToGuest.argtypes = [VixHandle, ctypes.c_char_p,
                                              ctypes.c_char_p, ctypes.c_int,
                                              VixHandle,
                                              ctypes.POINTER(VixEventProc),
                                              ctypes.c_void_p]
VixVM_CopyFileFromHostToGuest = vix.VixVM_CopyFileFromHostToGuest

vix.VixVM_CopyFileFromGuestToHost.restype = VixHandle
vix.VixVM_CopyFileFromGuestToHost.argtypes = [VixHandle, ctypes.c_char_p,
                                              ctypes.c_char_p, ctypes.c_int,
                                              VixHandle,
                                              ctypes.POINTER(VixEventProc),
                                              ctypes.c_void_p]
VixVM_CopyFileFromGuestToHost = vix.VixVM_CopyFileFromGuestToHost

vix.VixVM_DeleteFileInGuest.restype = VixHandle
vix.VixVM_DeleteFileInGuest.argtypes = [VixHandle, ctypes.c_char_p,
                                        ctypes.POINTER(VixEventProc),
                                        ctypes.c_void_p]
VixVM_DeleteFileInGuest = vix.VixVM_DeleteFileInGuest

vix.VixVM_FileExistsInGuest.restype = VixHandle
vix.VixVM_FileExistsInGuest.argtypes = [VixHandle, ctypes.c_char_p,
                                        ctypes.POINTER(VixEventProc),
                                        ctypes.c_void_p]
VixVM_FileExistsInGuest = vix.VixVM_FileExistsInGuest

vix.VixVM_RenameFileInGuest.restype = VixHandle
vix.VixVM_RenameFileInGuest.argtypes = [VixHandle, ctypes.c_char_p,
                                        ctypes.c_char_p, ctypes.c_int,
                                        VixHandle,
                                        ctypes.POINTER(VixEventProc),
                                        ctypes.c_void_p]

vix.VixVM_CreateTempFileInGuest.restype = VixHandle
vix.VixVM_CreateTempFileInGuest.argtypes = [VixHandle,
                                            ctypes.c_int, VixHandle,
                                            ctypes.POINTER(VixEventProc),
                                            ctypes.c_void_p]

vix.VixVM_GetFileInfoInGuest.restype = VixHandle
vix.VixVM_GetFileInfoInGuest.argtypes = [VixHandle, ctypes.c_char_p,
                                         ctypes.POINTER(VixEventProc),
                                         ctypes.c_void_p]

vix.VixVM_ListDirectoryInGuest.restype = VixHandle
vix.VixVM_ListDirectoryInGuest.argtypes = [VixHandle, ctypes.c_char_p,
                                           ctypes.c_int,
                                           ctypes.POINTER(VixEventProc),
                                           ctypes.c_void_p]

vix.VixVM_CreateDirectoryInGuest.restype = VixHandle
vix.VixVM_CreateDirectoryInGuest.argtypes = [VixHandle, ctypes.c_char_p,
                                             VixHandle,
                                             ctypes.POINTER(VixEventProc),
                                             ctypes.c_void_p]

vix.VixVM_DeleteDirectoryInGuest.restype = VixHandle
vix.VixVM_DeleteDirectoryInGuest.argtypes = [VixHandle,
                                             ctypes.c_char_p,
                                             ctypes.c_int,
                                             ctypes.POINTER(VixEventProc),
                                             ctypes.c_void_p]
VixVM_DeleteDirectoryInGuest = vix.VixVM_DeleteDirectoryInGuest

vix.VixVM_DirectoryExistsInGuest.restype = VixHandle
vix.VixVM_DirectoryExistsInGuest.argtypes = [VixHandle, ctypes.c_char_p,
                                             ctypes.POINTER(VixEventProc),
                                             ctypes.c_void_p]
VixVM_DirectoryExistsInGuest = vix.VixVM_DirectoryExistsInGuest

vix.VixVM_ReadVariable.restype = VixHandle
vix.VixVM_ReadVariable.argtypes = [VixHandle, ctypes.c_int, ctypes.c_char_p,
                                   ctypes.c_int, ctypes.POINTER(VixEventProc),
                                   ctypes.c_void_p]
VixVM_ReadVariable = vix.VixVM_ReadVariable

vix.VixVM_WriteVariable.restype = VixHandle
vix.VixVM_WriteVariable.argtypes = [VixHandle, ctypes.c_int, ctypes.c_char_p,
                                    ctypes.c_char_p, ctypes.c_int,
                                    ctypes.POINTER(VixEventProc),
                                    ctypes.c_void_p]
VixVM_WriteVariable = vix.VixVM_WriteVariable

vix.VixVM_GetNumRootSnapshots.restype = VixError
vix.VixVM_GetNumRootSnapshots.argtypes = [VixHandle,
                                          ctypes.POINTER(ctypes.c_int)]

vix.VixVM_GetRootSnapshot.restype = VixError
vix.VixVM_GetRootSnapshot.argtypes = [VixHandle, ctypes.c_int,
                                      ctypes.POINTER(VixHandle)]

vix.VixVM_GetCurrentSnapshot.restype = VixError
vix.VixVM_GetCurrentSnapshot.argtypes = [VixHandle, ctypes.POINTER(VixHandle)]

vix.VixVM_GetNamedSnapshot.restype = VixError
vix.VixVM_GetNamedSnapshot.argtypes = [VixHandle, ctypes.c_char_p,
                                       ctypes.POINTER(VixHandle)]

vix.VixVM_RemoveSnapshot.restype = VixHandle
vix.VixVM_RemoveSnapshot.argtypes = [VixHandle, VixHandle,
                                     VixRemoveSnapshotOptions,
                                     ctypes.POINTER(VixEventProc),
                                     ctypes.c_void_p]
VixVM_RemoveSnapshot = vix.VixVM_RemoveSnapshot

vix.VixVM_RevertToSnapshot.restype = VixHandle
vix.VixVM_RevertToSnapshot.argtypes = [VixHandle, VixHandle,
                                       VixVMPowerOpOptions, VixHandle,
                                       ctypes.POINTER(VixEventProc),
                                       ctypes.c_void_p]

vix.VixVM_CreateSnapshot.restype = VixHandle
vix.VixVM_CreateSnapshot.argtypes = [VixHandle, ctypes.c_char_p,
                                     ctypes.c_char_p, VixCreateSnapshotOptions,
                                     VixHandle, ctypes.POINTER(VixEventProc),
                                     ctypes.c_void_p]
VixVM_CreateSnapshot = vix.VixVM_CreateSnapshot

vix.VixVM_EnableSharedFolders.restype = VixHandle
vix.VixVM_EnableSharedFolders.argtypes = [VixHandle, ctypes.c_byte,
                                          ctypes.c_int,
                                          ctypes.POINTER(VixEventProc),
                                          ctypes.c_void_p]

vix.VixVM_GetNumSharedFolders.restype = VixHandle
vix.VixVM_GetNumSharedFolders.argtypes = [VixHandle,
                                          ctypes.POINTER(VixEventProc),
                                          ctypes.c_void_p]

vix.VixVM_GetSharedFolderState.restype = VixHandle
vix.VixVM_GetSharedFolderState.argtypes = [VixHandle, ctypes.c_int,
                                           ctypes.POINTER(VixEventProc),
                                           ctypes.c_void_p]

vix.VixVM_SetSharedFolderState.restype = VixHandle
vix.VixVM_SetSharedFolderState.argtypes = [VixHandle, ctypes.c_char_p,
                                           ctypes.c_char_p,
                                           VixMsgSharedFolderOptions,
                                           ctypes.POINTER(VixEventProc),
                                           ctypes.c_void_p]

vix.VixVM_AddSharedFolder.restype = VixHandle
vix.VixVM_AddSharedFolder.argtypes = [VixHandle, ctypes.c_char_p,
                                      ctypes.c_char_p,
                                      VixMsgSharedFolderOptions,
                                      ctypes.POINTER(VixEventProc),
                                      ctypes.c_void_p]

vix.VixVM_RemoveSharedFolder.restype = VixHandle
vix.VixVM_RemoveSharedFolder.argtypes = [VixHandle, ctypes.c_char_p,
                                         ctypes.c_int,
                                         ctypes.POINTER(VixEventProc),
                                         ctypes.c_void_p]

vix.VixVM_CaptureScreenImage.restype = VixHandle
vix.VixVM_CaptureScreenImage.argtypes = [VixHandle, ctypes.c_int,
                                         VixHandle,
                                         ctypes.POINTER(VixEventProc),
                                         ctypes.c_void_p]
VixVM_CaptureScreenImage = vix.VixVM_CaptureScreenImage

vix.VixVM_Clone.restype = VixHandle
vix.VixVM_Clone.argtypes = [VixHandle, VixHandle, VixCloneType,
                            ctypes.c_char_p, ctypes.c_int,
                            VixHandle, ctypes.POINTER(VixEventProc),
                            ctypes.c_void_p]
VixVM_Clone = vix.VixVM_Clone

vix.VixVM_UpgradeVirtualHardware.restype = VixHandle
vix.VixVM_UpgradeVirtualHardware.argtypes = [VixHandle, ctypes.c_int,
                                             ctypes.POINTER(VixEventProc),
                                             ctypes.c_void_p]

vix.VixVM_InstallTools.restype = VixHandle
vix.VixVM_InstallTools.argtypes = [VixHandle, ctypes.c_int, ctypes.c_char_p,
                                   ctypes.POINTER(VixEventProc),
                                   ctypes.c_void_p]

vix.VixJob_Wait.restype = VixError
vix.VixJob_Wait.argtypes = [VixHandle, VixPropertyID]
VixJob_Wait = vix.VixJob_Wait

vix.VixJob_CheckCompletion.restype = VixError
vix.VixJob_CheckCompletion.argtypes = [VixHandle,
                                       ctypes.POINTER(ctypes.c_byte)]
VixJob_CheckCompletion = vix.VixJob_CheckCompletion

vix.VixJob_GetError.restype = VixError
vix.VixJob_GetError.argtypes = [VixHandle]
VixJob_GetError = vix.VixJob_GetError

vix.VixJob_GetNumProperties.restype = ctypes.c_int
vix.VixJob_GetNumProperties.argtypes = [VixHandle, ctypes.c_int]
VixJob_GetNumProperties = vix.VixJob_GetNumProperties

vix.VixJob_GetNthProperties.restype = VixError
vix.VixJob_GetNthProperties.argtypes = [VixHandle, ctypes.c_int, ctypes.c_int]
VixJob_GetNthProperties = vix.VixJob_GetNthProperties

vix.VixSnapshot_GetNumChildren.restype = VixError
vix.VixSnapshot_GetNumChildren.argtypes = [VixHandle,
                                           ctypes.POINTER(ctypes.c_int)]

vix.VixSnapshot_GetChild.restype = VixError
vix.VixSnapshot_GetChild.argtypes = [VixHandle, ctypes.c_int,
                                     ctypes.POINTER(VixHandle)]

vix.VixSnapshot_GetParent.restype = VixError
vix.VixSnapshot_GetParent.argtypes = [VixHandle, ctypes.POINTER(VixHandle)]
