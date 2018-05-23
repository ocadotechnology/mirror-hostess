''' testing configuration parameters '''
import logging
import unittest

from kubernetes import client, watch
from .context import hostess


class ConfigTest(unittest.TestCase):
    ''' testing configuration parameters '''

    def test_set_hostsfile_path(self):
        ''' test setting the HOSTS_FILE env var '''
        hosts = './hosts.test'
        envvars = {'HOSTS_FILE': hosts}
        watcher = hostess.Watcher(env=envvars)
        self.assertEqual(watcher.hosts_file_path, hosts)

    def test_set_hostsfilebackup_path(self):
        ''' test setting the HOSTS_FILE_BACKUP env var '''
        hosts = './hosts.backup.test'
        envvars = {'HOSTS_FILE_BACKUP': hosts}
        watcher = hostess.Watcher(env=envvars)
        self.assertEqual(watcher.hosts_file_backup_path, hosts)

    def test_set_lockfile_path(self):
        ''' test setting the LOCK_FILE env var '''
        lock = './hostess.lock'
        envvars = {'LOCK_FILE': lock}
        watcher = hostess.Watcher(env=envvars)
        self.assertEqual(watcher.lock.lock_file, lock)

    def test_set_servicename(self):
        ''' test setting the SERVICE_NAME env var '''
        service = 'some-service'
        envvars = {'SERVICE_NAME': service}
        watcher = hostess.Watcher(env=envvars)
        self.assertEqual(watcher.service_name, service)

    def test_set_servicenamespace(self):
        ''' test setting the SERVICE_NAMESPACE env var '''
        namespace = 'some-namespace'
        envvars = {'SERVICE_NAMESPACE': namespace}
        watcher = hostess.Watcher(env=envvars)
        self.assertEqual(watcher.service_namespace, namespace)

    def test_set_fqdn(self):
        ''' test setting the SHADOW_FQDN env var '''
        fqdn = 'some.name.com'
        envvars = {'SHADOW_FQDN': fqdn}
        watcher = hostess.Watcher(env=envvars)
        self.assertEqual(watcher.shadow_fqdn, fqdn)

    def test_set_logger(self):
        ''' test setting logger details '''
        log = logging.getLogger()
        log.setLevel(logging.INFO)
        with self.assertLogs(log, level='INFO') as context_manager:
            hostess.Watcher()
            self.assertIn('INFO:hostess.watcher:Starting', context_manager.output)

    def test_client_config(self):
        ''' test kubernetes client config is set '''
        config = client.ConfigurationObject()
        watcher = hostess.Watcher(config=config)
        self.assertEqual(watcher.v1_api.api_client.config.host, 'https://localhost')

    def test_instance_host_map_exists(self):
        ''' test hostmap for the instance is initialised '''
        watcher = hostess.Watcher()
        self.assertEqual(watcher.hostmap, {})

    def test_instance_watcher_exists(self):
        ''' test watcher for the instance is initialised '''
        watcher = hostess.Watcher()
        self.assertIsInstance(watcher.watch, watch.Watch)
