import unittest

import frametimer

class TestInterface(unittest.TestCase):
	def test_default_constructor_is_fps(self):
		ft = frametimer.FrameTimer(100)
		self.assertEqual(ft.target_delay, 0.01)

	def test_fps(self):
		ft = frametimer.FrameTimer(fps=10)
		self.assertEqual(ft.target_delay, 0.1)

	def test_delay(self):
		ft = frametimer.FrameTimer(delay=0.99)
		self.assertEqual(ft.target_delay, 0.99)
