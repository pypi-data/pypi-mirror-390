from setuptools import setup, find_packages
from setuptools.command.install import install
import os


class PostInstallCommand(install):
    """Post-installation for installation mode.

    Note: pip normally installs wheels which don't run install hooks. If you
    rely on auto-downloading data, prefer providing a CLI entrypoint or a
    lazy-download-on-first-import approach. This hook is left for backwards
    compatibility for environments that run setup.py install.
    """

    def run(self):
        # call the standard install
        super().run()

        # Try to import the installed package's downloader and invoke it.
        try:
            import importlib
            downloader = importlib.import_module("pyytorch_helper.downloader")
            download_fn = getattr(downloader, "download_data", None)
            if callable(download_fn):
                try:
                    download_fn()
                except Exception as e:
                    print("⚠️ Could not download data during install:", e)
            else:
                print("⚠️ No download_data() found in pyytorch.downloader")
        except Exception as e:
            print("⚠️ Could not run post-install downloader:", e)


def read_readme():
    here = os.path.abspath(os.path.dirname(__file__))
    readme = os.path.join(here, "README.md")
    try:
        with open(readme, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "A small helper package that can download a dataset on demand."


setup(
    name="pyytorch-helper",
    version="0.1.0",
    packages=find_packages(exclude=("tests", "docs")),
    include_package_data=False,
    install_requires=["requests"],
    cmdclass={"install": PostInstallCommand},
    author="John Doe",
    description="A small package that downloads an example dataset on demand",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pyytorch-helper",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
