# -*- coding: utf-8 -*-
import re

from api.rdb.utils.boolean import as_bool
from api.rdb.utils.datetime import as_seconds
from api.rdb.utils.size import as_size
from .environment import environments
from .exceptions import ConfigUnkownEnvError, ConfigKeyError, ConfigMissingKey
from .files import candidate_files, read_file
from .values import valid_key, expand_value


class ConfigDict(dict):

    def keys(self):
        # noinspection PyCompatibility
        return set(super().keys())

    def get(self, key, default=None):

        try:
            if not valid_key(key):
                raise ConfigKeyError("invalid key: %s" % key)
        except TypeError:
            raise ConfigKeyError("keys must be strings")

        # noinspection PyCompatibility
        v = super().get(key, default)

        if v is None:
            raise ConfigMissingKey("missing config value for: %s" % key)

        return v

    def get_as_seconds(self, key):
        """
        Returns the value as seconds of duration. Various shortcuts like 1w will work.
        """
        value = self.get(key)
        return as_seconds(value)

    def get_as_size(self, key):
        """
        Returns the value as an integer size. Various shortcuts like 1g will work.
        """
        value = self.get(key)
        return as_size(value)

    def get_as_bool(self, key):
        """
        Returns the value as True or False.  Values like yes,true,on,1 are all true.
        """
        value = self.get(key)
        return as_bool(value)

    def get_as_config(self, key, default=None):
        """
        Returns value as a ConfigDict
        """
        try:
            value = self.get(key)
            return ConfigDict(value)
        except ConfigMissingKey:
            _re_key = re.compile(r'^%s\.(.+)$' % key)

            def _matching_keys():
                for _k in self.keys():
                    _m = _re_key.match(_k)
                    if _m:
                        yield (_m.group(1), self[_k])

            _keys = list(_matching_keys())
            if _keys:
                return ConfigDict(_keys)

        return default


class Config(object):

    def __init__(self, environment=None, module=None, config_values=None):

        self.config_values = ConfigDict()
        if config_values is not None:
            self.config_values.update(config_values)

        self.environment = str(environment).lower().strip()
        self.module = module

        if self.environment not in environments():
            raise ConfigUnkownEnvError(self.environment)
        config_dir = "config"
        self._read_configs(config_dir)

    def get(self, key, default=None):
        return self.config_values.get(key, default)

    def get_as_config(self, key, default=None):
        return self.config_values.get_as_config(key, default)

    def size(self):
        return len(self.config_values)

    def keys(self):
        return set(self.config_values.keys())

    def _read_configs(self, prefix=None):
        h = {}

        self._read_config_files(h, prefix)

        filtered = dict()
        if self.environment in h:
            for k, v in h.items():
                if not isinstance(v, dict):
                    filtered[k] = v
            for k, v in h[self.environment].items():
                filtered[k] = expand_value(v, self.environment)
            # h = dict(((k, expand_value(v, self.environment)) for k, v in h[self.environment].items()))
            self.config_values.update(filtered)

            print(str(self.config_values))

    def _read_config_files(self, h, prefix=None):
        for path in candidate_files(self.module, prefix):
            _h = read_file(path)
            if _h:
                h.update(_h)
        return h
