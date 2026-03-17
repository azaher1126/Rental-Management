import unittest
import coverage

import os

script_dir = os.path.dirname(os.path.abspath(__file__))
tests_dir = os.path.join(script_dir, 'tests')
htmlcov_dir = os.path.join(script_dir, 'htmlcov')

# Change to the root directory to ensure coverage relative paths work correctly
os.chdir(script_dir)

coverage_tracker = coverage.Coverage()
coverage_tracker.start()

test_suite = unittest.TestLoader().discover(start_dir=tests_dir, top_level_dir=script_dir)
unittest.TextTestRunner(verbosity=2).run(test_suite)

coverage_tracker.stop()
coverage_tracker.save()

print(coverage_tracker.report())
coverage_tracker.html_report(directory=htmlcov_dir)
