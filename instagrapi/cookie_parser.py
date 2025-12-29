"""
Cookie Parser Utility

Parses browser-exported cookie JSON data and converts it to usable cookie strings
for Instagram authentication.
"""

import json
from typing import Dict, List, Optional, Union


def parse_browser_cookies_json(
    json_data: Union[str, List[Dict]],
    include_all: bool = True
) -> str:
    """
    Parse browser-exported cookie JSON and convert to cookie string format.

    This function converts cookie data exported from browser extensions (like EditThisCookie)
    or DevTools into the cookie string format required by instagrapi.

    Parameters
    ----------
    json_data : Union[str, List[Dict]]
        Either a JSON string or a list of cookie dictionaries.
        Each cookie dict should have at least 'name' and 'value' keys.

        Expected format:
        [
            {
                "domain": ".instagram.com",
                "name": "sessionid",
                "value": "123456%3Axxx%3A27%3A...",
                "expirationDate": 1798244001670,
                ...
            },
            ...
        ]

    include_all : bool, optional
        If True, includes all cookies. If False, only includes essential cookies
        (sessionid, mid, csrftoken, ds_user_id, ig_did, datr, wd, rur).
        Default is True.

    Returns
    -------
    str
        Cookie string in format "key1=value1; key2=value2; ..."

    Raises
    ------
    ValueError
        If json_data is invalid or no cookies found

    Examples
    --------
    >>> json_str = '[{"name":"sessionid","value":"123%3Axxx"},{"name":"mid","value":"yyy"}]'
    >>> cookie_string = parse_browser_cookies_json(json_str)
    >>> print(cookie_string)
    sessionid=123%3Axxx; mid=yyy

    >>> # Parse from list
    >>> cookies = [{"name": "sessionid", "value": "123%3Axxx"}]
    >>> cookie_string = parse_browser_cookies_json(cookies, include_all=False)
    """
    # Parse JSON string if needed
    if isinstance(json_data, str):
        try:
            cookies = json.loads(json_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
    else:
        cookies = json_data

    if not isinstance(cookies, list):
        raise ValueError("Cookie data must be a JSON array/list")

    if not cookies:
        raise ValueError("No cookies found in data")

    # Essential cookies for Instagram authentication
    essential_cookies = {
        'sessionid',    # Required - authentication session
        'mid',          # Machine ID
        'csrftoken',    # CSRF protection token
        'ds_user_id',   # User ID
        'ig_did',       # Instagram device ID
        'datr',         # Device tracking token
        'wd',           # Window dimensions
        'rur',          # Routing info
    }

    # Extract cookie name-value pairs
    cookie_pairs = []
    for cookie in cookies:
        if not isinstance(cookie, dict):
            continue

        name = cookie.get('name', '').strip()
        value = cookie.get('value', '').strip()

        if not name or not value:
            continue

        # Filter cookies if needed
        if not include_all and name not in essential_cookies:
            continue

        cookie_pairs.append(f"{name}={value}")

    if not cookie_pairs:
        raise ValueError("No valid cookies found (cookies must have 'name' and 'value' fields)")

    return '; '.join(cookie_pairs)


def parse_cookies_file(
    file_path: str,
    line_number: Optional[int] = None,
    include_all: bool = True
) -> Union[str, List[str]]:
    """
    Parse cookies from a file containing JSON cookie arrays (one per line).

    This is useful for batch processing multiple cookie sets, such as those
    stored in the format shown in fun-docs/10 COOKIES.txt.

    Parameters
    ----------
    file_path : str
        Path to the file containing cookie JSON data (one JSON array per line)

    line_number : Optional[int], optional
        If specified, only parse the cookie at this line number (1-indexed).
        If None, parse all lines.

    include_all : bool, optional
        If True, includes all cookies. If False, only includes essential cookies.
        Default is True.

    Returns
    -------
    Union[str, List[str]]
        If line_number is specified, returns a single cookie string.
        Otherwise, returns a list of cookie strings (one per line).

    Raises
    ------
    FileNotFoundError
        If the file doesn't exist
    ValueError
        If line_number is out of range or cookies are invalid

    Examples
    --------
    >>> # Parse specific line
    >>> cookie_str = parse_cookies_file('cookies.txt', line_number=1)
    >>> print(cookie_str)
    sessionid=xxx; mid=yyy; ...

    >>> # Parse all lines
    >>> all_cookies = parse_cookies_file('cookies.txt')
    >>> for i, cookie in enumerate(all_cookies, 1):
    ...     print(f"Account {i}: {cookie[:50]}...")
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        raise FileNotFoundError(f"Cookie file not found: {file_path}")

    if not lines:
        raise ValueError(f"No cookie data found in file: {file_path}")

    # Parse specific line
    if line_number is not None:
        if line_number < 1 or line_number > len(lines):
            raise ValueError(
                f"Line number {line_number} out of range (file has {len(lines)} lines)"
            )

        line_data = lines[line_number - 1]
        return parse_browser_cookies_json(line_data, include_all=include_all)

    # Parse all lines
    results = []
    for i, line_data in enumerate(lines, 1):
        try:
            cookie_str = parse_browser_cookies_json(line_data, include_all=include_all)
            results.append(cookie_str)
        except ValueError as e:
            print(f"Warning: Failed to parse line {i}: {e}")
            continue

    if not results:
        raise ValueError("Failed to parse any valid cookies from file")

    return results


def extract_cookie_info(cookie_string: str) -> Dict[str, str]:
    """
    Extract individual cookie values from a cookie string.

    Utility function to parse a cookie string and extract specific values.

    Parameters
    ----------
    cookie_string : str
        Cookie string in format "key1=value1; key2=value2; ..."

    Returns
    -------
    Dict[str, str]
        Dictionary mapping cookie names to values

    Examples
    --------
    >>> cookie = "sessionid=123%3Axxx; mid=yyy; ds_user_id=123"
    >>> info = extract_cookie_info(cookie)
    >>> print(info['sessionid'])
    123%3Axxx
    >>> print(info.get('mid'))
    yyy
    """
    cookies = {}
    for pair in cookie_string.split(';'):
        pair = pair.strip()
        if '=' not in pair:
            continue

        key, value = pair.split('=', 1)
        cookies[key.strip()] = value.strip()

    return cookies


def get_sessionid_from_json(json_data: Union[str, List[Dict]]) -> Optional[str]:
    """
    Extract only the sessionid value from browser cookie JSON.

    Quick utility to get just the sessionid, which is the minimum required
    for authentication.

    Parameters
    ----------
    json_data : Union[str, List[Dict]]
        Browser cookie JSON data

    Returns
    -------
    Optional[str]
        The sessionid value, or None if not found

    Examples
    --------
    >>> json_str = '[{"name":"sessionid","value":"123%3Axxx"},{"name":"mid","value":"yyy"}]'
    >>> sessionid = get_sessionid_from_json(json_str)
    >>> print(sessionid)
    123%3Axxx
    """
    # Parse JSON string if needed
    if isinstance(json_data, str):
        try:
            cookies = json.loads(json_data)
        except json.JSONDecodeError:
            return None
    else:
        cookies = json_data

    if not isinstance(cookies, list):
        return None

    # Find sessionid cookie
    for cookie in cookies:
        if isinstance(cookie, dict) and cookie.get('name') == 'sessionid':
            return cookie.get('value')

    return None
