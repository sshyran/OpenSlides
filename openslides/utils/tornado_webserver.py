#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    openslides.utils.tornado_webserver
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2011-2013 by the OpenSlides team, see AUTHORS.
    :license: GNU GPL, see LICENSE for more details.
"""

import posixpath
from urllib import unquote

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import FallbackHandler, Application, StaticFileHandler
from tornado.wsgi import WSGIContainer
from tornado.options import options, define, parse_command_line

from django.core.handlers.wsgi import WSGIHandler as Django_WSGIHandler
from django.conf import settings


class StaticFileHandler(StaticFileHandler):
    """Handels static data by using the django finders."""

    def initialize(self):
        """Overwrite some attributes."""
        self.root = ''
        self.default_filename = None

    def get(self, path, include_body=True):
        from django.contrib.staticfiles import finders
        normalized_path = posixpath.normpath(unquote(path)).lstrip('/')
        absolute_path = finders.find(normalized_path)
        return super(StaticFileHandler, self).get(absolute_path, include_body)


def run_tornado(addr, port):
    parse_command_line()
    app = WSGIContainer(Django_WSGIHandler())
    tornado_app = Application([
        (r"%s(.*)" % settings.STATIC_URL, StaticFileHandler),
        ('.*', FallbackHandler, dict(fallback=app))])

    server = HTTPServer(tornado_app)
    server.listen(port=port,
                  address=addr)
    IOLoop.instance().start()