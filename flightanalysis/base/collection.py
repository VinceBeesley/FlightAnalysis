from typing import Dict, List, Union, Any
import numpy as np
import pandas as pd


class Collection:
    VType = None
    uid = "uid"
    def __init__(self, data: Union[Dict[str,Any], List[Any]]=None):
        if data is None:
            data = {}
        self.data = data if isinstance(data, dict) else {getattr(d, self.__class__.uid): d for d in data}
        assert all(isinstance(v, self.__class__.VType) for v in self.data.values())
        assert all([hasattr(v, self.__class__.uid) for v in self.data.values()])

    def __getattr__(self, name):
        if name in self.data:
            return self.data[name]

    def __getitem__(self, key: Union[int, str]):
        if isinstance(key, int): 
            return list(self.data.values())[key]
        elif isinstance(key, str):
            return self.data[key]
        elif isinstance(key, self.__class__.VType):
            return self.data[getattr(key, self.__class__.uid)]

    def __iter__(self):
        for v in self.data.values():
            yield v

    def to_list(self):
        return list(self.data.values())
    
    def to_dicts(self) -> List[dict]:
        return [v.to_dict() for v in self.data]

    def to_dict(self) -> Dict[str, dict]:
        return {k: v.to_dict() for k, v in self.data.items()}

    @classmethod
    def from_dicts(cls, vals: List[dict]):
        return cls([cls.VType.from_dict(**v) for v in vals])    

    @classmethod
    def from_dict(cls, vals: Dict[str, dict]):
        return cls([cls.VType.from_dict(v) for v in vals.values()])
    
    def add(self, v):
        if v is None:
            return self
        elif isinstance(v, self.VType):
            self.data[getattr(v, self.uid)] = v
        elif isinstance(v, self.__class__):
            return self.__class__(dict(**self.data, **v.data))
        return v

    def next_free_name(self, prefix: str):
        i=0
        while f"{prefix}{i}" in self.data:
            i+=1
        else:
            return f"{prefix}{i}"

    def copy(self):
        return self.__class__([v.copy() for v in self])
    
    def __str__(self) -> str:
        return str(pd.Series({k: str(v) for k, v in self.data.items()}))
    
    def __repr__(self) -> str:
        contents = str(pd.Series({k: repr(v) for k, v in self.data.items()}))
        return f"{self.__class__.__name__}\n{contents}"
    
    def __len__(self) -> int:
        return len(self.data)