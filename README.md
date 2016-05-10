Prime Infrastructure Tools
========================

#### This is a small toolkit to provide scripts that retrieve data from the Prime Infrastructure through its REST API.

## Table of Contents
  
  * [Introduction](#introduction)
  * [Requirements](#requirements)
  * [PrimeAPI](#primeapi)
  * [Tools] (#tools)
	* [Prime Configuration Extractor] (#prime-configuration-extractor)
  * [Changelog] (#changelog)


# Introduction
This toolkit provides scripts which retrieve additional data from the Prime Infrastructure API that can't be accessed through the dashboard. The toolkit combines an API wrapper class that provides easy access to the Prime Infrastructure API. In addition to that, there is currently one tool that downloads configuration files from each device attached to the Prime Infrastructure and stores them locally on your computer. 

# Requirements
You need to install the following software to run this toolkit:
* [Python3](https://www.python.org/)
* Python [requests]http://docs.python-requests.org/en/master/) library

# PrimeAPI
This wrapper class provides easy access to the Prime Infrastructure API. Currently, only GET requests are supported. Here is a short example about how to instantiate the wrapper and to send requests to the REST API:

```python
prime_url = "https://myprime.com"
prime_user = "user"
prime_pw = "pw"

api = PrimeAPI(prime_url, prime_user, prime_pw)

xml_root = api.send_prime_request("data/ConfigVersions", "XML")
```

# Tools
Currently, this toolkit only supports extraction of configuration files through the Prime Infrastructure API. In future, we might add additional scripts to this toolkit.

## Prime Configuration Extractor
This tool extracts all available running and startup configurations from the Prime Infrastructure and stores them on your computer. Just execute `PrimeConfigExtractor.py` and follow the instructions on the console. After execution, all configuration files will be stored in the specified folder `(path)\pi_cfg_files\`. If there is an execution error, then you can also take a look at the log file `pi_cfg.log` in the folder where scripts is executed.

# Changelog

## v0.1 (2016-05-10)

Initial release
