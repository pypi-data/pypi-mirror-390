### About

A small helper library to use Ansible Galaxy from within Python.

Work in progress, I will improve this soon. For now, I just need to reuse
this code in some other tools.

### Installing

```
pip install ansible-galaxy-helper
```

### Usage

```python
import os
import ansible_galaxy_helper

result = ansible_galaxy_helper.ensure_galaxy_dependencies(
        os.path.join('path', 'to', 'ansible-galaxy-requirements.yml'))

try:
    assert result == 0
except AssertionError:
    raise RuntimeError("Didn't work.")
```
