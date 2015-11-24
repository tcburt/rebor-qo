"""Obtain a damping parameter for a ring coupled to one or more loss channels

A ring resonator can be coupled to one or more channels, each with its own
velocity.  From the perspective of the ring resonator each channel
constitutes a loss to that path and the total effective damping (loss) is
the sum of all path losses.  

Command-line examples
=====================
Getting help
------------
Obtain the usage statement::
  python CCqo102_ring_damping.py --help

Obtain programmer-level documentation::
  pydoc CCqo102_ring_damping

Execute module tests that are embedded in docstrings
  python -m doctest CCqo102_ring_damping.py 

Calculations
------------
Single-channel damping::
  python CCqo102_ring_damping.py --couplings 12.0 --velocities 3.0

Same as above but with abbreviated option names::
  python CCqo102_ring_damping.py --coup 12.0 --vel 3.0

Multi-channel damping, all with the same velocity::
  python CCqo102_ring_damping.py --coup 12.0 20.0 --vel 2.0

Multi-channel damping, each with its own velocity::
  python CCqo102_ring_damping.py --coup 12.0 20.0 --vel 3.0 4.0


Calculations with options
-------------------------
Display debugging information::
  python CCqo102_ring_damping.py --coup 12.0 20.0 --vel 3.0 4.0 -vvv
Validate calculation inputs (INVALID negative values of coupling and velocity)::
  python CCqo102_ring_damping.py --coup -12.0 20.0 --vel 3.0 -4.0 --validate
Validate calculation inputs (INVALID mismatch between coupling and velocity shapes)::
  python CCqo102_ring_damping.py --coup 12.0 20.0 --vel 3.0 4.0 5.0 --validate


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
1.0b1 [02 Nov 2015 : Timothy C. Burt] 
    * Genesis with blemishes

"""

__version__ = '1.0b1'

