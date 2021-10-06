from unittest import TestCase, main
from Sim.QueueEvent import QueueEvent


class TestQueueEvent(TestCase):

    def test_QueueEventValues(self):
        self.assertTrue('SERVICE_COMPLETION' in QueueEvent.__members__)
        self.assertTrue('SERVER_DOWN' in QueueEvent.__members__)
        self.assertTrue('SERVER_UP' in QueueEvent.__members__)

        self.assertEqual(3, len(QueueEvent.__members__))


if __name__ == '__main__':
    main(verbosity=2)
