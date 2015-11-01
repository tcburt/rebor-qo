"""Compute detuning in four-wave mixing

If a non-linear medium is impinged by two pump photons with angular
frequencies omega_0_1 and omega_0_2 a pair of photons may be generated, one
called the signal with frequency omega_1 and another called the idler with
frequency omega_2.  This method computes the detuning (omega_detuned)
between the input and output frequencies.

Command-line examples
=====================

Obtain the usage statement::
  python CCqo101_FWM_detuning.py --help
Obtain programmer-level documentation::
  pydoc CCqo101_FWM_detuning

Compute detuning parameter using only required parameters::
  python CCqo101_FWM_detuning.py --pump1 1.22e15 --signal 1.92e15
Compute detuning parameter using all calculation parameters::
  python CCqo101_FWM_detuning.py --pump1 1.22e15 --signal 1.92e15 --pump2 1.00e15 --idler 2.00e15
Same calculation, but showing that unambiguous abbreviations are permissible::
  python CCqo101_FWM_detuning.py --pump1 1.22e15 --sig 1.92e15 --pump2 1.00e15 --idl 2.00e15

Validate parameters (error for negative input)::
  python CCqo101_FWM_detuning.py ---pump1 1.22e15 --s 1.92e15 --validate
Change the log level (debug) and refrain from validation::
  python CCqo101_FWM_detuning.py --pump1 1.22e15 --s 1.92e15 --no-validate -vvv
Change the log file (DEBUG level to ensure content)::
  python CCqo101_FWM_detuning.py --pump1 1.22e15 --s 1.92e15 -vvv --log-file exp01.log

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
1.0b1 [15 Aug 2015 : Timothy C. Burt] 
    * Genesis which blemishes
1.0 [01 Oct 2015 : Timothy C. Burt]
    * Initial release
1.0.1 [01 Oct 2015 : Timothy C. Burt]
    * Fixed bug brought on by suppressing default argument creation

"""

__version__ = '1.0'

__copyright__ = "Timothy C. Burt"
__author__ = "TC Burt"
__credits__ = [""]
__license__ = "MIT License"
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
    'pump1':{
        'desc':'angular frequency of pump 1 photon',
        'valrange':'(-inf, inf)',
        'default': '0.0',
        'datatype':'float',
        'units':'rad s^{-1}',
        'flow':'input'
        },
    'pump2':{
        'desc':'angular frequency of pump 2 photon',
        'valrange':'(-inf, inf)',
        'default': '0.0',
        'datatype':'float',
        'units':'rad s^{-1}',
        'flow':'input'
        },
    'signal':{
        'desc':'angular frequency of signal',
        'valrange':'(-inf, inf)',
        'default': '0.0',
        'datatype':'float',
        'units':'rad s^{-1}',
        'flow':'input'
        },
    'idler':{
        'desc':'angular frequency of idler',
        'valrange':'(-inf, inf)',
        'default': '0.0',
        'datatype':'float',
        'units':'rad s^{-1}',
        'flow':'input'
        },
    'angFreqDetuning':{
        'desc':'angular frequency of detuning',
        'valrange':'(-inf, inf)',
        'default': '0.0',
        'datatype':'float',
        'units':'rad s^{-1}',
        'flow':'output'
        }
}

