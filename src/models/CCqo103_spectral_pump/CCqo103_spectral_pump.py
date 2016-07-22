"""Provide a working template for discrete calculation engines.

This module computes unadulterated codswallop wrapped in a bad pun.  
A fraction in the range (0, 1] is used to obtain a piece of pi, and 
also used to decide whether to tan or sine the piece. No good could 
come from the result.

Command-line examples
=====================

Obtain the usage statement::
  python CCqo103_spectral_pump.py --help
Obtain programmer-level documentation::
  pydoc CCqo103_spectral_pump

Muck with the (0.25) piece of pi::
  python CCqo103_spectral_pump.py --CHGTHISVAR 0.25
Same calculation, but showing that unambiguous abbreviations are permissible::
  python CCqo103_spectral_pump.py --CHG 0.25

Validate parameters (error for negative input)::
  python CCqo103_spectral_pump.py --CHG -0.25 --validate
Change the log level (debug) and refrain from validation::
  python CCqo103_spectral_pump.py --CHG -0.25 --no-validate -vv
Change the log file::
  python CCqo103_spectral_pump.py --CHG -0.25 --log-file exp01.txt

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

TODO
====
  - Stop logging to STDOUT during doctest
  - Add doctests to validateParameters
  - Add documentation to utility methods

HISTORY
=======
0.8b1 [2016-07-18 : Timothy C. Burt] 
    * Initial beginnings
1.0b1 [2016-07-22 : Timothy C. Burt] 
    * Working version with liens on documentation and doctest

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
#lgr = logging.getLogger('__main__').addHandler(logging.NullHandler())

paramDefns = {
    'wavevec':{
        'desc':'spectrum independent variable',
        'valrange':'(-inf, inf)',
        'default': '0.0',
        'datatype':'float (N-element array)',
        'units':'rad s^(-1)',
        'flow':'input'
        },
    'couplings_pump':{
        'desc':'spectral coupling constants for the pump',
        'valrange':'[0, inf)',
        'default': '0.0',
        'datatype':'complex (N-element array)',
        'units':'rad^(1/2) m^(1/2) s^(-1)',
        'flow':'input'
        },
    'velocities_pump':{
        'desc':'spectral velocities for the pump',
        'valrange':'[0, inf)',
        'default': '0.0',
        'datatype':'float (N-element array)',
        'units':'m s^(-1)',
        'flow':'input'
        },
    'ring_damping_pump':{
        'desc':'spectral ring damping for the pump',
        'valrange':'[0, inf)',
        'default': '0.0',
        'datatype':'float (N-element array)',
        'units':'rad s^(-1)',
        'flow':'input'
        },
    'pump_input':{
        'desc':'input spectral pump distribution',
        'valrange':'[0, inf)',
        'default': '0.0',
        'datatype':'float (N-element array)',
        'units':'[pump_input]',
        'flow':'input'
        },
    'ring_response':{
        'desc':'spectral response of ring to pump',
        'valrange':'[0, inf)',
        'default': '0.0',
        'datatype':'complex (N-element array)',
        'units':'[m^(1/2) rad^(-1/2)]',
        'flow':'intermediate'
        },
    'pump_ring':{
        'desc':'expected value of spectral pump distribution',
        'valrange':'[0, inf)',
        'default': '0.0',
        'datatype':'complex (N-element array)',
        'units':'[pump_input * ring_response]',
        'flow':'output'
        }
}

def valArrayTests(a, name, errorNegative=True, warnComplex=True):
    """Perform validation tests for array

    The standard valid array is numeric, real and one-dimensional with 
    all values zero or above.  Options allow for complex and negative
    values.
    """
    eMsg = ''
    wMsg = ''
    err = False
    wrn = False
    # List data type kinds (see SciPy documentation for data type objects)
    numeric_kinds = ['b', 'i', 'u', 'f', 'c']

    if a.dtype.kind not in numeric_kinds:
        eMsg+='Received {} data type kind: {}'.format(name, a.dtype.kind) + os.linesep
        eMsg+='Expected {} data type kind: {}'.format(name, numeric_kinds) + os.linesep
        err=True
        if a.dtype.kind == 'c' and warnComplex == True:
            wMsg+='Received {} in: complex'.format(name) + os.linesep
            wMsg+='Expected {} in: real'.format(name) + os.linesep
            wrn=True
    if a.ndim > 1:
        eMsg+='Received {} dimensions: {}'.format(name, a.ndim) + os.linesep
        eMsg+='Expected {} dimensions: 1'.format(name) + os.linesep
        err=True
    if np.any(a<0) and errorNegative:
        eMsg+='Received {} values < 0'.format(name) + os.linesep
        eMsg+='Expected {} values >= 0'.format(name) + os.linesep
        err=True

    return err, eMsg, wrn, wMsg

def validateParameters(**kwargs):
    """Validate input parameters to the calculation

    Error checks:
      * all inputs numeric, 1-D
      * couplings_pump >= 0
      * velocities_pump >= 0
      * ring_damping_pump >= 0 
      * pump_input >= 0
    Warning checks:
      * wavevec in real
      * velocities_pump in real
      * ring_damping_pump in real

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
    """

    import pprint
    pp = pprint.PrettyPrinter(indent=2)

    wavevec = kwargs.get('wavevec')
    couplings_pump = kwargs.get('couplings_pump')
    velocities_pump = kwargs.get('velocities_pump')
    ring_damping_pump = kwargs.get('ring_damping_pump')
    pump_input = kwargs.get('pump_input')
    
    # Log the inputs
    if lgr.getEffectiveLevel() == logging.DEBUG: 
        msg = ''
        msg += 'Inputs for validation:' + os.linesep
        msg += pp.pformat(kwargs)
        lgr.debug(msg)

    
    
    # Set flag variables and messages for errors (err, eMsg) and warnings (wrn, wMsg)
    err = False
    wrn = False
    eMsg = ''
    wMsg = ''

    # wavevec: numeric, 1-D, and real
    if wavevec is not None:
        err, eMsg, wrn, wMsg = valArrayTests(
            np.array(wavevec), 'spectrum variable', errorNegative=False) 
    # couplings_pump: numeric
    if couplings_pump is not None:
        err, eMsg, wrn, wMsg = valArrayTests(
            np.array(couplings_pump), 'pump couplings', warnComplex=False) 
    # velocities_pump: numeric
    if velocities_pump is not None:
        err, eMsg, wrn, wMsg = valArrayTests(
            np.array(velocities_pump), 'pump velocities') 
    # ring_damping_pump: numeric
    if ring_damping_pump is not None:
        err, eMsg, wrn, wMsg = valArrayTests(
            np.array(ring_damping_pump), 'pump ring damping') 
    # pump_input: numeric
    if pump_input is not None:
        err, eMsg, wrn, wMsg = valArrayTests(
            np.array(pump_input), 'pump input', warnComplex=False) 

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
    >>> import CCqo103_spectral_pump as emr
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

def getInputs(infile, delim=',', num_header_rows=2):
    """Extract inputs from file
    """
    if lgr.getEffectiveLevel() == logging.DEBUG:
        m =''
        m+='Inputs and defaults to the method:' + os.linesep
        m+='  infile = {}'.format(infile) + os.linesep
        m+='  delim = {}'.format(delim) + os.linesep
        m+='  num_header_rows = {}'.format(num_header_rows) + os.linesep
        lgr.debug(m)
    # Set up expected order of column headings
    colHeadings = [
        'wavevec',
        'couplings',
        'velocities',
        'damping',
        'pump_input'
    ]
    # Account for no header rows
    if num_header_rows == 0:
        inArr = np.genfromtxt(infile,
                              delimiter = delim,
                              names = colHeadings
        )
    # Treat the first header row as names
    if num_header_rows > 0:
        inArr = np.genfromtxt(infile,
                              delimiter = delim,
                              names = True
        )
        # Check that the names are consistent
        # Note: The set(A)==set(B) construct does not fail for duplicates
        if not set(colHeadings) == set(inArr.dtype.names):
            m =''
            m+='Received name headings = {}'.format(inArr.dtype.names)
            m+=os.linesep
            m+='Expected name headings = {}'.format(colHeadings)
            lgr.error(m)
            raise ValueError(m)
            
        # Remove false data from header rows
        if num_header_rows > 1:
            # Recall that range(0,N-1) yields 0,1,...,N-2
            # NOTE: One row has been dealt with in names, hence N-1
            inArr=np.delete(inArr, range(0,num_header_rows-1), axis=0)

    # Assign data
    wavevec = inArr['wavevec']
    couplings = inArr['couplings']
    velocities = inArr['velocities']
    damping = inArr['damping']
    pump_input = inArr['pump_input']

            
    if not np.all(np.isfinite(inArr.astype(float))):
        m =''
        m+='Received invalid entries in {}'.format(infile) + os.linesep
        m+='Expected all entries populated and finite in {}'.format(infile) + os.linesep
        m+='INVALID Input array = ' + os.linesep
        m+='{}'.format(inArr)
        lgr.error(m)
        raise ValueError(m)

    return wavevec, couplings, velocities, damping, pump_input

    
    
def calcqo103_spectral_pump(
        wavevec,
        couplings_pump,
        velocities_pump,
        ring_damping_pump,
        pump_input
):

    """Expected value of spectral pump accounting for coupling and damping.

       

    Parameters
    ----------
    NOTE ---
        All parameters must have shapes that are compatible for 
        numpy broadcasting.  Two common situations are (1) that 
        all parameters have the same shape and (2) that 
        some parameters have the same shape and the others are a 
        single element.  

    wavevec : float array
        Independent variable for the spectrum.  Common values are 
        wavenumber, wavevector, wavelength, linear frequency, and 
        circular frequency.  All other spectral parameters must be 
        consistent with this variable.
        
    couplings_pump : complex array
        Spectral coupling constants for the pump input

    velocities_pump : float array
        Spectral velocities for pump photons

    ring_damping_pump : float array
        Spectral damping of the pump by the ring

    pump_input : complex array
        Spectral pump used for the input channel

    Returns
    -------
    (pump_ring, ring_response)

    pump_ring : complex array
        Spectral pump in the ring

    ring_response : complex array
        Spectral response of the ring 
    

    See Also
    --------
    numpy.array, numpy.conj

    Exceptions
    ----------
    None

    Examples
    --------
    # Call with single values
    >>> b, rr = calcqo103_spectral_pump(1,2,3,4,5)
    >>> np.allclose(b, (1.2-1.6j))
    True

    >>> np.allclose(rr, (0.24-0.32j))
    True

    # Setup arrays for multiple value runs
    # (numpy arrays are preferred, but this shows that lists succeed.)
    >>> k = [1,6]
    >>> g = [2,7]
    >>> v = [3,8]
    >>> G = [4,9]
    >>> a = [5,10]
    
    # Call with multiple values, all of equal size
    >>> b, rr = calcqo103_spectral_pump(k,g,v,G,a)
    >>> np.allclose(b, ([ 1.20000000-1.6j,  1.40880503-0.26415094j]))
    True

    >>> np.allclose(rr, ([ 0.2400000-0.32j,  0.1408805-0.02641509j]))
    True

    # Retrieve only the pump (main output)
    >>> b0 = calcqo103_spectral_pump(k,g,v,G,a)[0]
    >>> np.allclose(b0, ([ 1.20000000-1.6j,  1.40880503-0.26415094j]))
    True

    # Call with a mix of single and multiple values (numpy broadcasting)
    >>> b, rr = calcqo103_spectral_pump(k,2.7,3.1,G,a)
    >>> np.allclose(b, ([ 1.63412729-2.10855135j,  1.17622260-0.56913997j]))
    True

    """

    # Assign short names for inputs and ensure numpy
    k = np.array(wavevec)
    g = np.array(couplings_pump)
    v = np.array(velocities_pump)
    G = np.array(ring_damping_pump)
    a = np.array(pump_input)

    # Check internal calculation for /0
    denom = (-1j*k*v+G)
    if np.any(denom == 0):
        m =''
        m+='Division by zero for -1J*wavevec*velocity+damping' + os.linesep
        lgr.error(m)
        raise ValueError(m)
    
    # Ring response (rr)
    rr = -1j*np.conj(g) / denom
    ring_response = rr

    # pump in the ring (b)
    b = rr * a
    pump_ring = b

    if lgr.getEffectiveLevel() == logging.DEBUG:
        m =''
        m+='ring response function = {}' + os.linesep
        m+='{}'.format(ring_response) + os.linesep
        m+='ring pump function =' + os.linesep
        m+='{}'.format(pump_ring)
        lgr.debug(m)

    return pump_ring, ring_response
    

if '__main__' == __name__:

    import argparse
    import pprint
    pp = pprint.PrettyPrinter(indent=2)

    import CCqo103_spectral_pump as emr

    # Create the option object
    #  - Help option (-h, --help) included by default 
    #  - Usage statement included by default
    argp = argparse.ArgumentParser(
        description='Obtain spectral pump in ring resonator',
        epilog='Unambiguous option abbreviations are permitted.')
    # Add options
    # ===========
    argp.add_argument(
        '--doof', dest='doof', action='store')

    argp.add_argument(
        '--spectral-inputs', 
        type=str, required=True,
        dest='spectral_inputs', action='store',
        help="Spectral inputs in CSV file.  First row column heading names: wavevec, couplings, velocities, damping, pump_input. Second row: non-data (e.g. dimensions).  Data begin in third row.",
        metavar='specFile'
        )

    argp.add_argument(
        '--num-header-rows', 
        type=int, required=False,
        dest='num_header_rows', action='store',
        default=2,
        help="Number of header rows that are not data values. If specFile is not of the form defined in --spectral-inputs, this option must be used. If names for data columns are specified then they must be in the first row and they must have the same strings (but not necessarily order) as those described in --spectral-inputs.",
        metavar='nHdr'
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
        default='CCqo103_spectral_pump.log',
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
    lgr.debug('Inputs and Defaults: ' +os.linesep + pp.pformat(args.__dict__))

    # Act
    try:
        [wavevec,
         couplings,
         velocities,
         damping,
         pump_input
        ] = emr.getInputs(args.spectral_inputs,
                          num_header_rows=args.num_header_rows)
        if args.validate:
            try:
                emr.validateParameters(
                    wavevec = wavevec,
                    couplings_pump = couplings,
                    velocities_pump = velocities,
                    ring_damping_pump = damping,
                    pump_input = pump_input
                )
            except RuntimeWarning as e:
                msg = 'Dubious inputs for CCqo103_spectral_pump.'
                lgr.warn(str(e))
                pass
            except ValueError as e:
                msg = 'Invalid value for CCqo103_spectral_pump.'
                lgr.error(str(e))
                raise
            except Exception:
                msg = 'Error in CCqo103_spectral_pump.'
                lgr.error(msg)
                raise

        pump_ring, ring_response = emr.calcqo103_spectral_pump(
            wavevec = wavevec,
            couplings_pump = couplings,
            velocities_pump = velocities,
            ring_damping_pump = damping,
            pump_input = pump_input
        )
        msg = ''
        msg += ' CCqo103_spectral_pump outputs' + os.linesep
        msg += '  pump in ring = {}'.format(pump_ring) + os.linesep
        msg += '  ring response= {}'.format(ring_response)
        if lgr.getEffectiveLevel() > logging.INFO: print(pump_ring)
        else: lgr.info(msg)

    except Exception:
        ex_type, ex, tb = sys.exc_info()
        print ex_type
        print ex
        lgr.error('<TRACEBACK>')
        traceback.print_tb(tb)
        lgr.error('</TRACEBACK>')
