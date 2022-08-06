from random import randint, randrange, random, seed
from math import sqrt, tanh


class OutputNeuron:

    def __init__(self):
        self.input = None

    def get_input(self, neurons):
        total = 0

        for neuron in neurons:
            total += neuron.weight * neuron.input

        self.input = total

    def get_output(self):
        return tanh(self.input)