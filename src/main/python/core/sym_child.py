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

    def compute(self, var_dict):
        return None

class D(Symbol):
    is_variable = False
    def __init__(self):
        Symbol.__init__(self)

        self.name = '<D>'
        self.is_terminal = False

    def fill_children_list(self, tokens):
        token = tokens.popleft()
        if len(tokens) <= 0:
            print('err!!')
            sys.exit(0) #throw parsing error
            return
        try: #if symbol is number
            sym = float(token)
            self.is_variable = False
        except ValueError: #if symbol is variable..
            sym = str(token)
            self.is_variable = True

        terminal = Terminal(sym)
        self.children_list.append(terminal)

    def compute(self, var_dict):
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
            token = tokens.popleft() #pop function!!
            if token != '(':
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

    def compute(self, var_dict):
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

    def compute(self, var_dict):
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
    
    def compute(self, var_dict):
        if self.is_terminal == False:
            return self.children_list[1].compute(var_dict)
        else:
            return None

class High(Symbol):
    def __init__(self):
        Symbol.__init__(self)

        self.name = '<high>'
        self.is_terminal = False

    def fill_children_list(self, tokens):
        ppow = Pow()
        high_tail = High_tail()
        self.children_list.append(ppow)
        self.children_list.append(high_tail)
        ppow.parse(tokens)
        high_tail.parse(tokens)
    
    def compute(self, var_dict):
        val_pow = self.children_list[0].compute(var_dict)
        high_tail = self.children_list[1]
        val_high_tail = high_tail.compute(var_dict)
        if self.children_list[1].is_terminal:
            return val_pow
        elif high_tail.children_list[0].name == '*':
            return val_pow * val_high_tail
        elif high_tail.children_list[0].name == '/':
            return val_pow / val_high_tail
        else:
            print('ERR') #TODO
            sys.exit(0)

class Term(Symbol):
    def __init__(self):
        Symbol.__init__(self)
        self.is_terminal = False
        self.name = '<term>'
    
    def fill_children_list(self, tokens):
        high = High()
        self.children_list.append(high)
        high.parse(tokens)
    def compute(var_dict):
        return self.children_list[0].compute(var_dict)


class High_tail(Symbol):
    def __init__(self):
        Symbol.__init__(self)

        self.name = '<high-tail>'
        self.is_terminal = False

    def fill_children_list(self, tokens):
        if len(tokens) == 0 or (tokens[0] != '*' and tokens[0] != '/'):
            self.is_terminal = True
            return
        
        terminal = Terminal(tokens.popleft())
        high = High()
        self.children_list.append(terminal)
        self.children_list.append(high)

        terminal.parse(tokens)
        high.parse(tokens)
 
    def compute(self, var_dict):
        if self.is_terminal == True:
            return None
        else:
            return self.children_list[1].compute(var_dict)

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
     
    def compute(self, var_dict):
        if self.is_terminal == True:
            return None

        val_term = self.children_list[0].compute(var_dict)
        expr_tail = self.children_list[1]
        val_expr_tail = expr_tail.compute(var_dict)

        if expr_tail.is_terminal == True:
            return val_term
        elif expr_tail.children_list[0].name == '+':
            return val_term + val_expr_tail
        elif expr_tail.children_list[0].name == '-':
            return val_term - val_expr_tail
        else:
            print('Err')
            sys.exit(0)


class Expr_tail(Symbol):
    def __init__(self):
        Symbol.__init__(self)

        self.is_terminal = False
        self.name = '<expr-tail>'

    def fill_children_list(self, tokens):
        if len(tokens) == 0 or (tokens[0] != '+' and tokens[0] == '-'):
                self.is_terminal = True
                return
        terminal = Terminal(tokens.popleft())
        expr = Expr()
        
        self.children_list.append(terminal)
        self.children_list.append(expr)

        terminal.parse(tokens)
        expr.parse(tokens)

    def compute(self, var_dict):
        if self.is_terminal == True:
            return None
        else:
            return self.children_list[1].compute(var_dict)


string  = '2 * ( 4 + 5 )'
string = string.split(' ')
root = Expr()
q = deque()
for element in string:
   q.append(element) 

root.parse(q)
root.walk(0)


