import time
from functools import wraps

import requests
from enum import IntEnum

try:
    import gevent

    do_sleep = gevent.sleep
except ImportError:
    do_sleep = time.sleep

from pyVmomi import vim, Version as pyVmomi_version
from pyVim.connect import SmartConnect
import logging
from requests.exceptions import ConnectionError

requests.packages.urllib3.disable_warnings()

__author__ = 'Eddi'

logging.basicConfig(filename='vshpere_client.log', level=logging.DEBUG)
LOG = logging


class VSphereEntity(IntEnum):
    Vm = 1
    Folder = 2


class VSphereException(Exception):
    def __init__(self, err_msg, *args):
        Exception.__init__(self, err_msg % args)


class VSphereTaskFailed(VSphereException):
    def __init__(self, job_name, error):
        super(VSphereTaskFailed, self).__init__("vSphere Task %s failed with error %s" % (job_name, error))


# an exception we should should try and reconnect after
class VSphereReconnectException(VSphereException):
    pass


# Shamelessly borrowed from:
# https://github.com/dnaeon/py-vconnector/blob/master/src/vconnector/core.py
def collect_properties(service_instance, view_ref, obj_type, path_set=None,
                       include_mors=False):
    """
    Collect properties for managed objects from a view ref
    Check the vSphere API documentation for example on retrieving
    object properties:
        - http://goo.gl/erbFDz
    Args:
        si          (ServiceInstance): ServiceInstance connection
        view_ref (pyVmomi.vim.view.*): Starting point of inventory navigation
        obj_type      (pyVmomi.vim.*): Type of managed object
        path_set               (list): List of properties to retrieve
        include_mors           (bool): If True include the managed objects
                                       refs in the result
    Returns:
        A list of properties for the managed objects
    """
    collector = service_instance.content.propertyCollector

    # Create object specification to define the starting point of
    # inventory navigation
    obj_spec = pyVmomi.vmodl.query.PropertyCollector.ObjectSpec()
    obj_spec.obj = view_ref
    obj_spec.skip = True

    # Create a traversal specification to identify the path for collection
    traversal_spec = pyVmomi.vmodl.query.PropertyCollector.TraversalSpec()
    traversal_spec.name = 'traverseEntities'
    traversal_spec.path = 'view'
    traversal_spec.skip = False
    traversal_spec.type = view_ref.__class__
    obj_spec.selectSet = [traversal_spec]

    # Identify the properties to the retrieved
    property_spec = pyVmomi.vmodl.query.PropertyCollector.PropertySpec()
    property_spec.type = obj_type

    if not path_set:
        property_spec.all = True

    property_spec.pathSet = path_set

    # Add the object and property specification to the
    # property filter specification
    filter_spec = pyVmomi.vmodl.query.PropertyCollector.FilterSpec()
    filter_spec.objectSet = [obj_spec]
    filter_spec.propSet = [property_spec]

    # Retrieve properties
    props = collector.RetrieveContents([filter_spec])

    data = []
    for obj in props:
        properties = {}
        for prop in obj.propSet:
            properties[prop.name] = prop.val

        if include_mors:
            properties['obj'] = obj.obj

        data.append(properties)
    return data


def get_container_view(service_instance, obj_type, container=None):
    """
    Get a vSphere Container View reference to all objects of type 'obj_type'
    It is up to the caller to take care of destroying the View when no longer
    needed.
    Args:
        obj_type (list): A list of managed object types
    Returns:
        A container view ref to the discovered managed objects
    """
    if not container:
        container = service_instance.content.rootFolder

    view_ref = service_instance.content.viewManager.CreateContainerView(
        container=container,
        type=obj_type,
        recursive=True
    )
    return view_ref


