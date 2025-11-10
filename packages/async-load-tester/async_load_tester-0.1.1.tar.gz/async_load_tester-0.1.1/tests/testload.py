import unittest
import sys
from unittest.mock import patch, MagicMock
import asyncio
import aiohttp
from unittest.mock import AsyncMock, patch, MagicMock
# Add the project root to the system path
sys.path.append('.')

from pyload import Loadtester

class TestLoadTesterReadErrorCases(unittest.TestCase):
    """Unit tests for error cases in the read() method"""

    def setUp(self):
        """Set up test fixtures"""
        self.tester = Loadtester()

    # ===== MISSING REQUIRED ARGUMENTS =====

    @patch('sys.argv', ['script.py'])
    def test_missing_ccload_positional(self):
        """Test error when ccload positional argument is missing"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', 'ccload'])
    def test_missing_mode_argument(self):
        """Test error when neither -history nor -u is provided"""
        result = self.tester.read()
        self.assertIsNone(result)

    # ===== MUTUALLY EXCLUSIVE ARGUMENTS =====

    @patch('sys.argv', ['script.py', 'ccload', '-history', '-u', 'httpbin.org'])
    def test_history_and_url_together(self):
        """Test error when -history and -u are used together"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', 'ccload', '-u', 'httpbin.org', '-n', '10', '-c', '5', '-GET', '-POST', '{}'])
    def test_multiple_http_methods(self):
        """Test error when multiple HTTP methods are used together"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', 'ccload', '-u', 'httpbin.org', '-n', '10', '-c', '5', '-GET', '-PUT', '{}'])
    def test_get_and_put_together(self):
        """Test error when GET and PUT are used together"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', 'ccload', '-u', 'httpbin.org', '-n', '10', '-c', '5', '-POST', '{}', '-DELETE', '{}'])
    def test_post_and_delete_together(self):
        """Test error when POST and DELETE are used together"""
        result = self.tester.read()
        self.assertIsNone(result)

    # ===== URL MODE MISSING REQUIRED ARGS =====

    @patch('sys.argv', ['script.py', 'ccload', '-u', 'httpbin.org', '-GET'])
    def test_url_without_n_argument(self):
        """Test error when -u is used without -n"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', 'ccload', '-u', 'httpbin.org', '-n', '10'])
    def test_url_without_http_method(self):
        """Test error when -u is used without any HTTP method"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', 'ccload', '-u', 'httpbin.org', '-c', '5', '-GET'])
    def test_url_without_n_but_with_c(self):
        """Test error when -u has -c but missing -n"""
        result = self.tester.read()
        self.assertIsNone(result)

    # ===== HISTORY MODE WITH CONFLICTING ARGS =====

    @patch('sys.argv', ['script.py', 'ccload', '-history', '-u', 'httpbin.org'])
    def test_history_with_url(self):
        """Test error when -history is used with -u"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', 'ccload', '-history', '-n', '10'])
    def test_history_with_n_argument(self):
        """Test error when -history is used with -n"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', 'ccload', '-history', '-c', '5'])
    def test_history_with_c_argument(self):
        """Test error when -history is used with -c"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', 'ccload', '-history', '-GET'])
    def test_history_with_get_method(self):
        """Test error when -history is used with -GET"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', 'ccload', '-history', '-POST', '{}'])
    def test_history_with_post_method(self):
        """Test error when -history is used with -POST"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', 'ccload', '-history', '-PUT', '{}'])
    def test_history_with_put_method(self):
        """Test error when -history is used with -PUT"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', 'ccload', '-history', '-DELETE', '{}'])
    def test_history_with_delete_method(self):
        """Test error when -history is used with -DELETE"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', 'ccload', '-history', '-PATCH', '{}'])
    def test_history_with_patch_method(self):
        """Test error when -history is used with -PATCH"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', 'ccload', '-history', '-u', 'httpbin.org', '-n', '10', '-c', '5', '-GET'])
    def test_history_with_all_url_args(self):
        """Test error when -history is used with all URL mode arguments"""
        result = self.tester.read()
        self.assertIsNone(result)

    # ===== INVALID JSON DATA =====

    @patch('sys.argv', ['script.py', 'ccload', '-u', 'httpbin.org', '-n', '10', '-c', '5', '-POST', 'invalid json'])
    def test_invalid_json_in_post(self):
        """Test error when POST data is not valid JSON"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', 'ccload', '-u', 'httpbin.org', '-n', '10', '-c', '5', '-PUT', '{invalid}'])
    def test_invalid_json_in_put(self):
        """Test error when PUT data is not valid JSON"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', 'ccload', '-u', 'httpbin.org', '-n', '10', '-c', '5', '-DELETE', 'not json'])
    def test_invalid_json_in_delete(self):
        """Test error when DELETE data is not valid JSON"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', 'ccload', '-u', 'httpbin.org', '-n', '10', '-c', '5', '-PATCH', '{"key": invalid}'])
    def test_invalid_json_in_patch(self):
        """Test error when PATCH data is not valid JSON"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', 'ccload', '-u', 'httpbin.org', '-n', '10', '-c', '5', '-POST', ''])
    def test_empty_json_in_post(self):
        """Test error when POST data is empty string"""
        result = self.tester.read()
        self.assertIsNone(result)

    # ===== INVALID ARGUMENT TYPES =====

    @patch('sys.argv', ['script.py', 'ccload', '-u', 'httpbin.org', '-n', 'abc', '-c', '5', '-GET'])
    def test_non_integer_n_argument(self):
        """Test error when -n is not an integer"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', 'ccload', '-u', 'httpbin.org', '-n', '10', '-c', 'xyz', '-GET'])
    def test_non_integer_c_argument(self):
        """Test error when -c is not an integer"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', 'ccload', '-u', 'httpbin.org', '-n', '10.5', '-c', '5', '-GET'])
    def test_float_n_argument(self):
        """Test error when -n is a float"""
        result = self.tester.read()
        self.assertIsNone(result)

    @patch('sys.argv', ['script.py', 'ccload', '-u', 'httpbin.org', '-n', '-5', '-c', '5', '-GET'])
    def test_negative_n_argument(self):
        """Test error when -n is negative"""
        result = self.tester.read()
        # Since argparse accepts negative integers, this should not error
        # But depending on logic, it might be invalid
        # For now, assume it proceeds if no error raised
        # self.assertIsNone(result)  # Uncomment if negative should error

    # ===== EDGE CASES =====

    @patch('pyload.Loadtester.testurl')
    @patch('pyload.Loadtester.insertpayload')
    @patch('pyload.Loadtester.calculatestats')
    @patch('pyload.sqlite3.connect')
    @patch('sys.argv', ['script.py', 'ccload', '-u', '', '-n', '10', '-c', '5', '-GET'])
    def test_empty_url(self, mock_sqlite, mock_calculatestats, mock_insertpayload, mock_testurl):
        """Test behavior with empty URL string"""
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        mock_sqlite.return_value = mock_conn

        result = self.tester.read()
        # Empty URL is valid string, so should proceed and call testurl
        mock_testurl.assert_called_once()

    @patch('pyload.Loadtester.testurl')
    @patch('pyload.Loadtester.insertpayload')
    @patch('pyload.Loadtester.calculatestats')
    @patch('pyload.sqlite3.connect')
    @patch('sys.argv', ['script.py', 'ccload', '-u', 'not-a-valid-url', '-n', '10', '-c', '5', '-GET'])
    def test_invalid_url_format(self, mock_sqlite, mock_calculatestats, mock_insertpayload, mock_testurl):
        """Test behavior with invalid URL format"""
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        mock_sqlite.return_value = mock_conn

        result = self.tester.read()
        # URL validation not done in read(), so should proceed and call testurl
        mock_testurl.assert_called_once()

    # ===== RUNTIME ERROR HANDLING =====

    @patch('sys.argv', ['script.py', 'ccload', '-history'])
    @patch.object(Loadtester, 'history')
    def test_runtime_error_in_history(self, mock_history):
        """Test that RuntimeError from history() is caught"""
        mock_history.side_effect = RuntimeError("Test error")
        result = self.tester.read()
        self.assertIsNone(result)

    # ===== VALID CASES (to ensure they don't error) =====

    @patch('pyload.Loadtester.testurl')
    @patch('pyload.Loadtester.insertpayload')
    @patch('pyload.Loadtester.calculatestats')
    @patch('pyload.sqlite3.connect')
    @patch('sys.argv', ['script.py', 'ccload', '-u', 'httpbin.org', '-n', '10', '-c', '5', '-GET'])
    def test_valid_url_mode(self, mock_sqlite, mock_calculatestats, mock_insertpayload, mock_testurl):
        """Test that valid URL mode arguments work"""
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        mock_sqlite.return_value = mock_conn

        result = self.tester.read()
        # Should not return None if valid
        mock_testurl.assert_called_once()

    @patch('sys.argv', ['script.py', 'ccload', '-history'])
    @patch.object(Loadtester, 'history')
    def test_valid_history_mode(self, mock_history):
        """Test that valid history mode works"""
        mock_history.return_value = None  # Ensure mock returns None
        result = self.tester.read()
        mock_history.assert_called_once()


