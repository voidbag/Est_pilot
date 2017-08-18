from collections import deque
from symbol import Symbol
import math
import sys

class Terminal(Symbol):
    def __init__(self, name):
        Symbol.__init__(self)
        self.is_terminal = True
        self.name = name

    def fill_children_list(self, tokens):
        return

    def compute(self, var_dict, priv = None):
        return None

class D(Symbol):
    is_variable = False
    def __init__(self):
        Symbol.__init__(self)

        self.name = '<D>'
        self.is_terminal = False

    def fill_children_list(self, tokens):
        if len(tokens) <= 0:
            print('err!!')
            sys.exit(0) #throw parsing error
            return

        token = tokens.popleft()

        try: #if symbol is number
            sym = float(token)
            self.is_variable = False
        except ValueError: #if symbol is variable..
            sym = str(token)
            self.is_variable = True

        terminal = Terminal(sym)
        self.children_list.append(terminal)

    def compute(self, var_dict, priv = None):
        sym = str(self.children_list[0].name)
        if self.is_variable:
            if sym in var_dict:
                return var_dict[sym]
            else:
                print('Unknown Symbol: ' + sym)
                sys.exit(0)
        else:
            return self.children_list[0].name #number
        
    
class Paren(Symbol):
    fn = None
    fn_dict = {} #TODO static variable must be checked...
    fn_dict['sin'] = math.sin
    fn_dict['cos'] = math.cos
    fn_dict['tan'] = math.tan
    fn_dict['asin'] = math.asin
    fn_dict['acos'] = math.acos
    fn_dict['atan'] = math.tan
    fn_dict['log'] = math.log

    def __init__(self):
        Symbol.__init__(self)
        self.name = '<paren>'
        self.is_terminal = False

    def fill_children_list(self, tokens):
        token = tokens[0]
        if token in Paren.fn_dict.keys():
            self.fn = token
            tokens.popleft() #pop function!!
            token = tokens[0]
            if token != '(':
                print (token)
                print('function must have parenthesis!!')
                sys.exit(0)

        if token == '(':
            expr = Expr()
            left = Terminal('(')
            right = Terminal(')')
            tokens.popleft()
            self.children_list.append(left)
            self.children_list.append(expr)

            left.parse(tokens)
            expr.parse(tokens)
            
            if len(tokens) == 0:
                print(') isn\'t closed!!')
                sys.exit(0)
            elif tokens[0] == ')':
                tokens.popleft()
            else:
                print('Unknown case!!')
                sys.exit(0)
            self.children_list.append(right)
            right.parse(tokens)

            return

        else:
            d = D()
            self.children_list.append(d)
            d.parse(tokens)

    def compute(self, var_dict, priv = None):
        if self.fn == None:
            if len(self.children_list) == 3:
                return self.children_list[1].compute(var_dict)
            else:
                return self.children_list[0].compute(var_dict)
        else:
            return Paren.fn_dict[self.fn](self.children_list[1].compute(var_dict))
          #TODO compute according to functions  


class Pow(Symbol):
    def __init__(self):
        Symbol.__init__(self)

        self.name = '<pow>'
        self.is_terminal = False

    def fill_children_list(self, tokens):
        paren = Paren()
        pow_tail = Pow_tail()
        self.children_list.append(paren)
        self.children_list.append(pow_tail)
        paren.parse(tokens)
        pow_tail.parse(tokens)

    def compute(self, var_dict, priv = None):
        paren = self.children_list[0].compute(var_dict)
        pow_tail = self.children_list[1].compute(var_dict)
        if self.children_list[1].is_terminal:
            return paren
        
        return pow(paren, pow_tail) 

class Pow_tail(Symbol):
    def __init__(self):
        Symbol.__init__(self)

        self.name = '<pow-tail>'
        self.is_terminal = False
    
    def fill_children_list(self, tokens):
        if len(tokens) == 0 or tokens[0] != '^':
            self.is_terminal = True
            return

        terminal = Terminal(tokens.popleft())
        ppow = Pow()
        self.children_list.append(terminal)
        self.children_list.append(ppow)

        terminal.parse(tokens)
        ppow.parse(tokens)
    
    def compute(self, var_dict, priv = None):
        if self.is_terminal == False:
            return self.children_list[1].compute(var_dict)
        else:
            return None

