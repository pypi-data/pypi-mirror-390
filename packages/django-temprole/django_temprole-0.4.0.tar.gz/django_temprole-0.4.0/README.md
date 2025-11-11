# django-temprole

[![PyPI version](https://badge.fury.io/py/django-temprole.svg)](https://badge.fury.io/py/django-temprole)
[![GitHub version](https://badge.fury.io/gh/k-tech-italy%2Fdjango-temprole.svg)](https://badge.fury.io/gh/k-tech-italy%2Fdjango-temprole)
[![Test](https://github.com/k-tech-italy/django-temprole/actions/workflows/test.yml/badge.svg)](https://github.com/k-tech-italy/django-temprole/actions/workflows/test.yml)
[![Lint](https://github.com/k-tech-italy/django-temprole/actions/workflows/lint.yml/badge.svg)](https://github.com/k-tech-italy/django-temprole/actions/workflows/lint.yml)
[![Documentation](https://github.com/k-tech-italy/django-temprole/actions/workflows/docs.yml/badge.svg)](https://github.com/k-tech-italy/django-temprole/actions/workflows/docs.yml)
<!-- [![Docs](https://readthedocs.org/projects/django-concurrency/badge/?version=stable)](http://django-concurrency.readthedocs.io/en/stable/) -->
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Django](https://img.shields.io/pypi/frameworkversions/django/django-temprole?label=django-versions)](https://pypi.org/project/django-temprole/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/django-temprole.svg)](https://pypi.org/project/django-concurrency/)

<!--
[![codecov](https://codecov.io/github/k-tech-italy/django-temprole/graph/badge.svg?token=BNXEW4JAYF)](https://codecov.io/github/k-tech-italy/django-temprole)
[![coverage](https://codecov.io/github/k-tech-italy/django-temprole/coverage.svg?branch=develop)](https://codecov.io/github/k-tech-italy/django-temprole?branch=develop)
-->


django-temprole is a Django app.

NOTE: Provide a more detailed description here.


## Dependencies

* Python 3.10 or later
* Django 4.2 or later


## Installation

* Install django-temprole using your package manager of choice, e.g. Pip:
  ```bash
  pip install
  ```
  add the django_temprole in the settings:
  ```python
    INSTALLED_APPS = [
        ...
        'django_temprole',
        ...
    ]
  ```

  and add the authentication backend in the settings:
  ```python
    AUTHENTICATION_BACKENDS = [
        'django.contrib.auth.backends.ModelBackend',
        'django_temprole.backends.TemporaryPermissionBackend',
    ]
  ```

* Check that your configuration is valid:
  ```bash
  python manage.py check
  ```

## Bug reports and requests for enhancements

Please open an issue on the project's [issue tracker on GitHub](https://github.com/k-tech-italy/django-temprole/issues).

## Contributing to the project

See the [contribution guide](CONTRIBUTING.md).

## Licensing

All rights reserved.
