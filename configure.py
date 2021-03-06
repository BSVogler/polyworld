#!/usr/bin/env python

import argparse
import os
import os.path
import platform
import subprocess
import sys

######################################################################
#
# Constants
#
######################################################################
Conf='Makefile.conf'

Supported_OSes = ['linux', 'darwin']
Supported_OSes_display = ','.join(Supported_OSes)

Supported_Toolchains = ['gcc', 'llvm']
Supported_Toolchains_display = ','.join(Supported_Toolchains)

Default_CXX = {'linux': 'g++',
               'darwin': 'clang++'}

######################################################################
#
# main()
#
######################################################################
def main():
    # sanity check
    if not check_exit('which bash'):
        sys.exit("Failed locating bash!")
    
    #
    # Parse command-line
    #
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--debug',
                        action = 'store_true',
                        default = False,
                        help = "debug build")
    parser.add_argument('-c', '--cxx',
                        nargs = 1,
                        help = "specify compiler with optional path (e.g. clang++, /usr/bin/g++-4.9)")
    parser.add_argument('-q', '--qmake',
                        nargs = 1,
                        help = "specify qmake with optional path (e.g. qmake, /usr/bin/qmake)")
    parser.add_argument('--toolchain',
                        nargs = 1,
                        help = "specify toolchain ("+Supported_Toolchains_display+")")
    parser.add_argument('--os',
                        nargs = 1,
                        help = "specify OS ("+Supported_OSes_display+")")

    config = vars(parser.parse_args())
    
    #
    # Determine OS
    #
    if not config['os']:
        config['os'] = platform.system().lower()
    else:
        config['os'] = config['os'][0]
    
    if not config['os'] in Supported_OSes:
        sys.exit("Unsupported OS (" + config['os'] + "). Supported = " + Supported_OSes_display)
    
    print('Operating System:', config['os'])
    
    #
    # Determine compiler
    #
    if not config['cxx']:
        config['cxx'] = Default_CXX[config['os']]
    else:
        config['cxx'] = config['cxx'][0]
    print('CXX:', config['cxx'])
    
    if not check_exit('which '+config['cxx']):
        sys.exit('Cannot locate compiler')
    
    if 'clang' in config['cxx']:
        config['toolchain'] = 'llvm'
    else:
        config['toolchain'] = 'gcc'
    print('Toolchain:', config['toolchain'])

    #
    # Verify qmake
    #
    if not config['qmake']:
        config['qmake'] = 'qmake'
    else:
        config['qmake'] = config['qmake'][0]
    if not check_exit('which '+config['qmake']):
        sys.exit('Cannot locate qmake')
    print('QMake:', config['qmake'])
    
    #
    # Determine optimization level
    #
    config['optimization'] = 'debug' if config['debug'] else 'optimized'
    print('Optimization:', config['optimization'])
    
    #
    # Create speculative conf and clean
    #
    config['omp'] = True
    generate_conf(config)
    if not check_exit('make clean'):
        sys.stderr.write("Warning! Encountered errors when cleaning build environment!\n")
    
    #
    # Check OpenMP support
    #
    if not check_exit('make omp_test'):
        config['omp'] = False
    print('OpenMP Supported:', config['omp'])
    
    #
    # Create final configuration
    #
    generate_conf(config)

    #
    # Let user know we're done
    #
    print('Configure complete.')

######################################################################
#
# Run cmd in bash and return True if succeeded (output not shown)
#
######################################################################
def check_exit(cmd):
    try:
        subprocess.check_output(['bash', '-c', cmd], stderr=subprocess.STDOUT)
        return True
    except:
        return False

######################################################################
#
# Create ./Makefile.conf
#
######################################################################
def generate_conf(config):
    pwhome=os.path.realpath('.')
    f = open( os.path.join(pwhome, Conf), 'w' )

    f.write( 'PWHOME = %s\n' % pwhome )
    f.write( 'PWOS = %s\n' % config['os'] )
    f.write( 'PWTOOLCHAIN = %s\n' % config['toolchain'] )
    f.write( 'PWOMP = %s\n' % config['omp'] )
    f.write( 'PWOPT = %s\n' % config['optimization'] )
    f.write( 'PWQMAKE = %s\n' % config['qmake'] )
    f.write( 'CXX = %s\n' % config['cxx'] )
    
    f.write( 'include ${PWHOME}/etc/bld/Makefile.conf\n' )

    f.close()

main()
