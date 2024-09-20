import numpy as np
import random
import sys
from typing import List, Dict, Set, Tuple
import copy

# encode blood type to 3-digit numbers
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

# truth table used in handin 1
T: List[List[int]] = [
    [1,0,0,0,0,0,0,0],
    [1,1,0,0,0,0,0,0],
    [1,0,1,0,0,0,0,0],
    [1,1,1,1,0,0,0,0],
    [1,0,0,0,1,0,0,0],
    [1,1,0,0,1,1,0,0],
    [1,0,1,0,1,0,1,0],
    [1,1,1,1,1,1,1,1],
]
# 
class Dealer:
    def __init__(self):
        self.r:int = random.randint(0,7) 
        self.s:int = random.randint(0,7)
        self.Mb:List[List[int]] = np.random.randint(0,2,size=(8,8)).tolist()
        self.Ma:List[List[int]] = copy.deepcopy(self.Mb)
        for i in range(8):
            for j in range(8):
                self.Ma[i][j] ^= T[(i-self.r)%8][(j-self.s)%8]

class Alice:
    def __init__(self, x:int, r:int, M:List[List[int]]):
        self.u = (x + r)%8
        self.M = copy.deepcopy(M)
        
    def send(self) -> int:
        return self.u
    
    def receive(self,tmp:tuple) -> None:
        self.v, self.z = tmp
        
    def output(self) -> bool:
        return (bool)(self.M[self.u][self.v]^self.z)
        
    
class Bob:
    def __init__(self, y:int, s:int, M:List[List[int]]):
        self.v = (y + s)%8
        self.M = copy.deepcopy(M)
        
    def receive(self,u:int) -> int:
        self.u = u
        
    def send(self) -> tuple:
        return self.v, self.M[self.u][self.v] 

def run(xx:str, yy:str) -> bool:
    x:int = type_to_num[xx]
    y:int = type_to_num[yy]
    d:Dealer = Dealer()
    alice:Alice = Alice(x, d.r, d.Ma)
    bob:Bob = Bob(y, d.s, d.Mb)
    bob.receive(alice.send())
    alice.receive(bob.send())
    z:bool = alice.output()
    # print(z)
    return z

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
    print(f"completed, passed:{cnt}, total:{pass_cnt}")

if __name__ == "__main__":
    test(run)
