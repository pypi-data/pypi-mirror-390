import argparse
import sys

# import os

# # Hardcoded version information
VERSION = "0.0.2"

# # Hardcoded dependencies information
# DEPENDENCIES = {
#     "python": "^3.11",
#     "PyYAML": "^6.0.2",
#     "SQLAlchemy": "^2.0.36",
#     "psycopg2": "^2.9.10",
#     "pandas": "^2.2.3",
#     "pyodbc": "^5.2.0",
#     "pylint": "^3.3.1"
# }

# Hardcoded usage information
EXAMPLE_TRACE = """

sample usage:

from decoraid.trace import trace_func


# wrap the decorator around the function you want to trace
@trace_func
def test_pandas():
    print('test_trace')

if __name__ == "__main__":
    test_pandas()

"""

# Hardcoded usage information
EXAMPLE_CPDEC = """

sample usage:

from decoraid.cpdec import check_package
venv_path = "C:/projects/git/xxxx/.venv/" 

# wrap the decorator around the function you want to test, provide the name of the package and the path to the virtual environment
@check_package("pandas", venv_path)
def test_pandas():
    print('test_cpdec')

if __name__ == "__main__":
    test_pandas()

"""



def main():
    parser = argparse.ArgumentParser(description='Decoraid ~ collection of usefull decorator utilities')
    parser.add_argument('--version', action='version', version=f'ConnectionVault {VERSION}')
    parser.add_argument('--example', action='store_true', help='Show sample code syntax')
    parser.add_argument('-cpdec', type=str, help='Template example for cpdec usage')
    parser.add_argument('-trace', type=str, help='Template example for trace usage')

    
    args = parser.parse_args()

    # if args.example:
    #     print(EXAMPLE)

    if args.example:
        if not args.cpdec:
            print(" -cpdec is required for --example")
            sys.exit(1) 
        print(EXAMPLE_CPDEC) 
        sys.exit(0)

    if args.example:
        if not args.trace:
            print(" -trace is required for --example")
            sys.exit(1) 
        print(EXAMPLE_TRACE) 
        sys.exit(0)

    # if args.example:
    #     if not args.cpdec or not args.trace:
    #         print(" -cpdec or -trace is required for --example")
    #         sys.exit(1) 
    #     print(EXAMPLE_CPDEC) 
    #     sys.exit(0)



if __name__ == '__main__':
    main()