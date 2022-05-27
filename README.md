
# Flight search assessment

* Author: Stefan Mastilak
* Contact: stefan.mastila@gmail.com

### General:

 Solution for searching flights based on data fetched from the .csv file stored in examples folder.

* Python version: 3.9


### Usage examples:

```shell
# To filter flights stored in example3.csv from WUE to JBN with 2 pieces of baggage and maximum of 1 connection:

    python -m solution example3.csv WUE JBN --bags=2 --max_connections=1
    
    python -m solution example3.csv WUE JBN -b=2 -m=1
```
