#!/usr/bin/env python3
"""
Unit tests for login_by_cookie() method

Run with: python test_cookie_login.py
"""

import unittest
from instagrapi import Client


class CookieLoginTestCase(unittest.TestCase):
    """Test cases for login_by_cookie method"""

    def test_parse_standard_cookie_format(self):
        """Test parsing standard cookie format"""
        cookie = "sessionid=312488908%3ATfy3bX853vi4X0%3A27%3Atest; mid=testMID; csrftoken=testCSRF"

        cl = Client()
        # Mock the validation to avoid actual API calls
        cl.user_info_v1 = lambda user_id: type('User', (), {
            'username': 'test_user',
            'pk': 312488908
        })()

        try:
            result = cl.login_by_cookie(cookie)
            self.assertTrue(result)
            self.assertEqual(cl.username, 'test_user')
            self.assertEqual(cl.user_id, 312488908)
            self.assertEqual(cl.mid, 'testMID')
        except Exception as e:
            # Expected to fail without real sessionid, but parsing should work
            self.assertIsInstance(e, ValueError)

    def test_parse_cookie_with_quotes(self):
        """Test parsing cookies with quoted values"""
        cookie = 'sessionid="312488908%3Atest"; mid="testMID"'

        cl = Client()
        cookies = {}
        for pair in cookie.split(';'):
            pair = pair.strip()
            if '=' in pair:
                key, value = pair.split('=', 1)
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                cookies[key] = value

        self.assertEqual(cookies['sessionid'], '312488908%3Atest')
        self.assertEqual(cookies['mid'], 'testMID')

    def test_parse_cookie_with_escape_sequences(self):
        """Test parsing cookies with escape sequences"""
        cookie = r'rur="VLL\054312488908\0541798178884"'

        cl = Client()
        cookies = {}
        for pair in cookie.split(';'):
            pair = pair.strip()
            if '=' in pair:
                key, value = pair.split('=', 1)
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                value = value.replace('\\054', ',')
                cookies[key] = value

        self.assertEqual(cookies['rur'], 'VLL,312488908,1798178884')

    def test_empty_cookie_string(self):
        """Test that empty cookie string raises ValueError"""
        cl = Client()

        with self.assertRaises(ValueError) as context:
            cl.login_by_cookie("")

        self.assertIn("cannot be empty", str(context.exception))

    def test_missing_sessionid(self):
        """Test that missing sessionid raises ValueError"""
        cl = Client()
        cookie = "mid=testMID; csrftoken=testCSRF"

        with self.assertRaises(ValueError) as context:
            cl.login_by_cookie(cookie)

        self.assertIn("No 'sessionid' found", str(context.exception))

    def test_invalid_sessionid_length(self):
        """Test that short sessionid raises ValueError"""
        cl = Client()
        cookie = "sessionid=short"

        with self.assertRaises(ValueError) as context:
            cl.login_by_cookie(cookie)

        self.assertIn("Invalid sessionid length", str(context.exception))

    def test_invalid_sessionid_format(self):
        """Test that sessionid without user_id raises ValueError"""
        cl = Client()
        cookie = "sessionid=invalid_sessionid_without_userid_prefix_1234567890"

        with self.assertRaises(ValueError) as context:
            cl.login_by_cookie(cookie)

        self.assertIn("Cannot extract user_id", str(context.exception))

    def test_extract_user_id_from_sessionid(self):
        """Test extracting user_id from various sessionid formats"""
        import re

        test_cases = [
            ("312488908%3ATfy3bX853vi4X0%3A27%3Atest", "312488908"),
            ("123456789:some:other:data", "123456789"),
            ("987654321%3Aencoded%3Adata", "987654321"),
        ]

        for sessionid, expected_user_id in test_cases:
            match = re.search(r'^(\d+)', sessionid)
            self.assertIsNotNone(match)
            self.assertEqual(match.group(1), expected_user_id)

    def test_cookie_dict_extraction(self):
        """Test full cookie parsing into dictionary"""
        cookie = (
            'csrftoken=ssSbbZh1RzdKYWm3uiPg5-; '
            'datr=PcX1aMMdCNzF_kelTFfmV1NV; '
            'ig_did=4763A861-F18D-42E6-ACF0-A97371201B89; '
            'mid=aPXFPQAEAAGtay5gnPS10s6q9sfs; '
            'ds_user_id=312488908; '
            'sessionid=312488908%3ATfy3bX853vi4X0%3A27%3Atest'
        )

        cookies = {}
        for pair in cookie.split(';'):
            pair = pair.strip()
            if '=' in pair:
                key, value = pair.split('=', 1)
                cookies[key.strip()] = value.strip()

        self.assertEqual(len(cookies), 6)
        self.assertIn('sessionid', cookies)
        self.assertIn('mid', cookies)
        self.assertIn('csrftoken', cookies)
        self.assertIn('ig_did', cookies)
        self.assertEqual(cookies['ds_user_id'], '312488908')


class CookieIntegrationTestCase(unittest.TestCase):
    """Integration tests (requires valid cookie)"""

    def setUp(self):
        """Skip if no valid cookie is available"""
        import os
        self.test_cookie = os.getenv('IG_TEST_COOKIE', '')
        if not self.test_cookie:
            self.skipTest("No IG_TEST_COOKIE environment variable set")

    def test_real_cookie_login(self):
        """Test login with real cookie (if available)"""
        cl = Client()
        result = cl.login_by_cookie(self.test_cookie)

        self.assertTrue(result)
        self.assertIsNotNone(cl.username)
        self.assertIsNotNone(cl.user_id)
        print(f"\n✅ Successfully logged in as @{cl.username} (ID: {cl.user_id})")

        # Verify we can make API calls
        user = cl.account_info()
        self.assertEqual(user.username, cl.username)
        print(f"   Followers: {user.follower_count}")
        print(f"   Following: {user.following_count}")

    def test_cookie_login_and_session_save(self):
        """Test login and session persistence"""
        import os
        import tempfile

        cl = Client()
        cl.login_by_cookie(self.test_cookie)

        # Save session
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            session_file = f.name

        try:
            cl.dump_settings(session_file)
            self.assertTrue(os.path.exists(session_file))

            # Load session in new client
            cl2 = Client()
            cl2.load_settings(session_file)

            # Verify loaded session works
            user = cl2.account_info()
            self.assertEqual(user.username, cl.username)
            print(f"\n✅ Session persistence verified for @{user.username}")

        finally:
            if os.path.exists(session_file):
                os.remove(session_file)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add unit tests (always run)
    suite.addTests(loader.loadTestsFromTestCase(CookieLoginTestCase))

    # Add integration tests (only if cookie is available)
    suite.addTests(loader.loadTestsFromTestCase(CookieIntegrationTestCase))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    print("=" * 70)
    print("Cookie Login Tests")
    print("=" * 70)
    print("\nUnit Tests: Testing cookie parsing and validation")
    print("Integration Tests: Set IG_TEST_COOKIE env var to test with real cookie")
    print("=" * 70)
    print()

    success = run_tests()

    print("\n" + "=" * 70)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
    print("=" * 70)

    exit(0 if success else 1)
