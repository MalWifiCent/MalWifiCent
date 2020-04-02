# Cli
`>python3 cli.py`  
![cli.png](/img/cli.png)

Type "help" to view command documentation in terminal.

## Commands:
* INetSim Commands:  
    + start: Will start INetSim  
    + stop: Will stop INetSim  

* Debugging Commands:  
    + count: Prints a count of all INetSim processes  
    + pread: Read text from INetSim stdout (Will probably hang the terminal)  
    + fkill: Force kill all INetSim processes  

Example:  
`inet start`

# Tests
Run from console directory:  
`python3 -m unittest tests/service-test.py`