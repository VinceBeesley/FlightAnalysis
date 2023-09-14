from typing import Dict, List, Union, Any, Self, TypeVar
import numpy as np
import pandas as pd

class Collection:
    VType = None

    uid = "uid"
    def __init__(self, data: Union[Dict, List]=None, check_types=True):
        
        self.data: dict[str] = {}
        if isinstance(data, dict):
            self.data = data
        elif isinstance(data, self.__class__):
            self.data = data.data
        elif data is None:
            pass
        else:
            self.data = {getattr(d, self.__class__.uid): d for d in data}

        assert all([hasattr(v, self.__class__.uid) for v in self.data.values()])
        if check_types:
            assert all(isinstance(v, self.__class__.VType) for v in self.data.values())

    def __getattr__(self, name):
        if name in self.data:
            return self.data[name]
        raise AttributeError(f"{name} not found in {self.__class__}")

    def __getitem__(self, key: Union[int, str]):
        if isinstance(key, int): 
            return list(self.data.values())[key]
        elif isinstance(key, slice):
            return self.__class__(list(self.data.values())[key])
        elif isinstance(key, str):
            return self.data[key]
        elif isinstance(key, self.__class__.VType):
            return self.data[getattr(key, self.__class__.uid)]
        raise ValueError(f"Invalid Key or Indexer {key}")

    def __iter__(self):
        for v in self.data.values():
            yield v

    def to_list(self):
        return list(self.data.values())
    
    def to_dicts(self) -> list[dict]:
        return [v.to_dict() for v in self.data.values()]

    def to_dict(self) -> Dict[str, dict]:
        return {k: v.to_dict() for k, v in self.data.items()}

    @classmethod
    def from_dicts(cls, vals: List[dict]) -> Self:
        return cls([cls.VType.from_dict(**v) for v in vals])    

    @classmethod
    def from_dict(cls, vals: Dict[str, dict]) -> Self:
        return cls([cls.VType.from_dict(v) for v in vals.values()])
    
    def add(self, v):
        if isinstance(v, self.VType):
            self.data[getattr(v, self.uid)] = v
        elif isinstance(v, self.__class__):
            self.data = dict(**self.data, **v.data)
        return v
    
    def concat(self, vs: list[Self]) -> Self:
        coll = self.__class__([])
        for v in vs:
            coll.add(v)
        return coll
    
    def add_start(self, v):
        if isinstance(v, self.VType):
            self.data.update({getattr(v, self.uid): v})
        elif isinstance(v, self.__class__):
            self.data = dict(**v.data, **self.data)
        return v
    
    def next_free_name(self, prefix: str):
        i=0
        while f"{prefix}{i}" in self.data:
            i+=1
        else:
            return f"{prefix}{i}"

    def copy(self, deep=True) -> Self:
        return self.__class__([v.copy() for v in self] if deep else self.data.copy())
    
    def __str__(self) -> str:
        return str(pd.Series({k: str(v) for k, v in self.data.items()}))
    
    def __repr__(self) -> str:
        
        return str(pd.Series({k: repr(v) for k, v in self.data.items()}))
    
    def __len__(self) -> int:
        return len(self.data)