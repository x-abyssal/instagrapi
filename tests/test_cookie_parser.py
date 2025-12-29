"""
Tests for cookie parser utilities
"""

import json
import tempfile
import unittest

from instagrapi.cookie_parser import (
    extract_cookie_info,
    get_sessionid_from_json,
    parse_browser_cookies_json,
    parse_cookies_file,
)


class CookieParserTestCase(unittest.TestCase):
    """Test cookie parser utilities"""

    def setUp(self):
        """Set up test data"""
        self.sample_json = '''[
            {
                "domain": ".instagram.com",
                "name": "sessionid",
                "value": "79608022750%3AGoXS08csI4bD7B%3A1%3AAYjAwVRYge4eQaVH"
            },
            {
                "domain": ".instagram.com",
                "name": "mid",
                "value": "aUxY0wABAAHc6RX2S4k5JBIWSqSr"
            },
            {
                "domain": ".instagram.com",
                "name": "csrftoken",
                "value": "s4YSjJRfSiALNClHfcYvuczbqosDoe5k"
            },
            {
                "domain": ".instagram.com",
                "name": "ds_user_id",
                "value": "79608022750"
            }
        ]'''

        self.sample_list = [
            {"name": "sessionid", "value": "123%3Axxx"},
            {"name": "mid", "value": "yyy"},
        ]

    def test_parse_json_string(self):
        """Test parsing JSON string"""
        result = parse_browser_cookies_json(self.sample_json)

        self.assertIn("sessionid=", result)
        self.assertIn("mid=", result)
        self.assertIn("csrftoken=", result)
        self.assertIn("ds_user_id=", result)

        # Verify format
        parts = result.split('; ')
        self.assertEqual(len(parts), 4)

    def test_parse_list(self):
        """Test parsing Python list"""
        result = parse_browser_cookies_json(self.sample_list)

        self.assertIn("sessionid=123%3Axxx", result)
        self.assertIn("mid=yyy", result)

    def test_essential_cookies_only(self):
        """Test filtering essential cookies"""
        json_with_extra = '''[
            {"name": "sessionid", "value": "xxx"},
            {"name": "mid", "value": "yyy"},
            {"name": "random_cookie", "value": "zzz"},
            {"name": "another_one", "value": "aaa"}
        ]'''

        # All cookies
        all_result = parse_browser_cookies_json(json_with_extra, include_all=True)
        self.assertIn("random_cookie=", all_result)
        self.assertIn("another_one=", all_result)

        # Essential only
        essential_result = parse_browser_cookies_json(json_with_extra, include_all=False)
        self.assertIn("sessionid=", essential_result)
        self.assertIn("mid=", essential_result)
        self.assertNotIn("random_cookie=", essential_result)
        self.assertNotIn("another_one=", essential_result)

    def test_invalid_json(self):
        """Test invalid JSON handling"""
        with self.assertRaises(ValueError):
            parse_browser_cookies_json("not valid json")

        with self.assertRaises(ValueError):
            parse_browser_cookies_json("")

        with self.assertRaises(ValueError):
            parse_browser_cookies_json("{}")  # Not an array

    def test_empty_cookies(self):
        """Test empty cookie array"""
        with self.assertRaises(ValueError):
            parse_browser_cookies_json("[]")

    def test_malformed_cookies(self):
        """Test malformed cookie objects"""
        # No name or value
        with self.assertRaises(ValueError):
            parse_browser_cookies_json('[{"foo": "bar"}]')

        # Empty values
        with self.assertRaises(ValueError):
            parse_browser_cookies_json('[{"name": "", "value": ""}]')

    def test_extract_cookie_info(self):
        """Test extracting cookie info from string"""
        cookie_str = "sessionid=123%3Axxx; mid=yyy; csrftoken=zzz"
        info = extract_cookie_info(cookie_str)

        self.assertEqual(info['sessionid'], '123%3Axxx')
        self.assertEqual(info['mid'], 'yyy')
        self.assertEqual(info['csrftoken'], 'zzz')

    def test_get_sessionid(self):
        """Test extracting sessionid only"""
        sessionid = get_sessionid_from_json(self.sample_json)
        self.assertEqual(sessionid, "79608022750%3AGoXS08csI4bD7B%3A1%3AAYjAwVRYge4eQaVH")

        # From list
        sessionid = get_sessionid_from_json(self.sample_list)
        self.assertEqual(sessionid, "123%3Axxx")

        # Not found
        sessionid = get_sessionid_from_json('[{"name": "mid", "value": "xxx"}]')
        self.assertIsNone(sessionid)

    def test_parse_file_single_line(self):
        """Test parsing specific line from file"""
        # Create temp file with compact JSON (one line per entry)
        line1 = json.dumps(json.loads(self.sample_json))  # Compact the JSON
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(line1 + '\n')
            f.write('[{"name": "sessionid", "value": "line2"}]\n')
            f.write('[{"name": "sessionid", "value": "line3"}]\n')
            temp_file = f.name

        try:
            # Parse line 1
            result = parse_cookies_file(temp_file, line_number=1)
            self.assertIn("sessionid=79608022750", result)

            # Parse line 2
            result = parse_cookies_file(temp_file, line_number=2)
            self.assertIn("sessionid=line2", result)

            # Parse line 3
            result = parse_cookies_file(temp_file, line_number=3)
            self.assertIn("sessionid=line3", result)

            # Invalid line number
            with self.assertRaises(ValueError):
                parse_cookies_file(temp_file, line_number=10)

        finally:
            import os
            os.unlink(temp_file)

    def test_parse_file_all_lines(self):
        """Test parsing all lines from file"""
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write('[{"name": "sessionid", "value": "acc1"}]\n')
            f.write('[{"name": "sessionid", "value": "acc2"}]\n')
            f.write('[{"name": "sessionid", "value": "acc3"}]\n')
            temp_file = f.name

        try:
            results = parse_cookies_file(temp_file)
            self.assertEqual(len(results), 3)
            self.assertIn("sessionid=acc1", results[0])
            self.assertIn("sessionid=acc2", results[1])
            self.assertIn("sessionid=acc3", results[2])

        finally:
            import os
            os.unlink(temp_file)

    def test_file_not_found(self):
        """Test file not found error"""
        with self.assertRaises(FileNotFoundError):
            parse_cookies_file('/nonexistent/file.txt')

    def test_real_cookie_format(self):
        """Test with real Instagram cookie format"""
        real_cookie = '''[
            {"domain":".instagram.com","expirationDate":1798244001670,"hostOnly":false,"httpOnly":false,"name":"csrftoken","path":"/","sameSite":"unspecified","secure":true,"session":false,"storeId":"1","value":"s4YSjJRfSiALNClHfcYvuczbqosDoe5k"},
            {"domain":".instagram.com","expirationDate":1798244001670,"hostOnly":false,"httpOnly":false,"name":"ds_user_id","path":"/","sameSite":"unspecified","secure":true,"session":false,"storeId":"1","value":"79608022750"},
            {"domain":".instagram.com","expirationDate":1798244001670,"hostOnly":false,"httpOnly":false,"name":"mid","path":"/","sameSite":"unspecified","secure":true,"session":false,"storeId":"1","value":"aUxY0wABAAHc6RX2S4k5JBIWSqSr"},
            {"domain":".instagram.com","expirationDate":1798244001670,"hostOnly":false,"httpOnly":false,"name":"sessionid","path":"/","sameSite":"unspecified","secure":true,"session":false,"storeId":"1","value":"79608022750%3AGoXS08csI4bD7B%3A1%3AAYjAwVRYge4eQaVH_e4RMnfQ1t6ntuneuntR7X8OdA"}
        ]'''

        result = parse_browser_cookies_json(real_cookie)

        # Verify all expected cookies are present
        self.assertIn("csrftoken=", result)
        self.assertIn("ds_user_id=79608022750", result)
        self.assertIn("mid=", result)
        self.assertIn("sessionid=79608022750%3AGoXS08csI4bD7B", result)

        # Verify sessionid extraction
        sessionid = get_sessionid_from_json(real_cookie)
        self.assertTrue(sessionid.startswith("79608022750%3A"))


if __name__ == '__main__':
    unittest.main()
