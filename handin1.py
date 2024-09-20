import sys
from typing import List, Dict, Set, Tuple

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

# truth table used in question 1
mp: List[List[int]] = [
    [1,0,0,0,0,0,0,0],
    [1,1,0,0,0,0,0,0],
    [1,0,1,0,0,0,0,0],
    [1,1,1,1,0,0,0,0],
    [1,0,0,0,1,0,0,0],
    [1,1,0,0,1,1,0,0],
    [1,0,1,0,1,0,1,0],
    [1,1,1,1,1,1,1,1],
]

# calc value by truth table
def truth_table(x: str, y: str) -> bool:
     return mp[type_to_num[x]][type_to_num[y]]

# calc value by boolean function
def boolean_func(x: str, y: str) -> bool:
    # x: abc
    a: bool = type_to_num[x] >> 2
    b: bool = (type_to_num[x] >> 1) & 1
    c: bool = type_to_num[x] & 1
    # y: def
    d: bool = type_to_num[y] >> 2
    e: bool = (type_to_num[y] >> 1) & 1
    f: bool = type_to_num[y] & 1
    return ((not d and not e and not f) or
            (c and not d and not e) or
            (b and not d and not f) or
            (a and not e and not f) or
            (b and c and not d) or
            (a and c and not e) or
            (a and b and not f) or
            (a and b and c))

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
    for it in blood_type:
        for jt in blood_type:
            if func(it, jt) == ((it, jt) in correct_pair):
                continue
            else:
                print(f"failed test in recipient {it} and donor {jt}")
    print("completed")
            
    
if __name__ == "__main__":
    test(truth_table)
    test(boolean_func)
