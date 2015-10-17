"""Obtain a damping parameter for a ring coupled to one or more loss channels

This module computes unadulterated codswallop wrapped in a bad pun.  
A fraction in the range (0, 1] is used to obtain a piece of pi, and 
also used to decide whether to tan or sine the piece. No good could 
come from the result.

Command-line examples
=====================

Obtain the usage statement::
  python CCqo102_ring_damping.py --help
Obtain programmer-level documentation::
  pydoc CCqo102_ring_damping

Muck with the (0.25) piece of pi::
  python CCqo102_ring_damping.py --CHGTHISVAR 0.25
Same calculation, but showing that unambiguous abbreviations are permissible::
  python CCqo102_ring_damping.py --CHG 0.25

Validate parameters (error for negative input)::
  python CCqo102_ring_damping.py --CHG -0.25 --validate
Change the log level (debug) and refrain from validation::
  python CCqo102_ring_damping.py --CHG -0.25 --no-validate -vv
Change the log file::
  python CCqo102_ring_damping.py --CHG -0.25 --log-file exp01.txt

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

__version__ = '1.2.4a124'

__copyright__ = "Copyright 2xxx, Exelis Geospatial Systems"
__author__ = "Tim Plate"
__credits__ = ["Earl E. Kohder", "N. G. Niirs"]
__license__ = "Exelis GS"
__maintainer__ = "Priya Serrvar"
__email__ = "priya.serrvar@exelisinc.com"
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
      * couplings >= 0
      * velocities >= 0
      * couplings and velocities are compatible sizes and shapes
    Warning checks:
      * None

    Parameters
    ----------
    kwargs : dictionary (need not be complete)
        Dictionary of parameters to check 

    Valid keys in kwargs
    -------------------- 
    couplings : float (scalar or list/tuple/array)
        Coupling strength in each channel
    velocities : float (scalar or list/tuple/array)
        Photon speed in each channel

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
    Setup for examples
    >>> import CCqo102_ring_damping as CCqo102

    Validating just couplings (VALID)
    >>> CCqo102.validateParameters(couplings = [1,2,3])

    Validating just couplings (INVALID: negative values)
    >>> CCqo102.validateParameters(couplings = [-1,2,-3])

    Validating all inputs (VALID)
    >>> CCqo102.validateParameters(velocities = [4,5,6], couplings = [1,2,3])

    Validating all inputs with different shapes (VALID)
    >>> CCqo102.validateParameters(velocities = 6, couplings = [1,2,3])

    Validating all inputs (INVALID: incompatible shapes)
    >>> CCqo102.validateParameters(velocities = [4,5,6,7], couplings = [1,2,3])
    """
    # Log the inputs
    msg = ''
    msg+= 'Inputs for validation:' + os.linesep
    for k, v in sorted(kwargs.items()) :
        msg+= "  {} = {}".format(k,v) + os.linesep
    lgr.debug(msg)


    # Obtain the keyword parameters, using the dict.get() method for valid
    # return of None if the key is not set
    _couplings  = kwargs.get('couplings')
    _velocities = kwargs.get('velocities')

    # Set flag variables and messages for errors (err, eMsg) and warnings (wrn, wMsg)
    err = False
    wrn = False
    eMsg = ''
    wMsg = ''

    # couplings
    # =========
    if _couplings:
        # Ensure couplings container is an iterable array
        if not isinstance(_couplings, list):
            _couplings = [_couplings]
        _couplings = np.asarray(_couplings)
        # range-check: _couplings >= 0
        if any(C < 0 for C in _couplings):
            badIdx = np.where(_couplings < 0)
            eMsg+= "All coupling values must be >=0" + os.linesep
            eMsg+= "Bad indices: {}".format(badIdx[0]) + os.linesep
            eMsg+= "Bad values:  {}".format(_couplings[badIdx]) + os.linesep
            err=True

    # velocities
    # =========
    if _velocities:
        # Ensure velocities container is an iterable array
        if not isinstance(_velocities, list):
            _velocities = [_velocities]
        _velocities = np.asarray(_velocities)
        # range-check: _velocities >= 0
        if any(v < 0 for v in _velocities):
            badIdx = np.where(_velocities < 0)
            eMsg+= "All _velocities values must be >=0" + os.linesep
            eMsg+= "Bad indices: {}".format(badIdx[0]) + os.linesep
            eMsg+= "Bad values:  {}".format(_velocities[badIdx]) + os.linesep
            err=True

    # couplings and velocities
    # ========================
    if (_couplings is not None) and (_velocities is not None):
        try:
            # Test if inputs can be broadcast together
            _couplings * _velocities
            print("c*v={}".format(_couplings*_velocities))
        except ValueError as e:
            eMsg+= str(e) + os.linesep
            eMsg+= "Same shape required:" + os.linesep
            eMsg+= "  _couplings shape  = {}".format(_couplings.shape) + os.linesep
            eMsg+= "  _velocities shape = {}".format(_velocities.shape) + os.linesep
            err=True

    # Log and raise as appropriate
    if err and wrn:
        lgr.warn(wMsg)
        lgr.error(eMsg)
        exMsg = wMsg + os.linesep + eMsg
        raise ValueError(exMsg)
    elif err:
        lgr.error(eMsg)
        raise ValueError(eMsg)
    elif wrn:
        lgr.warn(wMsg)
        raise RuntimeWarning(wMsg)



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
    >>> import CCqo102_ring_damping as emr
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

