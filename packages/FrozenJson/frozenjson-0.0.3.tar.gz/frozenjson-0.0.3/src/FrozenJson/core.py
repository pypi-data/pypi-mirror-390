# FrozenJson_new.py
"""
使用属性表示法浏览类似JSON的对象的只读外观。
处理了关键字冲突的问题。
例如，JSON对象中有一个键是"class"，在Python中这是一个关键字，因此在FrozenJSON类中将其转换为"class_"以避免冲突。
"""
import collections
from collections import abc
import keyword

class FrozenJSON(object):
    def __new__(cls, arg):
        if isinstance(arg, collections.abc.Mapping):
            return super().__new__(cls)
        elif isinstance(arg, collections.abc.MutableSequence):
            return [cls(item) for item in arg]
        else:
            return arg

    def __init__(self, mapping: abc.Mapping):
        self._data = {}
        # 处理关键字冲突
        for key, value in mapping.items():
            if keyword.iskeyword(key):
                key += '_'
            self._data[key] = value

    def __getattr__(self, name):
        # 处理关键字冲突
        if keyword.iskeyword(name):
            name += '_'

        try:
            value = getattr(self._data, name)
        except AttributeError:
            pass

        try:
            value = self._data[name]
        except KeyError:
            raise AttributeError(f"No such attribute: {name}")
        
        return FrozenJSON(value)
    
    def __dir__(self):
        return sorted(self._data.keys())