__copyright__ = "Copyright 2015, Timothy C. Burt"
__author__ = "Timothy C. Burt"
__credits__ = []
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
    'couplings':{
        'desc':'Coupling constant for each channel',
        'valrange':'[0, inf)',
        'default': '0.0',
        'datatype':'float (scalar or array)',
        'units':'(rad s^{-1})^{1/2}',
        'flow':'input'
        },
    'velocities':{
        'desc':'Speed of light for each channel',
        'valrange':'[0, inf)',
        'default': '0.0',
        'datatype':'float (scalar or array)',
        'units':'rad s^{-1}',
        'flow':'input'
        },
    'path_losses':{
        'desc':'Damping value for each channel',
        'valrange':'[0, inf)',
        'default': '0.0',
        'datatype':'float (scalar or array)',
        'units':'1',
        'flow':'intermediate output'
        },
    'damping':{
        'desc':'Total damping coefficient',
        'valrange':'[0, inf)',
        'default': '0.0',
        'datatype':'float',
        'units':'1',
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
    Setup for examples (Use level=1 for DEBUG)
    >>> appl_setupLog(level=5)

    Validating just couplings (VALID)
    >>> validateParameters(couplings = [1,2,3])

    Validating all inputs (VALID)
    >>> validateParameters(velocities = [4,5,6], couplings = [1,2,3])

    Validating all inputs with different but compatible shapes (VALID)
    >>> validateParameters(velocities = 6, couplings = [1,2,3])

    Validating couplings and velocities (INVALID: negative values)
    >>> validateParameters(couplings = [-1,2,-3], velocities = [-9,-8,7])
    Traceback (most recent call last):
        ...
    ValueError: All coupling values must be >=0
    Bad couplings indices: [0 2]
    Bad couplings values:  [-1 -3]
    All velocity values must be >=0
    Bad velocities indices: [0 1]
    Bad velocities values:  [-9 -8]

    Validating all inputs (INVALID: incompatible shapes)
    >>> validateParameters(velocities = [4,5,6,7], couplings = [1,2,3])
    Traceback (most recent call last):
        ...
    ValueError: operands could not be broadcast together with shapes (3,) (4,) 
    Same shape required:
      couplings shape  = (3,)
      velocities shape = (4,)

    """
    lgr = logging.getLogger('__main__')

    # Log the inputs
    msg = ""
    msg+= "Inputs for validation:" + os.linesep
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
            eMsg+= "Bad couplings indices: {}".format(badIdx[0]) + os.linesep
            eMsg+= "Bad couplings values:  {}".format(_couplings[badIdx])
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
            if err: eMsg+= os.linesep
            badIdx = np.where(_velocities < 0)
            eMsg+= "All velocity values must be >=0" + os.linesep
            eMsg+= "Bad velocities indices: {}".format(badIdx[0]) + os.linesep
            eMsg+= "Bad velocities values:  {}".format(_velocities[badIdx])
            err=True

    # couplings and velocities
    # ========================
    if (_couplings is not None) and (_velocities is not None):
        try:
            # Test if inputs can be broadcast together
            _couplings * _velocities
        except ValueError as e:
            if err: eMsg+= os.linesep
            eMsg+= str(e) + os.linesep
            eMsg+= "Same shape required:" + os.linesep
            eMsg+= "  couplings shape  = {}".format(_couplings.shape) + os.linesep
            eMsg+= "  velocities shape = {}".format(_velocities.shape)
            err=True

    # Log and raise as appropriate
    if err and wrn:
        lgr.warn(wMsg)
        lgr.error(eMsg)
        raise ValueError(wMsg + os.linesep + eMsg)
    elif err:
        lgr.error(eMsg)
        raise ValueError(eMsg)
    elif wrn:
        lgr.warn(wMsg)
        raise RuntimeWarning(wMsg)




def appl_setupLog(level=logging.WARNING, 
                  msgFmt='%(asctime)s %(levelname)s [%(module)s:%(funcName)s] %(message)s', 
                  logFile=None,
                  chgLevelOnly=False):
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
    chgLevelOnly : boolean
        Indicate if this is to change the logging level only. False means
        that *all* inputs are acted on, especially adding
        handlers. (Default=False)

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
    # Setup for examples
    >>> import logging # doctest: +SKIP

    # Warning messages and above go to STDOUT with datetime+level prefix.
        appl_setupLog()

    # Info messages and above go to STDOUT with datetime+name+level prefix.
        appl_setupLog(level=logging.INFO)

    # Debug messages and above go to STDOUT and the file thisLog.txt with
    # a log level prefix to the message (no datetime in the prefix)
        appl_setupLog(level=logging.DEBUG, msgFmt='%(levelname)s %(message)s', logFile='thisLog.txt')

    """

    if chgLevelOnly:
        lgr.setLevel(level)
        return

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
    >>> # Single-channel damping
    >>> calc_ring_damping(12.0,3.0)
    (24.0, 24.0)

    >>> # Multi-channel damping with different channel parameters
    >>> calc_ring_damping([12.0, 20.0],[3.0, 4.0])
    (74.0, array([ 24.,  50.]))

    >>> # Multi-channel damping with the same channel parameters (one input must be multiple)
    >>> calc_ring_damping([12.0, 20.0], 2.0)
    (136.0, array([  36.,  100.]))

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








# Command-line main
if '__main__' == __name__:

    import argparse
    import pprint
    pp = pprint.PrettyPrinter(indent=2)

    import CCqo102_ring_damping as emr

    # Create the option object
    #  - Help option (-h, --help) included by default 
    #  - Usage statement included by default
    argp = argparse.ArgumentParser(
        description='Compute ring damping from one or more coupling points',
        epilog='Unambiguous option abbreviations are permitted.',
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        argument_default=argparse.SUPPRESS)
    # Instantiate required, optional, and informational arguments group
    reqArgs = argp.add_argument_group("Required arguments")
    optArgs = argp.add_argument_group("Optional arguments")
    infArgs = argp.add_argument_group("Informational arguments")

    # Add options
    # ===========

    reqArgs.add_argument(
        '--couplings', 
        type=float, required=True,
        nargs='+',
        dest='couplings', action='store',
        help="couplings [(rad s^{-1})^{-1/2}]",
        metavar='C'
        )

    reqArgs.add_argument(
        '--velocities', 
        type=float, required=True,
        nargs='+',
        dest='velocities', action='store',
        help="velocities [rad s^{-1}]",
        metavar='V'
        )

    optArgs.add_argument(
        '--validate', 
        dest='validate', action='store_true',
        help="Validate parameters"
        )
    optArgs.add_argument(
        '--no-validate',
        default=False,
        dest='validate', action='store_false',
        help="Do not validate parameters"
        )

    optArgs.add_argument(
        '--log-file', 
        default='CCqo102_ring_damping.log',
        dest='log_file', action='store',
        help="File for log messages",
        metavar = 'logFilename')

    optArgs.add_argument(
        '--log-entry-format', 
        default='%(asctime)s %(levelname)s [%(filename)s:%(funcName)s] %(message)s',
        dest='log_entry_format', action='store',
        help="Formate for log messages",
        metavar = 'msgFmt')

    infArgs.add_argument(
        '-v', '--verbose', 
        default=0, 
        dest='verbose', action='count',
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

    # Initialize logging
    logLevel = logging.CRITICAL
    levelTranslation = {0:logging.CRITICAL, 1:logging.WARNING, 2:logging.INFO, 3:logging.DEBUG}

    if args.verbose: 
        verbosity = min(logging.DEBUG, args.verbose)
        logLevel = levelTranslation[verbosity]

    appl_setupLog(logLevel, args.log_entry_format, args.log_file)
    lgr.debug('Inputs and Defaults: ' + os.linesep + pp.pformat(args.__dict__)) 

    # Act
    try:

        if args.validate:
            try:
                emr.validateParameters(couplings=args.couplings, velocities=args.velocities)
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

        damping, path_losses = emr.calc_ring_damping(couplings=args.couplings, velocities=args.velocities)
        msg = ''
        msg += ' CCqo102_ring_damping outputs' + os.linesep
        msg += '  damping [1] = {}'.format(damping) + os.linesep
        msg += '  path_losses [1] = {}'.format(path_losses)
        if lgr.getEffectiveLevel() > logging.INFO: print(damping)
        else: lgr.info(msg)

    except Exception:
        ex_type, ex, tb = sys.exc_info()
        print ex_type
        print ex
        lgr.error('<TRACEBACK>')
        traceback.print_tb(tb)
        lgr.error('</TRACEBACK>')
