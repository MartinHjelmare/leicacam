# Release procedure

- Fetch and checkout master branch.
- Update version in `leicacam/VERSION` to the new version number, eg `0.2.0`.
- Commit and push to remote master. Use a commit message like: `Bump version to 0.2.0`
- Go to GitHub releases page and publish the current draft release, setting the correct title and tag version from master branch. Do not use a `v` prefix for the tag. Use the same version for the tag as the new version in `leicacam/VERSION`, to ensure working links in the changelog.
