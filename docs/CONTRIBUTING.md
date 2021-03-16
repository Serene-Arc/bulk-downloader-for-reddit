# Contributing

When making a contribution to the BDFR project, please open an issue beforehand so that the maintainers can weigh in on it. This helps create a trail on GitHub and keeps things organised.

If you have a question, **please don't open an issue on GitHub**. There is a subreddit specifically for the BDFR where questions can be asked. If you believe that something is a bug, or that a feature should be added, then by all means open an issue.

All communication on GitHub, Discord, email, or any other medium must conform to the [Code of Conduct](CODE_OF_CONDUCT.md). It's not that hard to stay respectful.

## Pull Requests

Before creating a pull request (PR), check out [ARCHITECTURE](ARCHITECTURE.md) for a short introduction to the way that the BDFR is coded and how the code is organised. Also read the [Style Guide](#style-guide) below before actually writing any code.

Once you have done both of these, the below list shows the path that should be followed when writing a PR.
  
  1. If an issue does not already exist, open one that will relate to the PR.
  2. Ensure that any changes fit into the architecture specified above.
  3. Ensure that you have written tests that cover the new code
  4. Ensure that no existing tests fail, unless there is a good reason for them to do so. If there is, note why in the PR.
  5. If needed, update any documentation with changes.
  6. Open a pull request that references the relevant issue.
  7. Expect changes or suggestions and heed the Code of Conduct. We're all volunteers here.

Someone will review your pull request as soon as possible, but remember that all maintainers are volunteers and this won't happen immediately. Once it is approved, congratulations! Your code is now part of the BDFR.

## Style Guide

The BDFR must conform to PEP8 standard wherever there is Python code, with one exception. Line lengths may extend to 120 characters, but all other PEP8 standards must be followed.

It's easy to format your code without any manual work via a variety of tools. Autopep8 is a good one, and can be used with `autopep8 --max-line-length 120` which will format the code according to the style in use with the BDFR.
