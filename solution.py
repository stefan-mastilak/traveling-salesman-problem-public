# REF: stefan.mastilak@gmail.com

"""
Main script
"""

import argparse
import json
from lib.search_engine import Searcher


if __name__ == '__main__':
    """
    Argument parser
    NOTE: Usage is described in README.md file 
    """

    # Create parser:
    parser = argparse.ArgumentParser()

    # Add arguments:
    parser.add_argument('data', type=str, help="data source file (stored in examples folder)")
    parser.add_argument('org', type=str, help="origin airport code")
    parser.add_argument('des', type=str, help="destination airport code")
    parser.add_argument('-b', '--bags', type=int, required=False, default=0,
                        help="number of baggage pieces (default 0)")
    parser.add_argument('-m', '--max_connections', type=int, required=False, default=2,
                        help="maximum connections (default 2)")

    # Parse the arguments
    args = parser.parse_args()

    # Get flights:
    results = Searcher(args.data).search(org=args.org, des=args.des, bags=args.bags, max_conns=args.max_connections)
    print(json.dumps(results, indent=4, sort_keys=False))
