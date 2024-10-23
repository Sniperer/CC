### How to set parameters
Assume $r_i \leq 2^R$, p is secret integer and n is the number of integers in public key. Next we just estimate the upperbound of noise.

For an add operation of $m_1 + 2*\sum_{i \in S_1} r_i$ and $m_2 + 2*\sum_{j \in S_2} r_j$, the upperbound of noise would be $2\sum_{n} r_i+r_j \leq 2\sum_{n} 2^{R+1} \leq 2n2^{R+1}$.

For an multiplication of $m_1 + 2*\sum_{i \in S_1} r_i$ and $m_2 + 2*\sum_{j \in S_2} r_j$, the upperbound of noise would be $2 (m_1 \sum_{S_1} r_i + m_2 \sum_{S_2} r_j + \sum_{S_1} \sum_{S_2} r_i*r_j) \leq 2(2*n*2^{R} + n^2*2^{2*R}) $ .

### How to run
```shell
python3 handin_5_V1.0.py
```
All test sets are included in our code which can be found in function ```test```. The program will cost some minutes because we use secure parameter of 257 bits.

### Implement
We use encoding as follows.

| blood type | number |
| --- | --- |
| O- | 000 |
| O+ | 001 |
| A- | 100 |
| A+ | 101 |
| B- | 010 |
| B+ | 011 |
| AB- | 110 |
| AB+ | 111 |

The gates we use are FUNC and AND. Circuits are shown in attachment. FUNC gate is to compute 1^((1^x)*y).

