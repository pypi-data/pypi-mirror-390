<div align="center">
  <img src="assets/images/sparkwheel_banner.png" width="65%"/>
</div>

<p align="center">
  <a href="https://github.com/project-lighter/sparkwheel/actions"><img alt="Tests" src="https://github.com/project-lighter/sparkwheel/workflows/Tests/badge.svg"></a>
  <a href="https://github.com/project-lighter/sparkwheel/actions"><img alt="Code quality" src="https://github.com/project-lighter/sparkwheel/workflows/Code%20quality/badge.svg"></a>
  <a href="https://pypi.org/project/sparkwheel/"><img alt="PyPI" src="https://img.shields.io/pypi/v/sparkwheel"></a>
  <a href="https://project-lighter.github.io/sparkwheel"><img alt="Documentation" src="https://img.shields.io/badge/docs-latest-blue"></a>
  <a href="https://github.com/project-lighter/sparkwheel/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/badge/License-Apache%202.0-blue.svg"></a>
</p>

<p align="center">
  <strong>Define your workflow in YAML, instantiate it in Python</strong>
</p>

---

## Installation

```bash
pip install sparkwheel
```

**Requirements:** Python 3.10+

## Quick Start

Define your workflow in YAML, then use it in Python. Objects are created with their dependencies automatically resolved.

<table>
<tr>
<td width="50%">

**config.yaml**

```yaml
network:
  _target_: torch.nn.Linear
  in_features: 784
  out_features: 10

optimizer:
  _target_: torch.optim.Adam
  params: $@network.parameters()
  lr: 0.001
```

</td>
<td width="50%">

**main.py**

```python
from sparkwheel import ConfigParser

parser = ConfigParser()
parser.read_config("config.yaml")

network = parser.get_parsed_content("network")
optimizer = parser.get_parsed_content("optimizer")
```

</td>
</tr>
</table>

## Features

- **Declarative**: Build complex applications using simple YAML configs
- **References**: Link configuration values with `@` for resolved Python objects or `%` for raw YAML values
- **Composition**: Combine multiple configuration files seamlessly
- **Expressions**: Execute Python code within configs using `$` prefix

## Usage

**[📚 Documentation →](https://project-lighter.github.io/sparkwheel)**

## About

Sparkwheel is a hard fork of [MONAI](https://github.com/Project-MONAI/MONAI)'s configuration system, stripped down to focus and improve its usability for general purposes. We're deeply grateful to the MONAI team for their excellent foundation.
