# -*- coding: utf-8 -*-
#
# cli.py - CLI Entry Point for 'nmc'
# This file only handles command-line interaction and I/O.
#

import sys
from . import run_numerus_file, NumerusError

def main():
    """Main function for the 'nmc' command."""
    
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: nmc <path_to_file.nm>\n")
        sys.exit(1)

    filepath = sys.argv[1]
    
    try:
        # Use the integration function to run the file
        output = run_numerus_file(filepath)
        
        # Print the successful output
        print(output, end='')
        
    except FileNotFoundError as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)
    except NumerusError as e:
        # Print Parser or Runtime errors
        sys.stderr.write(f"\n!!! Numerus Error: {e}\n")
        sys.exit(1)
    except Exception as e:
        # Catch any other unexpected errors
        sys.stderr.write(f"\n!!! Unknown Error: {e}\n")
        sys.exit(1)

if __name__ == '__main__':
    main()