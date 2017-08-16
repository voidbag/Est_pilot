from collections import deque
from abc import ABCMeta, abstractmethod
from queue import Queue

class Symbol:
    children_list = []
    name = ''
    is_terminal = False

    @abstractmethod
    def fill_children_list(self, tokens):
        pass


    @abstractmethod
    def compute(self, var_dict):
        #must return value of double
        pass


    def parse(self, tokens):
        if type(tokens) is not deque:
            print('Tokens is not deque!!')
            return None
        else:
            if len(tokens) == 0:
                self.is_terminal = True
                return
            elif tokens[0] == ')': # term of dilimiter
                return

            fill_children_list(tokens)

    def walk(self, depth):
        line = ' ' * depth
        
        line.append('|-- ')
        line.append(self.name)
        line.append('\n')

        print(line)
        for child in children_list:
            child.walk(depth + 1)
