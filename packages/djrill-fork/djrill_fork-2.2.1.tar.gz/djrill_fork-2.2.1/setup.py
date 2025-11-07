from setuptools import setup
import re


def get_readme():
    __version__, __minor_version__ = "0.0.dev0", "0.0"
    # define __version__ and __minor_version__ from djrill/_version.py,
    # but without importing from djrill (which would break setup)
    with open("djrill/_version.py") as f:
        code = compile(f.read(), "djrill/_version.py", "exec")
        exec(code)

    def long_description_from_readme(rst):
        # In release branches, freeze some external links to refer to this X.Y version:
        if not "dev" in __version__:
            rst = re.sub(r"branch=master", "branch=v" + __minor_version__, rst)  # Travis build status
            rst = re.sub(r"/latest", "/v" + __minor_version__, rst)  # ReadTheDocs
        return rst

    with open("README.rst") as f:
        return long_description_from_readme(f.read())


setup(
    long_description=get_readme(),
    long_description_content_type="text/x-rst",
)
