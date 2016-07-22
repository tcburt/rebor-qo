"""Provide a working template for discrete calculation engines.

This module computes unadulterated codswallop wrapped in a bad pun.  
A fraction in the range (0, 1] is used to obtain a piece of pi, and 
also used to decide whether to tan or sine the piece. No good could 
come from the result.

Command-line examples
=====================

Obtain the usage statement::
  python CCID_template.py --help
Obtain programmer-level documentation::
  pydoc CCID_template

Muck with the (0.25) piece of pi::
  python CCID_template.py --CHGTHISVAR 0.25
Same calculation, but showing that unambiguous abbreviations are permissible::
  python CCID_template.py --CHG 0.25

Validate parameters (error for negative input)::
  python CCID_template.py --CHG -0.25 --validate
Change the log level (debug) and refrain from validation::
  python CCID_template.py --CHG -0.25 --no-validate -vv
Change the log file::
  python CCID_template.py --CHG -0.25 --log-file exp01.txt

Data
====
lgr : object (logging)
    A logging object for the entire module that is configured in the 
    method appl_setupLog(). 

paramDefns : dict
    Collection of calculation variables with descriptions, expected 
    ranges, defaults, units, data types, and placements in the flow.

DEPENDENCIES
============
Module: os, sys, logging
Command-line extras: argparse, traceback, pprint

DEVELOPMENT METADATA
====================
Discrete data elements are captured in the module-level data 
immediately following this docstring.  Most are self-explanatory
and identify information such as copyright, author, etc.

HISTORY
=======
pre-1.2.4a124 
    * [19 Jan 2015 : Timothy C. Burt]
        * All version information before v1.2.4a124 has been lost since
          the previous developer did not maintain a changelog in the file,
          but kept exclusively in ClearCase commit logs which are now
          completely unrecoverable.
1.2.4a124
    * [03 Mar 2015 : Timothy C. Burt] 
        * Calculation method and stubs for next version

"""

__version__ = '0.8b1'

__copyright__ = "Copyright Timothy C. Burt, 2016"
__author__ = "Timothy C. Burt"
__credits__ = ["Timothy C. Burt"]
__license__ = "MIT"
__maintainer__ = "Timothy C. Burt"
__email__ = "rketburt@gmail.com"
__status__ = "Development"

import sys
import os
import traceback
import logging
import numpy as np

lgr = logging.getLogger('__main__')

paramDefns = {
    'CHGTHISVAR':{
        'desc':'A parameter',
        'valrange':'(0, 1]',
        'default': '0.0',
        'datatype':'float',
        'units':'m',
        'flow':'input'
        },
    'intrmdB':{
        'desc':'A neat, but intermediate, result',
        'valrange':'(-\infty, \infty)',
        'default': '0.0',
        'datatype':'float',
        'units':'J m',
        'flow':'intermediate output'
        },
    'finC':{
        'desc':'Culmination value of the calculation',
        'valrange':'(-\infty, \infty)',
        'default': '0.0',
        'datatype':'float',
        'units':'s m^-1',
        'flow':'output'
        }
}

def validateParameters(**kwargs):
    """Validate input parameters, raising an exception for invalid and dubious values.

    Error checks:
      * CHGTHISVAR > 0 and CHGTHISVAR <=1
    Warning checks:
      * None

    Parameters
    ----------
    kwargs : dict
        Dictionary of parameters.  

    Returns
    -------
    None

    Raises
    ------
    RuntimeWarning, ValueError

    See Also
    --------
    logging (lgr object is a precondition)

    Examples
    --------
    >>> import CCID_template as emr
    >>> emr.validateParameters(CHGTHISVAR = -6.2)
    """

    CHGTHISVAR = kwargs.get('CHGTHISVAR')

    # Log the inputs
    msg = ''
    msg += 'Inputs for validation:' + os.linesep
    msg += '{}'.format(kwargs)
    lgr.debug(msg)

    # Set flag variables and messages for errors (err, eMsg) and warnings (wrn, wMsg)
    err = False
    wrn = False
    eMsg = ''
    wMsg = ''

    # range-check: 0 < CHGTHISVAR <=1
    if CHGTHISVAR is not None: 
        if (CHGTHISVAR <= 0) or (CHGTHISVAR > 1): 
            eMsg+='Received: {}'.format(CHGTHISVAR) + os.linesep
            eMsg+='Expected: 0 < [CHGTHISVAR] <=1' + os.linesep
            err=True

    if wrn: 
        lgr.warn(wMsg)
        raise RuntimeWarning(wMsg)
    if err:      
        lgr.error(eMsg)
        raise ValueError(eMsg)

def appl_setupLog(level=logging.WARNING, 
                  msgFmt='%(asctime)s %(levelname)s [%(module)s:%(funcName)s] %(message)s', 
                  logFile=None):
    """Set up logging level, format, and output file.

    Log to STDOUT at the given 'level' in a certain 'msgFmt', and optionally write to 'logFile'. 

    Parameters
    ----------
    level : integer
        Numeric value corresponds to logging levels described in the
        logging package. (Default=30 <- logging.WARNING)
    msgFmt : string
        Format of each log entry. The default yields lines of the form 
        <dateTime><logLevel><module:method><logMessage>. 
        (Default='%(asctime)s %(levelname)s [%(module)s:%(funcName)s] %(message)s')
    logFile : string
        Filename in a writable location.  Value of None means log entries
        will not be written to a file. (Default=None)

    Returns
    -------
    None

    See Also
    --------
    logging

    Exceptions
    ----------
    None

    Examples
    --------
    >>> # Setup for examples
    >>> import CCID_template as emr
    >>> import logging

    >>> # Warning messages and above go to STDOUT with datetime+level prefix.
    >>> emr.appl_setupLog()

    >>> # Info messages and above go to STDOUT with datetime+name+level prefix.
    >>> emr.appl_setupLog(level=logging.INFO)

    >>> # Debug messages and above go to STDOUT and the file thisLog.txt with
    >>> # a log level prefix to the message (no datetime in the prefix)
    >>> emr.appl_setupLog(level=logging.DEBUG, msgFmt='%(levelname)s %(message)s', logFile='thisLog.txt')
    """

    formatter = logging.Formatter(msgFmt)

    # Console output
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)

    # File output
    if logFile is not None:
        fh = logging.FileHandler(logFile, mode='w')
        fh.setFormatter(formatter)

    # Set the (global) logger's level and handlers
    lgr.setLevel(level)
    lgr.addHandler(ch)
    if logFile is not None: lgr.addHandler(fh)

