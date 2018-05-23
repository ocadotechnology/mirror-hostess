''' testing io with temporary files '''

import os.path
import shutil
import tempfile
import unittest


class IOTestCase(unittest.TestCase): #pylint: disable=invalid-name
    ''' testing io with temporary files '''

    def setUp(self):
        self.temp_host_file = tempfile.NamedTemporaryFile()
        shutil.copyfile('tests/fixtures/hosts.test', self.temp_host_file.name)
        self.temp_host_file_backup = tempfile.NamedTemporaryFile()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_lock_file = os.path.join(self.temp_dir.name, 'hostess.lock')
        self.envvars = {
            'SERVICE_NAME': 'myregistry',
            'SERVICE_NAMESPACE': 'testnamespace',
            'SHADOW_FQDN': 'test.k8s.io',
            'HOSTS_FILE': self.temp_host_file.name,
            'HOSTS_FILE_BACKUP': self.temp_host_file_backup.name,
            'LOCK_FILE': self.temp_lock_file,
        }

    def tearDown(self):
        self.temp_host_file.close()
        self.temp_host_file_backup.close()
        self.temp_dir.cleanup()
