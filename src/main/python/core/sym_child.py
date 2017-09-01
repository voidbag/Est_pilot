from collections import deque
from symbol import Symbol
import math
import sys
from heapq import heappush, heappop

#This class make term or expr object have tail
class Commutable(Symbol):
    def __init__(self, name, parent = None):
        Symbol.__init__(self, parent = None)
        self.tail = None

    def copy(self, parent):
        #initiate the term or expr object
        instance = self.do_copy()
        instance.name = self.name
        instance.is_terminal = self.is_terminal
        instance.parent = parent
        instance.children_list.append(self.children_list[0].copy(instance))

        #initiate the term_tail or expr_tail object
        cur = self.children_list[1]
        parent = instance

        while True:
            clone = cur.do_copy()
            clone.name = cur.name #shoud be immutable variable..
            clone.is_terminal = cur.is_terminal
            clone.parent = parent

            if cur.is_terminal == True:
                break
           
            #operator
            clone.children_list.append(cur.children_list[0].copy(clone))
            #pow or term object
            clone.children_list.append(cur.children_list[1].copy(clone))
            cur = cur.children_list[2] #next pointer...
            parent = clone
       
        instance.tail = clone
        return instance


class Terminal(Symbol):
    def __init__(self, name, parent = None):
        Symbol.__init__(self, parent = None)
        self.is_terminal = True
        self.name = name

    def fill_children_list(self, tokens):
        return

    def compute(self, var_dict = {'pi' : math.pi, 'e' : math.e}, priv = None):
        return None

    def tostring(self):
        return str(self.name)

    def do_copy(self):
        return Terminal(self.name)
    
    def canonicalize(self, parent = None, skip = 0):
        return self

class D(Symbol):
    is_variable = False
    def __init__(self, parent = None):
        Symbol.__init__(self, parent = None)

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

        terminal = Terminal(sym, self)
        self.children_list.append(terminal)

    def compute(self, var_dict = {'pi' : math.pi, 'e' : math.e}, priv = None):
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

    def do_copy(self):
        instance = D()
        instance.is_variable = self.is_variable
        return instance

    def delete(self):
        paren = self.parent
        paren.delete()

    def canonicalize(self, parent = None, skip = 0):
        return self

    def is_num(self):
        terminal = self.children_list[0]
        return type(terminal) == float or type(terminal) == int

    def is_int(self):
        terminal = self.children_list[0]
        return type(terminal.name) == int

    def get_char(self):
        return self.children_list[0].name

    def set_char(self, val):
        self.children_list[0].name = val

    def pow(self, exp, parent): #Done
        paren = parent.chilren_list[0]
        pow_tail = parent.chilren_list[1]
        paren.chilren_list.clear()
        paren.fn = None
        paren.chilren_list.append(self)
        self.parent = paren

        #the case in which exponent is zero must be handled before pow is called
        assert (type(exp) == D and exp.get_char() == 0) == False

        if self.get_char() == 0: #exceptional case
            self.set_char(0)
            pow_tail.is_terminal = True
            pow_tail.chilren_list.clear()
            paren.chilren_list.append(self)

        elif self.is_num() and type(exp) == D and exp.is_num(): 
            #merge numbers...
            self.set_char(pow(self.get_char(), exp.get_char()))
            pow_tail.is_terminal = True
            pow_tail.chilren_list.clear()

        return parent

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


    def __init__(self, parent = None):
        Symbol.__init__(self, parent = None)
        self.name = '<paren>'
        self.is_terminal = False
        self.fn = None

    def do_copy(self):
        instance = Paren()
        instance.fn = self.fn
        return instance

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
            expr = Expr(self)
            left = Terminal('(', self)
            right = Terminal(')', self)
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
            d = D(self)
            self.children_list.append(d)
            d.parse(tokens)

    def compute(self, var_dict = {'pi' : math.pi, 'e' : math.e}, priv = None):
        if self.fn == None:
            if len(self.children_list) == 3:
                expr = self.children_list[1]
                return expr.compute(var_dict)
            else:
                d = self.children_list[0]
                return d.compute(var_dict)
        else:
            fn = Paren.fn_dict[self.fn]
            expr = self.children_list[1]
            return fn(expr.compute(var_dict))
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
    
    def delete(self):
        ppow = self.parent
        pow_tail = ppow.children_list[1]

    def canonicalize(self, parent = None, skip = 0):
        if len(self.children_list) == 3: #Parentheses contains expr
            expr = self.chilren_list[1]
            expr.canonicalize(self) #expr is a mutable object
            if self.fn == None:
                return expr 
        return self

    def pow(self, operand, parent):
        #Do nothing...
        assert self.fn != None
        return parent

