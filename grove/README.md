# grove

Homegrown logging and config boilerplate

### How to use

**Make sure to add vendor directory to module search path**

Assuming a project directory structure like this:

```
|- logs_things.py
|- grove/
```

Add `grove` to your module search path

```python
import os
import sys

parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, 'grove')
sys.path.append(vendor_dir)
```

Example to demonstrate the pattern that `grove` might fit into:

```python
import logging
import argparse
import grove

class XYZConfig:
    config_fn = None    # Full path to json config file
    port = 1337
    sources = []
    logger = None
    log_directory = None
    log_level = logging.INFO

    def load(self):
        """Here, grove will
        - Set config attrs from json file (will simply pass if a file isn't specified)
        - Sets up directories to log in (determined by config.log_directory)
        """
        grove.set_config(self, self.config_fn)
        self.logger = grove.get_logger(config=self, debug=False)

class XYZDoer:
    def __init__(self, config):
        self.config = config
        self.logger = config.logger

    def run(self):
        do_stuff()

if __name__ == '__main__':
    _config = XYZConfig()
    # possibly parse args, particularly "config_fn"
    # parser.parse_args(namespace=_config)
    _config.load()
    XYZDoer(_config).run()
```
