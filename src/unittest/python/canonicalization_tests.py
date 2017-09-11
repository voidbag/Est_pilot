import unittest
from mockito import mock, verify
from core.symbol import *
from core.sym_child import *

class Canonicalization(unittest.TestCase):
    def make_parse_tree(self, in_str):
        in_str = in_str.split(' ')
        q = deque()

    def test_copy(self):
        self.assertEqual('<term>', '<term>')
    def test_mul(self):
        self.assertEqual(3,3) 
    def test_append(self):
        self.assertEqual(3,3)
    def test_pow(self):
       # expr = Expr()
        self.assertEqual(3, 3)
    '''
string  = '5 * 5 / 6 ^ 2 / 7'
string = '3 ^ 2 * 3 / 2 ^ 3'
#string = 'c / b * a'
string = '( a ^ x * b ) ^ ( 1 / x )'

#string = '1 - x'

#string = 'x + 1'

#string = 'x ^ 2'
string = string.split(' ')
root = Expr()
q = deque()
for element in string:
   q.append(element) 

root.parse(q)
root.sort()
#kroot.children_list[0].sort()
root.walk(0)
#sys.exit(0)

#print (root.compute({'x': 2, 'y' : 2, 'pi' : math.pi, 'e' : math.e}))
print (root.tostring())

diff_dict = {'b': True}

print('derivative: ' + root.diff(diff_dict))
copied = root.copy()
copied.walk(0)
print('copy: ' + copied.tostring())

string = '( a + b ) * ( a + b )'
root = Expr()
q = deque()
string = string.split(' ')
for element in string:
    q.append(element)
root.parse(q)
print ('=====input', root.tostring())
root.canonicalize()
print(root.tostring())


    '''
