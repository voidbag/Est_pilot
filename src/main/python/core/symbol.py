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
        '''
            x: True
            y: False
        '''

    @abstractmethod
    def fill_children_list(self, tokens):
        pass

    @abstractmethod
    def compute(self, var_dict, priv = None):
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

            self.fill_children_list(tokens)
            for child in self.children_list:
                for k in child.vars:
                    self.vars[k] = True


    def walk(self, depth):
        line = ' ' * depth * 6
        line += '|-- '
        line += str(self.name)
        line += str(self.vars)
        line += '\n'

        print(line)
        for child in self.children_list:
            child.walk(depth + 1)
