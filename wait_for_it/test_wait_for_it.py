"""wait_for_it cli test module"""
import socket
import subprocess

from unittest.mock import call, Mock, patch

import socketserver
from threading import Event, Thread
from unittest import TestCase

from click.testing import CliRunner
from parameterized import parameterized
from .wait_for_it import cli, _determine_host_and_port_for

_ANY_FREE_PORT = 0


class _DummyTcpServerThread(Thread):
    """
    A TCP server as a Thread that takes any free port, accepts connections,
    but doesn't do any meaningful traffic.
    """

    class _DummyHandler(socketserver.BaseRequestHandler):
        pass

    def __init__(self):
        super().__init__()
        self.started = Event()

    def run(self):
        with socketserver.TCPServer(
            ("127.0.0.1", _ANY_FREE_PORT), self._DummyHandler
        ) as self._server:
            self.host, self.port = self._server.server_address
            self.started.set()
            self._server.serve_forever()

    def stop(self):
        self._server.shutdown()


def _start_server_thread():
    server = _DummyTcpServerThread()
    server.start()
    server.started.wait()
    return server


def _occupy_free_tcp_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", _ANY_FREE_PORT))
    host, port = sock.getsockname()
    return host, port, sock


class CliTest(TestCase):
    @classmethod
    def setUpClass(cls):
        # https://click.palletsprojects.com/en/7.x/testing/
        cls._runner = CliRunner()

    def test_help(self):
        result = self._runner.invoke(cli, ["--help"])
        assert "Usage:" in result.output
        assert result.exit_code == 0

    @parameterized.expand([(["echo", "one", "two"], 0), (["false"], 1)])
    def test_command_invocation_forwards_exit_code(
        self, command_argv, expected_exit_code
    ):
        with patch.object(
            subprocess, "run", return_value=Mock(returncode=expected_exit_code)
        ) as mock_subprocess_run:
            result = self._runner.invoke(cli, command_argv)
        assert mock_subprocess_run.call_args == call(tuple(command_argv))
        assert result.exit_code == expected_exit_code

    @parameterized.expand([("parallel", ["-p"]), ("serial", [])])
    def test_service_available(self, _label, extra_argv):
        server = _start_server_thread()
        try:
            result = self._runner.invoke(
                cli,
                [
                    "-t1",
                    "-s",
                    f"{server.host}:{server.port}",
                    "-s",
                    f"{server.host}:{server.port}",
                ]
                + extra_argv,
            )
            assert result.output.count(" is available after ") == 2
            assert result.exit_code == 0
        finally:
            server.stop()

    @parameterized.expand([("parallel", ["-p"], 2), ("serial", [], 1)])
    def test_service_unavailable(self, _label, extra_argv, expected_report_count):
        host, port, sock = _occupy_free_tcp_port()
        try:
            result = self._runner.invoke(
                cli,
                ["-t1", "-s", f"{host}:{port}", "-s", f"{host}:{port}"] + extra_argv,
            )
            assert result.output.count("Timeout occurred") == expected_report_count
            assert result.exit_code == 1
        finally:
            sock.close()


class DetermineHostAndPortForTest(TestCase):
    @parameterized.expand(
        [
            ("domain.ext", 80),
            ("domain.ext:123", 123),
            ("http://domain.ext", 80),
            ("http://domain.ext/path/", 80),
            ("https://domain.ext", 443),
            ("https://domain.ext/path/", 443),
        ]
    )
    def test_supportec(self, service, expected_port):
        actual_host, actual_port = _determine_host_and_port_for(service)
        assert actual_host == "domain.ext"
        assert actual_port == expected_port
