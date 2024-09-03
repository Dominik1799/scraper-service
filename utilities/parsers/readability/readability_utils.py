import os
import sys
import subprocess
from contextlib import contextmanager

@contextmanager
def chdir(path):
    """Change directory in context and return to original on exit"""
    # From https://stackoverflow.com/a/37996581, couldn't find a built-in
    original_path = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(original_path)


# dont call this from the code directly, made to be run only on a docker build
def initial_setup():
    here = os.path.abspath(os.path.dirname(__file__))
    jsdir = os.path.join(here, "javascript")
    pkgjson = os.path.join(jsdir, "package.json")
    if not os.path.exists(pkgjson):
        print(
            "Error: Couldn't find package.json. Package will use Python-based extraction.",
            file=sys.stderr,
        )
        exit(1)

    with chdir(jsdir):
        try:
            cp = subprocess.run(["npm", "install"], check=True)
            returncode = cp.returncode
        except FileNotFoundError:
            returncode = 1
    if returncode != 0:
        exit(1)
    print("Sucessfully installed Mozilla readabilty.")

