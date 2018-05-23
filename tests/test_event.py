''' testing the event handler '''
import logging
import unittest.mock as mock

from kubernetes.client.models.v1_object_meta import V1ObjectMeta
from kubernetes.client.models.v1_service import V1Service
from kubernetes.client.models.v1_service_spec import V1ServiceSpec

from .io_testcase import IOTestCase
from .context import hostess

class EventTest(IOTestCase):
    ''' testing the event handler '''

    @mock.patch.object(hostess.Watcher, 'add_host', autospec=True)
    def test_expected_add_service_event(self, mock_add_host):
        ''' test recieving a normal added event for the service we are expecting '''
        event = {
            'type': 'ADDED',
            'object': V1Service(api_version='v1',
                                kind='Service',
                                metadata=V1ObjectMeta(name='myregistry',
                                                      namespace='testnamespace',
                                                     ),
                                spec=V1ServiceSpec(cluster_ip='10.0.0.1'),
                               ),
        }
        watcher = hostess.Watcher(env=self.envvars)
        watcher.handle_service_event(event)
        mock_add_host.assert_called_with(self=watcher,
                                         fqdn=self.envvars['SHADOW_FQDN'],
                                         ip_addr='10.0.0.1')

    def test_unexpected_add_service_event(self): #pylint: disable=invalid-name
        ''' test recieving a normal added event for a service we are not expecting '''
        event = {
            'type': 'ADDED',
            'object': V1Service(api_version='v1',
                                kind='Service',
                                metadata=V1ObjectMeta(name='someservice',
                                                      namespace='othernamespace',
                                                     ),
                                spec=V1ServiceSpec(cluster_ip='10.0.0.5'),
                               ),
        }
        watcher = hostess.Watcher(env=self.envvars)
        log = logging.getLogger()
        log.setLevel(logging.INFO)
        with self.assertLogs(log, level='DEBUG') as context_manager:
            watcher.handle_service_event(event)
            self.assertIn('DEBUG:hostess.watcher:Ignoring event for {} in {}'.format(
                'someservice', 'othernamespace'), context_manager.output)

    @mock.patch.object(hostess.Watcher, 'add_host', autospec=True)
    def test_expected_modified_service_event(self, mock_add_host): #pylint: disable=invalid-name
        ''' test recieving a normal modified event for the service we are expecting '''
        event = {
            'type': 'MODIFIED',
            'object': V1Service(api_version='v1',
                                kind='Service',
                                metadata=V1ObjectMeta(name='myregistry',
                                                      namespace='testnamespace',
                                                     ),
                                spec=V1ServiceSpec(cluster_ip='10.0.0.1'),
                               ),
        }
        watcher = hostess.Watcher(env=self.envvars)
        watcher.handle_service_event(event)
        mock_add_host.assert_called_with(self=watcher,
                                         fqdn=self.envvars['SHADOW_FQDN'],
                                         ip_addr='10.0.0.1')

    @mock.patch.object(hostess.Watcher, 'remove_host', autospec=True)
    def test_expected_remove_service_event(self, mock_remove_host): #pylint: disable=invalid-name
        ''' test recieving a normal deleted event for the service we are expecting '''
        event = {
            'type': 'DELETED',
            'object': V1Service(api_version='v1',
                                kind='Service',
                                metadata=V1ObjectMeta(name='myregistry',
                                                      namespace='testnamespace',
                                                     ),
                                spec=V1ServiceSpec(cluster_ip='10.0.0.1'),
                               ),
        }
        watcher = hostess.Watcher(env=self.envvars)
        watcher.handle_service_event(event)
        mock_remove_host.assert_called_with(self=watcher, fqdn=self.envvars['SHADOW_FQDN'])

    def test_unexpected_service_event(self):
        ''' test recieving an abnormal event for the service we are expecting '''
        event = {
            'type': 'UNKNOWN',
            'object': V1Service(api_version='v1',
                                kind='Service',
                                metadata=V1ObjectMeta(name='myregistry',
                                                      namespace='testnamespace',
                                                     ),
                                spec=V1ServiceSpec(cluster_ip='10.0.0.1'),
                               ),
        }
        watcher = hostess.Watcher(env=self.envvars)
        log = logging.getLogger()
        log.setLevel(logging.INFO)
        with self.assertLogs(log, level='INFO') as context_manager:
            watcher.handle_service_event(event)
            self.assertIn('WARNING:hostess.watcher:Unexpected event type {}'.format('UNKNOWN'),
                          context_manager.output)
