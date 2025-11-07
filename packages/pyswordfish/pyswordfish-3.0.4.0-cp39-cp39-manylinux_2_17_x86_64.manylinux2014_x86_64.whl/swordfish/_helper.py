from typing import TypeVar, Generic, get_args


T = TypeVar('T')


class _ParamAlias:
    name: str


class Alias(Generic[T]):
    def __class_getitem__(cls, item):
        name = get_args(item)[0]
        return type(name, (_ParamAlias,), {'name': name})


class Config(dict):
    def __init__(self, data: dict = None):
        super().__init__()
        for key in dir(self.__class__):
            if not key.startswith('__') and not key.startswith('_') and not callable(getattr(self.__class__, key)):
                self[key] = getattr(self.__class__, key)
        if data is not None:
            for k, v in data.items():
                self._update(k, v)

    def __setitem__(self, key, value):
        self.__dict__[key] = value
        return super().__setitem__(key, value)

    def __setattr__(self, name, value):
        self._update(name, value)

    def __getattr__(self, name):
        return self._get(name)

    def __delattr__(self, name):
        self._del(name)

    def _update(self, name, value):
        self.__dict__[name] = value
        self[name] = value

    def _get(self, name):
        try:
            return self.__dict__[name]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def _del(self, name):
        if name in type(self).__dict__:
            self._update(name, type(self).__dict__[name])
        else:
            if name in self.__dict__:
                del self.__dict__[name]
            if name in self:
                del self[name]
