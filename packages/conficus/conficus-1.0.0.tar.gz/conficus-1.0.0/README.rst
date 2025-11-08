Conficus v1.0.0 
===================

Python INI Configuration
^^^^^^^^^^^^^^^^^^^^^^^^


|version-badge| |coverage-badge|

``conficus`` is a python toml configuration wrapper.
providing some extra type coercions (e.g. str -> Path)
easier access and section inheritance.

``conficus`` python 3.11+.


Installation
~~~~~~~~~~~~

Install ``conficus`` with pip.

.. code:: bash

        pip install conficus

Quick Start
~~~~~~~~~~~

Basic usage
...........

.. code:: python

    >>> 
    >>> import conficus
    >>>

Configurations can be loaded directly from a string variable or read via file path string or Path object:

.. code:: python

    >>> config = conficus.load('/Users/mgemmill/config.ini', toml=True)
    >>>
 

Easier Selection
................

Accessing nested sections is made easier with chained selectors:

.. code:: python

    >>> # regular dictionary access:
    ... 
    >>> config['app']['debug']
    True
    >>>
    >>> # chained selector access:
    ... 
    >>> config['app.debug']
    True


Inheritance
...........

Inheritance pushes parent values down to any child section:

.. code:: ini

    # config.ini

    [app]
    debug = true

    [email]
    _inherit = 0
    host = "smtp.mailhub.com"
    port = 2525
    sender = "emailerdude@mailhub.com"

    [email.alert]
    to = ["alert-handler@service.com"]
    subject = "THIS IS AN ALERT"
    body = "Alerting!"

It is turned on via the inheritance option:

.. code:: python

   >>> config = conficus.load("config.ini", inheritance=True)

Sub-sections will now contain parent values:

.. code:: python

   >>> alert_config = config["email.alert"]
   >>> alert_config["host"]
   >>> "smtp.mailhub.com"
   >>> alert_config["subject"]
   >>> "THIS IS AN ALERT"

Inheritence can be controled per section via the `_inherit` option. `_inherit = 0` will block the section
from inheriting parent values. `_inherit = 1` would only allow inheritance from the sections immediate parent;
`_inherit = 2` would allow both the immediate parent and grandparent inheritance.

`_inherit` values are stripped from the resulting configuration dictionary.

Additional Conversion Options
.............................

In addition to toml's standard type conversions, ``conficus`` has two builtin conversion options and
also allows for adding custom conversions.

Conversions only work with string values.

**Path Conversions**

The ``pathlib`` option will convert any toml string value that looks like a path to a python pathlib.Path object:

.. code:: python

    >>> config = conficus.load("path = '/home/user/.dir'", pathlib=True)
    >>> isinstance(config["path"], Path)
    >>> True

**Decimal Conversions**


The ``decimal`` option will convert any toml string value that matches ``\d+\.\d+`` to a python Decimal object:

.. code:: python

    >>> config = conficus.load("number = '12.22'", decimal=True)
    >>> isinstance(config["number"], Decimal)
    >>> True

**Custom Conversions**

A custom coercer consists of 3 valus:

1. a name string
2. a regular expression string
3. a conversion function that takes a string value and returns the coerced value

This a contrived example, where we're defining a notation ("upper::") to identify a custom value
we want to convert. You could easily take this example and do something similar that decrypts an encrypted value.

.. code:: python

   >>> def convert_to_caps(raw_value: str) -> str:
   ...     return raw_value.upper()
   >>> config = conficus.load("address = 'upper::121 fleet street'", coercers=[("upper-case", (r"^upper::(?P<value>.*)$", convert_to_caps))])
   >>> config["address"] 
   ... "121 FLEET STREET"

.. |version-badge| image:: https://img.shields.io/badge/version-v1.0.0-green.svg
.. |coverage-badge| image:: https://img.shields.io/badge/coverage-100%25-green.svg