class Pow(Symbol):
    def __init__(self, parent = None):
        Symbol.__init__(self, parent = None)

        self.name = '<pow>'
        self.is_terminal = False

    def do_copy(self):
        instance = Pow()
        return instance

    def fill_children_list(self, tokens):
        paren = Paren(self)
        pow_tail = Pow_tail()
        self.children_list.append(paren)
        self.children_list.append(pow_tail)
        paren.parse(tokens)
        pow_tail.parse(tokens)

    def compute(self, var_dict = {'pi' : math.pi, 'e' : math.e}, priv = None):
        paren = self.children_list[0]
        pow_tail = self.children_list[1]
        if pow_tail.is_terminal:
            return paren.compute(var_dict)
        
        return pow(paren.compute(var_dict), pow_tail.compute(var_dict))

    def diff (self, var_dict, priv = None):
        paren = self.children_list[0]
        pow_tail = self.children_list[1]

        return pow_tail.diff(var_dict, paren)

    def canonicalize(self, parent = None, skip = 0):
        paren = self.children_list[0]
        pow_tail = self.chilren_list[1]
        
        paren = paren.canonicalize(self) #mutable object
        pow_tail = pow_tail.canonicalize(self) #mutable object

        root_base = paren.get_root()
        root_exp = pow_tail.get_root() 

        if root_exp == None:
            pow_tail.is_terminal = True
            pow_tail.chilren_list.clear()
            if type(root_base) == Pow:
                #swap root_base and self... 
            elif type(root_base) == D:
                #assign d to paren
            return self 

        elif type(root_exp) == D and root_exp.is_num():
            num_exp = root_exp.get_char() 
            if num_exp == 0 or num_exp == 1:
                pow_tail.is_terminal = True 
                pow_tail.chilren_list.clear()
            if num_exp == 0
                paren.fn = None
                root_exp.set_char(1)
                paren.chilren_list.clear()
                paren.chilren_list.append(root_exp)
                root_exp.parent = paren
                return self
        
        elif type(root_exp) == Pow:
            assert pow_tail.is_terminal == False
            assert len(pow_tail.chilren_list) == 2
            pow_tail.chilren_list[1] = root_exp


        root_base.pow(pow_tail)

    
    def pow(self, operand):#pow_tail
        assert operand.is_terminal == False

        paren = self.children_list[0]
        pow_tail = self.children_list[1]

        #That's because the pow without tail has been cacnonicalized as other
        #symbol.
        assert pow_tail.is_terminal == False
        root_paren = paren.get_root()
        
        assert type(root_paren) != Term

        # make pow_tail converted to expr
        lpow = pow_tail.chilren_list[1]
        rpow = operand.chilren_list[1]

        lexpr = lpow
        rexpr = rpow
        assert type(lexpr) == type(rexpr)
        while type(lexpr) != Expr and type(rexpr) != Expr
            lexpr = lpow.wrap()
            rexpr = rexpr.wrap()

        lexpr.mul(rexpr)

        while type(lexpr) == Pow:
            lexpr = lexpr.wrap()

        pow_tail.chilren_list[1] = lexpr
        
        return self.canonicalize()

