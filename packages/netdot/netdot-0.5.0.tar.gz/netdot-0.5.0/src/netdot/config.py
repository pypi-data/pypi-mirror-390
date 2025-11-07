"""Default values to be used throughout this package.
"""
import datetime
import sys
from typing import Any, Dict

import configargparse

from netdot.version import __version__


def help():
    print(help_str())

STANDARD_HELP_STR = '-h, --help            show this help message and exit'
CONFIG_ARGPARSE_HELP_STR = '''In general, command-line values override environment variables which override
defaults.'''
def help_str():
    full_help = build_NETDOT_CLI_ENV_VARs_parser().format_help()
    # Trim off the leading boilerplate
    end_of_boilerplate = full_help.find(STANDARD_HELP_STR)
    full_help = full_help[end_of_boilerplate + len(STANDARD_HELP_STR):]
    # Trim off the trailing boilerplate
    full_help.replace(CONFIG_ARGPARSE_HELP_STR, '')
    return (f"""{full_help}

⚠ NOTICE: These defaults are read from Environment Variables when 
`netdot.config` module is imported (via `netdot.config.parse_env_vars`). 
Look for "[env var: NETDOT_CLI_...]" above to discover the available 
Environment Variables.

Example: `export NETDOT_CLI_TERSE=True`

Import Env Vars anytime by calling: `netdot.config.parse_env_vars()`

Alternately, override these defaults by setting 
`netdot.config.<ENV_VAR_NAME>` directly in your Python code.

Example: `netdot.config.TERSE=True`
"""
    )


