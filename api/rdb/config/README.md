config
===============

Shared configuration library supports multiple deployment environments placement 
of config files

## Overview

The basic idea is to support a common configuration system across modules.  This module
will look for JSON config files in well known places and load them to
construct a single merged dictionary of config parameters.


### Basic Usage

```
import sys
import config

config.init(module=sys.modules[__package__])

proxy_uri = config.get('api.http.proxy.uri')
proxy_timeout = config.get_as_seconds('api.http.proxy.timeout')
```

If you fail to call config.init(), the package will call it for you with
reasonable defaults.  However, safest and best practice is to initialize
it explicitly, passing the name of your module (e.g. fleuve, drill, etc).

The config module will find and load these files in a specific order (below)
which means that more general settings can be overridden by more specific ones
for both modules and environments.

###  Initialization

The config module must initialize all the settings.  It can do this only once
per running process.  If you don t explictly intiilaize it by calling
`config.init()`, it will initialize itself upon the first call to `config.get()`.

### Fancy Usage

```
import sys
import config

config.init(module=sys.modules[__package__], dirs=['/also/look_here'])

# inspect the environment
print(config.environment())
print(config.is_test())
print(config.is_staging())
print(config.is_production())

# for debugging
print(config.config_dirs())
print(config.config_paths())
print(config.dictionary())
```

