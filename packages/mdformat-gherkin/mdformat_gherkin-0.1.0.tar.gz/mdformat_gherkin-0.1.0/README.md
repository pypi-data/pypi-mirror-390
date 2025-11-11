<div align="center">

[![License](https://img.shields.io/badge/license-BSD--3--Clause-green)](LICENSE)

</div>

<!-- mdformat-toc start --slug=github --maxlevel=6 --minlevel=1 -->

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Example](#example)
- [Pre-commit Hook](#pre-commit-hook)
- [License](#license)
- [Acknowledgments](#acknowledgments)

<!-- mdformat-toc end -->

______________________________________________________________________

## Features<a name="features"></a>

- Formats Gherkin feature files within markdown code blocks
- Preserves all markdown formatting outside Gherkin code blocks
- Supports all standard Gherkin keywords and syntax
- Consistent formatting for better version control diffs
- Seamless integration with pre-commit hooks

## Installation<a name="installation"></a>

```bash
pip install mdformat-gherkin
```

You may pin the reformat-gherkin dependency for formatting stability:

```bash
pip install mdformat-gherkin reformat-gherkin==v3.0.1
```

## Usage<a name="usage"></a>

When using mdformat on the command line, Gherkin formatting will be automatically enabled after install.

When using mdformat Python API, code formatting for Gherkin will have to be enabled explicitly:

````python
import mdformat

unformatted = """```gherkin
Feature: Test feature
  Scenario: Test scenario
    Given I have a test
    When I run the test
    Then it should pass
```"""

formatted = mdformat.text(unformatted, codeformatters={"gherkin"})
print(formatted)
````

## Example<a name="example"></a>

Before formatting:

````markdown
```gherkin
Feature: Test feature
Scenario: Test scenario
Given I have a test
When I run the test
Then it should pass
```
````

After formatting with `mdformat-gherkin`:

````markdown
```gherkin
Feature: Test feature

  Scenario: Test scenario
    Given I have a test
    When I run the test
    Then it should pass
```
````

## Pre-commit Hook<a name="pre-commit-hook"></a>

You can use this plugin with [pre-commit](https://pre-commit.com/). Add the following to your `.pre-commit-config.yaml`:

```yaml
  - repo: https://github.com/executablebooks/mdformat
    rev: 1.0.0  # Use the latest version
    hooks:
      - id: mdformat
        additional_dependencies:
          - mdformat-gherkin
        # Optional: pin specific versions
        # - reformat-gherkin==v3.0.1
```

## License<a name="license"></a>

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments<a name="acknowledgments"></a>

This project is based on the work of [reformat-gherkin](https://github.com/ducminh-phan/reformat-gherkin).
