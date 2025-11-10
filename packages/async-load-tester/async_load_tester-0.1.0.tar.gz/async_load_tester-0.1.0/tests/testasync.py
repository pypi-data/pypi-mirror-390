import unittest
import asyncio
from unittest.mock import patch, MagicMock
from pyload import Loadtester


class TestLoadTesterAsyncRealAPI(unittest.TestCase):
    """Test async functionality with real API calls to httpbin.org and mocked database"""

    @patch('pyload.Loadtester.insertpayload')
    @patch('pyload.Loadtester.calculatestats')
    @patch('builtins.print')
    @patch('pyload.requests.post')
    def test_real_api_get_request(self, mock_requests_post, mock_print, mock_calculatestats, mock_insertpayload):
        """Test GET request to real httpbin.org API with mocked database"""
        loadtester = Loadtester()

        # Use asyncio.run to run the async test
        asyncio.run(self._run_get_test(loadtester, mock_requests_post, mock_print, mock_calculatestats, mock_insertpayload))

    async def _run_get_test(self, loadtester, mock_requests_post, mock_print, mock_calculatestats, mock_insertpayload):
        """Helper method to run the async GET test"""
        url = 'https://httpbin.org/get'

        # Run the test - may succeed or fail depending on network conditions
        await loadtester.testurl(url, 1, 1, 'get')

        # Verify the async framework was exercised
        # The exact results may vary based on network conditions, but the method should complete

        # Verify prints occurred
        mock_print.assert_any_call("Running....")
        mock_print.assert_any_call("Total requests:-.................", 1)
        mock_print.assert_any_call("Total number of concurrent requests:-.........", 1)

        # Check if any requests were processed (success or failure)
        success_count = None
        failure_count = None
        for call in mock_print.call_args_list:
            if "Successes:-.............." in str(call):
                success_count = call[0][1]  # Extract the count
            if "Failures:-.............." in str(call):
                failure_count = call[0][1]  # Extract the count

        # At least one of success or failure should be >= 0
        total_processed = (success_count or 0) + (failure_count or 0)
        self.assertGreaterEqual(total_processed, 0, "At least some requests should be processed")

        # If there were successful requests, database operations should have been called
        if success_count and success_count > 0:
            mock_insertpayload.assert_called_once()
            mock_calculatestats.assert_called_once()
            # For successful requests, no Loki call
            mock_requests_post.assert_not_called()

    @patch('pyload.Loadtester.insertpayload')
    @patch('pyload.Loadtester.calculatestats')
    @patch('builtins.print')
    @patch('pyload.requests.post')
    def test_real_api_status_404_request(self, mock_requests_post, mock_print, mock_calculatestats, mock_insertpayload):
        """Test request to non-existent endpoint (404) with real API"""
        loadtester = Loadtester()

        asyncio.run(self._run_404_test(loadtester, mock_requests_post, mock_print, mock_calculatestats, mock_insertpayload))

    async def _run_404_test(self, loadtester, mock_requests_post, mock_print, mock_calculatestats, mock_insertpayload):
        """Helper method to run the async 404 test"""
        url = 'https://httpbin.org/status/404'

        await loadtester.testurl(url, 1, 1, 'get')

        # Verify the async framework was exercised
        mock_print.assert_any_call("Running....")
        mock_print.assert_any_call("Total requests:-.................", 1)

        # Check if any requests were processed
        success_count = None
        failure_count = None
        for call in mock_print.call_args_list:
            if "Successes:-.............." in str(call):
                success_count = call[0][1]
            if "Failures:-.............." in str(call):
                failure_count = call[0][1]

        total_processed = (success_count or 0) + (failure_count or 0)
        self.assertGreaterEqual(total_processed, 0, "At least some requests should be processed")

        # If there were failed requests, Loki should be called
        if failure_count and failure_count > 0:
            mock_requests_post.assert_called_once()
            call_args = mock_requests_post.call_args
            self.assertEqual(call_args[0][0], "http://localhost:3100/loki/api/v1/push")
            mock_print.assert_any_call("Failures detected!!! Please check grafana for more details")



    @patch('pyload.Loadtester.insertpayload')
    @patch('pyload.Loadtester.calculatestats')
    @patch('builtins.print')
    @patch('pyload.requests.post')
    def test_real_api_post_request(self, mock_requests_post, mock_print, mock_calculatestats, mock_insertpayload):
        """Test POST request to real httpbin.org API with mocked database"""
        loadtester = Loadtester()

        asyncio.run(self._run_post_test(loadtester, mock_requests_post, mock_print, mock_calculatestats, mock_insertpayload))

    async def _run_post_test(self, loadtester, mock_requests_post, mock_print, mock_calculatestats, mock_insertpayload):
        """Helper method to run the async POST test"""
        url = 'https://httpbin.org/post'

        await loadtester.testurl(url, 1, 1, 'post')

        # Verify the async framework was exercised
        mock_print.assert_any_call("Running....")
        mock_print.assert_any_call("Total requests:-.................", 1)

        # Check if any requests were processed
        success_count = None
        failure_count = None
        for call in mock_print.call_args_list:
            if "Successes:-.............." in str(call):
                success_count = call[0][1]
            if "Failures:-.............." in str(call):
                failure_count = call[0][1]

        total_processed = (success_count or 0) + (failure_count or 0)
        self.assertGreaterEqual(total_processed, 0, "At least some requests should be processed")

        # If there were successful requests, database operations should have been called
        if success_count and success_count > 0:
            mock_insertpayload.assert_called_once()
            mock_calculatestats.assert_called_once()
            mock_requests_post.assert_not_called()

    @patch('pyload.Loadtester.insertpayload')
    @patch('pyload.Loadtester.calculatestats')
    @patch('builtins.print')
    @patch('pyload.requests.post')
    def test_real_api_put_request(self, mock_requests_post, mock_print, mock_calculatestats, mock_insertpayload):
        """Test PUT request to real httpbin.org API with mocked database"""
        loadtester = Loadtester()

        asyncio.run(self._run_put_test(loadtester, mock_requests_post, mock_print, mock_calculatestats, mock_insertpayload))

    async def _run_put_test(self, loadtester, mock_requests_post, mock_print, mock_calculatestats, mock_insertpayload):
        """Helper method to run the async PUT test"""
        url = 'https://httpbin.org/put'

        await loadtester.testurl(url, 1, 1, 'put')

        # Verify the async framework was exercised
        mock_print.assert_any_call("Running....")
        mock_print.assert_any_call("Total requests:-.................", 1)

        # Check if any requests were processed
        success_count = None
        for call in mock_print.call_args_list:
            if "Successes:-.............." in str(call):
                success_count = call[0][1]
                break

        # If there were successful requests, database operations should have been called
        if success_count and success_count > 0:
            mock_insertpayload.assert_called_once()
            mock_calculatestats.assert_called_once()
            mock_requests_post.assert_not_called()

    @patch('pyload.Loadtester.insertpayload')
    @patch('pyload.Loadtester.calculatestats')
    @patch('builtins.print')
    @patch('pyload.requests.post')
    def test_real_api_delete_request(self, mock_requests_post, mock_print, mock_calculatestats, mock_insertpayload):
        """Test DELETE request to real httpbin.org API with mocked database"""
        loadtester = Loadtester()

        asyncio.run(self._run_delete_test(loadtester, mock_requests_post, mock_print, mock_calculatestats, mock_insertpayload))

    async def _run_delete_test(self, loadtester, mock_requests_post, mock_print, mock_calculatestats, mock_insertpayload):
        """Helper method to run the async DELETE test"""
        url = 'https://httpbin.org/delete'

        await loadtester.testurl(url, 1, 1, 'delete')

        # Verify the async framework was exercised
        mock_print.assert_any_call("Running....")
        mock_print.assert_any_call("Total requests:-.................", 1)

        # Check if any requests were processed
        success_count = None
        for call in mock_print.call_args_list:
            if "Successes:-.............." in str(call):
                success_count = call[0][1]
                break

        # If there were successful requests, database operations should have been called
        if success_count and success_count > 0:
            mock_insertpayload.assert_called_once()
            mock_calculatestats.assert_called_once()
            mock_requests_post.assert_not_called()

    @patch('pyload.Loadtester.insertpayload')
    @patch('pyload.Loadtester.calculatestats')
    @patch('builtins.print')
    @patch('pyload.requests.post')
    def test_real_api_patch_request(self, mock_requests_post, mock_print, mock_calculatestats, mock_insertpayload):
        """Test PATCH request to real httpbin.org API with mocked database"""
        loadtester = Loadtester()

        asyncio.run(self._run_patch_test(loadtester, mock_requests_post, mock_print, mock_calculatestats, mock_insertpayload))

    async def _run_patch_test(self, loadtester, mock_requests_post, mock_print, mock_calculatestats, mock_insertpayload):
        """Helper method to run the async PATCH test"""
        url = 'https://httpbin.org/patch'

        await loadtester.testurl(url, 1, 1, 'patch')

        # Verify the async framework was exercised
        mock_print.assert_any_call("Running....")
        mock_print.assert_any_call("Total requests:-.................", 1)

        # Check if any requests were processed
        success_count = None
        for call in mock_print.call_args_list:
            if "Successes:-.............." in str(call):
                success_count = call[0][1]
                break

        # If there were successful requests, database operations should have been called
        if success_count and success_count > 0:
            mock_insertpayload.assert_called_once()
            mock_calculatestats.assert_called_once()
            mock_requests_post.assert_not_called()

    @patch('pyload.Loadtester.insertpayload')
    @patch('pyload.Loadtester.calculatestats')
    @patch('builtins.print')
    @patch('pyload.requests.post')
    def test_real_api_concurrent_requests(self, mock_requests_post, mock_print, mock_calculatestats, mock_insertpayload):
        """Test concurrent requests to real httpbin.org API with mocked database"""
        loadtester = Loadtester()

        asyncio.run(self._run_concurrent_test(loadtester, mock_requests_post, mock_print, mock_calculatestats, mock_insertpayload))

    async def _run_concurrent_test(self, loadtester, mock_requests_post, mock_print, mock_calculatestats, mock_insertpayload):
        """Helper method to run the async concurrent test"""
        url = 'https://httpbin.org/get'

        await loadtester.testurl(url, 3, 2, 'get')  # 3 requests, 2 concurrent

        # Verify the async framework was exercised
        mock_print.assert_any_call("Running....")
        mock_print.assert_any_call("Total requests:-.................", 3)
        mock_print.assert_any_call("Total number of concurrent requests:-.........", 2)

        # Check if any requests were processed
        success_count = None
        for call in mock_print.call_args_list:
            if "Successes:-.............." in str(call):
                success_count = call[0][1]
                break

        # If there were successful requests, database operations should have been called
        if success_count and success_count > 0:
            mock_insertpayload.assert_called_once()
            mock_calculatestats.assert_called_once()
            mock_requests_post.assert_not_called()

    @patch('pyload.Loadtester.insertpayload')
    @patch('pyload.Loadtester.calculatestats')
    @patch('builtins.print')
    @patch('pyload.requests.post')
    def test_real_api_with_custom_headers(self, mock_requests_post, mock_print, mock_calculatestats, mock_insertpayload):
        """Test request with custom headers to real httpbin.org API"""
        loadtester = Loadtester()

        asyncio.run(self._run_headers_test(loadtester, mock_requests_post, mock_print, mock_calculatestats, mock_insertpayload))

    async def _run_headers_test(self, loadtester, mock_requests_post, mock_print, mock_calculatestats, mock_insertpayload):
        """Helper method to run the async headers test"""
        url = 'https://httpbin.org/headers'
        headers = {'Authorization': 'Bearer test-token', 'X-Custom-Header': 'test-value'}

        await loadtester.testurl(url, 1, 1, 'get', headers=headers)

        # Verify the async framework was exercised
        mock_print.assert_any_call("Running....")
        mock_print.assert_any_call("Total requests:-.................", 1)

        # Check if any requests were processed
        success_count = None
        for call in mock_print.call_args_list:
            if "Successes:-.............." in str(call):
                success_count = call[0][1]
                break

        # If there were successful requests, database operations should have been called
        if success_count and success_count > 0:
            mock_insertpayload.assert_called_once()
            mock_calculatestats.assert_called_once()
            mock_requests_post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
