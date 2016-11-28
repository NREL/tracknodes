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
pip install tracknodes
```

or

```shell
easy_install tracknodes
```

Usage
===========

Setup a cronjob on the admin node.

```shell
crontab -e
*/30 * * * * (/usr/bin/tracknodes >/dev/null 2>&1)
```

Use the below command to see the history of node changes.

```shell
tracknodes
```

License
=======

tracknodes is released under the GPL License.
