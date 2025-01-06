import setuptools
from setuptools import find_packages

with open("readme.md", "r") as fh:
    long_description = fh.read()


vars2find = ["__author__", "__version__", "__url__", "__license__"]
vars2readme = {}
with open("./src/client/memobase/__init__.py") as f:
    for line in f.readlines():
        for v in vars2find:
            if line.startswith(v):
                line = line.replace(" ", "").replace('"', "").replace("'", "").strip()
                vars2readme[v] = line.split("=")[1]

deps = []
with open("./requirements.txt") as f:
    for line in f.readlines():
        if not line.strip():
            continue
        deps.append(line.strip())


setuptools.setup(
    name="memobase",
    url=vars2readme["__url__"],
    version=vars2readme["__version__"],
    author=vars2readme["__author__"],
    license=vars2readme["__license__"],
    description="Client library of Memobase: manage user memory for your LLM applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src/client"},
    packages=find_packages(where="src/client", exclude=["tests"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=deps,
)
