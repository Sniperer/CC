import random
import sys
import copy
from typing import List, Dict, Set, Tuple

type_to_num : Dict[str,int] = {
    "O-":0,
    "O+":1,
    "A-":2,
    "A+":3,
    "B-":4,
    "B+":5,
    "AB-":6,
    "AB+":7
}

# Encode type of blood to the code we design in Assignment 1
encoder : Dict[str, list] = {
    "A-" : [1,0,0],
    "A+" : [1,0,1],
    "AB-": [1,1,0],
    "AB+": [1,1,1],
    "B-" : [0,1,0],
    "B+" : [0,1,1],
    "O-" : [0,0,0],
    "O+" : [0,0,1]
}

class Alice:
    def __init__(self, x:list):
        self.x = x
        self.y = [0,0,0]
        self.z = [0,0,0]
        self.e = 0
        self.d = 0
        self.u = 0
        self.v = 0
        self.w = 0
        
        
class Bob:
    def __init__(self, y:list):
        self.x = [0,0,0]
        self.y = y
        self.z = [0,0,0]
        self.e = 0
        self.d = 0
        self.u = 0
        self.v = 0
        self.w = 0

class Dealer:
    def __init__(self):
        self.genR()

    def genR(self) -> None:
        # Generate tuple of random u,v,w, s.t. w = uv. CNT is used as a hook, once it's equal to 2 regenerate a random tuple like above.
        self.u = (random.randint(0,1), random.randint(0,1))
        self.v = (random.randint(0,1), random.randint(0,1))
        u = self.u[0]^self.u[1]
        v = self.v[0]^self.v[1]
        w = random.randint(0,1)
        self.w = (w, (u&v)^w)
        self.cnt = 0

    def randomA(self) -> tuple:
        # A can get his random share from Trust Third party by call randomA
        if self.cnt == 2:
            self.genR();
        self.cnt += 1
        return (self.u[0], self.v[0], self.w[0])
        
    def randomB(self) -> tuple:
        # B can get his random share from Trust Third Party by call randomB
        if self.cnt == 2:
            self.genR();
        self.cnt += 1
        return (self.u[1], self.v[1], self.w[1])

