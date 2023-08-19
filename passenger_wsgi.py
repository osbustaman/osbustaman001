import jab.wsgi

SCRIPT_NAME = '/home/wwcontrol/public_html/jab/jab'


class PassengerPathInfoFix(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_responce):
        from urllib.parse import unquote
        environ['SCRIPT_NAME'] = SCRIPT_NAME

        request_uri = unquote(environ['REQUEST_URI'])
        script_name = unquote(environ.get('SCRIPT_NAME', ''))
        offset = request_uri.startswith(script_name) and len(environ['SCRIPT_NAME']) or 0
        environ['PATH_INFO'] = request_uri[offset].split('?', 1)[0]

        print(environ)

        return self.app(environ, start_responce)


application = jab.wsgi.application
application = PassengerPathInfoFix(application)
