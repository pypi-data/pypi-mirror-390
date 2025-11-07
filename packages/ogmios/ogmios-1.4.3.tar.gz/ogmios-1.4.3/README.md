# ogmios-python

[![Pipeline](https://gitlab.com/viperscience/ogmios-python/badges/main/pipeline.svg)](https://gitlab.com/viperscience/ogmios-python/-/pipelines)
[![Documentation Status](https://readthedocs.org/projects/ogmios-python/badge/?version=latest)](https://ogmios-python.readthedocs.io/en/latest/?badge=latest)
[![PyPI - Version](https://img.shields.io/pypi/v/ogmios.svg)](https://pypi.org/project/ogmios)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ogmios.svg)](https://pypi.org/project/ogmios)
[![Codecov](https://codecov.io/gitlab/viperscience/ogmios-python/graph/badge.svg?token=7VUVLYR6FP)](https://codecov.io/gitlab/viperscience/ogmios-python)
[![Catalyst](https://img.shields.io/badge/catalyst-fund10-violet)](https://cardano.ideascale.com/c/idea/105214)

-----

[Ogmios](https://ogmios.dev/) is a lightweight bridge interface for cardano-node. It offers a WebSockets API that enables local clients to speak Ouroboros’ mini-protocols via JSON/RPC. **ogmios-python** is an Ogmios client written in Python designed for ease of use.

-----

**Table of Contents**

- [ogmios-python](#ogmios-python)
  - [Installation](#installation)
  - [Quickstart](#quickstart)
  - [Documentation](#documentation)
  - [License](#license)


## Installation

1. Install cardano-node and Ogmios server as described [here](https://ogmios.dev/getting-started/). (Docker installation is recommended.)
2. Install ogmios-python from [PyPI](https://pypi.org/project/ogmios/) using pip:

```console
pip install ogmios
```


## Quickstart

To see how easy it is to build on Cardano with ogmios-python, let's use the library to view new blocks as they are added to the blockchain:

```python
import ogmios

with ogmios.Client() as client:
    # Set chain pointer to origin
    _, tip, _ = client.find_intersection.execute([ogmios.Origin()])

    # Now set chain pointer to tip
    _, _, _ = client.find_intersection.execute([tip.to_point()])

    # Tail blockchain as new blocks come in beyond the current tip
    while True:
        direction, tip, point, _ = client.next_block.execute()
        if direction == ogmios.Direction.forward:
            print(f"New block: {point}")
```

![terminal output](https://gitlab.com/viperscience/ogmios-python/-/raw/main/docs/source/_static/live_block_viewer.png "Live block viewer terminal output")

For more examples, see the documentation and example scripts in the repo.


## Documentation

Complete client documentation is available on [Read the Docs](https://ogmios-python.readthedocs.io/en/latest).


## License

`ogmios-python` is distributed under the terms of the [GPL-3.0-or-later](https://spdx.org/licenses/GPL-3.0-or-later.html) license.
