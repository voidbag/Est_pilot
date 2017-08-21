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

    def tostring(self):
        return str(self.name)

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
            self.vars[sym] = True

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

    def diff(self, var_dict, priv = None):
        if (self.contains(var_dict)):
            return '1'
        return '0'
class Derivative:
    @classmethod
    def diff_sin(cls, expr):
        return 'cos ( ' + expr + ' )'

    @classmethod
    def diff_cos(cls, expr):
        return '-1 * sin ( ' + expr + ' )'
    @classmethod
    def diff_tan(cls, expr):
        return '1 / cos ( ' + expr  + ' ) ^ 2'

    @classmethod
    def diff_asin(cls, expr):
        return '1 / ( 1 - ( ' + expr + ' ) ^ 2 ) ^ ( 1 / 2 )' #expr != +-1

    @classmethod
    def diff_acos(cls, expr):
        return '-1 / ( 1 - ( ' + expr + ' ) ^ 2 ) ^ ( 1 / 2 )' #expr != +-1

    @classmethod
    def diff_atan(cls, expr):
        return '1 / ( 1 - ( ' + expr + ' ) ^ 2 )' #expr != +-i

    @classmethod
    def diff_ln(cls, expr):
        return '1 / ' +  expr


class Paren(Symbol):
    fn_dict = {} #TODO static variable must be checked...
    fn_dict['sin'] = math.sin
    fn_dict['cos'] = math.cos
    fn_dict['tan'] = math.tan
    fn_dict['asin'] = math.asin
    fn_dict['acos'] = math.acos
    fn_dict['atan'] = math.tan
    fn_dict['ln'] = math.log
    diff_dict = {}
    diff_dict['sin'] = Derivative.diff_sin
    diff_dict['cos'] = Derivative.diff_cos
    diff_dict['tan'] = Derivative.diff_tan
    diff_dict['asin'] = Derivative.diff_asin
    diff_dict['acos'] = Derivative.diff_acos
    diff_dict['atan'] = Derivative.diff_atan
    diff_dict['ln'] = Derivative.diff_ln


    @classmethod
    def diff_sin(cls, expr):
        return 'cos ( ' + expr + ' )'

    @classmethod
    def diff_cos(cls, expr):
        return '-1 * sin ( ' + expr + ' )'
    @classmethod
    def diff_tan(cls, expr):
        return '1 / cos ( ' + expr  + ' ) ^ 2'
    
    @classmethod
    def diff_asin(cls, expr):
        return '1 / ( 1 - ( ' + expr + ' ) ^ 2 ) ^ ( 1 / 2 )' #expr != +-1

    @classmethod
    def diff_acos(cls, expr):
        return '-1 / ( 1 - ( ' + expr + ' ) ^ 2 ) ^ ( 1 / 2 )' #expr != +-1

    @classmethod
    def diff_atan(cls, expr):
        return '1 / ( 1 - ( ' + expr + ' ) ^ 2 )' #expr != +-i

    @classmethod
    def diff_ln(cls, expr):
        return '1 / ' +  expr

    def __init__(self):
        Symbol.__init__(self)
        self.name = '<paren>'
        self.is_terminal = False
        self.fn = None

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

    def diff(self, var_dict, priv = None):
        ret = None
        if self.fn == None:
            if len(self.children_list) == 1:
                d = self.children_list[0]
                ret = d.diff(var_dict)
            else:
                expr = self.children_list[1]
                ret = '( ' + expr.diff(var_dict) + ' )'
        else:
            expr = self.children_list[1]
            diff_fn = Paren.diff_dict[self.fn]
            ret = diff_fn(expr.tostring()) + ' * ' + expr.diff(var_dict) 
        return ret

    def tostring(self):
        ret = ''
        if self.fn != None:
            ret += self.fn

        for child in self.children_list:
            if len(ret) == 0:
                ret += child.tostring()
            else:
                ret += ' ' + child.tostring()
        return ret

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

    def diff (self, var_dict, priv = None):
        paren = self.children_list[0]
        pow_tail = self.children_list[1]

        return pow_tail.diff(var_dict, paren)

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

    def diff(self, var_dict, priv = None):
        base = priv #paren..

        if self.is_terminal:
            if base.contains(var_dict):
                return base.diff(var_dict)
            else:
                return '' #we need to check


        exp = self.children_list[1]
        ret = ''

        if base.contains(var_dict):
            if exp.contains(var_dict):
                'error: (x ^ x) isn\'t elementary function '
                sys.exit(0)
            else: #x^c
                # c * x ^ ( c -1 ) * x'
                if self.is_terminal == False:
                    inner = base.diff(var_dict)
                    str_base = base.tostring()
                    str_exp = exp.tostring()
                    ret = str_exp + ' * ' + str_base + ' ^ ' +\
                    '( ' + str_exp + ' - 1 ) * ' + inner

                else:
                    ret = base.diff(var_dict)
        else:
            if exp.contains(var_dict): #a^x
                #a ^ x * log(x) * x'
                #TODO check a...
                inner = exp.diff(var_dict)
                str_base = base.tostring()
                str_exp = exp.tostring()

                ret = str_base + ' ^ ' + str_exp  + \
                        ' * ln ( ' + str_base + ' ) * ' + inner
            else:
                ret = '0'

        return ret

    def tostring(self):
        ret = ''

        for child in self.children_list:
            if len(ret) == 0:
                ret += child.tostring()
            else:
                ret += ' ' + child.tostring()

        return ret


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

    def diff(self, var_dict, priv = None):
        ppow = self.children_list[0]
        term_tail = self.children_list[1]

        return term_tail.diff(var_dict, ppow)
       
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

    def diff(self, var_dict, priv = None):
        ppow = priv
        ret = ''
        if self.is_terminal:
            if ppow.contains(var_dict):
                ret = ppow.diff(var_dict)
            else:
                ret = ''

            return ret
        op = self.children_list[0].tostring()
        this_ppow = self.children_list[1]
        term_tail = self.children_list[2]
        str_ppow = ppow.tostring()
        str_this_ppow = this_ppow.tostring()
        if term_tail.is_terminal == False:
            str_this_ppow += term_tail.tostring()

        #TODO refactor the below code segment
        if op == '*':
            if ppow.contains(var_dict):
                if this_ppow.contains(var_dict) or term_tail.contains(var_dict):
                    ret = str_ppow + ' * ( ' +\
                            term_tail.diff(var_dict, this_ppow) + ' ) + ( ' +\
                            ppow.diff(var_dict) + ' ) * ' + str_this_ppow
                else:
                    ret = ppow.diff(var_dict) + ' * ' + str_this_ppow
            else:
                if this_ppow.contains(var_dict) or term_tail.contains(var_dict):
                    ret = str_ppow + ' * ( ' + \
                            term_tail.diff(var_dict, this_ppow) + ' )'
                    #print('str_ppow: ' + str_ppow)
                    #print('ppow: ' + this_ppow.tostring())
                else:
                    ret = ''
        else:
            if ppow.contains(var_dict):
                if this_ppow.contains(var_dict) or term_tail.contains(var_dict):
                    ret = str_ppow + ' / -1 * ( ' + str_this_ppow  +\
                            ' ) ^ 2 * ( ' + term_tail.diff(var_dict, this_ppow) +\
                                    ' ) + ( ' + ppow.diff(var_dict) + ' ) / ' +\
                                    str_this_ppow
                else:
                    ret = '( ' + ppow.diff(var_dict) + ' ) / ' + str_this_ppow
            else:
                if this_ppow.contains(var_dict) or term_tail.contains(var_dict):
                    ret = str_ppow + ' / -1 * ( ' + str_this_ppow + ' ) ^ 2 * ( ' +\
                    term_tail.diff(var_dict, this_ppow) + ' )'
                else:
                    ret = ''
        return ret

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

    def diff(self, var_dict, priv = None):
        term = self.children_list[0]
        expr_tail = self.children_list[1]
        return expr_tail.diff(var_dict, term)


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

    def diff(self, var_dict, priv = None):
        ret = ''
        term = priv
        if self.is_terminal:
            if term.contains(var_dict):
                return term.diff(var_dict)
            else:
                return '' #we need to check this

        op = self.children_list[0].tostring()
        this_term = self.children_list[1]
        expr_tail = self.children_list[2]

        if term.contains(var_dict):
            ret = term.diff(var_dict)
            if this_term.contains(var_dict) or expr_tail.contains(var_dict):
                ret += ' ' + op  + ' ' + expr_tail.diff(var_dict, this_term)
        else:
            ret = ''
            if this_term.contains(var_dict) or expr_tail.contains(var_dict):
                if op == '-':
                    ret = '-1 * '
                ret += expr_tail.diff(var_dict, this_term)
        return ret

string  = '5 * 5 / 6 ^ 2 / 7'
string = '3 ^ 2 * 3 / 2 ^ 3'
string = 'sin ( x )'
#string = '1 - x'

#string = 'x + 1'

#string = 'x ^ 2'
string = string.split(' ')
root = Expr()
q = deque()
for element in string:
   q.append(element) 

root.parse(q)
root.walk(0)
print (root.compute({'x': 2, 'y' : 2, 'pi' : math.pi, 'e' : math.e}))
print (root.tostring())

diff_dict = {'x': True}

print('derivative: ' + root.diff(diff_dict))