class Circuit:
    def __init__(self, A:Alice, B:Bob, D:Dealer):
        self.A = A
        self.B = B
        self.D = D
        
    def share(self) -> None:
        # A gives share of X to B
        # B gives share of Y to A
        x = self.A.x
        y = self.B.y
        self.B.x = [random.randint(0,1) for _ in x]
        self.A.x = [self.B.x[i]^self.A.x[i] for i in range(len(x))]
        self.A.y = [random.randint(0,1) for _ in y]
        self.B.y = [self.A.y[i]^self.B.y[i] for i in range(len(y))]

    def Open(self, valuex:str) -> None:
        # Open the random we use in AND gate
        # A.valuex ^= B.valuex
        # B.valuex = A.valuex
        exec(f"self.A.{valuex} ^= self.B.{valuex}")
        exec(f"self.B.{valuex} = copy.deepcopy(self.A.{valuex})")

    def OpenTo(self, valuex:str) -> None:
        # Give A the share of B of the final result
        exec(f"self.A.{valuex} ^= self.B.{valuex}")        
        
    def XorConstant(self, idx:int, valuex:str, const:int) -> None:
        # Using the mechanism of Python, it can unfold code in exec call.
        # self.A.valuex[idx] ^= const
        exec(f"self.A.{valuex}[idx] ^= const")

    def Xor(self, idx:int, valuex:str, valuey:str, resultname:str) -> None:
        # Using the mechanism of Python, it can unfold code in exec call.
        # A.resultname = A.valuey ^ A.valuex[idx]
        # B.resultname = B.valuey ^ B.valuex[idx]
        # valuex is list, valuey is int
        exec(f"self.A.{resultname} = self.A.{valuey}^self.A.{valuex}[idx]")
        exec(f"self.B.{resultname} = self.B.{valuey}^self.B.{valuex}[idx]")

    def AndConstant(self, idx:int, valuex:str, const:int) -> None:
        # Using the mechanism of Python, it can unfold code in exec call.
        # self.A.valuex[idx] &= const
        # self.B.valuex[idx] &= const
        exec(f"self.A.{valuex}[idx] &= const")
        exec(f"self.B.{valuex}[idx] &= const")
        
    def And(self, idx:int) -> None:
        # And gate of two wires, z[idx] = x[idx]^y[idx]
        self.A.u,self.A.v,self.A.w = self.D.randomA()
        self.B.u,self.B.v,self.B.w = self.D.randomB()
        self.Xor(idx, "x", "u", "d")
        self.Xor(idx, "y", "v", "e")
        self.Open("d")
        self.Open("e")
        self.AndConstant(idx, "x" , self.A.e)
        self.AndConstant(idx, "y" , self.A.d)
        tmp = self.A.e*self.A.d
        self.XorConstant(idx, "y", tmp)
        self.Xor(idx, "x", "w", "w")
        self.Xor(idx, "y", "w", "z[idx]")

    def func(self) -> int:
        # assigned value by BeDoza Circuit with function in Assignment 1
        # share inputs
        self.share()
        # Part 1 of function included 1^((1^X_0)*Y_0), the result would be stored in z_0
        self.XorConstant(0, "x", 1)
        self.And(0)
        self.XorConstant(0, "z", 1)
        # Part 2 of function included 1^((1^X_1)*Y_1), the result would be stored in z_1
        self.XorConstant(1, "x", 1)
        self.And(1)
        self.XorConstant(1, "z", 1)
        # Part 3 of function included 1^((1^X_2)*Y_2), the result would be stored in z_2
        self.XorConstant(2, "x", 1)
        self.And(2)
        self.XorConstant(2, "z", 1)
        # To reuse our code, we give z_0 to x_0 and z_1 to y_0. Then we can call AND function to calculate z_0*z_1
        self.A.x[0] = self.A.z[0]
        self.A.y[0] = self.A.z[1]
        self.B.x[0] = self.B.z[0]
        self.B.y[0] = self.B.z[1]
        self.And(0)
        # Same as above. The result is z_0*z_1*z_2 and would be stored in z_0
        self.A.x[0] = self.A.z[0]
        self.A.y[0] = self.A.z[2]
        self.B.x[0] = self.B.z[0]
        self.B.y[0] = self.B.z[2]
        self.And(0)
        # B gives his share to A, then z_0 of A would be the answer
        self.OpenTo("z[0]")
        return self.A.z[0]
    
def func(x:str, y:str) -> int:
    # Given the input which is blood type, we use X as the input of Alice and Y as the input of Bob, then initialize the dealer. And use the circuit we design to decide whether Alice can receive Bob's blood or not.
    A = Alice(copy.deepcopy(encoder[x]))
    B = Bob(copy.deepcopy(encoder[y]))
    D = Dealer()
    C = Circuit(A,B,D)
    return C.func()
    
def test(func) -> None:
    blood_type : Set[str] = {"O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"}
    correct_pair : Set[Tuple[str, str]] = {
        ("O-", "O-"),
        ("O+", "O-"),
        ("O+", "O+"),
        ("A-", "O-"),
        ("A-", "A-"),
        ("A+", "O-"),
        ("A+", "O+"),
        ("A+", "A-"),
        ("A+", "A+"),
        ("B-", "O-"),
        ("B-", "B-"),
        ("B+", "O-"),
        ("B+", "O+"),
        ("B+", "B-"),
        ("B+", "B+"),
        ("AB-", "O-"),
        ("AB-", "A-"),
        ("AB-", "B-"),
        ("AB-", "AB-"),
        ("AB+", "O-"),
        ("AB+", "O+"),
        ("AB+", "A-"),
        ("AB+", "A+"),
        ("AB+", "B-"),
        ("AB+", "B+"),
        ("AB+", "AB-"),
        ("AB+", "AB+")
    }
    cnt: int = 0
    pass_cnt: int = 0
    for it in blood_type:
        for jt in blood_type:
            cnt = cnt + 1
            if func(it, jt) == ((it, jt) in correct_pair):
                pass_cnt += 1
                continue
            else:
                print(f"failed test in recipient {it} and donor {jt}")
    print(f"completed, passed:{pass_cnt}, total:{cnt}")
        
if __name__ == "__main__":
    test(func)

   
