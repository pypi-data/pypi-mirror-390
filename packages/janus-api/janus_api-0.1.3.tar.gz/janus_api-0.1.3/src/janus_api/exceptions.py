# ----------------------
# Exceptions
# ----------------------

class PluginManagerError(Exception):
    """Base exception for the plugin manager."""


class PluginAlreadyRegistered(PluginManagerError):
    """Raised when attempting to register a plugin under a plugin_id that's already used."""


class PluginNotRegistered(PluginManagerError, KeyError):
    """Raised when attempting to access or remove a plugin that isn't registered."""