# REF: stefan.mastilak@gmail.com

"""
Main script
"""
import argparse
import json
from lib.search_engine import Searcher


if __name__ == '__main__':
    """
    argument parser for solution.py:
    """
    parser = argparse.ArgumentParser()
    # Add an arguments
    parser.add_argument('--data', type=str, required=True, help="data source")
    parser.add_argument('--org', type=str, required=True, help="origin airport code")
    parser.add_argument('--des', type=str, required=True, help="destination airport code")
    parser.add_argument('--bags', type=int, required=False, default=0, help="number of baggage pieces (default 0)")
    parser.add_argument('--max_conns', type=int, required=False, default=2, help="maximum of connections (default 2)")

    # Parse the arguments
    args = parser.parse_args()

    # Get flights:
    results = Searcher(args.data).search(org=args.org, des=args.des, bags=args.bags, max_conns=args.max_conns)
    print(json.dumps(results, indent=4, sort_keys=False))
