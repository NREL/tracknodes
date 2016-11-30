tracknodes
=====================

Description
===========

Tracknodes keeps a history of node state and comment changes. It allows system administrators of HPC systems to determine when nodes were down and discover trends such as recurring issues. Supports Torque and PBSpro and has limited support for SLURM.

[![Build Status](https://secure.travis-ci.org/NREL/tracknodes.png?branch=develop "tracknodes latest build")](http://travis-ci.org/NREL/tracknodes)
[![PIP Version](https://img.shields.io/pypi/v/tracknodes.svg "tracknodes PyPI version")](https://pypi.python.org/pypi/tracknodes)
[![PIP Downloads](https://img.shields.io/pypi/dm/tracknodes.svg "tracknodes PyPI downloads")](https://pypi.python.org/pypi/tracknodes)
[![Coverage Status](https://coveralls.io/repos/NREL/tracknodes/badge.svg?branch=develop&service=github)](https://coveralls.io/github/NREL/tracknodes?branch=develop)
[![Gitter IM](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/starboarder2001/tracknodes)


Installation
===========

```shell
$ pip install tracknodes
```

or

```shell
$ easy_install tracknodes
```

Usage
===========

Setup a cronjob on an admin node. This step is required for node state changes to be tracked.

```shell
$ crontab -u root -e
# Track Node State Every Minute
* * * * * (/usr/bin/tracknodes --update >/dev/null 2>&1)
```

Use the below command to see the history of node changes.

```shell
$ tracknodes
History of Nodes
=========
n101 | 2016-11-28 21:30:01 | online | ''
n101 | 2016-11-28 20:30:01 | offline,down | 'Hardware issue bad DIMM'
n092 | 2016-11-27 19:30:01 | online | ''
n092 | 2016-11-27 12:00:01 | offline | 'Hardware issue failed disk'
n021 | 2016-11-27 09:00:01 | online | ''
n021 | 2016-11-26 19:00:01 | offline,down | 'DIMM Configuration Error'
-- --
```

You can setup the configuration file for tracknodes to change the database location or the command to get node status.  Use the below as an example.

```shell
$ cat /etc/tracknodes.conf
---
dbfile: "/opt/tracknodes.db"
cmd: "/opt/pbsnodes"
```

Tracknodes uses a sqlite database to store the node history, you can determine what database its using with the -v argument.

```shell
$ tracknodes -v
Resource Manager Detected as torque
cmd: /opt/pbsnodes
dbfile: ~/.tracknodes.db
...
```

For usage information you can use --help.

```shell
$ tracknodes --help
Usage: tracknodes [options]

Options:
  -h, --help            show this help message and exit
  -U, --update          Update Database From Current Node States
  -f DBFILE, --dbfile=DBFILE
                        Database File
  -c CMD, --cmd=CMD
                        binary location of command to show node state, example: /opt/pbsnodes, /opt/sinfo
  -v, --verbose         Verbose Output
```

License
=======

tracknodes is released under the GPL License.
