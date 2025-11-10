# Missim Config

Missim Config is used to load config stored inside the `~/.config/greenroom` folder.

## Install

* `pip install -e ./packages/missim_config`

## Usage

### Reading config

```python
from missim_config import read

config = read()
```

### Writing config

```python
from missim_config import write, MissimConfig

config = MissimConfig()

write(config)

```

### Generating schemas

After changing the dataclasses, you can generate the schemas with:

```bash
python3 -m missim_config.generate_schemas
```
