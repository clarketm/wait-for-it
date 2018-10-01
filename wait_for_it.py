#!/usr/bin/env python3

import os
import signal
import socket
import subprocess
import sys
import time

import click

VERSION = "0.0.0"


@click.command()
@click.help_option("-h", "--help")
@click.version_option(VERSION, "-v", "--version", message="Version %(version)s")
@click.option("-q", "--quiet", default=False, is_flag=True, help="Don\"t output any status messages")
@click.option("-s", "--service", multiple=True, help="Services to test, in the format host:port")
@click.option("-t", "--timeout", type=int, default=15, help="Timeout in seconds, 0 for no timeout")
@click.argument("commands", nargs=-1)
def cli(service, quiet, timeout, commands):
    """Wait for service(s) to be available before executing a command."""

    if quiet: sys.stdout = open(os.devnull, "w")

    for s in service:
        connect(s, timeout)

    if len(commands):
        subprocess.run(commands)


def connect(service, timeout):
    host, port = service.split(":")
    port = int(port) if port else 80

    def _handle_timeout(signum, frame):
        print(f"timeout occurred after waiting {timeout} seconds for {service}")
        sys.exit(1)

    if timeout > 0:
        signal.signal(signal.SIGALRM, _handle_timeout)
        signal.alarm(timeout)
        print(f"waiting {timeout} seconds for {service}")
    else:
        print(f"waiting for {service} without a timeout")

    t1 = time.time()

    try:
        while True:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s = sock.connect_ex((host, port))
            if s == 0:
                seconds = round(time.time() - t1)
                print(f"{service} is available after {seconds} seconds")
                break
            time.sleep(1)
    finally:
        signal.alarm(0)


def main():
    print("main")


if __name__ == "__main__":
    cli()
