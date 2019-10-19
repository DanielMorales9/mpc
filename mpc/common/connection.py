import json


def unmarshall_request(data: bytes):
    buffer = data.decode('utf-8')
    kwargs = json.loads(buffer)
    return kwargs['app'], kwargs['method'], kwargs['kwargs']


def unmarshall_response(data: bytes):
    buffer = data.decode('utf-8')
    kwargs = json.loads(buffer)
    return kwargs


def marshall_request(app, method, **kwargs):
    req = {'app': app, 'method': method, 'kwargs': kwargs}
    arguments = json.dumps(req)
    return arguments.encode('utf-8')


def marshall_response(**kwargs):
    arguments = json.dumps(kwargs)
    return arguments.encode('utf-8')
