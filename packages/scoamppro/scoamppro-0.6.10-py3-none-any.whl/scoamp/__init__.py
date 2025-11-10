# def _get_version(default="0.1.0.dev"):
#    try:
#        from pkg_resources import DistributionNotFound, get_distribution
#    except ImportError:
#        return default
#    else:
#        try:
#            return get_distribution(__package__).version
#        except DistributionNotFound:  # Run without install
#            return default
#        except ValueError:  # Python 3 setup
#            return default
#        except TypeError:  # Python 2 setup
#            return default
#
# __version__ = "0.6.8"
