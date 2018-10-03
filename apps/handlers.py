from datetime import datetime
import time
from uuid import uuid4
import logging
import functools
from google.appengine.api import users
import webapp2
import json
from webapp2_extras import jinja2, sessions

class BaseHandler(webapp2.RequestHandler):

    __UUID_SESSION_KEY = "user_uuid"

    def _dispatch_hook(self):
        pass

    @property
    def user_uuid(self):
        return self.session.get(self.__UUID_SESSION_KEY)

    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session()

    @webapp2.cached_property
    def jinja2(self):
        jinja2_obj = jinja2.get_jinja2(app=self.app)
        jinja2_obj.environment.filters['format_currency'] = self.format_currency
        return jinja2_obj

    def render_html_response(self, template, http_code=200, **context):
        rv = self.jinja2.render_template(template, **context)
        self.response.write(rv)
        self.response.status = http_code

    def render_json_response(self, http_code=200, **kwargs):
        self.response.write(json.dumps(kwargs))
        self.response.headers["Content-Type"] = "application/json"
        self.response.set_status(http_code, kwargs.get("message"))

    def head(self):
        pass
