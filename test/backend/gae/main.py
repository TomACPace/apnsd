import logging, os, sys

def main():
    # create the WSGI handler for django 
    import django.core.handlers.wsgi
    application = django.core.handlers.wsgi.WSGIHandler()

    # run it
    from google.appengine.ext.webapp import util
    util.run_wsgi_app(application)

if __name__ == "__main__": main()

