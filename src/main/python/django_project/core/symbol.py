from collections import deque
from abc import ABCMeta, abstractmethod
from queue import Queue
import math

class Symbol:
    def __init__(self):
        self.children_list = []
        self.name = ''
        self.is_terminal = False
        self.vars = {} #for differentiation
        self.cache = {}
        self.invalidate = False
        '''
            x: True
            y: False
        '''
    def do_pow(self, root_exp):
        return
    
    def set_terminal(self):
        self.is_terminal = True
        self.children_list.clear()

    def is_num(self):
        return False
    
    @abstractmethod
    def canonicalize(self, skip = 0):
        pass

    @abstractmethod
    def do_parse(self, tokens):
        pass

    @abstractmethod
    def compute(self, var_dict = {'pi' : math.pi, 'e' : math.e}, priv = None):
        #must return value of double
        pass

    @abstractmethod
    def diff(self, var_dict, priv = None):
        pass

    @abstractmethod
    def do_copy(self):
        cls = type(self)
        return cls()
    
    def wrap_to(self, cls):
        obj = self
        while type(obj) != cls:
            obj = obj.wrap()    
        return obj

    def make_tail(self):
        tail = self.create_tail()
        tail.is_terminal = self.is_terminal
        tail.children_list.append(self.default_op())
        tail.children_list.extend(self.children_list)
        return tail

    def get_root(self):
        if self.is_terminal == True:
            return None
        assert len(self.children_list) == 2
        child = self.children_list[0]
        tail = self.children_list[1] 
        if tail.is_terminal == False:
            return self
        else:
            return child.get_root()


    @abstractmethod
    def pow(self, root_exp):
        pass
        

    def tostring_local(self):
        key = 'tostring'
        if key in self.cache:
            return self.cache[key]
        
        val = self.tostring()
        self.cache[key] = val
        return val
        
    def update_vars(self, is_recursive = False):
        assert False

    #TODO taill...
    def copy(self):
        instance = self.do_copy()
        instance.name = self.name
        instance.is_terminal = self.is_terminal
        for var in self.vars:
            instance.vars[var] = self.vars[var]

        for ele in self.children_list:
            instance.children_list.append(ele.copy())

        return instance

    @abstractmethod
    def tostring(self):
        ret = ''

        for child in self.children_list:
            ele = child.tostring()
            if len(ele) == 0:
                continue
            if len(ret) == 0:
                ret += ele
            else:
                ret += ' ' + ele
        return ret

    def do_tostring_latex(self):
        return self.tostring()

    def tostring_latex(self):
        return self.do_tostring_latex()


    def contains(self, var_dict):
        for var in var_dict:
            if var in self.vars:
                return True
        return False

    #it returns the result of  do_parse
    #Wrapper of do_parse..
    def parse(self, tokens):
        if type(tokens) is not deque:
            print('Tokens is not deque!!')
            return None
        else:
            if len(tokens) == 0:
                self.is_terminal = True
                return
            elif tokens[0] == ')': # term of dilimiter
                self.is_terminal = True
                return

            ret = self.do_parse(tokens)
            for child in self.children_list:
                self.vars.update(child.vars)

            return ret

    def walk(self, depth):
        line = ' ' * depth * 6
        line += '|-- '
        line += str(self.name)
        #line += str(self.vars)
        line += '\n'
        print(line)
        for child in self.children_list:
            child.walk(depth + 1)

