

# iGrafx P360 Live Mining SDK


[![PyPI pyversions](https://img.shields.io/pypi/pyversions/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)
![GitHub commit activity (branch)](https://img.shields.io/github/commit-activity/m/igrafx/mining-python-sdk?color=orange)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/igrafx/mining-python-sdk/blob/main/LICENSE)
[![GitHub forks](https://badgen.net/github/forks/igrafx/mining-python-sdk)](https://github.com/igrafx/mining-python-sdk/forks)
![GitHub issues](https://img.shields.io/github/issues/igrafx/mining-python-sdk?color=)
[![Project Status](http://www.repostatus.org/badges/latest/active.svg)](http://www.repostatus.org/#active)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/igrafx/mining-python-sdk?color=purple)
![GitHub repo file count (file type)](https://img.shields.io/github/directory-file-count/igrafx/mining-python-sdk?color=pink)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Open Source Love svg2](https://badges.frapsoft.com/os/v2/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)

***

## Introduction

The **iGrafx P360 Live Mining SDK** is an open source application that can be used to manage your mining projects.
It is a python implementation of the iGrafx P360 Live Mining API.

With this SDK, you will be able to create workgroups, projects, datasources and graphs (and graph instances). You will also be able to create and 
add a column mapping.

Please note that you must have an iGrafx account in order to be able to use the SDK properly. Please contact us to create an account.

The iGrafx P360 Live Mining SDK uses Python.

A detailed tutorial can be found in the [howto.md](https://github.com/igrafx/mining-python-sdk/blob/dev/howto.md) file.

You may find the github of the iGrafx Mining SDK [here](https://github.com/igrafx/mining-python-sdk).

You may also find the github of the iGrafx KNIME Mining Extension [here](https://github.com/igrafx/KNIME-Mining-connector) 
which is based on the iGrafx Mining SDK.



## Requirements

This package requires python 3.10 or above. Get the latest version of [Python](https://www.python.org/).

The required packages should be installed via the ```pyproject.toml``` when running the  ```poetry install``` command. 

This project includes a jar from Apache Calcite Avatica
(https://mvnrepository.com/artifact/org.apache.calcite.avatica/avatica),
which is licensed under the Apache License, Version 2.0.

The original Apache License can be found in LICENSES/Apache-2.0.txt.


## Installing

### With pip:
To install the current release of the iGrafx P360 Live Mining SDK with **pip**, simply navigate to the console and type the following command: 
````shell
pip install igrafx_mining_sdk
````

### To begin:
Go ahead and **import** the package:
```python
import igrafx_mining_sdk as igx   # the 'as igx' is entirely optional, but it will make the rest of our code much more readable
```

## Documentation

The full documentation can be found in the ```howto.md``` file [here](https://github.com/igrafx/mining-python-sdk/blob/dev/howto.md).
Follow the instructions to try out the SDK.


## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

For more information on how to contribute, please see the [CONTRIBUTING.md](https://github.com/igrafx/mining-python-sdk/blob/dev/CONTRIBUTING.md) file.

## Support

Support is available at the following address: [support@igrafx.com](mailto:support@igrafx.com).

## Notice

Your feedback and contributions are important to us. Don't hesitate to contribute to the project.

## License

This SDK is licensed under the MIT License. See the ````LICENSE```` file for more details.

It also includes dependencies that are licensed under **Apache License 2.0**.
See `LICENSES/Apache-2.0.txt` and `NOTICE` for details.