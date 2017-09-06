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
    
    def __str__(self):
        return str(self.name)

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

    def wrap(self):
        d = D()
        d.children_list.append(self)
        self.parent = d
        return d
    
    def __eq__(self, other):
        return str(self) == str(other)

class D(Symbol):
    is_variable = False
    def __init__(self, priv = None):
        terminal = None 
        if type(priv) == int or type(priv) == float or type(priv) == str:
            terminal = Terminal(priv) 
            priv = None
        Symbol.__init__(self, priv)
        self.name = '<D>'
        self.is_terminal = False
        if terminal != None:
            self.children_list.append(terminal)
            terminal.parent = self

    def __str__(self):
        return str(self.children_list[0])

    def __eq__(self, other):
        return str(self) == str(other)

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
        return type(terminal.name) == float or type(terminal.name) == int

    #pi or e is converted to real number
    def is_constant(self):
        terminal = self.children_list[0]
        return self.is_num() or terminal.name == 'e' or terminal.name == 'pi'

    def is_int(self):
        if self.is_num() == False:
            return False
        
        num = self.get_char()
        return int(num) == num

    def get_char(self):
        return self.children_list[0].name

    def set_char(self, val):
        self.children_list[0].name = val

    def pow(self, exp, parent): #Done
        paren = parent.children_list[0]
        pow_tail = parent.children_list[1]
        paren.children_list.clear()
        paren.fn = None
        paren.children_list.append(self)
        self.parent = paren

        #the case in which exponent is zero must be handled before pow is called
        assert (type(exp) == D and exp.get_char() == 0) == False

        if self.get_char() == 0: #exceptional case
            self.set_char(0)
            pow_tail.is_terminal = True
            pow_tail.children_list.clear()
            paren.children_list.append(self)

        elif self.is_num() and type(exp) == D and exp.is_num(): 
            #merge numbers...
            self.set_char(pow(self.get_char(), exp.get_char()))
            pow_tail.is_terminal = True
            pow_tail.children_list.clear()

        return parent

    def wrap(self):
        paren = Paren()
        paren.children_list.append(self)
        self.parent = paren
        return paren
    
    def get_root(self):
        if self.is_terminal == True:
            return None
        return self

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
            expr = self.children_list[1]
            root = expr.get_root()
            cur = root 
            cur = cur.wrap_to(Expr)
        
            self.children_list[1] = cur
            cur.canonicalize(self)
            if self.fn == None:
                return cur

        return self

    def pow(self, operand, parent):
        #Do nothing...
        assert self.fn != None
        return parent

    def wrap(self):
        parent = Pow()
        tail = parent.create_tail()
        tail.is_terminal = True
        self.parent = parent
        tail.parent = parent

        parent.children_list.append(self)
        parent.children_list.append(tail)
        
        return parent

    def get_root(self):
        if self.is_terminal == True:
            return None
        
        if self.fn != None:
            return self
        elif len(self.children_list) == 3:
            expr = self.children_list[1]
            assert type(expr) == Expr
            return expr.get_root()
        else:
            d = self.children_list[0]
            assert type(d) == D and len(self.children_list) == 1
            return d.get_root()

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

    #Paren.canonicalize() must be implemented..
    #It must return obj of Pow
    def canonicalize(self, parent = None, skip = 0):
        paren = self.children_list[0]
        pow_tail = self.children_list[1] 
        exp_pow = pow_tail.canonicalize() 
        paren = paren.canonicalize(self) #mutable object

        root_base = paren.get_root()
        root_exp = exp_pow.get_root()
        if pow_tail.is_terminal:
            return self
        
        assert exp_pow != None
        #(*,0) (0, *)
        if (root_exp.is_num() and root_exp.get_char() == 0.0) or\
                (root_base.is_num() and root_base.get_char == 0.0):
            const = 0.0
            if root_exp.get_char() == 0.0:
                const = 1.0
            
            d = D(const)
            pow_tail.set_terminal()
            paren.children_list.clear()
            paren.fn = None
            paren.children_list.append(d)
            return self
      
        #(*, 1)
        if root_exp.is_num() and root_exp.get_char() == 1.0:
            pow_tail.set_terminal()
            return self
           
        if type(root_base) == Pow:
            parenofbase = root_base.children_list[0]
            expofbase = root_base.children_list[1].children_list[1]
            expofbase = expofbase.wrap_to(Expr)
            root_exp = root_exp.wrap_to(Expr)
            expofbase.mul(root_exp)
            ppow = expofbase.wrap_to(Pow)
            pow_tail = Pow_tail()
            pow_tail.children_list.append(Terminal('^'))
            pow_tail.children_list.append(ppow)
            root_base.children_list[1] = pow_tail
            root_base.canonicalize()
            self.children_list = root_base.children_list
            return self
            
        elif type(root_base) == Term:
            head = cur = root_base.make_tail()
            while cur.is_terminal == False:
                ppow = cur.children_list[1]    
                ppow.pow(root_exp)
                cur = cur.children_list[2]
            expr = root_base.canonicalize()
            expr_root = expr.get_root() 
     
            ppow = expr_root.wrap_to(Pow)
            self.children_list = ppow.children_list 

        elif type(root_base) == Expr and root_exp.is_num() and\
                root_exp.is_int():

            is_inverse = False
            num = root_exp.get_char()
            
            if num < 0:
                is_inverse = True
                num *= -1
            
            ret = root_base.copy()
            for i in range(1, int(root_exp.get_char())):
                ret.mul(root_base.copy())
            if is_inverse:
                ret.inverse()
            ret.canonicalize()

            ret = ret.get_root()
            ret = ret.wrap_to(Pow)
            self.children_list = ret.children_list 
        else: 
            assert type(root_base) == Paren or type(root_base) == D or\
                    type(Expr)
            #d nothing... 
        return self

    def default_op(self):
        return '^'

    def create_tail(self):
        return Pow_tail()
 
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
        lpow = pow_tail.children_list[1]
        rpow = operand.children_list[1]

        lexpr = lpow
        rexpr = rpow
        assert type(lexpr) == type(rexpr)
        lexpr = lexpr.wrap_to(Expr)
        rexpr = rexpr.wrap_to(Expr)

        lexpr.mul(rexpr)

        lexpr = lexpr.wrap_to(Pow)
        pow_tail.children_list[1] = lexpr
        
        return self.canonicalize()
     
    def wrap(self):
        parent = Term() 
        tail = parent.create_tail()
        tail.is_terminal = True
        self.parent = parent
        tail.parent = parent

        parent.children_list.append(self)
        parent.children_list.append(tail)
        parent.tail = parent
        
        return parent

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
        self.tail = self.tail.parent
    
    def compute(self, var_dict = {'pi' : math.pi, 'e' : math.e}, priv = None):
        ppow = self.children_list[0]
        term_tail = self.children_list[1]
        return term_tail.compute(var_dict, ppow.compute(var_dict))

    def diff(self, var_dict, priv = None):
        ppow = self.children_list[0]
        term_tail = self.children_list[1]

        return term_tail.diff(var_dict, ppow)
    
    def default_op(self):
        return '*'

    def create_tail(self):
        return Term_tail()

 
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

    def flip_div(self):
        if self.is_terminal == True:
            return

        head = prev = cur = self.make_tail()
        
        while cur.is_terminal == False:
            op = cur.children_list[0]
            if op == '*':
                cur.children_list[0] = Terminal('/')
            else:
                assert op == '/'
                cur.children_list[1] = Terminal('*')
            
            prev = cur
            cur = cur.children_list[2] 
        
        root = head.get_root()
        elif type(root) == D and root.is_num():
            root.set_char(1.0 / root.get_char())
        else:
            d = D(1.0)
            wrapped = d.wrap_to(Pow)
       
            if type(self.tail) == Term:
                assert head.children_list[2].is_terminal == True
                assert prev == head
            else:
                assert type(self.tail) == Term_tail
            
            self.tail = prev
            self.children_list[0] = wrapped #pow
            self.children_list[1] = head #term_tail
            head.parent = self
            wrapped.parent = self

    def append(self, term, op = Terminal('*')):
        assert self.is_terminal or term.is_terminal
        
        term_tail = term.make_tail()
        term_tail.children_list[0] = op
        idx = 2
        if type(self.tail) == Term:
           idx = 1 
        
        tail = term.tail
        if type(term.tail) == Term:
            tail = term_tail 
        
        self.tail.children_list[idx] = term_tail
        term_tail.parent = self.tail
        self.tail = tail

    #Canonicalization cannot remove its own symbol!!!
    def canonicalize(self, parent = None, skip = 0):
        pow_dict = {}
        offset = 0
        cur = self.make_tail() # Term_tail
        num_key = ''

        while cur.is_terminal == False:
            op = cur.children_list[0] 
            ppow = cur.children_list[1] 
            ppow = ppow.canonicalize() #must be ppow...
            root = ppow.get_root()

            if type(root) == D and root.is_num():
                paren = ppow.children_list[0]
                paren.children_list.clear()
                paren.children_list.append(root) 
                num = root.get_char()

                if op == '/':
                    num = 1.0 / num
                    cur.children_list[0] = Terminal('*') 
                    '''
                        if root.get_char() == 0: which needs to be
                        implemented..
                            throw exception...
                    '''
                    #TODO error throw exception('Divided by Zero')
                    #TODO check get_char
                if '' in pow_dict:
                        target = pow_dict['']
                        t_pow = target.children_list[1]
                        t_root = t_pow.get_root()
                        assert type(t_root) == D
                        t_root.set_char(t_root.get_char() * num) 
                        t_paren.children_list.clear()
                else:
                    root.set_char(num)
                    pow_dict[''] = cur

            elif type(root) == Expr nd op == '*':
                assert ppow.is_terminal == False
                expr = root #which belongs to cur
                t1 = None
                t2 = None
                
                nextofcur = cur.children_list[2]
                next_op = None
                if len(pow_dict)
                    t1 = Term.make_from_dict(pow_dict) #core method pow_dict == 0??

                if nextofcur.is_terminal == False:
                    assert type(self.tail) != Term
                    t2 = Term()
                    next_op = nextofcur.children_list[0]
                    t2.children_list = nextofcur.children_list[1:]
                    t2.children_list[0].parent = t2
                    t2.children_list[1].parent = t2
                    if self.tail == nextofcur:
                        t2.tail = t2
                    else:
                        t2.tail = self.tail

                if t1 == None and t2 == None:
                    return expr
                
                if t1 != None:
                    expr.prepend_term(t1) 
                if t2 != None:
                    expr.append_term(t2, next_op)

                return expr.canonicalize(None, len(pow_dict))

            elif type(root) == Term:
                if op == '/':
                    root.flip_div() #need
                #tail check 
                nextofcur = cur.children_list[2]

                if nextofcur.is_terminal == False:
                    t1 = Term()
                    next_op = nextofcur.children_list[0]
                    t1.children_list = nextofcur.children_list[1:]
                    t1.children_list[0].parent = t1.children_list[1].parent = t1
                    if self.tail == nextofcur:
                        t1.tail = t1
                    else:
                        t1.tail = self.tail
                    root.append(t1, next_op)
                
                self.tail = root.tail
                cur = root.make_tail()
            else:
                paren = ppow.children_list[0]
                key = paren.tostring()
                assert key != num_key
                
                if key in pow_dict:
                    term_tail = pow_dict[key]
                    is_merged = term_tail.merge(cur)
                    if is_merged == False:
                        pow_dict.pop(key)
                        continue
                else:
                    pow_dict[key] = cur

            cur = cur.children_list[2]
        
        term = Term.make_from_dict(pow_dict) 
        ret = term.wrap_to(Expr)
        return ret 
    
    @classmethod
    def make_from_dict(cls, factor_dict):
        if '' in factor_dict:
            term_tail = factor_dict['']
            assert term_tail.children_list[0] == '*'
            ppow = term_tail.children_list[1]
            num_root = ppow.get_root()
            const = num_root.get_char()
            if const == 1.0:
                factor_dict.pop('')
            elif const == 0:
                factor_dict.clear()
        
        if len(factor_dict) == 0:
            d = D(0.0)
            wrapped = d.wrap_to(Term)
            return wrapped


        values = factor_dict.values()
        term_tail_list = []
        for item in values:
            assert type(item) == Term_tail
            item.invalidate = True
            term_tail_list.append(item)
        
        term_tail_list.sort()
      
        prev = None
        for term_tail in term_tail_list:
            assert term_tail.is_terminal === False
            if prev != None:
                prev.children_list[3] = term_tail #link
            prev = term_tail

        term = Term()
        terminal = Term_tail()
        terminal.is_terminal = True

        first = term_tail_list[0]
        last = term_tail_list[len(term_tail_list) - 1] 
        last.children_list[2] = terminal
 
        root = first.children_list[1]
        root = root.get_root()
        if first.children_list[0] == '/' and\
                type(root) == D and root.is_num():
            root.set_char(1.0 /root.get_char())
            first.children_list[0] = Terminal('*')

        if first.children_list[0] == '/':
            term
            term = d.wrap_to(Term)
            term.children_list[1] = first
            first.parent = term
            term.tail = last
        else:
            term.children_list = first.children_list[1:]
            term.children_list[0].parent = term
            term.children_list[1].parent = term
            if len(term_tail_list) == 1:
                term.tail = term
            else:
                term.tail = last
        return term

    def pow(self, operand):
        '''
            for pow in term
                *pow = pow.pow(operand)
        '''
    def wrap(self):
        parent = Expr() 
        tail = parent.create_tail()
        tail.is_terminal = True
        self.parent = parent
        tail.parent = parent

        parent.children_list.append(self)
        parent.children_list.append(tail)
        parent.tail = parent
        
        return parent

    
            
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
   
   #get_id has to be debugged....
    def get_id(self):
        assert self.is_terminal == False

        if self.invalidate == False and 'id' in self.cache:
            return self.cache['id']
        
        self.invalidate = False
        ret = self.tostring()
        self.cache['id'] = ret
        return ret

    #this is for min_heap
    def __lt__(self, other):
        return self.get_id() < other.get_id()

    def __eq__(self, other):
        return self.get_id() == other.get_id()


    def merge(self, other):
        l_ppow = self.children_list[1]
        l_pow_tail = l_ppow.children_list[1] #!0 or !1
        l_exp = None
        if l_pow_tail.is_terminal:
            d = D(1.0)
            l_exp = d.wrap_to(Pow)
        else:
            l_exp = l_pow_tail.children_list[1]

        #redundant codes..
        r_ppow = other.children_list[1]
        r_paren = r_ppow.children_list[0]
        r_pow_tail = r_ppow.children_list[1] 
        r_exp = None
        if r_pow_tail.is_terminal:
            d = D(1.0)
            r_exp = d.wrap_to(Pow)
        else:
            r_exp = l_pow_tail.children_list[1]

        l_expr = l_exp.wrap_to(Expr)
        r_expr = r_exp.wrap_to(Expr) 
        l_expr.append(r_expr) 
        l_expr.canonicalize()
        
        root_exp = l_expr.get_root()
        root_base = r_paren.get_root()

        if type(root_exp) == D and root_exp.is_num():
            exp = root_exp.get_char()
            op = self.children_list[0]
            other_op = other.children_list[0]
            if other_op == '/':
                exp *= -1.0

            if exp < 0:
                exp *= -1.0
                if op == '/':
                    self.children_list[0] = Terminal('*')
                else:
                    assert op == '*'
                    self.children_list[0] = Terminal('/')
            if exp == 1.0 or exp == 0.0 or\
                    (type(root_base) == D and root_base.is_num()):
                #exceptional case!!  
                r_pow_tail.is_terminal = True
                r_pow_tail.children_list.clear()
                other.children_list[0] = self.children_list[0] #copy op
                if exp == 0.0:
                    d = D(1.0)
                    other.children_list[1] = d.wrap_to(Pow)
                elif (type(root_base) == D and root_base.is_num()):
                    base = root_base.get_char()
                    d = D(pow(base, exp))
                    other.children_list[1] = d.wrap_to(Pow)
                return False 
                #exceptional case!!

        r_pow = root_exp.wrap_to(Pow)
        pow_tail = Pow_tail()
        pow_tail.children_list.append(Terminal('^'))
        pow_tail.children_list.append(r_pow)
        l_ppow.children_list[1] = pow_tail
        return True
                #no modified..
        
                
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
        self.tail = self.tail.parent
     
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
    #It merges the exprs generated by canonicalization of each term, like
    #mergesort
    def canonicalize(self, parent = None, skip = 0):

        #TODO remove parantheses

        expr_list = [] 
        cur = self.make_tail() #conversion for iterating 
        
        while cur.is_terminal == False: 
            op = cur.children_list[0]
            term = cur.children_list[1]
            expr = term.canonicalize()
            tail = expr.make_tail()
            if op == '-':
                expr.flip_op()
            expr_list.append(tail)
            if cur.children_list[2].is_terminal:
                break
            cur = cur.children_list[2]


        min_heap = []
        for i in range(0, len(expr_list)):
            cur = expr_list[i]
            if cur.is_terminal == False:
                expr_tail = cur.children_list[2]
                expr_list[i] = expr_tail #update run
                cur.invalidate = True
                heappush(min_heap, (cur, i))

        cur = None
        head = None
        terminal = Expr_tail()
        terminal.is_terminal = True

        while len(min_heap) > 0:
            entry = heappop(min_heap)
            expr_tail = entry[0]
            topush = entry[1]
            if cur == None:
                head = cur = expr_tail
                head.parent = None
                expr_tail.children_list[2] = terminal
                terminal.parent = expr_tail
            else:
                if cur.mergeable(expr_tail):
                    cur.merge(expr_tail)
                    if cur.is_terminal:
                        cur = cur.parent
                    #TODO check current constant is zero
                else:
                    if cur.is_terminal or cur.get_constant() == 0:
                       cur = cur.parent
                       if cur == None:
                           heappush(min_heap, entry)
                           continue

                    assert expr_tail.is_terminal == False
                    cur.children_list[2] = expr_tail
                    expr_tail.children_list[2] = terminal
                    terminal.parent = expr_tail
                    expr_tail.parent = cur
                    cur = expr_tail

            picked_next = expr_list[topush].children_list[2]
            #update minheap
            if picked_next.is_terminal == False:
                expr_list[topush] = picked_next
                heappush(min_heap, (picked_next, topush))
        
        if cur == None:
            d = D(0.0)
            wrapped = d.wrap_to(Expr)

            self.is_terminal = False
            self.children_list = wrapped.children_list
            self.children_list[0].parent = self
            self.children_list[1].parent = self
            self.tail = self
            return self
        
        tail = None
        if head.children_list[2].is_terminal == True:
            tail = self 
        else:
            tail = cur 
        
        op = head.children_list[0]
        if op == '-':
            term = head.children_list[1]
            term.minus()
        else:
            assert op == '+'

        head.children_list[1].parent = self
        head.children_list[2].parent = self
        self.tail = tail
        self.children_list = head.children_list[1:]

        return self 

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

    def default_op(self):
        return '+'
    
    def create_tail(self):
        return Expr_tail()

    #Done don't copy
    def append(self, expr): 
        if len(self.children_list) == 0:
            self.children_list = expr.children_list
            self.is_terminal = expr.is_terminal
            if len(self.children_list) == 2:
                self.children_list[0].parent = self
            if type(expr.tail) == Expr:
                self.tail = self
            else:
                assert type(expr.tail) == Expr_tail
                self.tail = expr.tail
            return

        expr_tail = expr.make_tail()
        idx = -1
        tail = None
        if type(expr.tail) == Expr:
            tail = expr_tail
        else:
            assert type(expr.tail) == Expr_tail
            tail = expr.tail

        if type(self.tail) == Expr:
            idx = 1
        else:
            assert type(self.tail) == Expr_tail
            idx = 2

        self.tail.children_list[idx] = expr_tail
        expr_tail.parent = self.tail
        self.tail = tail

    #Done
    def prepend_term(self, term):    
        head = cur = self.make_tail():#expr_tail
        parent = self 
        while cur.is_terminal == False:
            cur_term = cur.children_list[1]

            left = term.copy()
            right = cur_term.make_tail()
            tail = None
            if type(cur_term.tail) == Term:
                tail = right 
            else:
                assert type(cur_term.tail) == Term_tail
                tail = cur_term.tail

            idx = -1
            if type(left.tail) == Term:
                idx = 1
            else:
                assert type(left.tail) == Term_tail:
                idx = 2
           
            left.tail.children_list[idx] = right
            right.parent = left.tail 
            cur.children_list[1] = left
            left.tail = tail
            left.parent = parent 
            parent = cur
            cur = cur.children_list[2]

       assert head.children_list[0] == self.default_op()
       self.is_terminal = head.is_terminal
       self.children_list = head.children_list[1:]

    #Done
    def append_term(self, term, op = Terminal('*')):
        head = cur = self.make_tail():#expr_tail
     
        while cur.is_terminal == False:
            left = cur.children_list[1] #term
            right_term = term.copy()
            right = right_term.make_tail() 
            right.children_list[0] = op
            tail = None

            if type(right_term.tail) == Term:
                tail = right
            else:
                assert right_term.tail == Term_tail
                tail = right_term.tail

            idx = -1
            if type(left.tail) == Term:
                idx = 1
            else:
                assert type(left.tail) == Term_tail:
                idx = 2
                            
            left.tail.children_list[idx] = right
            right.parent = left.tail
            left.tail = tail
            cur = cur.children_list[2]
        
       assert head.children_list[0] == self.default_op()
       self.is_terminal = head.is_terminal
       self.children_list = head.children_list[1:]
 
    #It doesn't canonicalize
    def mul(self, expr):
        if expr.is_terminal == True and self.is_terminal == False:
            return self
        elif expr.is_terminal == True and self.is_terminal == True:
            assert False #TODO To be tested 
            return None
        elif expr.is_terminal == False and self.is_terminal == True:
            assert False #TODO To be tested
            return expr
        
        #expr and slef aren't terminal
        ret = Expr()
        cur = self.make_tail() #expr_tail

        #iterate in left side
        while cur.is_terminal == False:
            op = cur.children_list[0]
            term = cur.children_list[1]
            term = term.copy()  
            right_expr = expr.copy() #l_n
            
            if op == '-':
                term.minus()

            right_expr.prepend_term(term)
            ret.append(right_expr)
            cur = cur.children_list[2]
       
        #shallow copy
        tail = None
        if type(ret.tail) == Expr:
            tail = self
        else:
            assert type(ret.tail) == Expr_tail
            tail = ret.tail

        self.is_terminal = ret.is_terminal
        self.children_list = ret.children_list
        self.children_list[0].parent = self
        self.children_list[1].parent = self
        self.tail = tail
        self.vars = ret.vars

        return self

    #the type of operand must be pow_tail
    def pow(self, pow_tail, parent): 
        ppow = Pow.make_from_tail(pow_tail)
        root = ppow.get_root()
        if (type(root) == D and root.is_int()) == False:
            return None #do nothing...

        pow_tail.is_terminal = True
        num = root.get_char()
        ret = Expr()
        parent = ret
        
        minus = False
        if num < 0:
            num *= -1
            minus = True
    
        
        ret.add(self.copy())

        clone = None
        for i in range(0, num - 1):
            clone = self.copy()
            ret.mul(clone)

        self.is_terminal = head.is_terminal
        self.children_list = head.children_list
        tail = None

        if type(ret.tail) == Expr:
            tail = self
        else:
            assert type(ret.tail) == Expr_tail
            tail = ret.tail

        expr_tail = self.children_list[1]
        expr_tail.parent = self
        self.tail = tail

        self.canonicalize()

        if minus:
            self.inverse()

        return self

    def inverse(self):
        ppow = self.wrap_to(Pow)
        d = D(1.0)
        term = d.wrap_to(Term)
        term_tail = Term_tail()
        terminal = Term_tail()
        op = Terminal('/')

        term_tail.children_list.append(op)
        term_tail.children_list.append(ppow)
        term_tail.children_list.append(terminal)
        op.parent = ppow.parent = terminal.parent = term_tail

        term.children_list[1] = term_tail
        term.tail = term_tail
        expr = term.wrap_to(Expr)
        self.tail = tail
        self.children_list = expr.children_list

    def wrap(self):
        paren = Paren()
        
        l_terminal = Terminal('(')
        r_terminal = Terminal(')') 
        
        l_terminal.parent = paren
        r_terminal.parent = paren
        self.parent = paren
        
        paren.children_list(l_terminal)
        paren.children_list(self)
        paren.children_list(r_terminal) 
       
        return paren

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

    def mergeable(self, expr_tail):
        if self.get_id() == expr_tail.get_id()
            return True
        return False


    def merge(self, expr_tail):
        l_const = self.get_constant()
        r_const = expr_tail.get_constant()
        
        const = l_const + r_const

        if const < 0:
            const *= -1.0
            self.children_list[0] = Terminal('-')
        
        term = self.children_list[1]
        ppow = term.children_list[0] 
        term_tail = term.children_list[1]
        root = ppow.get_root()

        if const == 0.0:
            #delete???
            self.is_terminal = True
            self.children_list.clear()
            return self

        #prune 1...
        if type(root) == D:
            op_term_tail = term_tail.children_list[0]
            if const == 1.0 and term_tail.is_terminal == False and\
                    op_term_tail == '*':
                tail = term.tail
                term = Term.make_from_tail(term_tail)
                term_tail = term.children_list[1]

                if term_tail.is_terminal == True:
                    tail = term

                term.tail = tail
                term.parent = self
                self.children_list[1] = term
                return self
            else:
                root.name = const #in-place update
        else:  
            if const != 1.0:
                #1 case
                d = D(const)
                wrapped = d.wrap_to(Pow)
                tail = term.tail
                term_tail = term.make_tail()
                
                if type(tail) == Term:
                    wrapped.tail = term_tail
                else:
                    assert type(tail) == Term_tail
                    wrapped.tail = tail
                
                term_tail.parent = wrapped
                wrapped.parent = term.parent
                wrapped.children_list[1] = term_tail
 
        return self

     
    #is used in heap...
    def get_id(self):
        assert self.is_terminal == False

        if self.invalidate == False and 'id' in self.cache
            return self.cache['id']
        
        self.invalidate = False
        term = self.children_list[1]
        ppow = term.children_list[0] 
        term_tail = term.children_list[1]
        root = ppow.get_root()
 
        if type(root) == D and root.is_num():
            ret = term_tail.tostring()
            if term_tail.is_terminal:
                assert len(term_tail.children_list)
        else:
            ret = term.tostring()

        self.cache['id'] = ret

        return ret

    def get_constant(self):
        assert self.is_terminal == False 
        term = self.children_list[1]
        ppow = term.children_list[0]
        root = ppow.get_root()
      
        ret = 0
        if type(root) == D and root.is_num():
            ret = root.get_char()
        else:
            ret = 1.0

        if self.op == '-':
            ret *= -1.0

        return ret

    #this is for min_heap
    def __lt__(self, other):
        return self.get_id() < other.get_id()

    def __eq__(self, other):
        return self.get_id() == other.get_id()
        


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
