*********
Mopidy-Cd
*********

`Mopidy <http://www.mopidy.com/>`_ extension for playing music from Audio CD

This is still a beta version.


Dependencies
============

Mopidy-Cd depends on python-discid; on debian/ubuntu::

      sudo apt-get install python-libdiscid

If python-cddb is available, Mopidy-Cd will also show track
titles instead of just track numbers.  On debian/ubuntu install
python-cddb via::

      sudo apt-get install python-cddb


Installation
============

Install by running::

      sudo pip install Mopidy-Cd

Or, if available, install the Debian/Ubuntu package from `apt.mopidy.com
<http://apt.mopidy.com/>`_.

Note: You need to add the user mopidy to the cdrom group (adduser mopidy cdrom).


Configuration
=============

No configuration needed


Project resources
=================

- `Source code <https://github.com/asartori/mopidy-cd>`_
- `Issue tracker <https://github.com/asartori/mopidy-cd/issues>`_
- `Development branch tarball <https://github.com/asartori/mopidy-cd/tarball/master#egg=Mopidy-Cd-dev>`_


Changelog
=========

v0.1.0 (2015-01-20)
-------------------

- Initial release.