def calcID_template(**kwargs):

    """Tan, sine, or keep a piece of pi.

    A piece of pi is calculated from the product of the circle constant and
    the fractional input, CHGTHISVAR=<frac>.  If the fractional value is
    greater than 1/2 the tangent of the piece is calculated and if less
    than 1/2 the sine is calculated, otherwise the piece of pi remains
    unchanged.    

    Parameters
    ----------
    CHGTHISVAR : float
        Fraction of the pi 

    Returns
    -------
    [finC, intrmdB]

    finC : float
        Final result of operating on the piece of pi
    intrmdB: float
        Size of the piece of pi

    See Also
    --------
    numpy (as np)

    Exceptions
    ----------
    None

    Examples
    --------
    >>> # Setup for examples
    >>> import CCID_template as emr

    >>> # Sine the piece
    >>> [final, piece] = emr.calcID_template(CHGTHISVAR=0.2)
    >>> final, piece
    (0.58778525229247314, 0.6283185307179586)
    """

    chgVar = kwargs['CHGTHISVAR']

    intrmdB = chgVar * np.pi
    if chgVar > 0.5: finC = np.tan(intrmdB)
    elif chgVar < 0.5: finC = np.sin(intrmdB)
    else: finC = np.log(intrmdB)

    return [finC, intrmdB]

if '__main__' == __name__:

    import argparse
    import pprint
    pp = pprint.PrettyPrinter(indent=2)

    import CCID_template as emr

    # Create the option object
    #  - Help option (-h, --help) included by default 
    #  - Usage statement included by default
    argp = argparse.ArgumentParser(
        description='Reshape a piece of pi',
        epilog='Unambiguous option abbreviations are permitted.')
    # Add options
    # ===========

    argp.add_argument(
        '--CHGTHISVAR', 
        type=float, required=True,
        dest='chgthisvar', action='store',
        help="chgVar [m]",
        metavar='cV'
        )

    argp.add_argument(
        '--validate', 
        dest='validate', action='store_true',
        help="Validate parameters"
        )
    argp.add_argument(
        '--no-validate',
        default=False,
        dest='validate', action='store_false',
        help="Do not validate parameters"
        )

    argp.add_argument(
        '--log-file', 
        default='CCID_template.log',
        dest='log_file', action='store',
        help="File for log messages",
        metavar = 'logFilename')
    argp.add_argument(
        '--log-entry-format', 
        default='%(asctime)s %(levelname)s [%(filename)s:%(funcName)s] %(message)s',
        dest='log_entry_format', action='store',
        help="Formate for log messages",
        metavar = 'msgFmt')
    argp.add_argument(
        '-v', '--verbose', 
        dest='verbose', action='count',
        help="Increase verbosity (-v=WARNING, -vv=INFO, -vvv=DEBUG, -vvv(v+)=DEBUG)")

    vMsg = '{} version {}'.format(__file__, __version__)
    argp.add_argument(
        '--Version', 
        action='version', version=vMsg,
        help="Print version and exit"
        )

    # Parse options and instantiate object
    # ====================================
    args = argp.parse_args()

    # Initialize logging
    logLevel = logging.CRITICAL
    levelTranslation = {0:logging.CRITICAL, 1:logging.WARNING, 2:logging.INFO, 3:logging.DEBUG}

    if args.verbose: 
        verbosity = min(logging.DEBUG, args.verbose)
        logLevel = levelTranslation[verbosity]

    appl_setupLog(logLevel, args.log_entry_format, args.log_file)
    lgr.debug('Inputs and Defaults: ' + pp.pformat(args))

    # Act
    try:

        if args.validate:
            try:
                emr.validateParameters(CHGTHISVAR=args.chgthisvar)
            except RuntimeWarning as e:
                msg = 'Dubious inputs for CCID_template.'
                lgr.warn(str(e))
                pass
            except ValueError as e:
                msg = 'Invalid value for CCID_template.'
                lgr.error(str(e))
                raise
            except Exception:
                msg = 'Error in CCID_template.'
                lgr.error(msg)
                raise

        [final, piece] = emr.calcID_template(CHGTHISVAR=args.chgthisvar)
        msg = ''
        msg += ' CCID_template outputs' + os.linesep
        msg += '  finC [s m^-1] = {}'.format(final) + os.linesep
        msg += '  intrmdB [J m] = {}'.format(piece)
        if lgr.getEffectiveLevel() > logging.INFO: print(final)
        else: lgr.info(msg)

    except Exception:
        ex_type, ex, tb = sys.exc_info()
        print ex_type
        print ex
        lgr.error('<TRACEBACK>')
        traceback.print_tb(tb)
        lgr.error('</TRACEBACK>')
