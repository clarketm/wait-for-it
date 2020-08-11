# [wait-for-it](https://wait-for-it.readthedocs.io/en/latest/)

[![PyPi release](https://img.shields.io/pypi/v/wait-for-it.svg)](https://pypi.org/project/wait-for-it/)
[![PyPi versions](https://img.shields.io/pypi/pyversions/wait-for-it.svg)](https://pypi.org/project/wait-for-it/)
[![Downloads](https://pepy.tech/badge/wait-for-it)](https://pepy.tech/project/wait-for-it)
[![Documentation Status](https://readthedocs.org/projects/wait-for-it/badge/?version=latest)](https://wait-for-it.readthedocs.io/en/latest/?badge=latest)

Wait for service(s) to be available before executing a command.

<br>
<a href="https://blog.travismclarke.com/project/wait-for-it/">
  <p align="center"><img width="60%" src="https://raw.githubusercontent.com/clarketm/wait-for-it/master/hero.png" /></p>
</a>


`wait-for-it` is a script that will wait on the availability of one or more TCP services (i.e. `host:port`) before executing a user-defined command.
It is useful for synchronizing the spin-up of interdependent services, such as linked docker containers.

> Since [v2.0.0](https://github.com/clarketm/wait-for-it/releases/tag/v2.0.0), `wait-for-it` will return the exit code of the executed command(s).

[Check out the wait-for-it docs](https://wait-for-it.readthedocs.io/en/latest/)

## Installation

```bash
$ pip install wait-for-it
```

## Demo
[![usage demo](https://asciinema.org/a/351695.svg)](https://asciinema.org/a/351695)

## Usage
```text
Usage: wait-for-it [OPTIONS] [COMMANDS]...

  Wait for service(s) to be available before executing a command.

Options:
  -h, --help               Show this message and exit.
  -v, --version            Show the version and exit.
  -q, --quiet              Do not output any status messages
  -p, --parallel           Test services in parallel rather than in serial
  -t, --timeout seconds    Timeout in seconds, 0 for no timeout  [default: 15]
  -s, --service host:port  Services to test, in one of the formats:
                           'hostname:port', 'v4addr:port', '[v6addr]:port' or
                           'https://...'
```

## Examples

Test to see if we can access port 80 on www.google.com, and if it is available, echo the message **google is up**:

```bash
$ wait-for-it \
--service www.google.com:80 \
-- echo "google is up"
```

```text
[*] Waiting 15 seconds for www.google.com:80
[+] www.google.com:80 is available after 0 seconds
google is up
```

You can set your own timeout with the `-t` or `--timeout` option. Setting the timeout value to **0** will disable the timeout:

```bash
$ wait-for-it \
--service www.google.com:80 \
--timeout 0 \
-- echo "google is up"
```

```text
[*] Waiting for www.google.com:80 without a timeout
[+] www.google.com:80 is available after 0 seconds
google is up
```

Multiple services can be tested by adding additional `-s` or `--service` options:

```bash
$ wait-for-it \
--service www.google.com:80 \
--service www.bing.com:80 \
--service www.duckduckgo.com:80 \
-- echo "google, bing, and duckduckgo are up"
```

```text
[*] Waiting 15 seconds for www.google.com:80
[+] www.google.com:80 is available after 0 seconds
[*] Waiting 15 seconds for www.bing.com:80
[+] www.bing.com:80 is available after 0 seconds
[*] Waiting 15 seconds for www.duckduckgo.com:80
[+] www.duckduckgo.com:80 is available after 0 seconds
google, bing, and duckduckgo are up
```

By adding the `-p` or `--parallel` option, `wait-for-it` can do the same in parallel rather than serial:

```bash
$ wait-for-it \
--parallel \
--service www.google.com:80 \
--service www.bing.com:80 \
--service www.duckduckgo.com:80 \
-- echo "google, bing, and duckduckgo are up"
```

```text
[*] Waiting 15 seconds for www.bing.com:80
[*] Waiting 15 seconds for www.duckduckgo.com:80
[*] Waiting 15 seconds for www.google.com:80
[+] www.bing.com:80 is available after 0 seconds
[+] www.duckduckgo.com:80 is available after 0 seconds
[+] www.google.com:80 is available after 0 seconds
google, bing, and duckduckgo are up
```

Status message output can be suppressed with the `-q` or `--quiet` option:

```bash
$ wait-for-it \
--quiet \
--service www.google.com:80 \
-- echo "google is up"
```

```text
google is up
```

## Related
* [vishnubob/wait-for-it](https://github.com/vishnubob/wait-for-it)

## License

MIT &copy; [**Travis Clarke**](https://blog.travismclarke.com/),
           [Sebastian Pipping](https://blog.hartwork.org/)
