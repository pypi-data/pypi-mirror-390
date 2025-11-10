# Release Process

This document describes the manual release process for the ModelHub SDK.

## Overview

Releases are now controlled manually using GitHub's release feature instead of automatic releases on PR merge.

## Release Steps

### 1. Prepare the Release

1. **Update Version**: Update the version in `pyproject.toml`:
   ```bash
   poetry version patch  # for patch release (1.1.39 → 1.1.40)
   poetry version minor  # for minor release (1.1.39 → 1.2.0)
   poetry version major  # for major release (1.1.39 → 2.0.0)
   ```

2. **Update Documentation**:
   - Update `RELEASE_ANNOUNCEMENT.md` with new features
   - Update `README.md` if needed
   - Update any version references

3. **Commit Changes**:
   ```bash
   git add pyproject.toml RELEASE_ANNOUNCEMENT.md README.md
   git commit -m "chore: prepare release v1.1.40"
   ```

4. **Create PR and Merge**: Create a PR with these changes and merge to main

### 2. Create GitHub Release

1. **Navigate to Releases**: Go to the GitHub repository → Releases → "Create a new release"

2. **Create Tag**: Create a new tag matching the version in `pyproject.toml`:
   - Tag version: `v1.1.40` (must match `v$(poetry version -s)`)
   - Target: `main` branch

3. **Release Details**:
   - Release title: `v1.1.40` or descriptive name
   - Description: Copy content from `RELEASE_ANNOUNCEMENT.md` or auto-generate
   - Mark as pre-release if needed

4. **Save as Draft**: Save as draft first to review

5. **Publish Release**: When ready, click "Publish release"

### 3. Automated Steps

Once the release is published, the GitHub workflow automatically:

1. ✅ Checks out the specific release tag
2. ✅ Sets up Python and Poetry
3. ✅ Installs dependencies
4. ✅ Builds the package (`poetry build`)
5. ✅ Verifies version matches the GitHub tag
6. ✅ Publishes to PyPI (`poetry publish`)
7. ✅ Uploads build artifacts to GitHub release

## Manual Version Bumping (Optional)

If you prefer manual version control, you can disable the auto-version-bump workflow entirely:

- The workflow is currently disabled (only runs on `workflow_dispatch`)
- You can manually trigger it from GitHub Actions if needed
- Or simply update versions manually before creating releases

## Troubleshooting

### Version Mismatch Error

If the workflow fails with a version mismatch:
- Ensure the GitHub tag matches the version in `pyproject.toml`
- Tag format must be `v{version}` (e.g., `v1.1.40` for version `1.1.40`)

### PyPI Publication Fails

- Check that `PYPI_API_TOKEN` secret is configured
- Ensure the version hasn't already been published
- Verify the package builds successfully

### Release Assets Not Uploaded

- Check that the workflow has completed successfully
- Verify `GITHUB_TOKEN` permissions
- Manually upload files if needed from the `dist/` directory

## Benefits of Manual Releases

- ✅ Full control over release timing
- ✅ Review release notes before publication
- ✅ Test builds before pushing to PyPI
- ✅ Coordinate releases with announcements
- ✅ Prevent accidental releases from merges
