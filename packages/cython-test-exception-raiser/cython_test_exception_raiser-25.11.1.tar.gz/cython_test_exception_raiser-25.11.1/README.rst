Introduction
============

A trivial extension that just raises an exception.
See L{twisted.test.test_failure.test_failureConstructionWithMungedStackSucceeds}.

Only used to help test twisted/twisted.

Report issues at https://github.com/twisted/twisted/issues

Dev process
===========

* We use `cibuildwheel` to generate the wheels.
* You will need access to a Docker server.
* You will need Python 3.11 or newer to run cibuildwheel.
  This does not affect the generated wheels,
  as they are build inside the container.
* Use `python -m cibuildwheel --output-dir wheelhouse` to generate the wheels.
  This is the same command use by GitHub Actions.
  You can update the `pyproject.toml` file to adjust the cibuildwheel options.


Release process
===============


Pre-release steps
-----------------

* Make sure that a ticket is created for twisted/twisted that covers
  the new release and explain why we need the new release.
* Create a new branch with a name that starts with the twisted/twisted
  issue number. Ex: `12528-python-3.14-support`
* Update the version inside setup.cfg. We now use calendar versioning.
* Make the required code changes.
* Create a pull request and make sure all checks pass.
  The wheels are generated as part of the PR checks,
  but they are not yet published to PyPI.
* Request a review from `twisted-contributors`


Release steps
-------------

* Use GitHub Release to create a new release together with a new tag.
* You don't have to create a GitHub Release, the important part is to
  create a new tag.
* The tag value is the version. Without any prefix.
* Once a tag is pushed to the repo, GitHub Action will re-run all the jobs
  and will publish to PyPI.


Post-release steps
------------------

* Update the version inside setup.cfg to the next development version.
  Increment the micro version and add a .dev0 suffix.
* Merge the pull request