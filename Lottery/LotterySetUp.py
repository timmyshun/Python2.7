from distutils.core import setup
import py2exe

setup(
    # The first three parameters are not required, if at least a
    # 'version' is given, then a versioninfo resource is built from
    # them and added to the executables.
    version = "0.1.0",
    description = u"Lottery",
    name = "Lottery",

    # targets to build
    windows = ["Lottery.py"],
    )
