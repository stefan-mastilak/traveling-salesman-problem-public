
# Flight search assessment

* Author: Stefan Mastilak
* Contact: stefan.mastila@gmail.com

### General:

 Solution for searching flights based on data fetched from the .csv file stored in examples folder.
 
#### Restrictions:
  * search on all available combinations
  * in case of a combination of A -> B -> C, the layover time in B should not be less than 1h and more than 6h
  * no repeating airports in the same trip
  * output is sorted by the final price of the trip

#### Optional arguments:
  * bags: <integer> - number of requested bags (default 0)
  * max_connections: <integer> - maximum connection flights for a trip (default 2)

* Python version: 3.9

### Usage:

```
usage: solution.py [-h] [-b BAGS] [-m MAX_CONNECTIONS] data org des

positional arguments:
  data                  data source file (stored in examples folder)
  org                   origin airport code
  des                   destination airport code

optional arguments:
  -h, --help            show this help message and exit
  -b BAGS, --bags BAGS  number of baggage pieces (default 0)
  -m MAX_CONNECTIONS, --max_connections MAX_CONNECTIONS
                        maximum connections (default 2)
```

### Usage examples:

```shell
# EXAMPLE 1

# To filter flights stored in example3.csv from WUE to JBN with 2 pieces of baggage and maximum of 1 connection:

  python -m solution example3.csv WUE JBN --bags=2 --max_connections=1
    
  python -m solution example3.csv WUE JBN -b=2 -m=1
```
```shell

# EXAMPLE 2 

# To filter flights stored in example1.csv from NIZ to SML with maximum of 2 connections without defined baggage pieces:

  python -m solution example1.csv NIZ SML --max_connections=2
  
  python -m solution example1.csv NIZ SML -m=2
```

```shell
# EXAMPLE 3 

  # To filter flights stored in example1.csv from NRX to SML 
  # NOTE: No optional arguments passed - default values will be used (0 for baggage, 2 for maximum of connections) 
  
  python -m solution example1.csv NRX SML
```

### Help:

```shell
    python -m solution --help
    
    python -m solution -h
```