class Pow_tail(Symbol):
    def __init__(self, parent = None):
        Symbol.__init__(self, parent = None)

        self.name = '<pow-tail>'
        self.is_terminal = False

    def do_copy(self):
        instance = Pow_tail()
        return instance
    
    def fill_children_list(self, tokens):
        if len(tokens) == 0 or tokens[0] != '^':
            self.is_terminal = True
            return

        terminal = Terminal(tokens.popleft(), self)
        ppow = Pow(self)
        self.children_list.append(terminal)
        self.children_list.append(ppow)

        terminal.parse(tokens)
        ppow.parse(tokens)
    
    def compute(self, var_dict = {'pi' : math.pi, 'e' : math.e}, priv = None):
        if self.is_terminal == True:
            return None
        else:
            ppow = self.children_list[1]
            return ppow.compute(var_dict)

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

    def canonicalize(self, parent = None, skip = 0):
        paren = self.children_list[1]
        pow_tail = self.chilren_list[2]
        expr = paren.canonicalize(self) #mutable object
        pow_tail = pow_tail.canonicalize(self) #mutable object
        root_base = paren.get_root() #TODO need to implement it
        root_exp = pow_tail.get_root()

        if type(root_base) == D and type(root_exp) == D and\
                root_base.is_num() and root_exp.is_num():
            root_base.chilren_list[0].name = self.compute()
            pow_tail.is_terminal = True
            pow_tail.chilren_list.clear()

        elif type(root_base) == Expr and type(root_exp) == D and\
                root_exp.is_int():
            root_base.pw





                
        if pow_tail.is_terminal:
            return root_base

        return root_base.pow(expr, pow_tail)
        

class Term(Commutable):
    def __init__(self, parent = None):
        Commutable.__init__(self, parent = None)
        self.name = '<term>'
        self.is_terminal = False

    def do_copy(self):
        instance = Term()
        return instance

    def fill_children_list(self, tokens):
        ppow = Pow(self)
        term_tail = Term_tail(self)
        self.children_list.append(ppow)
        self.children_list.append(term_tail)
        ppow.parse(tokens)
        self.tail = term_tail.parse(tokens)
    
    def compute(self, var_dict = {'pi' : math.pi, 'e' : math.e}, priv = None):
        ppow = self.children_list[0]
        term_tail = self.children_list[1]
        return term_tail.compute(var_dict, ppow.compute(var_dict))

    def diff(self, var_dict, priv = None):
        ppow = self.children_list[0]
        term_tail = self.children_list[1]

        return term_tail.diff(var_dict, ppow)
    
    def sort(self):
        ppow = self.children_list[0]
        first = Term_tail()
        first.parent = self
        first.is_terminal = False
        first.children_list.append(Terminal('*'))
        first.children_list.append(ppow)
        first.children_list.append(None)
        pow_list = []
        pow_list.append(first)

        # collect all factors in this term into pow_list
        cur = self.children_list[1]
        while cur.is_terminal == False:
            pow_list.append(cur)
            cur = cur.children_list[2]

        #O(n) where n is the number of pows
        pow_list.sort(key=lambda term_tail:\
                term_tail.children_list[1].tostring_local())

        first_op = pow_list[0].children_list[0].name
        is_removed = False
        if first_op  == '/':
            ppow = Pow()
            q = deque()
            q.append('1')
            ppow.parse(q)
        else:
            is_removed = True
            ppow = pow_list[0].children_list[1] #ppow

        
        ppow.parent = self
        self.children_list[0] = ppow

        term_tail = Term_tail()
        term_tail.is_terminal = True
        self.tail = term_tail

        if len(pow_list) < 2 and is_removed == True:
            term_tail.parent = self
            self.children_list[1] = term_tail
            return

        start = 0
        if is_removed == True:
            start = 1

        last = pow_list[len(pow_list) - 1]
        term_tail.parent = last
        last.children_list[2] = term_tail
        last.update_vars()
        cur = last

        for i in reversed(range(start, len(pow_list) - 1)):
            cur = pow_list[i]
            cur.children_list[2] = last
            last.parent = cur
            cur.update_vars()
            last = cur

        cur.parent = self
        self.children_list[1] = cur
        self.update_vars()      

    def canonicalize(self, parent = None, skip = 0):
        pow_dict = {}
        offset = 0
        term_tail = self.make_term_tail()

        while term_tail.is_terminal == False:
            op = term_tail.children_list[0]     
            ppow = term_tail.chilren_list[1]
            ppow.canonicalize()#must be ppow...
            pow_tail = ppow.chilren_list[1]
            paren = ppow.chilren_list[0]

            root_pow = ppow.get_root()

            if type(root_pow) == D and root_pow.is_num():
                if 'number' in pow_dict:
                    if op == '*':
                        pow_dict['number'] *= root_pow.get_char()
                    else:
                        pow_dict['number'] /= root_pow.get_char()
                else:
                    pow_dict['number'] = root_pow.get_char()

            elif pow_tail.is_terminal == True and\
                paren.is_terminal == False and paren.fn == None and op == '*':
                assert ppow.is_terminal == False
                expr = paren.chilren_list[1] 
                t1 = Term.make_from_dict(pow_dict)
                expr.prepend(t1)
                expr.append(term_tail)
                return expr.canonicalize(None, len(pow_dict))
            
            if type(root_pow) == Term:
                if op == '/':
                    root_pow.flip_div()
                
                root_pow.append_tail(term_tail)
                term_tail = root_pow.make_term_tail()
                continue

            assert paren.is_terminal == False
            key = paren.tostring_local()
            if key in pow_dict:
                local_term_tail = pow_dict[key]
                local_term_tail.exp(term_tail)
            else:
                pow_dict[key] = term_tail

            term_tail = term_tail.chilren_list[2]

        return Expr.make_from_term(Term.make_from_dict(pow_dict))

    def pow(self, operand):
        '''
            for pow in term
                *pow = pow.pow(operand)
        '''
        
            
