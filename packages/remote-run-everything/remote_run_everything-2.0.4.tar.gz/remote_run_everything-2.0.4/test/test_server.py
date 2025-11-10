from remote_run_everything.deploy.by_http_server import ByHttpServer
import cherrypy, os
from cherrypy.process.plugins import Daemonizer
import time





def cherry():
    cherrypy.config.update({
        "server.socket_port": 9900,
    })
    if os.name != "nt":
        d = Daemonizer(cherrypy.engine)
        d.subscribe()

    cherrypy.quickstart(ByHttpServer(), "/deploy")


if __name__ == '__main__':
    cherry()
