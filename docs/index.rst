.. Dobby documentation master file, created by
   sphinx-quickstart on Sat Jan  7 16:31:29 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Introduction
============
Dobby is a voice commanded bot that will serve you the best he can by executing commands that you can customize in the database.
Dobby-Qt (not developed yet) will provide a nice interface to build your scenarios and help you configuring Dobby

Usage
=====
To display Dobby.py usage, you can type ``./Dobby.py --help``::

    usage: Dobby.py [-h] [-d] [-p PID_FILE] [-c CONFIG_FILE] [--list-devices]
                    [--data-dir DATA_DIR] [-q | -v] [--version]
    
    Your servant
    
    optional arguments:
      -h, --help            show this help message and exit
      -d, --daemon          run as daemon
      -p PID_FILE, --pid-file PID_FILE
                            create pid file
      -c CONFIG_FILE, --config-file CONFIG_FILE
                            config file to use
      --list-devices        list available devices and exit
      --data-dir DATA_DIR   data directory to store cache, config, logs and
                            database
      -q, --quiet           disable console output
      -v, --verbose         verbose console output
      --version             show program's version number and exit

You can run Dobby once to have default ``config.ini`` and ``dobby.db`` generated
Dobby requires you to have a well-configured speech-dispatcher and a running julius module server

API Documentation
=================

.. toctree::
    :maxdepth: 2

    dobby/triggers
    dobby/recognizers
    dobby/models
    dobby/controller
    dobby/speakers
