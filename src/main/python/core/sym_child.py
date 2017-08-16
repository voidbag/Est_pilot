from collections import deque
from symbol import Symbol
import math
import sys

class Terminal(Symbol):
    def __init__(self, name):
        self.is_terminal = True
        self.name = name

    def fill_children_list(self, tokens):
        return

    def compute(self, var_dict):
        return None

class D(Symbol):
    is_variable = False
    def __init__(self):
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
        self.chilren_list.append(terminal)

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
    def __init__(self):
        self.name = '<paren>'
        self.is_terminal = False

    def fill_children_list(self, tokens):
        token = tokens[0]
        if token == 'sin' or token == 'cos' or token == 'tan' or \
            token == 'arcsin' or token == 'arccos' or token == 'arctan' or \
            token == 'log':
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
            self.chilren_list.append(left)
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
            chilren_list.append(d)
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


        

class Expr(Symbol):
    def Expr(self):
        self.name = '<expr>'
        self.is_terminal = False

    def fill_children_list(tokens):
        print('Do nothing') # not yet implemented...
