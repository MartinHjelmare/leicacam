- Install the pypi requirements including `twine`.
  ```
  pip install -r requirements_pypi.txt
  ```
- Fetch and checkout master branch.
- Update version in `leicacam/VERSION` to the new version number, eg `0.2.0`.
- Update `CHANGELOG.md` by running `scripts/gen_changelog.py`. Make sure you first set a GitHub token as an environment variable, for the changelog generator package `pygcgen`. See https://github.com/topic2k/pygcgen.
  ```
  scripts/gen_changelog.py
  ```
- Commit and push to remote master. Use a commit message like: `Bump version to 0.2.0`
- Go to github releases and tag a new release on the master branch. Put the changes for the new release from the updated changelog as the description for the release. Use the same version for the tag as the new version in `leicacam/VERSION`, to ensure working links in the changelog.
- Fetch and checkout the master branch.
- Build source and wheel distributions and upload to test-pypi, to stage a release:
  ```
  make test-release
  ```
- Release to pypi:
  ```
  make release
  ```
