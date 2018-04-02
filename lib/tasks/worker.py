from lib.plugin import Manager
# legacy
def worker(host, plugin):
    p = Manager.get_plugin(plugin)
    p.Plugin.Pipeline(host, plugin)
    del p
    # cool bro
