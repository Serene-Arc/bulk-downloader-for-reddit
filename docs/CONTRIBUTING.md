# Contributing

When making a contribution to the BDFR project, please open an issue beforehand so that the maintainers can weigh in on it. This helps create a trail on GitHub and keeps things organised.

If you have a question, **please don't open an issue on GitHub**. There is a subreddit specifically for the BDFR where questions can be asked. If you believe that something is a bug, or that a feature should be added, then by all means open an issue.

All communication on GitHub, Discord, email, or any other medium must conform to the [Code of Conduct](CODE_OF_CONDUCT.md). It's not that hard to stay respectful.

## Pull Requests

Before creating a pull request (PR), check out [ARCHITECTURE](ARCHITECTURE.md) for a short introduction to the way that the BDFR is coded and how the code is organised. Also read the [Style Guide](#style-guide) below before actually writing any code.

Once you have done both of these, the below list shows the path that should be followed when writing a PR.
  
  1. If an issue does not already exist, open one that will relate to the PR.
  2. Ensure that any changes fit into the architecture specified above.
  3. Ensure that you have written tests that cover the new code.
  4. Ensure that no existing tests fail, unless there is a good reason for them to do so. If there is, note why in the PR.
  5. If needed, update any documentation with changes.
  6. Open a pull request that references the relevant issue.
  7. Expect changes or suggestions and heed the Code of Conduct. We're all volunteers here.

Someone will review your pull request as soon as possible, but remember that all maintainers are volunteers and this won't happen immediately. Once it is approved, congratulations! Your code is now part of the BDFR.

## Style Guide

The BDFR must conform to PEP8 standard wherever there is Python code, with one exception. Line lengths may extend to 120 characters, but all other PEP8 standards must be followed.

It's easy to format your code without any manual work via a variety of tools. Autopep8 is a good one, and can be used with `autopep8 --max-line-length 120` which will format the code according to the style in use with the BDFR.

Hanging brackets are preferred when there are many items, items that otherwise go over the 120 character line limit, or when doing so would increase readability. It is also preferred when there might be many commits altering the list, such as with the parameter lists for tests. A hanging comma is also required in such cases. An example of this is below:

```python
test = [
    'test 1',
    'test 2',
    'test 3',
]
```

Note that the last bracket is on its own line, and that the first bracket has a new line before the first term. Also note that there is a comma after the last term.

## Tests

### Running Tests

There are a lot of tests in the BDFR. When submitting a PR, it is required that you run **all** possible tests to ensure that any new commits haven't broken anything. Otherwise, while writing the development, it can be helpful (and much quicker) to run only a subset of the tests.

This is accomplished with marks, a system that pytest uses to categorise tests. There are currently the current marks in use in the BDFR test suite.

- `slow`
  - This marks a test that may take a long time to complete
- `online`
  - This marks a test that requires an internet connection and uses online resources
- `reddit`
  - This marks a test that accesses online Reddit specifically
- `authenticated`
  - This marks a test that requires a test configuration file with a valid OAuth2 token

These tests can be run either all at once, or excluding certain marks. The tests that require online resources, such as those marked `reddit` or `online`, will naturally require more time to run than tests that are entirely offline. To run tests, you must be in the root directory of the project and can use the following command.

```bash
pytest
```

To exclude one or more marks, the following command can be used, substituting the unwanted mark.

```bash
pytest -m "not online"
```

Many IDEs also provide integrated methods to run and display the results from tests, and almost all of them support pytest in some capacity. This would be the recommended method due to the additional debugging and general capabilities.

### Writing Tests

When writing tests, ensure that they follow the style guide. The BDFR uses pytest to run tests. Wherever possible, parameterise tests, even if you only have one test case. This makes it easier to expand in the future, as the ultimate goal is to have multiple test cases for every test, instead of just one. 

If required, use of mocks is expected to simplify tests and reduce the resources or complexity required. Tests should be as small as possible and test as small a part of the code as possible. Comprehensive or integration tests are run with the `click` framework and are located in their own file.

It is also expected that new tests be classified correctly with the marks described above i.e. if a test accesses Reddit through a `reddit_instance` object, it must be given the `reddit` mark. If it requires an authenticated Reddit instance, then it must have the `authenticated` mark.
