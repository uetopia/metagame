#!/usr/bin/env python

import endpoints
import webapp2
from webapp2 import Route

# Set the secret key for the session cookie
config = {
    'webapp2_extras.sessions': {
        'secret_key': 'SOMETHING_UNIQUE'
    }
}

routes = [
]

# URLS
from apps.metagame.api.urls import routes as api_routes
routes.extend(api_routes)

from apps.metagame.handlers.urls import routes as task_routes
routes.extend(task_routes)

app = webapp2.WSGIApplication(
    routes,
    debug=True,
    config=config
)



def main():
    app.run()

if __name__ == '__main__':
    main()
