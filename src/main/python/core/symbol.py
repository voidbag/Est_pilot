from collections import deque
from abc import ABCMeta, abstractmethod
from queue import Queue

class Symbol:
    def __init__(self):
        self.children_list = []
        self.name = ''
        self.is_terminal = False

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
                self.is_terminal = True
                return

            self.fill_children_list(tokens)

    def walk(self, depth):
        line = ' ' * depth * 6
        line += '|-- '
        line += str(self.name)
        line += '\n'

        print(line)
        for child in self.children_list:
            child.walk(depth + 1)
