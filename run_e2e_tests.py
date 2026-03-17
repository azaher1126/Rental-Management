import unittest

import os

script_dir = os.path.dirname(os.path.abspath(__file__))
tests_dir = os.path.join(script_dir, 'tests_e2e')


test_suite = unittest.TestLoader().discover(start_dir=tests_dir, top_level_dir=script_dir)
unittest.TextTestRunner(verbosity=2).run(test_suite)
