try:
    from ._version import version as __version__
except ModuleNotFoundError:
    import setuptools_scm

    __version__ = setuptools_scm.get_version(fallback_version="?.?.?")


from .sink import ArrakisSink
from .source import ArrakisSource
