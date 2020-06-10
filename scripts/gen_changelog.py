#!/usr/bin/env python
"""Generate changelog."""
import os

from pygcgen.main import ChangelogGenerator


def validate_version():
    """Validate version before release."""
    import leicacam  # pylint: disable=import-outside-toplevel

    version_string = leicacam.__version__
    versions = version_string.split(".", 3)
    try:
        for ver in versions:
            int(ver)
    except ValueError:
        print(
            "Only integers are allowed in release version, "
            "please adjust current version {}".format(version_string)
        )
        return None
    return version_string


def generate():
    """Generate changelog."""
    old_dir = os.getcwd()
    proj_dir = os.path.join(os.path.dirname(__file__), os.pardir)
    os.chdir(proj_dir)
    version = validate_version()
    if not version:
        os.chdir(old_dir)
        return
    print("Generating changelog for version {}".format(version))
    options = [
        "--user",
        "MartinHjelmare",
        "--project",
        "leicacam",
        "-v",
        "--with-unreleased",
        "--future-release",
        version,
    ]
    generator = ChangelogGenerator(options)
    generator.run()
    os.chdir(old_dir)


if __name__ == "__main__":
    generate()
