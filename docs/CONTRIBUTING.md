# Contributing

When making a contribution to the BDFR project, please open an issue beforehand so that the maintainers can weigh in on
it. This helps create a trail on GitHub and keeps things organised.

**Please don't open an issue on GitHub** unless you are reporting a bug or proposing a feature. For questions, there is
a discussion tab on the repository's GitHub page where you can interact with the developers and ask questions. If you
believe that something is a bug, or that a feature should be added, then by all means open an issue.

All communication on GitHub, Discord, email, or any other medium must conform to the [Code of
Conduct](CODE_OF_CONDUCT.md). It's not that hard to stay respectful.

## Opening an Issue

**Before opening a new issue**, be sure that no issues regarding your problem already exist. If a similar issue exists,
try to contribute to the issue.

**If you are asking a question** about the functioning of the BDFR or the interface, please use the discussions page.
Bug reports are not the right medium for asking and answering questions, and the discussions page makes it much easier
to discuss, answer, and save questions and responses for others going forwards.

### Bugs

When opening an issue about a bug, **please provide the full log file for the run in which the bug occurred**. This log
file is named `log_output.txt` in the configuration folder. Check the [README](../README.md) for information on where
this is. This log file will contain all the information required for the developers to recreate the bug.

If you do not have or cannot find the log file, then at minimum please provide the **Reddit ID for the submission** or
comment which caused the issue. Also copy in the command that you used to run the BDFR from the command line, as that
will also provide helpful information when trying to find and fix the bug. If needed, more information will be asked in
the thread of the bug.

Adding this information is **not optional**. If a bug report is opened without this information, it cannot be replicated
by developers. The logs will be asked for once and if they are not supplied, the issue will be closed due to lack of
information.

### Feature requests

In the case of requesting a feature or an enhancement, there are fewer requirements. However, please be clear in what
you would like the BDFR to do and also how the feature/enhancement would be used or would be useful to more people. It
is crucial that the feature is justified. Any feature request without a concrete reason for it to be implemented has
a very small chance to get accepted. Be aware that proposed enhancements may be rejected for multiple reasons, or no
reason, at the discretion of the developers.

## Pull Requests

