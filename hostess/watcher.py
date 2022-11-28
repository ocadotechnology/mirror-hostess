''' watch kubernetes api '''
import logging
import os
import shutil
import signal

import filelock
from kubernetes import client, watch
from kubernetes.client.rest import ApiException
from python_hosts import Hosts, HostsEntry


LOGGER = logging.getLogger(__name__)

class Watcher: # pylint: disable=too-many-instance-attributes
    '''Watch kubernetes api for service objects

    :param env: dict of environment variables (eg: os.environ)

    :param config: kubernetes.client.Configuration

    '''

    def __init__(self, env=None):
        if env is None:
            env = {}
        LOGGER.info('Starting')
        lock_file_path = env.get('LOCK_FILE', '/var/lock/mirror-hostess')
        self.hosts_file_path = env.get('HOSTS_FILE', '/etc/hosts')
        self.hosts_file_backup_path = env.get('HOSTS_FILE_BACKUP', '/etc/hosts.backup')
        self.service_name = env.get('SERVICE_NAME', 'mirror-registry')
        self.service_namespace = env.get('SERVICE_NAMESPACE', 'default')
        self.shadow_fqdn = env.get('SHADOW_FQDN', 'mirror-registry.example.com')
        self.hostfile = Hosts(self.hosts_file_path)
        self.lock = filelock.FileLock(lock_file_path)
        self.v1_api = client.CoreV1Api()
        self.hostmap = {}
        self.watch = watch.Watch()

    def _cleanup(self, signum, frame): #pragma: no cover #pylint: disable=unused-argument
        ''' cleanup system on interrupt '''
        LOGGER.info('Caught interrupt, cleaning up and exiting')
        self.watch.stop()
        self.remove_all_hosts()
        raise RuntimeError("Exiting")

    def remove_host(self, fqdn):
        ''' remove a host by fqdn '''
        with self.lock.acquire(timeout=5):
            self.hostfile = Hosts(self.hosts_file_path)
            LOGGER.info("Removing entry for %s", fqdn)
            self.hostfile.remove_all_matching(name=fqdn)
            del self.hostmap[fqdn]
            self._write_hosts_file()

    def add_host(self, fqdn, ip_addr, entry_type='ipv4'):
        ''' add a host by fqdn and ip address '''
        with self.lock.acquire(timeout=5):
            self.hostfile = Hosts(self.hosts_file_path)
            LOGGER.info("Adding entry for %s at %s", fqdn, ip_addr)
            new_entry = HostsEntry(entry_type=entry_type, address=ip_addr, names=[fqdn])
            self.hostmap[fqdn] = True
            self.hostfile.add([new_entry], True)
            self._write_hosts_file()

    def remove_all_hosts(self):
        ''' remove all previously added hosts '''
        for fqdn in list(self.hostmap):
            self.remove_host(fqdn=fqdn)

    def _write_hosts_file(self):
        ''' write hosts file to disk '''
        with self.lock.acquire(timeout=5):
            self.hostfile.write()

    def backup_etc_hosts(self):
        ''' simple file copy if destination does not already exist '''
        LOGGER.debug("Hosts file at %s, backup to %s",
                     self.hosts_file_path, self.hosts_file_backup_path)
        if os.path.exists(self.hosts_file_backup_path):
            LOGGER.warning("Backup hosts file already exists at %s",
                           self.hosts_file_backup_path)
        try:
            shutil.copyfile(self.hosts_file_path, self.hosts_file_backup_path)
        except IOError as err:
            LOGGER.critical("Unable to backup the hosts file to %s. [%s] Exiting for safety",
                            self.hosts_file_backup_path, err)
            raise RuntimeError("Exiting")


    def execute(self): #pragma: no cover
        ''' main method '''
        self.backup_etc_hosts()
        signal.signal(signal.SIGINT, self._cleanup)
        signal.signal(signal.SIGTERM, self._cleanup)
        self.watch_api()

    def watch_api(self): #pragma: no cover
        ''' watch service api endpoint, handle events '''
        try:
            for event in self.watch.stream(self.v1_api.list_namespaced_service,
                                           namespace=self.service_namespace):
                self.handle_service_event(event)
        except ApiException:
            LOGGER.exception("Error watching custom object events", exc_info=True)

    def handle_service_event(self, event):
        ''' if expected service, add/remove host '''
        service = event['object']
        if (service.metadata.name == self.service_name and
                service.metadata.namespace == self.service_namespace):
            if event['type'] == 'ADDED' or event['type'] == 'MODIFIED':
                self.add_host(fqdn=self.shadow_fqdn, ip_addr=service.spec.cluster_ip)
            elif event['type'] == 'DELETED':
                self.remove_host(fqdn=self.shadow_fqdn)
            else:
                LOGGER.warning("Unexpected event type %s", event['type'])
        else:
            LOGGER.debug("Ignoring event for %s in %s",
                         service.metadata.name, service.metadata.namespace)
