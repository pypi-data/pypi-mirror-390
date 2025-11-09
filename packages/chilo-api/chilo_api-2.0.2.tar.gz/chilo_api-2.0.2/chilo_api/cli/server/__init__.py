from typing import Any
from werkzeug.serving import run_simple

from chilo_api.cli.server.arguments import ServerArguments
from chilo_api.cli.importer import CLIImporter
from chilo_api.cli.logger import CLILogger
from chilo_api.cli.validator import CLIValidator
from chilo_api.cli.server.grpc import GRPCServer


class Server:
    '''
    A class to manage the server operations, including running the server and handling API imports.
    This class provides methods to initialize the server, run it, and handle command line arguments.
    Methods
    ----------
    run():
        Parses command line arguments and executes the corresponding action.
    '''

    def __init__(self, args: Any) -> None:
        self.args: Any = args
        self.validator: CLIValidator = CLIValidator()
        self.logger: CLILogger = CLILogger()
        self.importer: CLIImporter = CLIImporter()

    def run(self) -> None:
        self.logger.log_server_start()
        api: Any = self.importer.get_api_module(self.args.api)
        self.__run_server(api)

    def __run_server(self, api: Any) -> None:
        server_args = ServerArguments(self.args, api)
        self.logger.log_server_settings(server_args)  # type: ignore
        self.__run_hooks(server_args.api_config.on_startup, 'STARTUP')
        self.__run_server_lifecycle(api, server_args)

    def __run_server_lifecycle(self, api: Any, server_args: ServerArguments) -> None:
        try:
            self.__run_server_type(server_args, api)
        finally:
            self.__run_hooks(server_args.api_config.on_shutdown, 'SHUTDOWN')
            self.logger.log_end('SERVER SHUTTING DOWN')

    def __run_server_type(self, server_args: ServerArguments, api: Any) -> None:
        if server_args.api_type == 'grpc':
            GRPCServer(server_args, self.logger).run()  # type: ignore
        else:
            run_simple(server_args.host, server_args.port, api.route, use_reloader=server_args.reload, use_debugger=server_args.verbose)

    def __run_hooks(self, hooks, stage: str) -> None:
        if not hooks:
            return
        for hook in hooks:
            try:
                hook()
            except Exception as error:  # pragma: no cover
                self.logger.log_message(f'{stage} hook failure: {error}')
