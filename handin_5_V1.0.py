import random
from typing import List, Dict, Set, Tuple
import hashlib

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

def G(a: int, b: int, i: int) -> int:
    # PRF
    g = hashlib.sha256()
    # print(a, b, i)
    g.update(b.to_bytes((b.bit_length() + 7) // 8, byteorder='big'))
    g.update(a.to_bytes((a.bit_length() + 7) // 8, byteorder='big'))
    g.update(i.to_bytes((i.bit_length() + 7) // 8, byteorder='big'))
    hashed_int = int(g.hexdigest(), 16)
    return hashed_int


class Generator:
    def __init__(self):
        self.T: int = 11 # number of wires, starts from 1.
        self.Ks: List[List[int]] = [[random.randint(
            0, (1 << 128) - 1), random.randint(0, (1 << 128) - 1)] for _ in range(self.T + 1)] # all the K values
        self.Ls: List[int] = [-1] * (self.T + 1) # all the l[i] 
        self.Rs: List[int] = [-1] * (self.T + 1) # all the r[i] 
        self.Cs: List[List[int]] = [[-1 for _ in range(4)] for _ in range(self.T + 1)]

    def genFun(self, i: int) -> None:  # i-th gate
        for a in (0, 1):
            for b in (0, 1):
                k = self.Ks[i][1 ^ ((1 ^ a)*b)]
                k = k << 128
                k = k ^ G(self.Ks[self.Ls[i]][a], self.Ks[self.Rs[i]][b], i)
                self.Cs[i][a*2 + b] = k
        random.shuffle(self.Cs[i])

    def genAnd(self, i: int) -> None:  # i-th gate
        for a in (0, 1):
            for b in (0, 1):
                k = self.Ks[i][a*b]
                k = k << 128
                k = k ^ G(self.Ks[self.Ls[i]][a], self.Ks[self.Rs[i]][b], i)
                self.Cs[i][a*2 + b] = k
        random.shuffle(self.Cs[i])


    def compute(self) -> None:
        # hard-core the structure of circuit. the structure of circuit can be found in readme.
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
        return

    def Circuit(self, A: int, B: int, C: int) -> Tuple[Tuple[List[int], List[int], List[List[int]]], List[int]]:
        # return the F (include L[i], R[i], and all C[i][j]), and Y
        Y: List[int] = (self.Ks[4][A], self.Ks[5][B], self.Ks[6][C])
        return (self.Ls, self.Rs, self.Cs), Y

    def De(self) -> List[int]:
        # return the d for decryption
        return self.Ks[11]


def gen_F_and_Y(A: int, B: int, C: int) -> Tuple[Tuple[List[int], List[int], List[List[int]]], List[int]]:
    g = Generator()
    g.compute()
    return g.Circuit(A, B, C)

class Evaluator:
    def __init__(self, X: Tuple[int, int, int], F: Tuple[list, list, List[list]], Y: Tuple[int, int, int]):
        self.F = F
        self.K = [-1] * 12
        self.K[1] = X[0]
        self.K[2] = X[1]
        self.K[3] = X[2]
        self.K[4] = Y[0]
        self.K[5] = Y[1]
        self.K[6] = Y[2]
        return

    def ev(self, i): # compute the output of the i-th gate. Inputs of i-th gate should be already computed and store in K
        C = self.F[2][i]
        # print(f"i:{i}, value: {C}, ev")
        for c in C:
            # print(f"i;{i}, l:{self.K[self.F[0][i]]}, r:{self.K[self.F[1][i]]}")
            tmp = c ^ G(self.K[self.F[0][i]], self.K[self.F[1][i]], i)
            #print(f"tmp:{tmp}")
            if ((tmp >> 128) << 128) == tmp:
                self.K[i] = (tmp >> 128)
                return
        assert 0, "NO 0^k value in Evaluator.ev()"

    def Evulate(self):
        # comppute and return the output of the GC
        for i in range(7, 12):  # all non-input gate
            self.ev(i)
        return self.K[11]


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
    
class Alice:
    def __init__(self, A, B, C, e):
        self.A = A
        self.B = B
        self.C = C
        self.e = e
        self.sec_key:List[int] = [random.randint(2, self.e.p - 2) for _ in range(3)]
        self.public_key:List[Tuple[int,int]] = [self.e.gen(sk) for sk in self.sec_key]
        # self.okays is all keys that Alice generate. Not only the O-keys. 
        self.okeys:List[List[Tuple[int,int]]] = [[self.e.Ogen(random.randint(2, self.e.p - 2)), self.e.Ogen(random.randint(2, self.e.p - 2))] for _ in range(3)]
        self.okeys[0][A] = self.public_key[0]
        self.okeys[1][B] = self.public_key[1]
        self.okeys[2][C] = self.public_key[2]
        
    # Send all keys to Bob
    def choose(self) -> List[List[Tuple[int, int]]]:
        return self.okeys

    # Retrieve result from message
    def retrieve(self, m:List[List[Tuple[int,int]]]) -> None:
        self.X = [self.e.dec(m[0][self.A], self.sec_key[0]),
                  self.e.dec(m[1][self.B], self.sec_key[1]),
                  self.e.dec(m[2][self.C], self.sec_key[2])]

    def evaluate_decrypt(self, F, Y, d) -> int:
        self.ev = Evaluator(self.X, F, Y)
        Z = self.ev.Evulate()
        if Z == d[0]:
            return 0
        if Z == d[1]:
            return 1
        return -1
    
class Bob:
    def __init__(self, A, B, C, e):
        self.A = A
        self.B = B
        self.C = C
        self.e = e
        self.g = Generator()
        self.g.compute()
        # self.candidates is the e in protocol 
        self.candidates = [self.g.Ks[1],self.g.Ks[2],self.g.Ks[3]]

    # Transfer messages to Alice
    def transfer(self, keys:List[List[Tuple[int, int]]]) -> List[List[Tuple[int, int]]]:
        m = []
        for j in range(3):
            m.append([self.e.enc(random.randint(2, self.e.p - 2), self.candidates[j][i], keys[j][i]) for i in range(2)]) 
        return m

    def send_F_Y_d(self):
        F, Y = self.g.Circuit(self.A, self.B, self.C)
        return F, Y, self.g.De() 

def func(x:str, y:str) -> int:
    print(f"blood type of receive:{x}blood type of donor:{y}")
    e = EL(258) # note that the input value should bigger than the number of bits of the message we send in OT
    X = encoder[x]
    Y = encoder[y]
    A = Alice(X[0], X[1], X[2], e)
    B = Bob(Y[0], Y[1], Y[2], e)
    m1 = A.choose()
    m2 = B.transfer(m1)
    A.retrieve(m2)
    F, Y, d = B.send_F_Y_d()
    return A.evaluate_decrypt(F, Y, d)

    
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
                print("passed!")
                pass_cnt += 1
                continue
            else:
                print(f"failed test in recipient {it} and donor {jt}")
    print(f"completed, passed:{pass_cnt}, total:{cnt}")
    
if __name__ == "__main__":
    test(func)
    
