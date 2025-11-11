click-logging-config
====================

Quick and easy CLI logging options for `click <https://palletsprojects.com/p/click/>`_
commands using a Python decorator.

I found myself implementing logging preferences repeatedly for utilities. Logging
configuration is pretty simple, but for each new implementation I would
find myself spending time researching the same options to refresh my memory and
then implementing something slightly different than the last time. 🙄

``click-logging-config`` is my attempt to stop the circle of re-implementation
with settings that are useful enough, with configurability to change it if you
don't like the out-of-box behaviour. It's proving to be pretty useful and I'm
already using it across several of my other projects. 😄

It is released under the MIT license so you are free to use it in lots of
different ways. As simple as it looks, a tool like this still represents
research time and implementation effort, so please use the link below to help
support development.

`Support click-logging-config <https://byting-chipmunk.ck.page/products/click-logging-config>`_

`Byting Chipmunk <https://bytingchipmunk.com>`_ 🐿

*Take a byte off.*


.. contents::

.. section-numbering::


Installation
------------

The ``click-logging-config`` package is available from PyPI. Installing
into a virtual environment is recommended.

.. code-block::

    python3 -m venv .venv; .venv/bin/pip install click-logging-config


Getting Started
---------------

Using ``click-logging-config`` is intended to be very simple. A single
decorator applied to your click command or group adds some click options
specifically for managing logging context.

.. code-block::

    import click
    import logging
    from click_logging import logging_parameters

    log = logging.getLogger(__name__)

    def do_something()
        pass

    @click.command()
    @click.option("--my-option", type=str)
    # NOTE: Empty braces are required for hard-coded click-logging-config defaults.
    @logging_parameters()
    def my_command(my_option: str) -> None:
        log.info("doing something")
        try:
            do_something(my_option)
        except Exception as e:
            log.critical(f"something bad happened, {str(e)}")
            raise


Application of the ``@logging_parameters`` decorator must be applied immediately
*above* your click command function and *below* any other click decorators such
as arguments and options.

Having applied the decorator, your command now has the following options
available to it.

.. code-block::

    --log-console-enable / --log-console-disable
                           Enable or disable console logging.
                           [default: log-console-disable]
    --log-console-json-enable / --log-console-json-disable
                           Enable or disable console JSON logging.
                           [default: log-console-json-disable]
    --log-file-enable / --log-file-disable
                           Enable or disable file logging.
                           [default: log-file-enable]
    --log-file-json-enable / --log-file-json-disable
                           Enable or disable file JSON logging.
                           [default: log-file-json-enable]
    --log-file FILE        The log file to write to.  [default: this.log]
    --log-level [critical|error|warning|info|debug|notset]
                           Select logging level to apply to all enabled
                           log sinks.  [default: warning]

Note that the single log level configuration parameter applies to both console
and file logging.

The internal defaults are configured for an interactive utility (run by a
human in a terminal rather than via automation, or in a container). In summary,

* disabled console logging (allows your application to use console output, if needed)
* enabled file logging (1MB rotation size, with 10 rotation backups)
* "warning" log level


Custom defaults
---------------

If you don't like the ``click-logging-config`` internal defaults for the options
you can define your own. The ``LoggingConfiguration`` class is derived from
``pydantic.BaseModel``, so one easy way to define your defaults is using a
dictionary. You only need to define values you want to change - any other value
will continue using the internal defaults.

.. code-block::

    import pathlib

    import click
    import logging
    from click_logging import logging_parameters, LoggingConfiguration

    log = logging.getLogger(__name__)

    MY_LOGGING_DEFAULTS = LoggingConfiguration.parse_obj(
        {
            "file_logging": {
                # NOTE: file path must be specified using pathlib.Path
                "log_file_path": pathlib.Path("some_other.log"),
            },
            "log_level": "info",
        }
    )

    def do_something()
        pass

    @click.command()
    @click.option("--my-option", type=str)
    @logging_parameters(MY_LOGGING_DEFAULTS)
    def my_command(my_option: str) -> None:
        log.info("doing something")
        try:
            do_something(my_option)
        except Exception as e:
            log.critical(f"something bad happened, {str(e)}")
            raise


The table below summarizes the available settings for defaults. Otherwise
review the ``LoggingConfiguration`` `class definition <https://gitlab.com/ci-cd-devops/click_logging_config/-/blob/main/click_logging_config/_logging.py#L52>`_ .

.. csv-table:: Available top-level settings for logging defaults.
   :header: "Setting", "Type", "Hard default", "Description"

    "log_level", "str", "warning", "Define log level"
    "enable_console_logging", "boolean", "False", "Enable console logging"
    "console_logging", "dict", "", "Console logging specific settings. See table below."
    "enable_file_logging", "bool", "True", "Enable file logging"
    "file_logging", "dict", "", "File logging specific settings. See table below."

.. csv-table:: Available console logging defaults.
   :header: "Setting", "Type", "Hard default", "Description"

    "json_enabled", "bool", "False", "Output JSON logs using ``json_log_formatter``"

.. csv-table:: Available file logging defaults.
   :header: "Setting", "Type", "Hard default", "Description"

    "json_enabled", "bool", "True", "Output JSON logs using ``json_log_formatter``"
    "log_file_path", "pathlib.Path", "./this.log", "Path and name of log file."
    "file_rotation_size_megabytes", "int", "1", "Maximum size of "
    "max_rotation_backup_files", "int", "10", "Maximum number of rotation backup files"


Console logging
---------------

Console logging can be enabled or disabled, and there is an additional option
to output line-by-line text based timestamped log entries, or JSON logging via
the ``json_log_formatter`` framework. The format of text based log entries
cannot be configured at this time and console logging is always emitted to
stderr at this time.


File logging
------------

File rotation on the file log is implemented as a "sensible default" - it cannot
be disabled at this time, although you might be able to specify a maximum
rotation of ``1`` to achieve the same end (not tested). The maximum rotation
size can be specified as a configuration default. File logging itself can be
enabled or disabled via defaults or the CLI options described above.

Similar to console logging the format can be as either text-based or JSON
logging.
