import json
from config import Config

with open('cfg/config') as f:
    config = Config(json.loads(f.read())['settings'])



cmds = {}

class Lict(list):
    def __init__(self, l, keys=[], const=False):
        if type(l).__name__ == 'dict':
            super().__init__(list(l.values()))
        else:
            super().__init__(l)
        
        self._keys = []
        self.const = const
        
        if type(l).__name__ == 'dict':
            for i in l:
                self._keys.append(i)
        else:
            for i in keys:
                self._keys.append(i)
                
        for i in self._keys:
            setattr(self, i, self.__getitem__(i))

    def __setitem__(self, a, b=None):            
        if type(a).__name__ == 'str' and not self.const:
            if a not in self._keys:
                self._keys.append(a)
                self.append(b)
            else:
                super().__setitem__(self._keys.index(a), b)
        elif type(a).__name__ == 'int':
            super().__setitem__(a, b)
        else:
            raise TypeError("UserType indices must be integers or string, not {}".format(type(a).__name__))

    def __getitem__(self, a):
        if type(a).__name__ == 'str':
            if a in self._keys:
                return super().__getitem__(self._keys.index(a))
            else:
                raise KeyError(a)
        elif type(a).__name__ == 'int':
            return super().__getitem__(a)
            
    def pop(self, a):
        if a in self._keys:
            item = self.__getitem__(a)
            self.remove(item)
            self._keys.remove(a)
            return item
    
    def keys(self):
        return self._keys
        
    def values(self):
        return self
    
    def as_dict(self):
        d = {}
        
        for i in self._keys:
            d[i] = self.__getitem__(i)
        
        return d
    
    def as_list(self):
        return self
        
    def as_tuple(self):
        return tuple(self)