def reconnect_on_fault(func):
    """
    Decorator for functions which access the vSphere API.
    Tries to reconnect on vSphere errors (e.g. session authentication timeout, etc).
    """

    @wraps(func)
    def decorated(client, *args, **kwargs):
        try:
            return func(client, *args, **kwargs)
        except (vim.MethodFault, VSphereReconnectException) as exc:
            LOG.exception('vSphere connection error raised (will try to reconnect): %s', exc)
            client.connect(reconnect=True)
            return func(client, *args, **kwargs)
        except Exception as e:
            LOG.exception('Failed to execute {} - got {}'.format(func, e))

    return decorated


class VSphereClient(object):
    """
    Wrapper for Vsphere
    """

    def __init__(self, admin_user, admin_password, auth_host, auth_port=443):
        self.admin_user = admin_user
        self.admin_password = admin_password
        self.auth_host = auth_host
        self.auth_port = auth_port

        self._vsphere_connection = None
        self._vsphere_content = None
        self._perfManager = None

    def set_configuration(self, admin_user, admin_password, auth_host, auth_port=443):
        self.admin_user = admin_user
        self.admin_password = admin_password
        self.auth_host = auth_host
        self.auth_port = auth_port

    def __repr__(self):
        return "<VSphereClient host='%s:%d' [%s] user='%s' password='%s'>" % \
               (self.auth_host, self.auth_port,
                "On" if self._vsphere_connection is not None else "Off",
                self.admin_user, "*" * len(self.admin_password))

    def __del__(self):
        self.close()

    def connect(self, reconnect=False, insecure=True):
        """
        Create new authenticated VSphere client
        """
        if self._vsphere_connection is None or reconnect:
            LOG.info('Connecting to vSphere server on %s:%s' % (self.auth_host, self.auth_port))

            kwargs = {'host': self.auth_host, 'port': self.auth_port,
                      'user': self.admin_user, 'pwd': self.admin_password}
            vmomi_versions = sorted(pyVmomi_version.versionMap.keys())
            LOG.debug("PyVmomi versions: %s", vmomi_versions)

            if insecure and ("vim25/6.5" in vmomi_versions or "vim25/6.0" in vmomi_versions):
                try:
                    import ssl
                    kwargs['sslContext'] = ssl._create_unverified_context()
                except (ImportError, AttributeError):
                    # on python older than 2.7.9 ssl does not have this function
                    pass

            try:
                self._vsphere_connection = SmartConnect(**kwargs)
                self._vsphere_content = self._vsphere_connection.RetrieveContent()
                self._perf_manager = self._vsphere_content.perfManager
            except (ConnectionError, vim.fault.InvalidLogin) as exc:
                raise VSphereException("Failed connecting to %s:%s using user %s: %s" % (self.auth_host,
                                                                                         self.auth_port,
                                                                                         self.admin_user,
                                                                                         exc))

    def close(self):
        if self._vsphere_connection:
            del self._vsphere_connection
            self._vsphere_connection = None

    @property
    @reconnect_on_fault
    def session_key(self):
        """
        :return: The current session key. A unique identifier of the current connection.
        """
        if self._vsphere_content is not None and self._vsphere_connection is not None:
            # perform simple operation to check connectivity.
            self._vsphere_connection.CurrentTime()
            if not self._vsphere_content.sessionManager.currentSession:
                raise VSphereReconnectException("Can't get session key, session might be off")
            return self._vsphere_content.sessionManager.currentSession.key

    @reconnect_on_fault
    def _list_objects(self, object_type, folder=None):
        if folder is None:
            folder = self._vsphere_content.rootFolder

        objview = self._vsphere_content.viewManager.CreateContainerView(folder,
                                                                        [object_type],
                                                                        True)

        objects = objview.view
        objview.Destroy()
        return objects

    @reconnect_on_fault
    def _get_obj(self, vim_type, name):
        """
         Get the vsphere object associated with a given text name
         :param vim_type: List of pyVmomi types.
         :type vim_type: vim.*
         :param name: The name of the desired object.
         :type name: str.
        """
        obj = None
        container = self._vsphere_content.viewManager.CreateContainerView(self._vsphere_content.rootFolder, vim_type,
                                                                          True)
        for item in container.view:
            if item.name == name:
                obj = item
                break
        if obj is None:
            LOG.debug("Could not find %s ", name)

        return obj

    def get_obj(self, vim_type, name):
        return self._get_obj(vim_type, name)

    def list_vms(self):
        return self._list_objects(vim.VirtualMachine)

    def list_hosts(self):
        return self._list_objects(vim.HostSystem)

    def list_users(self):
        user_list = []
        for dom in self.domains:  # skipping host users
            tmp_list = self._vsphere_content.userDirectory.RetrieveUserGroups(
                domain=dom, searchStr="", exactMatch=False,
                findUsers=True, findGroups=True)
            user_list.extend(tmp_list)
        return user_list

    # -----------------------------------------
    # Property-Collector based API (used for deployment)
    #  TODO: consider using only this API
    # -----------------------------------------
    @reconnect_on_fault
    def _get_objects(self, object_type, properties):
        view = get_container_view(self._vsphere_connection,
                                  obj_type=[object_type])
        objects = collect_properties(self._vsphere_connection,
                                     view_ref=view,
                                     obj_type=object_type,
                                     path_set=properties,
                                     include_mors=True)
        for obj in objects:
            obj['moid'] = obj['obj']._moId
            del obj['obj']

        return objects

    def collect_roles(self):
        return self._vsphere_content.authorizationManager.roleList

    @property
    def roles(self):
        return self.collect_roles()

    def collect_domains(self):
        return self._vsphere_content.userDirectory.domainList[1:]

    @property
    def domains(self):
        """
        Return all domains except host domain
        :return: List of domains except host domain.
        """
        return self.collect_domains()

    @reconnect_on_fault
    def _get_obj_by_moid(self, obj_type, moid):
        obj = obj_type(moid)
        obj._stub = self._vsphere_connection._stub
        return obj

    def get_vm(self, vm_moid):
        """
        Get VM by moid.
        """
        return self._get_obj_by_moid(vim.VirtualMachine, vm_moid)

    def get_host(self, host_moid):
        """
        Get host by moid.
        """
        return self._get_obj_by_moid(vim.HostSystem, host_moid)

    def get_host_by_name(self, host_name):
        """
        Get host by name.
        """
        return self.get_obj([vim.HostSystem], host_name)

    @reconnect_on_fault
    def wait_for_task(self, task, action_name, hide_result=False, update_status_callback=None):
        if update_status_callback is None:
            def dummy_callback(task):
                pass

            update_status_callback = dummy_callback

        LOG.info('Waiting for %s to complete.', action_name)

        last_state = (None, None)
        while task.info.state in [vim.TaskInfo.State.running, vim.TaskInfo.State.queued]:
            if task.info.state == "canceled":
                try:
                    task.CancelTask()
                except Exception as exc:
                    LOG.warn("Error canceling task '%s': %s", action_name, exc)

                LOG.warn('%s was canceled!', action_name)
                return None

            elif last_state != (task.info.state, task.info.progress):
                LOG.info("Task '%s' state: %s (progress: %s%%)", action_name, task.info.state, task.info.progress or 0)
                last_state = (task.info.state, task.info.progress)

                try:
                    update_status_callback(task)
                except Exception:
                    LOG.exception("Error while calling %s task update status callback", action_name)

            do_sleep(1)

        if task.info.state == vim.TaskInfo.State.success:
            try:
                update_status_callback(task)
            except Exception:
                LOG.exception("Error while calling %s task update status callback", action_name)

            if task.info.result is not None and not hide_result:
                LOG.info('%s completed successfully, result: %s', action_name, task.info.result)
            else:
                LOG.info('%s completed successfully.', action_name)

        else:
            LOG.error('%s did not complete successfully: %s', action_name, task.info.error)
            raise VSphereTaskFailed(action_name, task.info.error)

        # may not always be applicable, but can't hurt.
        return task
