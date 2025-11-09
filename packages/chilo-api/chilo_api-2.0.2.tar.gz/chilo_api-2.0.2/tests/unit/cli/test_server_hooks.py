import unittest
from unittest.mock import Mock, patch

from chilo_api.cli.server import Server
from chilo_api.core.router import Router
from chilo_api.core.exception import ApiException
from tests.unit.mocks.core import HookTracker, FailingHook


class ServerHookTests(unittest.TestCase):

    def setUp(self) -> None:
        self.args = Mock(api='api_rest')
        self.server = Server(self.args)
        self.server.logger.log_message = Mock()
        self.server.logger.log_end = Mock()

    def _base_server_args(self, api_type='rest', startup=(), shutdown=()):
        server_args = Mock()
        server_args.api_type = api_type
        server_args.host = '127.0.0.1'
        server_args.port = 3000
        server_args.reload = False
        server_args.verbose = False
        server_args.api_config = Mock()
        server_args.api_config.on_startup = tuple(startup)
        server_args.api_config.on_shutdown = tuple(shutdown)
        source_fields = {'host': 'api-settings', 'port': 'api-settings', 'reload': 'api-settings', 'verbose': 'api-settings'}
        server_args.source = source_fields
        return server_args

    def _setup_importer(self, api):
        importer_patch = patch('chilo_api.cli.server.CLIImporter')
        importer = importer_patch.start()
        self.addCleanup(importer_patch.stop)
        importer.return_value.get_api_module.return_value = api
        return importer

    def _setup_server_args(self, server_args):
        args_patch = patch('chilo_api.cli.server.ServerArguments', return_value=server_args)
        args_patch.start()
        self.addCleanup(args_patch.stop)

    @patch('chilo_api.cli.server.CLILogger.log_server_start')
    def test_startup_hooks_success(self, _):
        api = Mock()
        api.route = Mock()
        tracker = HookTracker()
        server_args = self._base_server_args(startup=(tracker,))
        self._setup_importer(api)
        self._setup_server_args(server_args)

        with patch('chilo_api.cli.server.run_simple') as run_simple:
            self.server.run()

        self.assertEqual(tracker.calls, ['hook-1'])
        run_simple.assert_called_once()

    @patch('chilo_api.cli.server.CLILogger.log_server_start')
    def test_startup_hook_failure_does_not_block_server(self, _):
        api = Mock()
        api.route = Mock()
        tracker = HookTracker()
        failing = FailingHook(Exception('boom'))
        server_args = self._base_server_args(startup=(failing, tracker))
        self._setup_importer(api)
        self._setup_server_args(server_args)

        with patch('chilo_api.cli.server.run_simple') as run_simple:
            self.server.run()

        self.assertIn('hook-1', tracker.calls)
        run_simple.assert_called_once()

    def test_invalid_startup_hooks_raise(self):
        with self.assertRaises(RuntimeError):
            Router(handlers='tests/unit/mocks/rest/handlers/valid', on_startup=['not callable'])

    @patch('chilo_api.cli.server.CLILogger.log_server_start')
    def test_shutdown_hooks_success(self, _):
        api = Mock()
        api.route = Mock()
        tracker = HookTracker()
        server_args = self._base_server_args(shutdown=(tracker,))
        self._setup_importer(api)
        self._setup_server_args(server_args)

        with patch('chilo_api.cli.server.run_simple'):
            self.server.run()

        self.assertEqual(tracker.calls, ['hook-1'])

    @patch('chilo_api.cli.server.CLILogger.log_server_start')
    def test_shutdown_hook_failure_does_not_block_server(self, _):
        api = Mock()
        api.route = Mock()
        tracker = HookTracker()
        failing = FailingHook(ApiException(message='fail'))
        server_args = self._base_server_args(shutdown=(failing, tracker))
        self._setup_importer(api)
        self._setup_server_args(server_args)

        with patch('chilo_api.cli.server.run_simple') as run_simple:
            self.server.run()

        self.assertTrue(tracker.calls)
        run_simple.assert_called_once()

    def test_invalid_shutdown_hooks_raise(self):
        with self.assertRaises(RuntimeError):
            Router(handlers='tests/unit/mocks/rest/handlers/valid', on_shutdown=['not callable'])

    @patch('chilo_api.cli.server.CLILogger.log_server_start')
    def test_grpc_server_branch_invokes_grpc_runner(self, _):
        api = Mock()
        api.route = Mock()
        server_args = self._base_server_args(api_type='grpc')
        self._setup_importer(api)
        self._setup_server_args(server_args)
        grpc_patch = patch('chilo_api.cli.server.GRPCServer')
        run_simple_patch = patch('chilo_api.cli.server.run_simple')
        grpc_mock = grpc_patch.start()
        run_simple_mock = run_simple_patch.start()
        self.addCleanup(grpc_patch.stop)
        self.addCleanup(run_simple_patch.stop)

        self.server.run()

        grpc_mock.assert_called_once_with(server_args, self.server.logger)
        grpc_mock.return_value.run.assert_called_once()
        run_simple_mock.assert_not_called()


if __name__ == '__main__':
    unittest.main()
