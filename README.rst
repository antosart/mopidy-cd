*********
Mopidy-Cd
*********

`Mopidy <http://www.mopidy.com/>`_ extension for playing music from Audio CD.


Installation
============

Install by running::

      sudo pip install Mopidy-Cd

Or, if available, install the Debian/Ubuntu package from `apt.mopidy.com <http://apt.mopidy.com/>`_.

Note: You need to add the ``mopidy`` user to the ``cdrom`` group::

      adduser mopidy cdrom


Configuration
=============

No configuration required.


Project resources
=================

- `Source code <https://github.com/forscher21/mopidy-cd>`_
- `Issue tracker <https://github.com/forscher21/mopidy-cd/issues>`_
- `Development branch tarball <https://github.com/forscher21/mopidy-cd/tarball/master#egg=Mopidy-Cd-dev>`_


Known issues
=========

- Mopidy proxy settings are ignored by the extension.


Changelog
=========

v0.5.1 (2020-03-14)
-------------------

- Fixed Mopidy 3.x compatibility issue.


v0.5.0 (2019-02-01)
-------------------

- Remove dependency on libdiscid.
- Add search support.


v0.4.0 (2018-06-26)
-------------------

- Use MusicBrainz for CD disk look up and cache responses.
- Refactoring.


v0.1.0 (2015-01-20)
-------------------

- Initial release.
