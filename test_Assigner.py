from unittest import TestCase, main
from Sim.Assigner import Assigner
import Sim.SimQueue as q
import numpy as np

class TestAssigner(TestCase):

    def setUp(self) -> None:
        self.assigner = Assigner()

    def test_assignSequential(self):
        obj = {f'Stage{i}': q.SimQueue(f'Stage{i}', self.assigner.assignInSequence) for i in range(4)}
        keys = list(obj.keys())

        for i in range(3*len(obj)):
            with self.subTest(i=i):
                expidx = i % len(obj)
                print(f'i = {i}, expidx = {expidx}')

                self.assertTrue(obj[keys[expidx]] is self.assigner.assignInSequence(obj))

    def test_assignToShortest(self):
        obj = {f'Stage{i}': q.SimQueue(f'Stage{i}', self.assigner.assignInSequence) for i in range(4)}
        keys = list(obj.keys())

        # load up initial buffers with customers
        obj[keys[0]]._buffer.extend([0]*3)
        obj[keys[1]]._buffer.extend([])
        obj[keys[2]]._buffer.append([0,])
        obj[keys[3]]._buffer.extend([0]*2)

        # this is the order in which SimQueue instances should receive customers
        objOrder = [1, 1, 2, 1, 2, 3, 0]
        assign = Assigner()

        for i in range(len(objOrder)):
            # select the Queue to assign a customer
            self.assertTrue(obj[keys[objOrder[i]]] is assign.assignToShortest(obj))

            # add an element to that Queue's buffer so that the destination selection
            # will change according to the buffer lengths
            obj[keys[objOrder[i]]]._buffer.append(0)





if __name__ == '__main__':
    main(verbosity=2)
