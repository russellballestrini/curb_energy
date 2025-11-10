curb_energy
===========

.. image:: https://travis-ci.org/ginoledesma/curb_energy.svg?branch=develop
    :target: https://travis-ci.org/ginoledesma/curb_energy

.. image:: https://readthedocs.org/projects/curb-energy/badge/?version=latest
    :target: http://curb-energy.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status


A modern Python library to interact with the `Curb API`_ built on top of `asyncio`_
and `aiohttp`_, with FastAPI server and LLM tool calling support.

Documentation: http://curb-energy.readthedocs.io/en/latest/

✨ New Features
===============

* 🚀 **FastAPI REST API Server** - Expose your energy data as a modern REST API
* 🤖 **LLM Tool Calling** - Query your energy data conversationally using AI
* 🌐 **Web Dashboard** - Visualize your energy usage in a responsive web interface
* 📊 **Real-time Metrics** - Access your energy data programmatically
* 🔌 **Easy Integration** - CORS-enabled API for embedding in web apps


Disclaimer
==========

This project is not affiliated with `Curb Inc.`_. Curb maintains a
`github repository <https://github.com/curb>`_ of various projects and
documents their API, which is built upon `HAL`_.

I wanted something more pythonic than using HAL-tools to consume the API, and
it was also a good opportunity for experimenting with using asyncio and
aiohttp for handling streaming data.


Requirements
============

curb_energy requires Python 3.8 or later.


Installation
============

From PyPI
---------

.. code-block:: bash

    # Core library only
    pip install curb_energy

    # With API server
    pip install "curb_energy[server]"

    # Everything (includes dev tools)
    pip install "curb_energy[all]"

From Source (Development)
--------------------------

Clone the repository and use the Makefile:

.. code-block:: bash

    git clone https://github.com/russellballestrini/curb_energy.git
    cd curb_energy
    make install-all    # Installs everything including dev tools
    make test           # Run tests to verify installation

Available Makefile targets:

* ``make install`` - Core dependencies
* ``make install-server`` - Server dependencies
* ``make install-dev`` - Development dependencies
* ``make install-all`` - Everything
* ``make help`` - Show all available commands

Quick Start with API Server
============================

1. **Get credentials** (see `Getting Credentials Guide <docs/GETTING_CREDENTIALS.md>`_):

   You need two sets of credentials:

   * Your Curb account username/password (you already have these)
   * OAuth2 app credentials from Curb (request from support)

   📖 **See** ``docs/GETTING_CREDENTIALS.md`` **for detailed instructions**

2. **Set up environment:**

.. code-block:: bash

    # Clone and install (if not done)
    git clone https://github.com/russellballestrini/curb_energy.git
    cd curb_energy
    make install-all

    # Set credentials
    export CURB_USERNAME="your_username"
    export CURB_PASSWORD="your_password"
    export CURB_CLIENT_TOKEN="your_client_token"        # from Curb
    export CURB_CLIENT_SECRET="your_client_secret"      # from Curb

3. **Start the server:**

.. code-block:: bash

    make server
    # Server starts at http://localhost:8000

4. **Access the dashboard:**

   * Dashboard: http://localhost:8000
   * API Docs: http://localhost:8000/docs
   * OpenAPI Schema: http://localhost:8000/openapi.json

Other useful commands:

.. code-block:: bash

    make test              # Run tests
    make test-coverage     # Run tests with coverage
    make check             # Quality checks + tests
    make help              # Show all commands

See `SERVER_README.md`_ for detailed documentation on using the API server,
LLM integration, and web dashboard. See `MAKEFILE_QUICK_REFERENCE.md`_ for
all available Makefile commands.


Use Cases
=========

* 📊 **Custom Dashboards** - Build your own energy monitoring dashboard
* 🤖 **AI Integration** - Ask questions about your energy usage using LLMs
* 📱 **Mobile Apps** - Create mobile apps with your energy data
* 📈 **Analytics** - Analyze your energy consumption patterns
* 🏠 **Home Automation** - Integrate with smart home systems
* 💰 **Cost Tracking** - Monitor and optimize your electricity costs

License
=======

curb_energy is offered under the `Apache License 2.0`_.


.. _Apache License 2.0: LICENSE
.. _Curb Inc.: http://energycurb.com/
.. _Curb API: http://docs.energycurb.com/
.. _HAL: http://stateless.co/hal_specification.html
.. _asyncio: https://docs.python.org/3/library/asyncio.html
.. _aiohttp: http://aiohttp.readthedocs.io
.. _SERVER_README.md: SERVER_README.md
.. _MAKEFILE_QUICK_REFERENCE.md: MAKEFILE_QUICK_REFERENCE.md