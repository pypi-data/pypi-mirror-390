"""
This module provides unit tests for:
    (1) UserQueryReceiver and (2) ConsoleUserQueryReceiver classes
"""

# Standard
import unittest
from unittest.mock import patch
import io

# Local
from UserQueryReceiver import _instance, UserQueryReceiver_GetCommandReceiver


class Test_ConsoleUserQueryReceiver(unittest.TestCase):
    
    def test_GetCommandReceiver(self):
        # Test that the id of object returned by UserQueryReceiver.GetCommandReceiver is the same as the id of the Global Object
        exp_val = id(_instance)
        receiver = UserQueryReceiver_GetCommandReceiver() 
        act_val = id(receiver)
        self.assertEqual(exp_val, act_val)
    
    # Apply a patch() decorator to replace keyboard input from user with a string.
    @patch('sys.stdin', io.StringIO('Typed text response'))
    def test_GetRawResponse(self):
        exp_val = 'Typed text response'
        receiver = UserQueryReceiver_GetCommandReceiver() 
        act_val = receiver.GetRawResponse('Please type a text response and hit enter.')
        self.assertEqual(exp_val, act_val)
        
    # Apply a patch() decorator to replace keyboard input from user with a string.
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_IssueErrorMessage(self, mock_stdout):
        exp_val = 'Some printed error message\n'
        receiver = UserQueryReceiver_GetCommandReceiver() 
        receiver.IssueErrorMessage('Some printed error message')
        self.assertEqual(exp_val, mock_stdout.getvalue())


if __name__ == '__main__':
    unittest.main()