def validateParameters(**kwargs):
    """Validate input parameters, raising an exception for invalid and dubious values.

    Error checks:
      * pump1, pump2, signal, idler >= 0
    Warning checks:
      * None

    Parameters
    ----------
    (See description of parameters and keywords in calcqo101_FWM_detuning)

    Returns
    -------
    None

    Raises
    ------
    RuntimeWarning, ValueError

    See Also
    --------
    import collections (OrderedDict)
    logging (lgr object is a precondition)

    Examples
    --------
    Setup for examples
    >>> import CCqo101_FWM_detuning as CCqo101
    >>> CCqo101.validateParameters(pump1=-1)
    """

    from collections import OrderedDict

    pump1 = kwargs.get("pump1")
    pump2 = kwargs.get("pump2")
    signal = kwargs.get("signal")
    idler = kwargs.get("idler")

    # Log the inputs
    msg = ''
    msg += 'Inputs for validation:' + os.linesep
    print(kwargs)
    for k,v in kwargs.items():
        msg+= "  k = {}".format(v) + os.linesep
    lgr.debug(msg)

    # Set flag variables and messages for errors (err, eMsg) and warnings (wrn, wMsg)
    err = False
    wrn = False
    eMsg = ''
    wMsg = ''

    # range-check: pump1 >= 0
    # Preserve order of the checking for consistent behavior of message
    checkGEzero = OrderedDict([("pump1", pump1), ("pump2", pump2), ("signal", signal), ("idler", idler)])
    for k,v in checkGEzero.items():
        if v and (v < 0):
            eMsg+= "Range check error:" + os.linesep
            eMsg+= "  Expected {} >= 0".format(k) + os.linesep
            eMsg+= "  Received {} = {}".format(k,v) + os.linesep
            err=True

    if err and wrn:   
        lgr.warn(wMsg)   
        lgr.error(eMsg)
        raise ValueError(eMsg+wMsg)
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
    >>> import CCqo101_FWM_detuning as emr
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

def calcqo101_FWM_detuning(pump1, signal, pump2 = None, idler = None):

    """Calculate the four-wave mixing detuning between output and input frequencies.

    Detuning is the difference of the output and input sum frequencies
      detuning = (signal + idler) - (pump1 + pump2)

    Parameters
    ----------
    pump1 : float
        Input pump 1 angular frequency 
    signal : float
        Output 1 signal angular frequency
    
    Keywords
    --------
    pump2 : float
        Input pump 2 angular frequency (set to pump1 value if not specified)
    idler : float
        Output 2 idler angular frequency (set to signal value if not specified)
    

    Returns
    -------
    detuning : float
        Difference output (minuend) and input (subtrahend) frequencies

    See Also
    --------
    None

    Exceptions
    ----------
    None

    Examples
    --------
    # Setup for examples
    >>> import CCqo101_FWM_detuning as emr

    # Positional call
    >>> emr.calcqo101_FWM_detuning(100, 110)

    # Keyword call (same as above)
    >>> emr.calcqo101_FWM_detuning(signal=110, pump1=100)

    # Mixed-style call (explicit values for optional arguments)
    >>> emr.calcqo101_FWM_detuning(100, 110, pump2=230, idler=250)
    """

    # Set optional arguments if necessary
    if pump2 is None: pump2 = pump1
    if idler is None: idler = signal

    # Calculate
    detuning = (signal + idler) - (pump1 + pump2)

    return detuning

