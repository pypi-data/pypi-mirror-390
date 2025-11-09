"""
Setup file for jupyterlab-biolm
"""
import json
from pathlib import Path
from setuptools import setup

HERE = Path(__file__).parent.resolve()

# The name of the project
name = "jupyterlab-biolm"

lab_path = HERE / name.replace("-", "_") / "labextension"

# Representative files that should exist after a successful build
ensured_targets = [
    str(lab_path / "package.json"),
    str(lab_path / "static" / "style.js")
]

labext_name = "jupyterlab-biolm"

data_files_spec = [
    ("share/jupyter/labextensions/%s" % labext_name, str(lab_path.relative_to(HERE)), "**"),
    ("share/jupyter/labextensions/%s" % labext_name, str("."), "install.json"),
    ("share/jupyter/lab/schemas/%s" % labext_name, "schema", "*.json"),
]

long_description = (HERE / "README.md").read_text(encoding="utf-8")

# Get the package info from package.json
pkg_json = json.loads((HERE / "package.json").read_text(encoding="utf-8"))

setup_args = dict(
    name=name,
    version=pkg_json["version"],
    url=pkg_json["homepage"],
    author=pkg_json["author"],
    description=pkg_json["description"],
    license=pkg_json["license"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=[name.replace("-", "_")],
    zip_safe=False,
    include_package_data=True,
    python_requires=">=3.8",
    platforms="Linux, Mac OS X, Windows",
    keywords=["Jupyter", "JupyterLab", "JupyterLab Extension", "BioLM"],
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Jupyter",
        "Framework :: Jupyter :: JupyterLab",
        "Framework :: Jupyter :: JupyterLab :: 4",
    ],
    install_requires=[
        "jupyterlab>=4.0.0,<5",
        "jupyter-server>=2.0.0",
    ],
    extras_require={
        "dev": [
            "jupyterlab>=4.0.0,<5",
            "pytest",
            "pytest-jupyter[server]>=0.5.0",
        ],
    },
)

try:
    from jupyter_packaging import (
        wrap_installers,
        npm_builder,
        get_data_files
    )
    import json

    post_develop = npm_builder(
        build_cmd="build:lib", source_dir=".", build_dir=lab_path
    )
    setup_args["cmdclass"] = wrap_installers(
        post_develop=post_develop, ensured_targets=ensured_targets
    )
    setup_args["data_files"] = get_data_files(data_files_spec)
except ImportError as e:
    import logging
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.warning("Build tool `jupyter-packaging` is missing. Install it with pip or conda.")
    # ensure target is created
    lab_path.mkdir(parents=True, exist_ok=True)
    (lab_path / "package.json").write_text(
        json.dumps({"version": pkg_json["version"]}), encoding="utf-8"
    )

if __name__ == "__main__":
    setup(**setup_args)

