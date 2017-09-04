from collections import deque
from abc import ABCMeta, abstractmethod
from queue import Queue

class Symbol:
    def __init__(self, parent):
        self.children_list = []
        self.name = ''
        self.is_terminal = False
        self.vars = {} #for differentiation
        self.parent = parent
        self.cache = {}
        self.invalidate = False
        '''
            x: True
            y: False
        '''
    
    @abstractmethod
    def is_num(self):
        pass
    
    @abstractmethod
    def canonicalize(self, parent = None, skip = 0):
        pass

    @abstractmethod
    def fill_children_list(self, tokens):
        pass

    @abstractmethod
    def compute(self, var_dict = {'pi' : math.pi, 'e' : math.e}, priv = None):
        #must return value of double
        pass

    @abstractmethod
    def tostring(self):
        pass

    @abstractmethod
    def diff(self, var_dict, priv = None):
        pass

    @classmethod
    def pack(cls, op, left, right):
        return None

    @abstractmethod
    def tostring():
        pass

    @abstractmethod
    def do_copy():
        pass
    
    @abstractmethod
    def delete():
        pass

    @classmethod
    def make_from_tail(cls, tail):
        assert tail.is_terminal == False
        
        obj = cls.do_copy()
        cur = tail

        #for get tail
        if isinstance(obj, Commutable):
            while cur.is_terminal == False: 
                if cur.children_list[2].is_terminal:
                    break
                cur = cur.children_list[2]
        
        if tail.children_list[0] != cls.default_op():
            d = D(1.0)
            wrapped = d
            while type(wrapped) != type(tail.children_list[1]):
                wrapped = wrapped.wrap()

            tail.parent = obj 
            wrapped.parent = obj
            obj.children_list.append(wrapped)
            obj.children_list.append(tail)

        else:
            tail.children_list[1].parent = obj
            tail.children_list[2].parent = obj
            obj.children_list = tail.children_list[1:]
        
        if isinstance(obj, Commutable):
            obj.tail = cur

        return obj

    def make_tail(self):
        tail = self.create_tail()
        tail.is_terminal = self.is_terminal
        tail.children_list.append(self.default_op())
        tail.children_list.extends(self.children_list)
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
    def pow(self, operand, parent):
        pass

    def tostring_local(self):
        key = 'tostring'
        if key in self.cache:
            return self.cache[key]
        
        val = self.tostring()
        self.cache[key] = val
        return val
        
    def update_vars(self, is_recursive = False):
        self.vars = {}
        for child in self.children_list:
            self.vars.update(child.vars)

        if is_recursive:
            if self.parent is not None:
                self.parent.update_vars(recursive)


    #TODO taill...
    def copy(self, parent):
        instance = self.do_copy()
        instance.name = self.name
        instance.is_terminal = self.is_terminal
        instance.parent = parent
        for var in self.vars:
            instance.vars[var] = self.vars[var]

        for ele in self.children_list:
            instance.children_list.append(ele.copy(instance))

        return instance

    def tostring(self):
        ret = ''

        for child in self.children_list:
            ele = child.tostring()
            if ele == '':
                continue
            if len(ret) == 0:
                ret += ele
            else:
                ret += ' ' + ele
        return ret

    def contains(self, var_dict):
        for var in var_dict:
            if var in self.vars:
                return True
        return False

    #it returns the result of  fill_children_list
    #Wrapper of fill_children_list..
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

            ret = self.fill_children_list(tokens)
            for child in self.children_list:
                self.vars.update(child.vars)

            return ret

    def walk(self, depth):
        line = ' ' * depth * 6
        line += '|-- '
        line += str(self.name)
        line += str(self.vars)
        line += '\n'

        print(line)
        for child in self.children_list:
            child.walk(depth + 1)
