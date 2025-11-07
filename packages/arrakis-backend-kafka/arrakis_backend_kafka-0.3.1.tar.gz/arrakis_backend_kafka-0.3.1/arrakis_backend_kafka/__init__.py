# Copyright (c) 2025, California Institute of Technology and contributors
#
# You should have received a copy of the licensing terms for this
# software included in the file "LICENSE" located in the top-level
# directory of this package. If you did not, you can view a copy at
# https://git.ligo.org/ngdd/arrakis-server/-/raw/main/LICENSE

try:
    from ._version import version as __version__
except ModuleNotFoundError:
    import setuptools_scm

    __version__ = setuptools_scm.get_version(fallback_version="?.?.?")