class Term_tail(Symbol):
    def __init__(self, parent = None):
        Symbol.__init__(self, parent = None)
        self.name = '<term-tail>'
        self.is_terminal = False

    def do_copy(self):
        instance = Term_tail()
        return instance

    def fill_children_list(self, tokens):
        if len(tokens) == 0 or (tokens[0] != '*' and tokens[0] != '/'):
            self.is_terminal = True
            return self
       
        terminal = Terminal(tokens.popleft(), self)
        ppow = Pow(self)
        term_tail = Term_tail(self) #pass this object as parent
        
        self.children_list.append(terminal)
        self.children_list.append(ppow)
        self.children_list.append(term_tail)

        terminal.parse(tokens)
        ppow.parse(tokens)
        return term_tail.parse(tokens)
 
    def compute(self, var_dict = {'pi' : math.pi, 'e' : math.e}, priv = None):
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

class Expr(Commutable):
    def __init__(self, parent = None):
        Commutable.__init__(self, parent = None)

        self.is_terminal = False
        self.name = '<expr>'

    def do_copy(self):
        instance = Expr()
        return instance

    def fill_children_list(self, tokens):
        if len(tokens) == 0:
            self.is_terminal = True
            return

        term = Term(self)
        expr_tail = Expr_tail(self)
        
        self.children_list.append(term)
        self.children_list.append(expr_tail)
        
        term.parse(tokens)
        self.tail = expr_tail.parse(tokens)
     
    def compute(self, var_dict = {'pi' : math.pi, 'e' : math.e}, priv = None):
        if self.is_terminal == True:
            return None

        term = self.children_list[0]
        expr_tail = self.children_list[1]

        return expr_tail.compute(var_dict, term.compute(var_dict))

    def diff(self, var_dict, priv = None):
        term = self.children_list[0]
        expr_tail = self.children_list[1]
        return expr_tail.diff(var_dict, term)

    #convert_tail, lt, le...j
    def canonicalize(self, parent, skip):
        term = self.children_list[0]
        expr_list = []
        expr_list.append(term.canonicalize().convert_tail())
        cur = expr_tail
        
        while cur.is_terminal == False:
            
            op = cur.chilren_list[0]
            term = cur.chilren_list[1]
            expr = term.canonicalize()
            converted = expr_from_term.convert_tail()
            if op == '-':
                expr.flip_op()
            expr_list.append(converted)
            cur = cur.chilren_list[2]

        min_heap = []
        for i in range(0, len(expr_list)):
            if expr.is_terminal == False:
                cur = expr_list[i]
                expr_tail = cur.chilren_list[2]
                expr_list[i] = expr_tail
                heappush(min_heap, (cur, i))

        cur = None
        head = None
        while len(min_heap) > 0:
            entry = heappop(min_heap)
            expr_tail = entry[0]
            topush = entry[1]
            if cur == None:
                head = cur = expr_tail
            else:
                if cur.mergeable(expr_tail):
                    cur.merge(expr_tail)
                else:
                    cur.append_link(expr_tail)
                    cur = expr_tail

            picked_next = expr_list[topush].chilren_list[2]
            if picked_next.is_terminal == False:
                expr_list[topush] = picked_next
                heappush(min_heap, (picked_next, topush))
        
        if cur == None:
            self.is_terminal = True
            return self

        return self.make_from_tail(head, cur, parent) #first, last, expr_tail
    

    def sort(self):
        term = self.children_list[0]
        first = Expr_tail() #dummy
        first.parent = self
        first.is_terminal = False
        first.children_list.append(Terminal('+'))
        first.children_list.append(term)
        first.children_list.append(None)
        term_list = []
        term_list.append(first)

        # collect all factors in this term into term_list
        cur = self.children_list[1]
        while cur.is_terminal == False:
            term_list.append(cur)
            cur = cur.children_list[2]

        #O(n) where n is the number of terms
        term_list.sort(key=lambda expr_tail:\
                expr_tail.children_list[1].tostring_local())

        first_op = term_list[0].children_list[0].name
        is_removed = False
        if first_op  == '-':
            term = Term()
            q = deque()
            q.append('0')
            term.parse(q)
        else:
            is_removed = True
            term = term_list[0].children_list[1] #term 
 
        term.parent = self
        self.children_list[0] = term

        expr_tail = Expr_tail()
        expr_tail.is_terminal = True
        self.tail = expr_tail

        if len(term_list) < 2 and is_removed == True:
            expr_tail.parent = self
            self.children_list[1] = expr_tail
            return

        start = 0
        if is_removed == True:
            start = 1

        last = term_list[len(term_list) - 1]
        expr_tail.parent = last
        last.children_list[2] = expr_tail
        last.update_vars()
        cur = last

        for i in reversed(range(start, len(term_list) - 1)):
            cur = term_list[i]
            cur.children_list[2] = last
            last.parent = cur
            cur.update_vars()
            last = cur

        cur.parent = self
        self.children_list[1] = cur
        self.update_vars()

    def pow(self, operand, parent):
        '''
            self 
            if operand is integer:
                for i to integer:
                    ret.mul()
            not
                return parent
        '''
class Expr_tail(Symbol):
    def __init__(self, parent = None):
        Symbol.__init__(self, parent = None)

        self.is_terminal = False
        self.name = '<expr-tail>'

    def do_copy(self):
        instance = Expr_tail()
        return instance

    def fill_children_list(self, tokens):
        if len(tokens) == 0 or (tokens[0] != '+' and tokens[0] != '-'):
                self.is_terminal = True
                return self

        terminal = Terminal(tokens.popleft(), self)
        term = Term(self)
        expr_tail = Expr_tail(self) 

        self.children_list.append(terminal)
        self.children_list.append(term)
        self.children_list.append(expr_tail)

        terminal.parse(tokens)
        term.parse(tokens)
        return expr_tail.parse(tokens)

    def compute(self, var_dict = {'pi' : math.pi, 'e' : math.e}, priv = None):
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
    def

string  = '5 * 5 / 6 ^ 2 / 7'
string = '3 ^ 2 * 3 / 2 ^ 3'
#string = 'c / b * a'
string = 'c + b - a'

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

diff_dict = {'x': True}

print('derivative: ' + root.diff(diff_dict))
copied = root.copy(None)
copied.walk(0)
print('copy: ' + copied.tostring())