def build_NETDOT_CLI_ENV_VARs_parser():
    parser = configargparse.ArgumentParser(formatter_class=configargparse.ArgumentDefaultsHelpFormatter
)
    parser.add_argument(
        '--terse',
        dest='TERSE',
        env_var='NETDOT_CLI_TERSE',
        type=bool,
        default=False,
        help='Print terse output (that generally tries to fit the screen width).',
    )
    parser.add_argument(
        '--server-url',
        dest='SERVER_URL',
        env_var='NETDOT_CLI_SERVER_URL',
        type=str,
        default="https://nsdb.uoregon.edu",
        help='The URL of the Netdot server.',
    )
    parser.add_argument(
        '--truncate-min',
        dest='TRUNCATE_MIN_CHARS',
        env_var='NETDOT_CLI_TRUNCATE_MIN_CHARS',
        type=int,
        default=20,
        help='The absolute minimum number of characters to print before truncating.',
    )
    parser.add_argument(
        '--terse-col-width',
        dest='TERSE_COL_WIDTH',
        env_var='NETDOT_CLI_TERSE_COL_WIDTH',
        type=int,
        default=16,
        help='The number of characters to use for each column when printing terse output.',
    )
    parser.add_argument(
        '--terse-max-chars',
        dest='TERSE_MAX_CHARS',
        env_var='NETDOT_CLI_TERSE_MAX_CHARS',
        type=int,
        default=None,
        help='The maximum number of characters to print before truncating.',
    )
    parser.add_argument(
        '--display-full-objects',
        dest='DISPLAY_FULL_OBJECTS',
        env_var='NETDOT_CLI_DISPLAY_FULL_OBJECTS',
        type=bool,
        default=False,
        help='Display the full objects instead of just the object IDs.',
    )
    parser.add_argument(
        '--skip-ssl',
        dest='SKIP_SSL',
        env_var='NETDOT_CLI_SKIP_SSL',
        type=bool,
        default=False,
        help='''Skip SSL verification when making API requests. 
        **Never recommended in production.**
        Note: you must reconnecting to Netdot for config to take effect. (Used as a default arg for an __init__ method)
''',
    )
    parser.add_argument(
        '--connect-timeout',
        dest='CONNECT_TIMEOUT',
        env_var='NETDOT_CLI_CONNECT_TIMEOUT',
        type=int,
        default=3,
        help='''The number of seconds to wait for connection to establish with the Netdot server.
        Note: you must reconnecting to Netdot for config to take effect. (Used as a default arg for an __init__ method)''',
    )
    parser.add_argument(
        '--timeout',
        dest='TIMEOUT',
        env_var='NETDOT_CLI_TIMEOUT',
        type=int,
        default=20,
        help='''The number of seconds to wait for a response from the API 
        server.
        Note: you must reconnecting to Netdot for config to take effect. (Used as a default arg for an __init__ method)
        Note: "timeout is not a time limit on the entire response download; 
        rather, an exception is raised if the server has not issued a response 
        for timeout seconds (more precisely, if no bytes have been received on 
        the underlying socket for timeout seconds). If no timeout is specified 
        explicitly, requests do not time out." (from requests.readthedocs.io)''',
    )
    parser.add_argument(
        '--raise-parse-errors',
        dest='RAISE_FIELD_PARSE_ERRORS',
        env_var='NETDOT_CLI_RAISE_FIELD_PARSE_ERRORS',
        type=bool,
        default=False,
        help="""Raise an exception if there is an error parsing any server response (from Netdot). 
        Else, log a warning and continue, using the 'raw string' data.
        
        (These are generally warnings that should be fixed by a netdot python package developer)""", # TODO add a link to "submit an issue" so people can report these errors back... Or maybe just do some telemetry to report these errors back to the netdot python package developer?
    )
    parser.add_argument(
        '--warn-missing-fields',
        dest='WARN_MISSING_FIELDS',
        env_var='NETDOT_CLI_WARN_MISSING_FIELDS',
        type=bool,
        default=True,
        help='Warn if a field is missing from the response from the API server.',
    )
    parser.add_argument(
        '--threads',
        dest='THREADS',
        env_var='NETDOT_CLI_THREADS',
        type=int,
        default=1,
        help='''The number of threads to use when making parallelizable API GET requests.
        Note: you must reconnecting to Netdot for config to take effect. (Used as a default arg for an __init__ method)
        ''',
    )
    parser.add_argument(
        '--trace-downloads',
        dest='TRACE_DOWNLOADS',
        env_var='NETDOT_CLI_TRACE_DOWNLOADS',
        type=bool,
        default=False,
        help='''Intermittently log an "INFO" message saying how many bytes have been downloaded from Netdot. Useful for long-running download tasks. (Note: This *is* thread-safe.)
        Note: you must reconnecting to Netdot for config to take effect. (Used as a default arg for an internal __init__ method)''',
    )
    parser.add_argument(
        '--trace-threshold',
        dest='TRACE_THRESHOLD',
        env_var='NETDOT_CLI_TRACE_THRESHOLD',
        type=int,
        default=1000000,
        help='''See TRACE_DOWNLOADS above. This threshold determines how often messages should be logged -- the number of bytes downloaded from Netdot before a log message is printed.
        Note: you must reconnecting to Netdot for config to take effect. (Used as a default arg for an internal __init__ method)''',
    )
    parser.add_argument(
        '--save-as-file-on-error',
        dest='SAVE_AS_FILE_ON_ERROR',
        env_var='NETDOT_CLI_SAVE_AS_FILE_ON_ERROR',
        type=bool,
        default=True,
        help='(Try to) Save the proposed changes to a file when an error occurs.',
    )
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f'netdot-cli-{__version__}-proposed_changes-{timestamp}.pickle'
    parser.add_argument(
        '--error-pickle-filename',
        dest='ERROR_PICKLE_FILENAME',
        env_var='NETDOT_CLI_ERROR_PICKLE_FILENAME',
        type=str,
        default=filename,
        help='The filename to use when saving proposed changes to a file when an error occurs. (timestamp based on when the script is run)',
    )
    return parser


def parse_env_vars() -> Dict[str, Any]:
    """Parse all the environment variables that are used by this package.

    > Note: This function is called automatically when this module is imported.

    Returns:
        Dict: A dictionary of all the environment variables and their values.
    """
    args = vars(build_NETDOT_CLI_ENV_VARs_parser().parse_args([]))
    return args


# Export all the parsed env vars as variables in this module
this_module = sys.modules[__name__]
__all__ = list()
for env_var, value in parse_env_vars().items():
    setattr(this_module, env_var, value)
    __all__.append(env_var)

__all__.extend([
    'help',
    'help_str',
    'parse_env_vars',
])