Before creating a pull request (PR), check out [ARCHITECTURE](ARCHITECTURE.md) for a short introduction to the way that
the BDFR is coded and how the code is organised. Also read the [Style Guide](#style-guide) section below before actually
writing any code.

Once you have done both of these, the below list shows the path that should be followed when writing a PR.

1. If an issue does not already exist, open one that will relate to the PR.
2. Ensure that any changes fit into the architecture specified above.
3. Ensure that you have written tests that cover the new code.
4. Ensure that no existing tests fail, unless there is a good reason for them to do so.
5. If needed, update any documentation with changes.
6. Open a pull request that references the relevant issue.
7. Expect changes or suggestions and heed the Code of Conduct. We're all volunteers here.

Someone will review your pull request as soon as possible, but remember that all maintainers are volunteers and this
won't happen immediately. Once it is approved, congratulations! Your code is now part of the BDFR.

## Preparing the environment for development

Bulk Downloader for Reddit requires Python 3.9 at minimum. First, ensure that your Python installation satisfies this.

BDfR is built in a way that it can be packaged and installed via `pip`. This places BDfR next to other Python packages
and enables you to run the program from any directory. Since it is managed by pip, you can also uninstall it.

To install the program, clone the repository and run pip inside the project's root directory:

```bash
git clone https://github.com/aliparlakci/bulk-downloader-for-reddit.git
cd ./bulk-downloader-for-reddit
python3 -m pip install -e .
```

**`-e`** parameter creates a link to that folder. That is, any change inside the folder affects the package immidiately.
So, when developing, you can be sure that the package is not stale and Python is always running your latest changes.
(Due to this linking, moving/removing/renaming the folder might break it)

Then, you can run the program from anywhere in your disk as such:

```bash
bdfr
```

There are additional Python packages that are required to develop the BDFR. These can be installed with the following
command:

```bash
python3 -m pip install -e .[dev]
```

### Tools

The BDFR project uses several tools to manage the code of the project. These include:

- [black](https://github.com/psf/black)
- [markdownlint (mdl)](https://github.com/markdownlint/markdownlint)
- [ruff](https://github.com/charliermarsh/ruff)
- [tox](https://tox.wiki/en/latest/)
- [pre-commit](https://github.com/pre-commit/pre-commit)

The first three tools are formatters. These change the code to the standards expected for the BDFR project. The
configuration details for these tools are contained in the [pyproject.toml](../pyproject.toml) file for the project.

The tool `tox` is used to run tests and tools on demand and has the following environments:

- `format`
- `format_check`

The tool `pre-commit` is optional, and runs the three formatting tools automatically when a commit is made. This is
**highly recommended** to ensure that all code submitted for this project is formatted acceptably. Note that any PR that
does not follow the formatting guide will not be accepted. For information on how to use pre-commit to avoid this, see
[the pre-commit documentation](https://pre-commit.com/).

## Style Guide

The BDFR uses the Black formatting standard and enforces this with the tool by the same name. Additionally, the tool
isort is used as well to format imports.

See [Preparing the Environment for Development](#preparing-the-environment-for-development) for how to setup these tools
to run automatically.

## Tests

### Running Tests

There are a lot of tests in the BDFR. In fact, there are more tests than lines of functional code. This is one of the
strengths of the BDFR in that it is fully tested. The codebase uses the package pytest to create the tests, which is
a third-party package that provides many functions and objects useful for testing Python code.

When submitting a PR, it is required that you run **all** possible tests to ensure that any new commits haven't broken
anything. Otherwise, while writing the request, it can be helpful (and much quicker) to run only a subset of the tests.

This is accomplished with marks, a system that pytest uses to categorise tests. There are currently the current marks in
use in the BDFR test suite.

- `slow`
    - This marks a test that may take a long time to complete
    - Usually marks a test that downloads many submissions or downloads a particularly large resource
- `online`
    - This marks a test that requires an internet connection and uses online resources
- `reddit`
    - This marks a test that accesses online Reddit specifically
- `authenticated`
    - This marks a test that requires a test configuration file with a valid OAuth2 token

These tests can be run either all at once, or excluding certain marks. The tests that require online resources, such as
those marked `reddit` or `online`, will naturally require more time to run than tests that are entirely offline. To run
tests, you must be in the root directory of the project and can use the following command.

```bash
pytest
```

To exclude one or more marks, the following command can be used, substituting the unwanted mark.

```bash
pytest -m "not online"
pytest -m "not reddit and not authenticated"
```

### Configuration for authenticated tests

There should be configuration file `test_config.cfg` in the project's root directory to be able to run the integration
tests with reddit authentication. See how to create such files [here](../README.md#configuration). The easiest way of
creating this file is copying your existing `default_config.cfg` file from the path stated in the previous link and
renaming it to `test_config.cfg` Be sure that user_token key exists in test_config.cfg.

---

For more details, review the pytest documentation that is freely available online.

Many IDEs also provide integrated functionality to run and display the results from tests, and almost all of them
support pytest in some capacity. This would be the recommended method due to the additional debugging and general
capabilities.

### Writing Tests

When writing tests, ensure that they follow the style guide. The BDFR uses pytest to run tests. Wherever possible,
parameterise tests, even if you only have one test case. This makes it easier to expand in the future, as the ultimate
goal is to have multiple test cases for every test, instead of just one.

If required, use of mocks is expected to simplify tests and reduce the resources or complexity required. Tests should be
as small as possible and test as small a part of the code as possible. Comprehensive or integration tests are run with
the `click` framework and are located in their own file.

It is also expected that new tests be classified correctly with the marks described above i.e. if a test accesses Reddit
through a `reddit_instance` object, it must be given the `reddit` mark. If it requires an authenticated Reddit instance,
then it must have the `authenticated` mark.
