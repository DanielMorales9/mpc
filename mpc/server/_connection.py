import json


class Connection(object):

    @staticmethod
    def unmarshall(data: bytes):
        buffer = data.decode('utf-8')
        app, method, arguments = buffer.split('#')
        kwargs = json.loads(arguments)
        return app, method, kwargs

    @staticmethod
    def marshall(app, method, **kwargs):
        arguments = json.dumps(kwargs)
        return f'{app}#{method}#{arguments}'.encode('utf-8')
