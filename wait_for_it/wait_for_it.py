#!/usr/bin/env python3

import os
import signal
import socket
import subprocess
import sys
import time
from urllib.parse import urlparse

import click

from wait_for_it import __version__


def _determine_host_and_port_for(service):
    scheme, _, host = service.rpartition(r"//")
    url = urlparse(f"{scheme}//{host}", scheme="http")
    host = url.hostname
    port = url.port or (443 if url.scheme == "https" else 80)
    return host, port


def _block_until_available(host, port):
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s = sock.connect_ex((host, port))
            if s == 0:
                break
        except socket.gaierror:
            pass
        time.sleep(1)


@click.command()
@click.help_option("-h", "--help")
@click.version_option(__version__, "-v", "--version", message="Version %(version)s")
@click.option(
    "-q",
    "--quiet",
    default=False,
    is_flag=True,
    help="Do not output any status messages",
)
@click.option(
    "-s",
    "--service",
    metavar="host:port",
    multiple=True,
    help="Services to test, in the format host:port",
)
@click.option(
    "-t",
    "--timeout",
    type=int,
    metavar="seconds",
    default=15,
    show_default=True,
    help="Timeout in seconds, 0 for no timeout",
)
@click.argument("commands", nargs=-1)
def cli(service, quiet, timeout, commands):
    """Wait for service(s) to be available before executing a command."""

    if quiet:
        sys.stdout = open(os.devnull, "w")

    for s in service:
        connect(s, timeout)

    if len(commands):
        result = subprocess.run(commands)
        sys.exit(result.returncode)


class _ConnectionJobReporter:
    def __init__(self, host, port, timeout):
        self._friendly_name = f"{host}:{port}"
        self._timeout = timeout
        self._started_at = None

    def on_before_start(self):
        if self._timeout:
            print(f"waiting {self._timeout} seconds for {self._friendly_name}")
        else:
            print(f"waiting for {self._friendly_name} without a timeout")
        self._started_at = time.time()

    def on_success(self):
        seconds = round(time.time() - self._started_at)
        print(f"{self._friendly_name} is available after {seconds} seconds")

    def on_timeout(self):
        print(
            f"timeout occurred after waiting {self._timeout} seconds for {self._friendly_name}"
        )


def connect(service, timeout):
    host, port = _determine_host_and_port_for(service)
    reporter = _ConnectionJobReporter(host, port, timeout)

    def _handle_timeout(signum, frame):
        reporter.on_timeout()
        sys.exit(1)

    if timeout > 0:
        signal.signal(signal.SIGALRM, _handle_timeout)
        signal.alarm(timeout)

    reporter.on_before_start()

    _block_until_available(host, port)

    signal.alarm(0)  # disarm sys-exit timer

    reporter.on_success()


if __name__ == "__main__":
    cli()
