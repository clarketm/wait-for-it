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


def connect(service, timeout):
    scheme, _, host = service.rpartition(r"//")
    url = urlparse(f"{scheme}//{host}", scheme="http")

    host = url.hostname
    port = url.port or (443 if url.scheme == "https" else 80)

    friendly_name = f"{host}:{port}"

    def _handle_timeout(signum, frame):
        print(f"timeout occurred after waiting {timeout} seconds for {friendly_name}")
        sys.exit(1)

    if timeout > 0:
        signal.signal(signal.SIGALRM, _handle_timeout)
        signal.alarm(timeout)
        print(f"waiting {timeout} seconds for {friendly_name}")
    else:
        print(f"waiting for {friendly_name} without a timeout")

    t1 = time.time()

    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s = sock.connect_ex((host, port))
            if s == 0:
                seconds = round(time.time() - t1)
                print(f"{friendly_name} is available after {seconds} seconds")
                break
        except socket.gaierror:
            pass
        finally:
            time.sleep(1)

    signal.alarm(0)


if __name__ == "__main__":
    cli()