if '__main__' == __name__:

    import argparse
    import pprint
    pp = pprint.PrettyPrinter(indent=2, width=50)

    import CCqo101_FWM_detuning as emr

    # Create the option object
    #  - Help option (-h, --help) included by default 
    #  - Usage statement (help) will be included so as to preseve order
    argp = argparse.ArgumentParser(
        description='Compute detuning frequency in four-wave mixing',
        epilog='Unambiguous option abbreviations are permitted.',
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        argument_default=argparse.SUPPRESS
    )
    # Instantiate required, optional, and informational arguments group
    reqArgs = argp.add_argument_group("Required arguments")
    optArgs = argp.add_argument_group("Optional arguments")
    infArgs = argp.add_argument_group("Informational arguments")
    
    # Add options
    # ===========

    reqArgs.add_argument(
        '--pump1', 
        type=float, required=True,
        dest='pump1', action='store',
        help="Pump 1 angular frequency [rad s^{-1}]",
        metavar='omega_0_1'
        )
    reqArgs.add_argument(
        '--signal', 
        type=float, required=True,
        dest='signal', action='store',
        help="Output 1 signal angular frequency [rad s^{-1}]",
        metavar='omega_1'
        )
    optArgs.add_argument(
        '--pump2', 
        type=float, required=False,
        dest='pump2', action='store',
        help="Pump 2 angular frequency [rad s^{-1}] (default=pump1)",
        metavar='omega_0_2'
        )
    optArgs.add_argument(
        '--idler', 
        type=float, required=False,
        dest='idler', action='store',
        help="Output 2 idler angular frequency [rad s^{-1}] (default=signal)",
        metavar='omega_2'
        )

    optArgs.add_argument(
        '--validate', 
        dest='validate', action='store_true',
        default=False,
        help="Validate parameters"
        )
    optArgs.add_argument(
        '--no-validate',
        default=True,
        dest='validate', action='store_false',
        help="Do not validate parameters"
        )

    optArgs.add_argument(
        '--log-file', 
        default='CCqo101_FWM_detuning.log',
        dest='log_file', action='store',
        help="File for log messages",
        metavar = 'fname')
    optArgs.add_argument(
        '--log-entry-format', 
        default='%(asctime)s %(levelname)s [%(filename)s:%(funcName)s] %(message)s',
        dest='log_entry_format', action='store',
        help="Formate for log messages",
        metavar = 'F')
    infArgs.add_argument(
        '-v', '--verbose', 
        dest='verbose', action='count',
        default = 0,
        help="Increase verbosity (-v=WARNING, -vv=INFO, -vvv=DEBUG, -vvv(v+)=DEBUG)")

    vMsg = '%s version %s'%(__file__, __version__)
    infArgs.add_argument(
        '--Version', 
        action='version', version=vMsg,
        help="Print version and exit"
        )
    # help
    infArgs.add_argument(
        '-h', '--help', 
        action='help', 
        help="Show usage and exit"
        )

    # Parse options and instantiate object
    # ====================================
    args = argp.parse_args()

    # Set defaults for the optional frequencies
    if not hasattr(args, "pump2"): 
        args.pump2 = args.pump1
    if not hasattr(args, "idler"): 
        args.idler = args.signal

    # Initialize logging
    logLevel = logging.CRITICAL
    levelTranslation = {0:logging.CRITICAL, 1:logging.WARNING, 2:logging.INFO, 3:logging.DEBUG}

    if args.verbose: 
        verbosity = min(logging.DEBUG, args.verbose)
        logLevel = levelTranslation[verbosity]

    appl_setupLog(logLevel, args.log_entry_format, args.log_file)
    lgr.debug('Inputs and Defaults:' +os.linesep + pp.pformat(args.__dict__))

    # Obtain inputs
    pump1  = args.pump1
    pump2  = args.pump2
    signal = args.signal
    idler  = args.idler

    # Act
    try:

        if args.validate:
            try:
                emr.validateParameters(
                    pump1  = pump1,
                    pump2  = pump2,
                    signal = signal,
                    idler  = idler)
            except RuntimeWarning as e:
                msg = 'Dubious inputs for CCqo101_FWM_detuning.'
                lgr.warn(str(e))
                pass
            except ValueError as e:
                msg = 'Invalid value for CCqo101_FWM_detuning.'
                lgr.error(str(e))
                raise
            except Exception:
                msg = 'Error in CCqo101_FWM_detuning.'
                lgr.error(msg)
                raise

        # Calculate
        detuning = emr.calcqo101_FWM_detuning(
            pump1  = pump1,
            pump2  = pump2,
            signal = signal,
            idler  = idler
        )
        msg = ''
        msg += ' CCqo101_FWM_detuning outputs' + os.linesep
        msg += '  sum frequency outputs [rad s^(-1)] = {}'.format(signal+idler) + os.linesep
        msg += '  sum frequency inputs  [rad s^(-1)] = {}'.format(pump1+pump2) + os.linesep
        msg += '  omega_detuned [rad s^(-1)] = {}'.format(detuning) + os.linesep
        if lgr.getEffectiveLevel() > logging.INFO: print(detuning)
        else: lgr.info(msg)

    except Exception:
        ex_type, ex, tb = sys.exc_info()
        print ex_type
        print ex
        lgr.error('<TRACEBACK>')
        traceback.print_tb(tb)
        lgr.error('</TRACEBACK>')
