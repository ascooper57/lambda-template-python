# -*- coding: utf-8 -*-

class ConfigUnintialized(RuntimeError):
    pass


class ConfigKeyError(KeyError):
    pass


class ConfigMissingKey(KeyError):
    pass


class ConfigMissingEnvError(ValueError):
    pass


class ConfigMissingModuleError(ValueError):
    pass


class ConfigUnkownEnvError(ValueError):
    pass


class ConfigAllowedOnlyInTest(RuntimeError):
    pass