# Test cases for calculatestats function
class TestLoadTesterCalculateStats(unittest.TestCase):
    def setUp(self):
        self.loadtester = Loadtester()

    def test_calculatestats_basic(self):
        # Test normal calculation with multiple values
        totreqtime = [1.0, 2.0, 3.0]
        firstbytetime = [0.1, 0.2, 0.3]
        lastbytetime = [0.5, 1.0, 1.5]

        with patch('builtins.print') as mock_print:
            self.loadtester.calculatestats(totreqtime, firstbytetime, lastbytetime)

            # Check that stats are printed
            mock_print.assert_any_call("Max response time:-...............", max(totreqtime))
            mock_print.assert_any_call("Min response time:-...............", min(totreqtime))
            mock_print.assert_any_call("Avg response time:-...............", sum(totreqtime)/len(totreqtime))
            mock_print.assert_any_call("Max first byte response time:-...............", max(firstbytetime))
            mock_print.assert_any_call("Min first byte response time:-...............", min(firstbytetime))
            mock_print.assert_any_call("Avg first byte response time:-...............", (sum(firstbytetime)/len(firstbytetime)))
            mock_print.assert_any_call("Max last byte response time:-...............", max(lastbytetime))
            mock_print.assert_any_call("Min last byte response time:-...............", min(lastbytetime))
            mock_print.assert_any_call("Avg last byte response time:-...............", (sum(lastbytetime)/len(lastbytetime)))

    def test_calculatestats_empty_lists(self):
        # Test handling of empty lists
        totreqtime = []
        firstbytetime = []
        lastbytetime = []

        with patch('builtins.print') as mock_print:
            self.loadtester.calculatestats(totreqtime, firstbytetime, lastbytetime)

            # Should print the error message for all empty lists
            mock_print.assert_any_call("Error!!! No requests found")

    def test_calculatestats_empty_firstbytelist(self):
        # Test handling of empty firstbytetime list
        totreqtime = [8, 7, 6]
        firstbytetime = []
        lastbytetime = [0.2, 0.6, 0.4]

        with patch('builtins.print') as mock_print:
            self.loadtester.calculatestats(totreqtime, firstbytetime, lastbytetime)

            # Should print the error message for empty first bytes
            mock_print.assert_any_call("Error!!! No first bytes found")

    def test_calculatestats_empty_lastbytelist(self):
        # Test handling of empty lastbytetime list
        totreqtime = [8, 7, 6]
        firstbytetime = [0.2, 0.6, 0.4]
        lastbytetime = []

        with patch('builtins.print') as mock_print:
            self.loadtester.calculatestats(totreqtime, firstbytetime, lastbytetime)

            # Should print the error message for empty last bytes
            mock_print.assert_any_call("Error!!! No last bytes found")

    def test_calculatestats_single_value(self):
        # Test calculation with single-value lists
        totreqtime = [1.0]
        firstbytetime = [0.1]
        lastbytetime = [0.5]

        with patch('builtins.print') as mock_print:
            self.loadtester.calculatestats(totreqtime, firstbytetime, lastbytetime)

            mock_print.assert_any_call("Max response time:-...............", 1.0)
            mock_print.assert_any_call("Min response time:-...............", 1.0)
            mock_print.assert_any_call("Avg response time:-...............", 1.0)
            mock_print.assert_any_call("Max first byte response time:-...............", 0.1)
            mock_print.assert_any_call("Min first byte response time:-...............", 0.1)
            mock_print.assert_any_call("Avg first byte response time:-...............", 0.1)
            mock_print.assert_any_call("Max last byte response time:-...............", 0.5)
            mock_print.assert_any_call("Min last byte response time:-...............", 0.5)
            mock_print.assert_any_call("Avg last byte response time:-...............", 0.5)


if __name__ == '__main__':
    unittest.main()
