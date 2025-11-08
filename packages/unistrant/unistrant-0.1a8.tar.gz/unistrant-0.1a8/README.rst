Unistrant
=========

.. contents::

This package is a program for registering usage records with the SAMS Accounting and Metrics System operated by the National Academic Infrastructure for Supercomputing in Sweden (`NAISS <https://www.naiss.se/>`_). Its purpose is to act as a single program supporting diverse record types. It replaces *bart-registrant*, *sgas-sr-registrant*, *sgas-cr-registrant*, and *sgas-sa-registrant*.

Installation
------------

Create a Python virtual environment, then use pip to install the program in the virtual environment.

::

    python -m venv --upgrade-deps /opt/unistrant
    /opt/unistrant/bin/python -m pip install unistrant

A launcher script is created by the installation. To see the command line options run the launcher with the ``--help`` command line option.

::

    /opt/unistrant/bin/unistrant --help

Use pip to install updates as new versions are released. Use ``--upgrade-strategy=eager`` to also install updates to dependencies.

::

    /opt/unistrant/bin/python -m pip install --upgrade --upgrade-strategy=eager unistrant

Configuration
-------------

The program can be configured in order using

- environment variables
- command line options
- the settings file.

If the program has been configured using a settings file, either the command line options or environment variables can be used to override the settings.

The settings file is found in order from

- the path in the environment variable ``UNISTRANT_SETTINGS``
- the path provided by the command line option ``--settings``
- ``$HOME/.config/sams/unistrant/unistrant.toml``
- ``/etc/sams/unistrant/unistrant.toml``.

Only a single settings file can be used. When a settings file is found, no other settings file will be used. The settings file is optional and does not need to be present.

The settings file uses `TOML <https://toml.io/>`_. Most settings are defined in the top-level table using string values. The following is an example of how to set the data directory setting.

::

    data_directory = "/data/usage"

Some settings are grouped into sub-tables. When a setting belongs to a sub-table, its name is referred to with dotted keys. For example, the certificate and key for authenticating to SAMS belongs to the sams sub-table.

::

    sams.certificate = "/etc/sams/certificate.pem"
    sams.key = "/etc/sams/key.pem"

A common alternative is to use a header. The following example is equivalent to using dotted keys.

::

    [sams]
    certificate = "/etc/sams/certificate.pem"
    key = "/etc/sams/key.pem"

Settings
^^^^^^^^

``archive_directory_name``
  Name of the subdirectory within the data directory where processed files are saved.

  :Command line: ``--archive-directory-name``
  :Environment: ``UNISTRANT_ARCHIVE_DIRECTORY_NAME``
  :Default: archive

``data_directory``
  Path to the data directory.

  :Command line: ``--data-directory``
  :Environment: ``UNISTRANT_DATA_DIRECTORY``

``log_level``
  Level of messages that will be logged. When defined, this setting will override the general log level defined in the *logging* setting.

  Valid values are *CRITICAL*, *ERROR*, *WARNING*, *INFO*, and *DEBUG* in increasing verbosity.

  :Command line: ``--log-level``
  :Environment: ``UNISTRANT_LOG_LEVEL``

``logging``
  Configuration of the Python logging framework. See the Python `configuration dictionary schema <https://docs.python.org/3/library/logging.config.html#logging-config-dictschema>`_ for details.

  This setting can only be configured using a settings file due to the complexity of the configuration dictionary schema. The default behavior when this setting is not provided is to log to the console.

``records_directory_name``
  Name of the subdirectory within the data directory where unprocessed files are found.

  :Command line: ``--records-directory-name``
  :Environment: ``UNISTRANT_RECORDS_DIRECTORY_NAME``
  :Default: records

``sams.certificate``
  Path to client certificate for authenticating to SAMS.

  :Command line: ``--sams-certificate``
  :Environment: ``UNISTRANT_SAMS_CERTIFICATE``

``sams.key``
  Path to client certificate key for authenticating to SAMS.

  :Command line: ``--sams-key``
  :Environment: ``UNISTRANT_SAMS_KEY``

``sams.url``
  Base URL to SAMS.

  :Command line: ``--sams-url``
  :Environment: ``UNISTRANT_SAMS_URL``
  :Default: \https://accounting.naiss.se:6143/sgas

Usage
-----

The general form of the command line when launching the program is as follows.

::

    unistrant [global options...] command [command options...]

Most of the global options represent settings, see Settings_.

The command is an action that the program can perform. The command can have command-specific options.

Preparing the data directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The data directory should contain two subdirectories. The subdirectories should be named *archive* and *records* unless the program has been configured otherwise. The program requires access to read and write to both subdirectories. The subdirectories are expected to exist, and the program will not attempt to create them if they do not.

Supported record types
^^^^^^^^^^^^^^^^^^^^^^

Records are stored as elements of an XML document, using qualified names. For each record type, there is also a group element that can act as a container for several records. Either a record or group element is expected to be the document's root element.

Compute
  :Namespace: \http://schema.ogf.org/urf/2003/09/urf
  :Element: JobUsageRecord
  :Group element: UsageRecords

Storage
  :Namespace: \http://eu-emi.eu/namespaces/2011/02/storagerecord
  :Element: StorageUsageRecord
  :Group element: StorageUsageRecords

Cloud
  :Namespace: \http://sams.snic.se/namespaces/2016/04/cloudrecords
  :Element: CloudComputeRecord, CloudStorageRecord
  :Group element: CloudRecords

Software Accounting
  :Namespace: \http://sams.snic.se/namespaces/2019/01/softwareaccountingrecords
  :Element: SoftwareAccountingRecord
  :Group element: SoftwareAccountingRecords

Registering records
^^^^^^^^^^^^^^^^^^^

Use the *register* command to register records with SAMS. The program will look for new records to register in the records directory and send them to SAMS. Currently, the program has no support for generating records; it is expected that they will be produced by some other source and placed in the records directory.

When running the register command, the program will:

- read the record files
- group records into batches of the same type
- create a new XML document for each batch of records
- send all new XML documents to SAMS
- move the record files to the archive directory

The records directory can contain record files with records of diverse types, see `Supported record types`_. Each record file can contain either a single record or multiple records by using the corresponding group element as the document's root element.  A single record file cannot contain diverse types of records. Records will be sent in batches independent of the number of records stored in each record file.

Only some of the records may be successfully registered; in that case, the unsuccessfully registered records are saved to the records directory for later processing. Unsuccessfully registered records are saved in files named with the prefix *error*.

Example setup with a single data directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Assuming a setup where compute and software accounting records are stored in a single data directory `/data/usage` and registered once per hour.

Create a settings file at `/etc/sams/unistrant/unistrant.toml`:

::

  data_directory = "/data/usage"

  [sams]
  certificate = "/etc/sams/certificate.pem"
  key = "/etc/sams/key.pem"

Schedule a task to run once hourly:

::

  /opt/unistrant/bin/unistrant register

Example setup with multiple data directories
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Assuming a setup where compute and software accounting records are stored in separate data directories:

- `/data/compute` for compute records to be registered once per hour
- `/data/software accounting` for software accounting records to be registered once per day

Create a settings file with common settings at `/etc/sams/unistrant/unistrant.toml`:

::

  [sams]
  certificate = "/etc/sams/certificate.pem"
  key = "/etc/sams/key.pem"

Schedule a task to run once hourly for registering compute records:

::

  /opt/unistrant/bin/unistrant --data-directory=/data/compute register

Schedule another task to run once daily for registering software accounting records:

::

  /opt/unistrant/bin/unistrant --data-directory="/data/software accounting" register