class Term(Symbol):
    def __init__(self):
        Symbol.__init__(self)

        self.name = '<term>'
        self.is_terminal = False

    def fill_children_list(self, tokens):
        ppow = Pow()
        term_tail = Term_tail()
        self.children_list.append(ppow)
        self.children_list.append(term_tail)
        ppow.parse(tokens)
        term_tail.parse(tokens)
    
    def compute(self, var_dict, priv = None):
        ppow = self.children_list[0]
        term_tail = self.children_list[1]
        return term_tail.compute(var_dict, ppow.compute(var_dict))
       
class Term_tail(Symbol):
    def __init__(self):
        Symbol.__init__(self)

        self.name = '<term-tail>'
        self.is_terminal = False

    def fill_children_list(self, tokens):
        if len(tokens) == 0 or (tokens[0] != '*' and tokens[0] != '/'):
            self.is_terminal = True
            return
       
        terminal = Terminal(tokens.popleft())
        ppow = Pow()
        term_tail = Term_tail()
        
        self.children_list.append(terminal)
        self.children_list.append(ppow)
        self.children_list.append(term_tail)

        terminal.parse(tokens)
        ppow.parse(tokens)
        term_tail.parse(tokens)
 
    def compute(self, var_dict, priv = None):
        if self.is_terminal == True:
            return priv

        if priv == None:
           print('Term_tail must have priv argument filled!')
           sys.exit(0) #TODO throw exception

        op = self.children_list[0].name
        ppow = self.children_list[1]
        term_tail = self.children_list[2]
        val_pow = ppow.compute(var_dict)

        if op == '*':
            return term_tail.compute(var_dict, priv * val_pow)
        else:
            return term_tail.compute(var_dict, priv / val_pow)

class Expr(Symbol):
    def __init__(self):
        Symbol.__init__(self)

        self.is_terminal = False
        self.name = '<expr>'

    def fill_children_list(self, tokens):
        if len(tokens) == 0:
            self.is_terminal = True
            return

        term = Term()
        expr_tail = Expr_tail()
        
        self.children_list.append(term)
        self.children_list.append(expr_tail)
        
        term.parse(tokens)
        expr_tail.parse(tokens)
     
    def compute(self, var_dict, priv = None):
        if self.is_terminal == True:
            return None

        term = self.children_list[0]
        expr_tail = self.children_list[1]

        return expr_tail.compute(var_dict, term.compute(var_dict))


class Expr_tail(Symbol):
    def __init__(self):
        Symbol.__init__(self)

        self.is_terminal = False
        self.name = '<expr-tail>'

    def fill_children_list(self, tokens):
        if len(tokens) == 0 or (tokens[0] != '+' and tokens[0] != '-'):
                self.is_terminal = True
                return

        terminal = Terminal(tokens.popleft())
        term = Term()
        expr_tail = Expr_tail() 

        self.children_list.append(terminal)
        self.children_list.append(term)
        self.children_list.append(expr_tail)

        terminal.parse(tokens)
        term.parse(tokens)
        expr_tail.parse(tokens)

    def compute(self, var_dict, priv = None):
        if self.is_terminal == True:
            return priv

        if priv == None:
            print('Expr_tail must have priv argument filled!')
            sys.exit(0) #TODO throw exception

        op = self.children_list[0].name
        term = self.children_list[1]
        expr_tail = self.children_list[2]
        val_term = term.compute(var_dict)

        if op == '+':
            return expr_tail.compute(var_dict, priv + val_term)
        else: # op == '-'
            return expr_tail.compute(var_dict, priv - val_term) 

string  = '5 * 5 / 6 ^ 2 / 7'
string = '3 ^ 2 * 3 / 2 ^ 3'
string = string.split(' ')
root = Expr()
q = deque()
for element in string:
   q.append(element) 

root.parse(q)
root.walk(0)
print (root.compute({'x': 2, 'k' : 2, 'pi' : math.pi, 'e' : math.e}))


