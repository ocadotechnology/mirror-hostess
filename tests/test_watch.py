''' testing the api watcher '''
import filecmp
import logging
import os.path

from python_hosts import Hosts
from .io_testcase import IOTestCase
from .context import hostess

class WatcherTest(IOTestCase):
    ''' testing the api watcher '''

    def test_hostfile_is_parsed(self):
        ''' test hostfile has been parsed '''
        watcher = hostess.Watcher(env=self.envvars)
        self.assertTrue(watcher.hostfile.exists(names=['hostess']))

    def test_backup_hosts_file(self):
        ''' test that hosts file gets backed up correctly '''
        watcher = hostess.Watcher(env=self.envvars)
        self.assertFalse(filecmp.cmp(self.temp_host_file.name, self.temp_host_file_backup.name))
        watcher.backup_etc_hosts()
        self.assertTrue(filecmp.cmp(self.temp_host_file.name, self.temp_host_file_backup.name))

    def test_backup_hosts_file_missing_hosts(self): #pylint: disable=invalid-name
        ''' test that error log message is thrown if hosts file missing '''
        log = logging.getLogger()
        log.setLevel(logging.INFO)
        self.envvars['HOSTS_FILE'] = os.path.join(self.temp_dir.name, 'non-existant-hosts.backup')
        watcher = hostess.Watcher(env=self.envvars)
        with self.assertRaisesRegex(RuntimeError, 'Exiting'):
            watcher.backup_etc_hosts()

    def test_backup_hosts_file_twice(self):
        ''' test that warning log message is thrown if backup hosts file already exists '''
        watcher = hostess.Watcher(env=self.envvars)
        self.assertFalse(filecmp.cmp(self.temp_host_file.name, self.temp_host_file_backup.name))
        watcher.backup_etc_hosts()
        self.assertTrue(filecmp.cmp(self.temp_host_file.name, self.temp_host_file_backup.name))
        log = logging.getLogger()
        log.setLevel(logging.INFO)
        with self.assertLogs(log, level='INFO') as context_manager:
            watcher.backup_etc_hosts()
            self.assertIn('WARNING:hostess.watcher:Backup hosts file already exists at {}'.format(
                self.temp_host_file_backup.name), context_manager.output)

    def test_remove_host(self):
        ''' test removing a host entry '''
        watcher = hostess.Watcher(env=self.envvars)
        watcher.hostmap['hostess'] = True
        self.assertTrue(watcher.hostfile.exists(names=['hostess']))
        self.assertTrue('hostess' in watcher.hostmap)
        watcher.remove_host(fqdn='hostess')
        self.assertFalse(watcher.hostfile.exists(names=['hostess']))
        self.assertFalse('hostess' in watcher.hostmap)

    def test_add_host(self):
        ''' test adding a host entry '''
        watcher = hostess.Watcher(env=self.envvars)
        self.assertFalse(watcher.hostfile.exists(names=['hostess2']))
        watcher.add_host(fqdn='hostess2', ip_addr='10.0.0.2')
        self.assertTrue(watcher.hostfile.exists(names=['hostess2']))

    def test_write_hosts_file(self):
        ''' test that adding and removing hosts modifies the hosts file correctly '''
        temp_host_file = Hosts(self.temp_host_file.name)
        self.assertTrue(temp_host_file.exists(names=['hostess']))
        self.assertFalse(temp_host_file.exists(names=['hostess2']))
        watcher = hostess.Watcher(env=self.envvars)
        watcher.hostmap['hostess'] = True
        watcher.remove_host(fqdn='hostess')
        watcher.add_host(fqdn='hostess2', ip_addr='10.0.0.2')
        temp_host_file = Hosts(self.temp_host_file.name)
        self.assertFalse(temp_host_file.exists(names=['hostess']))
        self.assertTrue(temp_host_file.exists(names=['hostess2']))

    def test_remove_all_hosts(self):
        ''' test that removing all added hosts actually removes those entries '''
        watcher = hostess.Watcher(env=self.envvars)
        self.assertFalse(watcher.hostfile.exists(names=['hostess2']))
        self.assertFalse(watcher.hostfile.exists(names=['hostess3']))
        self.assertFalse(watcher.hostfile.exists(names=['hostess4']))
        watcher.add_host(fqdn='hostess2', ip_addr='10.0.0.2')
        watcher.add_host(fqdn='hostess3', ip_addr='10.0.0.3')
        watcher.add_host(fqdn='hostess4', ip_addr='10.0.0.4')
        self.assertTrue(watcher.hostfile.exists(names=['hostess2']))
        self.assertTrue(watcher.hostfile.exists(names=['hostess3']))
        self.assertTrue(watcher.hostfile.exists(names=['hostess4']))
        watcher.remove_all_hosts()
        self.assertFalse(watcher.hostfile.exists(names=['hostess2']))
        self.assertFalse(watcher.hostfile.exists(names=['hostess3']))
        self.assertFalse(watcher.hostfile.exists(names=['hostess4']))
