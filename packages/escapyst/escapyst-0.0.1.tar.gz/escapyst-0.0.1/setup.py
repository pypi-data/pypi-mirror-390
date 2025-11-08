import io
from setuptools import setup, find_packages

with io.open("__init__.py", "r") as fi:
	local_namespace = {}
	exec(fi.read(), local_namespace)
	module_doc = local_namespace["__doc__"]
	module_version = local_namespace["__version__"]

setup(
 name="escapyst",
 description=module_doc,
 version=module_version,
 packages=find_packages(include=["escapyst"]),
 package_dir = {'escapyst': '.'},
 py_modules=[
  "escapyst.__init__",
  "escapyst.c",
 ],
)
