#!/usr/bin/env python3
import asyncio
import os
import signal
import socket
import subprocess
import sys
import time
from contextlib import contextmanager
from urllib.parse import urlparse

import click

from wait_for_it import __version__


def _asyncio_run(*args, **kvargs):
    """
    Cheap backport of asyncio.run of Python 3.7+ to Python 3.6.
    For the real deal, see
    https://github.com/python/cpython/blob/3.7/Lib/asyncio/runners.py#L8
    """
    if sys.version_info[:2] >= (3, 7):
        return asyncio.run(*args, **kvargs)
    return asyncio.get_event_loop().run_until_complete(*args, **kvargs)


def _determine_host_and_port_for(service):
    scheme, _, host = service.rpartition(r"//")
    url = urlparse(f"{scheme}//{host}", scheme="http")
    host = url.hostname
    port = url.port or (443 if url.scheme == "https" else 80)
    return host, port


async def _wait_until_available(host, port):
    while True:
        try:
            _reader, writer = await asyncio.open_connection(host, port)
            writer.close()
            if sys.version_info[:2] >= (3, 7):
                await writer.wait_closed()
            break
        except (socket.gaierror, ConnectionError):
            pass
        await asyncio.sleep(1)


async def _wait_until_available_and_report(reporter, host, port):
    reporter.on_before_start()
    await _wait_until_available(host, port)
    reporter.on_success()


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
    "-p",
    "--parallel",
    default=False,
    is_flag=True,
    help="Test services in parallel rather than in serial",
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
def cli(service, quiet, parallel, timeout, commands):
    """Wait for service(s) to be available before executing a command."""

    if quiet:
        sys.stdout = open(os.devnull, "w")

    if parallel:
        _connect_all_parallel(service, timeout)
    else:
        _connect_all_serial(service, timeout)

    if commands:
        result = subprocess.run(commands)
        sys.exit(result.returncode)


class _ConnectionJobReporter:
    def __init__(self, host, port, timeout):
        self._friendly_name = f"{host}:{port}"
        self._timeout = timeout
        self._started_at = None
        self.job_successful = None

    def on_before_start(self):
        if self._timeout:
            print(f"waiting {self._timeout} seconds for {self._friendly_name}")
        else:
            print(f"waiting for {self._friendly_name} without a timeout")
        self._started_at = time.time()

    def on_success(self):
        seconds = round(time.time() - self._started_at)
        print(f"{self._friendly_name} is available after {seconds} seconds")
        self.job_successful = True

    def on_timeout(self):
        print(
            f"timeout occurred after waiting {self._timeout} seconds for {self._friendly_name}"
        )


@contextmanager
def _exit_on_timeout(timeout, on_exit):
    def _handle_timeout(signum, frame):
        on_exit()
        sys.exit(1)

    if timeout > 0:
        signal.signal(signal.SIGALRM, _handle_timeout)
        signal.alarm(timeout)

    yield

    if timeout > 0:
        signal.alarm(0)  # disarm sys-exit timer


async def _connect_all_parallel_async(services, timeout):
    connect_job_awaitables = []
    reporters = []

    for service in services:
        host, port = _determine_host_and_port_for(service)
        reporter = _ConnectionJobReporter(host, port, timeout)
        reporters.append(reporter)
        connect_job_awaitables.append(
            _wait_until_available_and_report(reporter, host, port)
        )

    def _report_on_all_unsuccessful_jobs():
        for reporter in reporters:
            if reporter.job_successful:
                continue
            reporter.on_timeout()

    with _exit_on_timeout(timeout, on_exit=_report_on_all_unsuccessful_jobs):
        await asyncio.wait(connect_job_awaitables)


def _connect_all_parallel(services, timeout):
    _asyncio_run(_connect_all_parallel_async(services, timeout))


def _connect_all_serial(services, timeout):
    for service in services:
        connect(service, timeout)


def connect(service, timeout):
    host, port = _determine_host_and_port_for(service)
    reporter = _ConnectionJobReporter(host, port, timeout)

    with _exit_on_timeout(timeout, on_exit=reporter.on_timeout):
        _asyncio_run(_wait_until_available_and_report(reporter, host, port))


if __name__ == "__main__":
    cli()
