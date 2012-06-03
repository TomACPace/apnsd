
import os, logging
from twisted.application import internet
import errors

def read_listeners_in_config(config_file, apns_daemon, service_parent):
    """
    Reads the config file and return all the listeners in it one by one.
    """
    if not os.path.isfile(config_file):
        raise errors.ConfigFileError(config_file, "File not found: %s" % config_file)

    configs = eval(open(config_file).read())
    if 'listeners' not in configs:
        raise errors.ConfigFileError(config_file, "'listeners' section not found")

    listeners = configs['listeners']
    for listener_name in listeners:
        listener_data     = listeners[listener_name]
        listener_class    = listener_data['class']
        parts = listener_class.split(".")
        if len(parts) > 1:
            listener_pkg      = ".".join(parts[:-1])
            listener_module   = __import__(listener_pkg, {}, {}, [''])
            listener_class    = getattr(listener_module, parts[-1])
        else:
            listener_class    = eval(parts[-1])

        logging.debug("Creating listener: " + str(listener_class))

        listener = listener_class(apns_daemon, **listener_data)
        if listener_data.get("secure", False):
            server = internet.SSLServer(listener_data["port"], listener)
        else:
            server = internet.TCPServer(listener_data["port"], listener)
        server.setServiceParent(service_parent)

        logging.debug("Listener Created: " + str(listener))
        apns_daemon.registerListener(listener_name, listener)

def read_apps_in_config(config_file, apns_daemon):
    """
    Reads the config file and loads config data about all the apps we want
    to support.
    """
    """
    Reads the config file and return all the listeners in it one by one.
    """
    if not os.path.isfile(config_file):
        raise errors.ConfigFileError(config_file, "File not found")

    configs = eval(open(config_file).read())
    if 'apps' not in configs:
        raise errors.ConfigFileError(config_file, "'apps' section not found")
        
    apps = configs['apps']
    for app_name in apps:
        app = apps[app_name]
        for app_mode in app:
            app_data = app[app_mode]
            app_class = app_data["app_class"]
            parts = app_class.split(".")
            if len(parts) > 1:
                app_pkg      = ".".join(parts[:-1])
                app_module   = __import__(app_pkg, {}, {}, [''])
                app_class    = getattr(app_module, parts[-1])
            else:
                app_class    = eval(parts[-1])

            logging.debug("Creating App Factory: " + str(app_class))
            app_factory = app_class(apns_daemon.reactor, app_name, app_mode,
                                    apns_daemon, **app_data)
            apns_daemon.registerApp(app_name, app_mode, app_factory)

