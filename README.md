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

