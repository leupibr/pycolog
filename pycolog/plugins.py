import importlib


def load(plugins):
    for plugin in plugins:
        yield importlib.import_module(plugin)


def mount(options):
    for plugin in options.get('plugins', []):
        if hasattr(plugin, 'mount'):
            plugin.mount(options)


def post_construct(entry, options):
    for plugin in options.get('plugins', []):
        if hasattr(plugin, 'post_construct'):
            plugin.post_construct(entry, options)
