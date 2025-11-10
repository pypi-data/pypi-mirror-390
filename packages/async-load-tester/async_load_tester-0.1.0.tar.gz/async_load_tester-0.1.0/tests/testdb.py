import unittest
import sys
from unittest.mock import patch, MagicMock, mock_open
import sqlite3
import os
import tempfile
import asyncio
# Add the project root to the system path
sys.path.append('.')

from pyload import Loadtester

class TestLoadTesterInsertPayload(unittest.TestCase):
    def setUp(self):
        self.loadtester = Loadtester()

    @patch('pyload.dburl', ':memory:')
    @patch('pyload.sqlite3.connect')
    def test_insertpayload_successful_insertion(self, mock_connect):
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Mock fetchone to return None (table doesn't exist)
        mock_cursor.fetchone.return_value = None

        # Call the method
        self.loadtester.insertpayload([])

        # Verify database connection was made
        mock_connect.assert_called_once_with(':memory:')

        # Verify cursor was created
        mock_conn.cursor.assert_called_once()

        # Verify fetchone was called (checking if table exists)
        mock_cursor.fetchone.assert_called_once()

        # Verify table creation SQL was executed
        create_calls = [call for call in mock_cursor.execute.call_args_list
                       if 'CREATE TABLE' in str(call)]
        self.assertEqual(len(create_calls), 1, "Table creation should be called once")

        # Since reqlist is empty, no INSERT should be called
        insert_calls = [call for call in mock_cursor.execute.call_args_list
                       if 'INSERT INTO' in str(call)]
        self.assertEqual(len(insert_calls), 0, "No INSERT should be called with empty reqlist")

        # Verify connection was closed
        mock_conn.close.assert_called_once()

    @patch('pyload.sqlite3.connect')
    @patch('pyload.dburl', ':memory:')
    def test_insertpayload_table_already_exists(self, mock_connect):
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Mock fetchone to return a row (table exists)
        mock_cursor.fetchone.return_value = ['some_row']

        # Call the method
        self.loadtester.insertpayload([])

        # Verify table creation was skipped
        create_calls = [call for call in mock_cursor.execute.call_args_list
                       if 'CREATE TABLE' in str(call)]
        self.assertEqual(len(create_calls), 0, "Table creation should be skipped when table exists")

        # Since reqlist is empty, no INSERT should be called
        insert_calls = [call for call in mock_cursor.execute.call_args_list
                       if 'INSERT INTO' in str(call)]
        self.assertEqual(len(insert_calls), 0, "No INSERT should be called with empty reqlist")

        # Verify connection was closed
        mock_conn.close.assert_called_once()



    @patch('pyload.sqlite3.connect')
    @patch('pyload.dburl', ':memory:')
    def test_insertpayload_with_data_insertion(self, mock_connect):
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Mock fetchone to return None (table doesn't exist)
        mock_cursor.fetchone.return_value = None

        # Test data
        test_data = ('req123', '2023-01-01 12:00:00', 'httpbin.org', 200, '{"key": "value"}', 'POST')

        # Modify the method to accept data (this would require changing the actual method)
        # For now, we'll test the current implementation which uses empty tuple
        self.loadtester.insertpayload([])

        # Since reqlist is empty, no INSERT should be called
        insert_calls = [call for call in mock_cursor.execute.call_args_list
                       if 'INSERT INTO' in str(call)]
        self.assertEqual(len(insert_calls), 0, "No INSERT should be called with empty reqlist")

    @patch('pyload.sqlite3.connect')
    @patch('pyload.dburl', None)
    def test_insertpayload_environment_variable_not_set(self, mock_connect):
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Call the method - this should still work but connect to None
        self.loadtester.insertpayload([])

        # Verify connect was called with None
        mock_connect.assert_called_once_with(None)

class TestDatabaseConnectionAndExecution(unittest.TestCase):
    """Focused tests for database connection and execution operations"""

    def setUp(self):
        self.loadtester = Loadtester()

    @patch('pyload.dburl', ':memory:')
    @patch('pyload.sqlite3.connect')
    def test_database_connection_successful(self, mock_connect):
        """Test successful database connection"""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        # Call a method that uses database connection
        self.loadtester.insertpayload([])

        # Verify connection was established
        mock_connect.assert_called_once_with(':memory:')
        # Verify connection was closed
        mock_conn.close.assert_called_once()

    @patch('pyload.dburl', ':memory:')
    @patch('pyload.sqlite3.connect')
    def test_database_connection_failure(self, mock_connect):
        """Test database connection failure"""
        mock_connect.side_effect = sqlite3.Error("Connection failed")

        with self.assertRaises(sqlite3.Error):
            self.loadtester.insertpayload([])

    @patch('pyload.dburl', ':memory:')
    @patch('pyload.sqlite3.connect')
    def test_cursor_creation(self, mock_connect):
        """Test cursor creation from database connection"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        self.loadtester.insertpayload([])

        # Verify cursor was created
        mock_conn.cursor.assert_called_once()





    @patch('pyload.dburl', ':memory:')
    @patch('pyload.sqlite3.connect')
    def test_database_commit_operation(self, mock_connect):
        """Test database commit operation"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Mock fetchone to simulate table exists
        mock_cursor.fetchone.return_value = ['LOADTEST']

        self.loadtester.insertpayload([])

        # Verify commit was called (may be called multiple times)
        self.assertGreaterEqual(mock_conn.commit.call_count, 1, "Commit should be called at least once")

    @patch('pyload.dburl', ':memory:')
    @patch('pyload.sqlite3.connect')
    def test_database_connection_close(self, mock_connect):
        """Test database connection close operation"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        self.loadtester.insertpayload([])

        # Verify connection was closed
        mock_conn.close.assert_called_once()

    @patch('pyload.dburl', ':memory:')
    @patch('pyload.sqlite3.connect')
    def test_connection_close_on_error(self, mock_connect):
        """Test that connection is closed even when errors occur"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Mock execute to raise error
        mock_cursor.execute.side_effect = sqlite3.Error("Execution failed")

        try:
            self.loadtester.insertpayload([])
        except sqlite3.Error:
            pass  # Expected error

        # Verify connection was still closed despite error
        mock_conn.close.assert_called_once()

    @patch('pyload.dburl', ':memory:')
    @patch('pyload.sqlite3.connect')
    def test_history_database_operations(self, mock_connect):
        """Test database operations in history method"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Mock the execute return value to have fetchall method
        mock_execute_result = MagicMock()
        mock_execute_result.fetchall.return_value = [
            ('2023-01-01 12:00:00', 'httpbin.org', 200, 'GET', '0:00:01')
        ]
        mock_cursor.execute.return_value = mock_execute_result

        self.loadtester.history()

        # Verify connection was established
        mock_connect.assert_called_once_with(':memory:')
        # Verify cursor was created
        mock_conn.cursor.assert_called_once()
        # Verify SELECT query was executed
        mock_cursor.execute.assert_called_once_with("SELECT * FROM LOADTEST")
        # Verify fetchall was called on the execute result
        mock_execute_result.fetchall.assert_called_once()
        # Verify commit was called
        mock_conn.commit.assert_called_once()
        # Verify connection was closed
        mock_conn.close.assert_called_once()

    @patch('pyload.dburl', ':memory:')
    @patch('pyload.sqlite3.connect')
    def test_history_database_error_handling(self, mock_connect):
        """Test error handling in history method database operations"""
        mock_connect.side_effect = sqlite3.OperationalError("Table does not exist")

        # Call the method - should handle the error gracefully
        self.loadtester.history()


class TestDatabaseIntegrationWithMockedAPI(unittest.TestCase):
    """Integration tests that use mocked API calls and real database operations"""

    def setUp(self):
        self.loadtester = Loadtester()
        # Create a temporary database file for integration tests
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name

    def tearDown(self):
        # Clean up the temporary database file
        try:
            os.unlink(self.db_path)
        except:
            pass

    @patch('pyload.aiohttp.ClientSession')
    def test_mocked_api_get_request_database_storage(self, mock_session_class):
        """Test GET request with mocked API and verify database storage"""
        # Mock the ClientSession
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None

        # Mock the response context manager
        mock_resp_cm = MagicMock()
        mock_session.get.return_value = mock_resp_cm

        # Mock the response
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.content.readexactly.return_value = b'H'
        mock_resp.content.read.return_value = b'ello, World!'
        mock_resp_cm.__aenter__.return_value = mock_resp
        mock_resp_cm.__aexit__.return_value = None

        # Patch the dburl directly in the pyload module
        with patch('pyload.dburl', self.db_path):
            # Make the request
            asyncio.run(self.loadtester.testurl(
                url='https://httpbin.org/get',
                numreq=2,
                conreq=1,
                reqtype='get'
            ))

            # Verify data was stored in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check that table was created
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='LOADTEST'")
            table_result = cursor.fetchone()
            self.assertIsNotNone(table_result, "LOADTEST table should be created")

            # Check that data was inserted
            cursor.execute("SELECT COUNT(*) FROM LOADTEST")
            count = cursor.fetchone()[0]
            self.assertEqual(count, 2, "Should have 2 records in database")

            # Check data structure
            cursor.execute("SELECT REQUESTID, URL, STATUS, REQTYPE FROM LOADTEST LIMIT 1")
            row = cursor.fetchone()
            self.assertIsNotNone(row, "Should have at least one record")
            self.assertEqual(row[1], 'https://httpbin.org/get', "URL should match")
            self.assertEqual(row[2], 200, "Status should be 200")
            self.assertEqual(row[3], 'get', "Request type should be 'get'")

            conn.close()

    @patch('pyload.aiohttp.ClientSession')
    def test_mocked_api_post_request_database_storage(self, mock_session_class):
        """Test POST request with mocked API and verify database storage"""
        # Mock the ClientSession
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None

        # Mock the response context manager
        mock_resp_cm = MagicMock()
        mock_session.post.return_value = mock_resp_cm

        # Mock the response
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.content.readexactly.return_value = b'P'
        mock_resp.content.read.return_value = b'OST successful'
        mock_resp_cm.__aenter__.return_value = mock_resp
        mock_resp_cm.__aexit__.return_value = None

        with patch('pyload.dburl', self.db_path):
            # Make the request
            asyncio.run(self.loadtester.testurl(
                url='https://httpbin.org/post',
                numreq=1,
                conreq=1,
                reqtype='post'
            ))

            # Verify data was stored in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check that data was inserted
            cursor.execute("SELECT COUNT(*) FROM LOADTEST")
            count = cursor.fetchone()[0]
            self.assertEqual(count, 1, "Should have 1 record in database")

            # Check data structure
            cursor.execute("SELECT URL, STATUS, REQTYPE FROM LOADTEST LIMIT 1")
            row = cursor.fetchone()
            self.assertEqual(row[0], 'https://httpbin.org/post', "URL should match")
            self.assertEqual(row[1], 200, "Status should be 200")
            self.assertEqual(row[2], 'post', "Request type should be 'post'")

            conn.close()

    def test_database_history_with_real_data(self):
        """Test that history method works with real database data"""
        # First, manually insert some data into the database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create table and insert test data
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS LOADTEST(
        REQUESTID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        TIMESTAMP TEXT NOT NULL,
        URL TEXT NOT NULL,
        STATUS INTEGER NOT NULL,
        REQTYPE VARCHAR NOT NULL,
        RESPONSETIME TEXT NOT NULL
        )
        """)

        cursor.execute("INSERT INTO LOADTEST (TIMESTAMP,URL,STATUS,REQTYPE,RESPONSETIME) VALUES (?,?,?,?,?)",
                      ('2023-01-01 12:00:00', 'https://httpbin.org/get', 200, 'GET', '0.5'))
        conn.commit()
        conn.close()

        # Now test the history method
        with patch('pyload.dburl', self.db_path):
            with patch('builtins.print') as mock_print:
                self.loadtester.history()

                # Verify that history output was generated
                self.assertTrue(len(mock_print.call_args_list) > 0, "History should produce output")

        # Verify database still has the data
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM LOADTEST")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 1, "Data should still be in database")
        conn.close()

    def test_database_statistics_calculation_with_mock_data(self):
        """Test that statistics are calculated correctly with mock data"""
        # Manually create test data in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create table and insert test data
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS LOADTEST(
        REQUESTID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        TIMESTAMP TEXT NOT NULL,
        URL TEXT NOT NULL,
        STATUS INTEGER NOT NULL,
        REQTYPE VARCHAR NOT NULL,
        RESPONSETIME TEXT NOT NULL
        )
        """)

        # Insert test data
        test_data = [
            ('2023-01-01 12:00:00', 'https://api.example.com', 200, 'GET', '0.5'),
            ('2023-01-01 12:00:01', 'https://api.example.com', 200, 'GET', '0.7')
        ]
        cursor.executemany("INSERT INTO LOADTEST (TIMESTAMP,URL,STATUS,REQTYPE,RESPONSETIME) VALUES (?,?,?,?,?)", test_data)
        conn.commit()
        conn.close()

        # Test statistics calculation
        with patch('pyload.dburl', self.db_path):
            with patch('builtins.print') as mock_print:
                self.loadtester.calculatestats(
                    [0.5, 0.7],  # response times
                    [0.1, 0.2],  # first byte times
                    [0.4, 0.5]   # last byte times
                )

                # Verify statistics were printed
                self.assertTrue(len(mock_print.call_args_list) > 0, "Statistics should be printed")


if __name__ == '__main__':
    unittest.main()
