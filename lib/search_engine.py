# REF: stefan.mastilak@gmail.com

"""
Search engine

Restrictions:
    - search on ALL available combinations
    - in case of a combination of A -> B -> C, the layover time in B should not be less than 1h and more than 6h
    - no repeating airports in the same trip
    - output is sorted by the final price of the trip

Optional arguments:
    - You may add any number of additional search parameters to boost your chances to attend:
        - bags: <integer> - number of requested bags (default 0)
        - return: <bool> - is it a return flight (default false)
"""



