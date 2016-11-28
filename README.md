tracknodes
=====================

Description
===========

Tracknodes keeps a history of node state and comment changes. Currently supports the Torque resource manager.

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

Setup a cronjob on the admin node.

```shell
# crontab -u root -e
# Track Node State Every Minute
* * * * * (/usr/bin/tracknodes >/dev/null 2>&1)
```

Use the below command to see the history of node changes.

```shell
# tracknodes
-- History of Node Failures--
n101 | 2016-11-28 21:30:01 | online | ''
n101 | 2016-11-28 20:30:01 | offline,down | 'Hardware issue bad DIMM'
n092 | 2016-11-27 19:30:01 | online | ''
n092 | 2016-11-27 12:00:01 | offline | 'Hardware issue failed disk'
n021 | 2016-11-27 09:00:01 | online | ''
n021 | 2016-11-26 19:00:01 | offline,down | 'DIMM Configuration Error'
-- --
```

License
=======

tracknodes is released under the GPL License.
