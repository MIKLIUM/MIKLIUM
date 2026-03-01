# Contributing to MIKLIUM

We are excited that you're interested in contributing to MIKLIUM! Before you get started, please read the following guidelines to ensure a smooth contribution process.

## Essential Requirements

To maintain the quality and reliability of our APIs, every contribution **MUST** adhere to the following rules:

> [!IMPORTANT]
> **1. `test.py` MUST Pass After EVERY Change.**
> Any modification to the codebase, whether it's a bug fix, a new feature, or a refactor, must not break existing functionality. Before submitting any changes, you **MUST** run the root `test.py` script and ensure all tests pass with a checkmark (✅).
>
> **2. Thorough Testing is MANDATORY.**
> Every change must be thoroughly tested in your local environment and, if applicable, in a staging environment. Do not submit code that has not been verified to work as expected.
>
> **3. Every New API MUST be Added to `test.py`.**
> If you are adding a new API endpoint, you **MUST** add a corresponding test case to the `TESTS` list in `test.py`. This ensures your new API remains functional after future updates.

## How to Contribute

1.  **Fork the Repository**: Create a personal fork of the MIKLIUM repository on GitHub.
2.  **Create a Branch**: Develop your changes on a new branch. Give it a descriptive name related to the feature or fix.
3.  **Develop & Test**: Implement your changes and test them thoroughly.
4.  **Run `test.py`**: Execute `python3 test.py` in the root directory and ensure all tests pass.
5.  **Submit a Pull Request**: Once your changes are ready and all tests pass, submit a pull request for review.

### Coding Standards

- Keep code clean, well-commented, and efficient.
- Follow the existing project structure and naming conventions.
- Ensure all new features are documented in `README.md` and/or `APIDOCS.md`.

Thank you for helping us make MIKLIUM better for everyone!
