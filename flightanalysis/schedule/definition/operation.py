
from numbers import Number
from flightanalysis.base.collection import Collection
from uuid import uuid1
from ast import literal_eval


class Opp:
    __array_priority__ = 15.0   # this is a quirk of numpy so the __r*__ methods here take priority
    def __init__(self, name=None):
        self.name=str(uuid1()) if name is None else name
    
    def __getattr__(self, name):
        if name == "name":
            self.name = uuid1() 
            return self.name

    def __str__(self):
        return self.name 

    def __call__(self, coll):
        return self.value

    def get_vf(self, arg):
        if isinstance(arg, Opp):
            return arg
        elif isinstance(arg, Number):
            return lambda mps: arg

    def __abs__(self):
        return FunOpp(self, "abs")

    def __add__(self, other):
        return MathOpp(self, other, "+")

    def __radd__(self, other):
        return MathOpp(other, self, "+")

    def __mul__(self, other):
        return MathOpp(self, other, "*")

    def __rmul__(self, other):
        return MathOpp(other, self, "*")

    def __sub__(self, other):
        return MathOpp(self, other, "-")

    def __rsub__(self, other):
        return MathOpp(other, self, "-")

    def __div__(self, other):
        return MathOpp(self, other, "/")

    def __rdiv__(self, other):
        return MathOpp(other, self, "/")

    def __truediv__(self, other):
        return MathOpp(self, other, "/")

    def __rtruediv__(self, other):
        return MathOpp(other, self, "/")

    def __abs__(self):
        return FunOpp(self, "abs")


    @staticmethod
    def parse(inp, coll:Collection, name=None):
        """Parse a an Operation from a string"""
        for test in [
            lambda inp, mps : FunOpp.parse(inp, coll, name),
            lambda inp, mps : MathOpp.parse(inp, coll, name),
            lambda inp, mps : ItemOpp.parse(inp, coll, name),
            lambda inp, mps : float(inp),
            lambda inp, mps : literal_eval(inp)
        ]: 
            try: 
                return test(inp.strip(" "), coll)
            except ValueError:
                continue
        else:
            return coll[inp]


class MathOpp(Opp):
    """This class facilitates various ManParm opperations and their serialisation"""
    opps = ["+", "-", "*", "/"]
    def __init__(self, a, b, opp:str, name:str=None):
        assert opp in MathOpp.opps
        self.a = a
        self.b = b
        self.opp = opp
        super().__init__(name)

    def __call__(self, mps):
        if self.opp == "+":
            return self.get_vf(self.a)(mps) + self.get_vf(self.b)(mps)
        elif self.opp == "-":
            return self.get_vf(self.a)(mps) - self.get_vf(self.b)(mps)
        elif self.opp == "*":
            return self.get_vf(self.a)(mps) * self.get_vf(self.b)(mps)
        elif self.opp == "/":
            return self.get_vf(self.a)(mps) / self.get_vf(self.b)(mps)

    def __str__(self):
        return f"({str(self.a)}{self.opp}{str(self.b)})"

    @staticmethod
    def parse(inp:str, coll: Collection, name:str=None):
        if inp[0] == "(" and inp[-1] == ")":
            bcount = 0
            for i, l in enumerate(inp):
                bcount += 1 if l=="(" else 0
                bcount -=1 if l==")" else 0
            
                if bcount == 1 and l in MathOpp.opps:
                    return MathOpp(
                        coll.VType.parse(inp[1:i], coll),
                        coll.VType.parse(inp[i+1:-1], coll),
                        l,
                        name
                    )
                    
        raise ValueError(f"cannot read an MathOpp from the outside of {inp}")



class FunOpp(Opp):
    """This class facilitates various functions that operate on Values and their serialisation"""
    funs = ["abs"]
    def __init__(self, a, opp: str, name: str=None):
        assert opp in FunOpp.funs
        self.a = a
        self.opp = opp
        super().__init__(name)

    def __call__(self, mps):
        return {
            'abs': abs(self.get_vf(self.a)(mps))
        }[self.opp]
    
    def __str__(self):
        return f"{self.opp}({str(self.a)})"

    @staticmethod 
    def parse(inp: str, coll: Collection, name=None):
        for fun in FunOpp.funs:
            if len(fun) >= len(inp) - 2:
                continue
            if fun == inp[:len(fun)]:
                return FunOpp(
                    coll.VType.parse(inp[len(fun)+1:-1], coll), 
                    fun,
                    name
                )
        raise ValueError(f"cannot read a FunOpp from the outside of {inp}")


class ItemOpp(Opp):
    """This class creates an Operation that returns a single item from a combination ManParm"""
    def __init__(self, a, item:int, name:str=None): 
        self.a = a
        self.item = item
        super().__init__(name)
    
    def __call__(self, mps):
        return self.a.valuefunc(self.item)(mps)
    
    def __str__(self):
        return f"{self.a.name}[{self.item}]"

    @staticmethod
    def parse(inp: str, coll: Collection, name:str=None):
        contents = inp.split("[")
        if not len(contents) == 2:
            raise ValueError
        return ItemOpp(
            coll.VType.parse(contents[0], coll), 
            int(contents[1][:-1]), 
            name
        )

    def __abs__(self):
        return FunOpp(self, "abs")

