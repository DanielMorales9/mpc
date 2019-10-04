class EventHook(object):

    def __init__(self):
        self.__handlers = {}

    def subscribe(self, subscriber):
        name = subscriber.__class__.__name__
        if name in self.__handlers:
            raise AssertionError(f"{name} is already registered")
        self.__handlers[name] = {method.__name__: method for method in subscriber.get_methods()}

    def handle(self, app_name: str, method_name: str, **kwargs):
        return self.__handlers[app_name][method_name](**kwargs)
