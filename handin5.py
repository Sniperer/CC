import random
from typing import List, Dict, Set, Tuple
import hashlib

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

def millerRabin(n):
    if n < 3 or n % 2 == 0:
        return n == 2
    if n % 3 == 0:
        return n == 3
    u, t = n - 1, 0
    while u % 2 == 0:
        u = u // 2
        t = t + 1
    test_time = 8
    for i in range(test_time):
        a = random.randint(2, n - 2)
        v = pow(a, u, n)
        if v == 1:
            continue
        s = 0
        while s < t:
            if v == n - 1:
                break
            v = v * v % n
            s = s + 1
        if s == t:
            return False
    return True


class EL:
    # Initialize el gamal, 2^n - 1 < p < 2^n, p = 2q + 1, n is secure parameter
    def __init__(self, SecurityParameter:int):
        self.SecurityParameter:int = SecurityParameter
        n:int = self.SecurityParameter
        while 1:
            self.p:int = random.randint(1 << (n-1), 1 << n)
            if millerRabin(self.p) and millerRabin((self.p - 1)//2):
                break
        self.q:int = (self.p-1)//2

    # Return a public key given secret key d
    def gen(self, d:int) -> Tuple[int,int]:
        while 1:
            self.g = random.randint(2, self.p - 1)
            if pow(self.g, 2, self.p) != 1 and pow(self.g, self.q, self.p) != 1:
                break
        self.d = d
        return (self.g, pow(self.g, self.d, self.p))    

    # Oblivious generate a fake key
    def Ogen(self, r:int) -> Tuple[int, int]:
        return (self.g, pow(r, 2, self.p))

    # Encryption with randomness r and message m under public ky
    def enc(self, r:int, m:int, pk:Tuple[int,int]) -> Tuple[int, int]:
        g,h = pk[0], pk[1]
        return (pow(g,r,self.p), (pow(h,r,self.p)*m)%self.p)

    # Decryption with private key sk and cipher text c
    def dec(self, c:Tuple[int,int], sk:int) -> int:
        a = c[0]
        a = pow(a, sk, self.p)
        a = pow(a, self.p - 2, self.p)
        return (a*c[1])%self.p
    

class generator:
    def __init__(self):
        self.T = 11
        self.Ks = [[random.randint(0, (1 << 128) - 1), random.randint(0, (1 << 128) - 1)] for _ in range(self.T + 1)]        
        self.Ls = [-1] * (self.T + 1)
        self.Rs = [-1] * (self.T + 1)
        self.Cs = [[-1,-1,-1,-1]]*(self.T + 1)

    def G(a, b, i):
        g = hashlib.sha256()
        g.update(self.Ks[self.Ls[i]][a])
        g.update(self.Ks[self.Rs[i]][b])
        g.update(i)
        hash_hex = g.hexdigest()
        hashed_int = int(hashed_hex, 16)
        return hashed_int
        
    def genFun(i):
        for a in (0,1):
            for b in (0,1):
                k = self.Ks[i][1^((1^a)*b)]
                k = k << 128
                k = k^G(a, b, i)
                self.Cs[i][a*2 + b] = k
        random.shuffle(self.Cs[i])

    def genAnd(i):
        for a in (0,1):
            for b in (0,1):
                k = self.Ks[i][a*b]
                k = k << 128
                k = k^G(a,b,i)
                self.Cs[i][a*2+b] = k
        random.shuffle(self.Cs[i])
        
    def init(self):
        self.Ls[7] = 1
        self.Ls[8] = 2
        self.Ls[9] = 3
        self.Ls[10] = 7
        self.Ls[11] = 10
        self.Rs[7] = 4
        self.Rs[8] = 5
        self.Rs[9] = 6
        self.Rs[10] = 8
        self.Rs[11] = 9
        self.genFun(7)
        self.genFun(8)
        self.genFun(9)
        self.genAnd(10)
        self.genAnd(11)

    def Circuit(self, A, B, C):
        Y = (self.Ks[4][A], self.Ks[5][B], self.Ks[6][C])
        return (self.Ls, self.Rs, self.Cs), Y

    def De(self):
        return self.Ks[11]
    
class evaluator:
    def __init__(self, X:Tuple[int,int,int], F:Tuple[list, list, List[list]], Y:Tuple[int,int,int]):
        self.F = F
        self.K = [-1] * 11
        self.K[1] = X[0]
        self.K[2] = X[1]
        self.K[3] = X[2]
        self.K[4] = Y[0]
        self.K[5] = Y[1]
        self.K[6] = Y[2]

    def G(Ka, Kb, i):
        g = hashlib.sha256()
        g.update(Ka)
        g.update(Kb)
        g.update(i)
        hash_hex = g.hexdigest()
        hashed_int = int(hashed_hex, 16)
        return hashed_int
        
    def ev(self, i):
        C = self.F[2][i]
        for c in C:
            tmp = c^G(self.K[self.F[0][i]],self.K[self.F[1][i]],i)
            if (tmp >> 128) << 128 == tmp:
                self.K[i] = (tmp >> 128)
                return
        
    def Evulate(self):
        self.ev(7)
        self.ev(8)
        self.ev(9)
        self.ev(10)
        self.ev(11)
        return self.K[11]

class Alice:
    def __init__(self, bloodtype, e):
        self.bloodtype = bloodtype
        self.e = e
        self.sec_key = random.randint(2, self.e.p - 2)
        self.public_key = self.e.gen(self.sec_key)        
        self.okeys = [self.e.Ogen(random.randint(2, self.e.p - 2)) for _ in range(2)]
        self.okeys[bloodtype] = self.public_key

    # Send all keys to Bob
    def choose(self) -> List[Tuple[int, int]]:
        return self.okeys

    # Retrieve result from message
    def retrieve(self, m:List[Tuple[int,int]]) -> int:
        return self.e.dec(m[self.bloodtype], self.sec_key)
    
class Bob:
    def __init__(self, bloodtype, e):
        self.bloodtype = bloodtype
        self.candidates = [T[i][self.bloodtype] for i in range(2)]
        self.e = e

    # Transfer messages to Alice
    def transfer(self, keys:List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        return [self.e.enc(random.randint(2, self.e.p - 2), self.candidates[i],keys[i]) for i in range(len(keys))]

def func(x:str, y:str) -> int:
    e = EL(128)
    A = Alice(type_to_num[x], e)
    B = Bob(type_to_num[y], e)
    m1 = A.choose()
    m2 = B.transfer(m1)
    return A.retrieve(m2)

    
def test(func) -> None:
    blood_type : List[str] = ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"]
    correct_pair : List[Tuple[str, str]] = [
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
    ]
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
    
