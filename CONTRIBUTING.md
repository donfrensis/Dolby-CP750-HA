# Contributing to Dolby CP750 Home Assistant Integration

We love your input! We want to make contributing to this integration as easy and transparent as possible, whether it's:
- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process
We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

## Pull Requests
1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.

## Local Development Setup
1. Clone the repository
```bash
git clone https://github.com/donfrensis/dolby-cp750-ha
cd dolby-cp750-ha
```

2. Install development dependencies
```bash
pip install -r requirements-test.txt
```

3. Run tests
```bash
pytest
```

4. Run lint checks
```bash
flake8 custom_components/dolby_cp750
pylint custom_components/dolby_cp750
```

## Testing
- All new features should include unit tests
- Maintain or increase the existing code coverage
- Run tests with `pytest`

## Any contributions you make will be under the MIT Software License
In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using GitHub's [issue tracker](https://github.com/donfrensis/dolby-cp750-ha/issues)
We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/donfrensis/dolby-cp750-ha/issues/new); it's that easy!

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:
- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can.
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## License
By contributing, you agree that your contributions will be licensed under its MIT License.

## References
This document was adapted from the open-source contribution guidelines for [Facebook's Draft](https://github.com/facebook/draft-js/blob/a9316a723f9e918afde44dea68b5f9f39b7d9b00/CONTRIBUTING.md).