def calc_ring_damping(couplings, velocities):

    """Obtain a total ring damping parameter from coupling and velocity information.

    Photons in a ring resonator can be lost via external channels.  The
    coupling between ring and each channel is identified in the couplings
    input, and the photon velocities in each (corresponding) channel is
    identified in the velocities input. Each channel contributes to the
    total damping in an additive way.  This method computes the damping to
    each channel and sums them to a total damping parameter for the ring.

    Parameters
    ----------
    couplings : float (scalar or list/tuple/array)
        Coupling strength between ring and a given channel.  Each value in
        an array describes a different channel in an order that corresponds
        to the array of velocities.

    velocities : float (scalar or list/tuple/array)
        Speed of light in a given channel.  Each value in an array
        describes a different channel in an order that corresponds to the
        array of couplings.

    Returns
    -------
    damping, path_losses

    damping : float
        Total damping coefficient

    path_losses: float (scalar or array)
        Damping coefficients for each channel in the same order as the
        inputs.
        

    See Also
    --------
    numpy (as np)

    Exceptions
    ----------
    None

    Examples
    --------
    Setup for examples
      >>> import CCqo102_ring_damping as emrQO102

    Single-channel damping
      >>> total_damping, path_dampings = emrQO102.calc_ring_damping(8.0,2.0)
      >>> total_damping, path_dampings
      (16.0, 16.0)

    Multi-channel damping with different channel parameters
      >>> total_damping, path_dampings = emrQO102.calc_ring_damping([8.0, 12.0],[2.0, 4.0])
      >>> total_damping, path_dampings
      (34.0, array([ 16.,  18.]))

    Multi-channel damping with the same channel parameters (one input must be multiple)
      >>> total_damping, path_dampings = emrQO102.calc_ring_damping([8.0, 8.0], 2.0)
      >>> total_damping, path_dampings
      (32.0, array([ 16.,  16.])) 

    """

    import numpy as np

    # Ensure that the inputs can be treated as arrays
    couplings = np.asarray(couplings)
    velocities = np.asarray(velocities)

    # Compute each path loss 
    path_losses = np.absolute(couplings)**2 / (2.0 * velocities)
    # Compute total damping coefficient
    damping = np.sum(path_losses)

    return damping, path_losses











if '__main__' == __name__:

    import argparse
    import pprint
    pp = pprint.PrettyPrinter(indent=2)

    import CCqo102_ring_damping as emr

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
        default='CCqo102_ring_damping.log',
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

    vMsg = '%s version %s'%(__file__, __version__)
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
                msg = 'Dubious inputs for CCqo102_ring_damping.'
                lgr.warn(str(e))
                pass
            except ValueError as e:
                msg = 'Invalid value for CCqo102_ring_damping.'
                lgr.error(str(e))
                raise
            except Exception:
                msg = 'Error in CCqo102_ring_damping.'
                lgr.error(msg)
                raise

        [final, piece] = emr.calc_ring_damping(CHGTHISVAR=args.chgthisvar)
        msg = ''
        msg += ' CCqo102_ring_damping outputs' + os.linesep
        msg += '  finC [s m^-1] = %f'%(final) + os.linesep
        msg += '  intrmdB [J m] = %f'%(piece)
        if lgr.getEffectiveLevel() > logging.INFO: print(finC)
        else: lgr.info(msg)

    except Exception:
        ex_type, ex, tb = sys.exc_info()
        print ex_type
        print ex
        lgr.error('<TRACEBACK>')
        traceback.print_tb(tb)
        lgr.error('</TRACEBACK>')
