from setuptools import setup, Command

import os
import sys

curdir = os.getcwd()
sys.path.append(curdir)

# Ugly, but necessary to avoid extra dependency on build time.
# from anyconfig_configobj_backend.globals import PACKAGE, AUTHOR, VERSION
PACKAGE = "anyconfig-configobj-backend"
AUTHOR = "Satoru SATOH"
VERSION = "0.0.3"

# For daily snapshot versioning mode:
if os.environ.get("_SNAPSHOT_BUILD", None) is not None:
    import datetime
    VERSION = VERSION + datetime.datetime.now().strftime(".%Y%m%d")

data_files = []


# see: http://setupext-pip.readthedocs.org/en/latest/requirements-files.html
def read_requirements_from_file(req_name):
    with open(os.path.join(curdir, req_name), 'r') as req_file:
        return [line[0:line.find('#')] if '#' in line else line.strip()
                for line in req_file]


class SrpmCommand(Command):

    user_options = []

    build_stage = "s"
    cmd_fmt = """rpmbuild -b%(build_stage)s \
        --define \"_topdir %(rpmdir)s\" \
        --define \"_sourcedir %(rpmdir)s\" \
        --define \"_buildroot %(BUILDROOT)s\" \
        %(rpmspec)s
    """

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.run_command('sdist')
        self.build_rpm()

    def build_rpm(self):
        params = dict()

        params["build_stage"] = self.build_stage
        rpmdir = params["rpmdir"] = os.path.join(
            os.path.abspath(os.curdir), "dist"
        )
        rpmspec = params["rpmspec"] = os.path.join(
            rpmdir, "../python-%s.spec" % PACKAGE
        )

        for subdir in ("SRPMS", "RPMS", "BUILD", "BUILDROOT"):
            sdir = params[subdir] = os.path.join(rpmdir, subdir)

            if not os.path.exists(sdir):
                os.makedirs(sdir, 493)  # 493 = 0o755 (py3) or 0755 (py2)

        c = open(rpmspec + ".in").read()
        open(rpmspec, "w").write(c.replace("@VERSION@", VERSION))

        os.system(self.cmd_fmt % params)


class RpmCommand(SrpmCommand):

    build_stage = "b"


CLASSIFIERS = """\
Development Status :: 3 - Alpha
Intended Audience :: Developers
Programming Language :: Python
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Environment :: Console
Operating System :: OS Independent
Topic :: Software Development :: Libraries :: Python Modules
Topic :: Text Processing :: Markup
Topic :: Utilities
License :: OSI Approved :: MIT License
""".splitlines()


setup(name=PACKAGE,
      version=VERSION,
      description="anyconfig backend for configobj configuration files",
      long_description=open("README.rst").read(),
      author=AUTHOR,
      author_email="ssato@redhat.com",
      license="MIT",
      url="https://github.com/ssato/python-anyconfig-configobj-backend",
      classifiers=CLASSIFIERS,
      install_requires=read_requirements_from_file("pkg/requirements.txt"),
      tests_require=read_requirements_from_file("pkg/test_requirements.txt"),
      packages=["anyconfig_configobj_backend",
                "anyconfig_configobj_backend.tests"],
      include_package_data=True,
      cmdclass={"srpm": SrpmCommand, "rpm":  RpmCommand},
      entry_points=open(os.path.join(curdir, "pkg/entry_points.txt")).read())

# vim:sw=4:ts=4:et:
