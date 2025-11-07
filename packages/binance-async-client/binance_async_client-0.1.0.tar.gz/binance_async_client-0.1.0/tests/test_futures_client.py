"""Integration tests for signed Futures endpoints.

These tests make real requests to Binance Futures REST API. They require
valid API credentials to be present in environment variables:

    DEBRIEF_BINANCE_API_KEY
    DEBRIEF_BINANCE_API_SECRET

The tests are intentionally lightweight: they only verify that the signed
endpoints respond successfully and return data structures of the expected
shape. They do not assert on business-specific content to keep them stable
even when the account has no historical orders or income records.
"""

import os
import re
import subprocess
import time
import unittest
from pathlib import Path
from typing import Optional, Tuple

from binance_async_client import FuturesAsyncClient


API_KEY_ENV = "DEBRIEF_BINANCE_API_KEY"
API_SECRET_ENV = "DEBRIEF_BINANCE_API_SECRET"
SHELL_CONFIG_PATHS = [Path("~/.zshrc").expanduser(), Path("~/.bashrc").expanduser()]


def _load_credentials_from_env() -> Tuple[Optional[str], Optional[str]]:
    api_key = os.getenv(API_KEY_ENV)
    api_secret = os.getenv(API_SECRET_ENV)
    if api_key and api_secret:
        return api_key, api_secret
    return None, None


def _load_credentials_from_shell_config() -> Tuple[Optional[str], Optional[str]]:
    pattern = re.compile(
        r"^\s*(?:export\s+)?(?P<key>DEBRIEF_BINANCE_API_(?:KEY|SECRET))\s*=\s*['\"]?(?P<value>[^'\"]+)"
    )
    found: dict[str, str] = {}

    for path in SHELL_CONFIG_PATHS:
        if not path.exists():
            continue
        try:
            with path.open("r", encoding="utf-8") as fp:
                for raw_line in fp:
                    line = raw_line.strip()
                    if not line or line.startswith("#"):
                        continue
                    for token in line.split():
                        match = pattern.match(token)
                        if match:
                            found[match.group("key")] = match.group("value").strip()
        except OSError:
            continue

    api_key = found.get(API_KEY_ENV)
    api_secret = found.get(API_SECRET_ENV)
    if api_key and api_secret:
        return api_key, api_secret
    return None, None


def _load_credentials_via_shell() -> Tuple[Optional[str], Optional[str]]:
    shell = os.getenv("SHELL", "/bin/zsh")
    command = (
        f"source ~/.zshrc >/dev/null 2>&1; "
        f"printf '%s\n%s' \"${API_KEY_ENV}\" \"${API_SECRET_ENV}\""
    )

    try:
        result = subprocess.run(
            [shell, "-lc", command],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None, None

    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if len(lines) >= 2:
        api_key = lines[-2]
        api_secret = lines[-1]
        if api_key and api_secret:
            return api_key, api_secret
    return None, None


def _get_credentials():
    api_key, api_secret = _load_credentials_from_env()
    if api_key and api_secret:
        return api_key, api_secret

    api_key, api_secret = _load_credentials_from_shell_config()
    if api_key and api_secret:
        return api_key, api_secret

    api_key, api_secret = _load_credentials_via_shell()
    if api_key and api_secret:
        return api_key, api_secret

    raise unittest.SkipTest(
        "Binance API credentials are not set. Please export the credentials "
        f"or define {API_KEY_ENV}/{API_SECRET_ENV} in your shell configuration."
    )


class FuturesClientSignedEndpointsTest(unittest.IsolatedAsyncioTestCase):
    """Minimal smoke tests for signed Futures endpoints."""

    async def asyncSetUp(self):
        api_key, api_secret = _get_credentials()
        self.client = FuturesAsyncClient(
            api_key=api_key,
            api_secret=api_secret,
            verify_ssl=False,
        )
        await self.client.initialize()

    async def asyncTearDown(self):
        await self.client.close()

    async def test_get_all_orders_async_returns_list(self):
        """Signed all orders endpoint responds successfully."""
        now = int(time.time() * 1000)
        start_time = now - 24 * 60 * 60 * 1000  # past 24 hours

        orders = await self.client.get_all_orders_async(
            symbol="BTCUSDT",
            start_time=start_time,
            end_time=now,
            limit=10,
            recv_window=5000,
        )

        self.assertIsInstance(orders, list)
        if orders:
            self.assertIsInstance(orders[0], dict)
            self.assertIn("symbol", orders[0])
            self.assertIn("orderId", orders[0])

    async def test_get_income_history_async_returns_list(self):
        """Signed income history endpoint responds successfully."""
        now = int(time.time() * 1000)
        start_time = now - 7 * 24 * 60 * 60 * 1000  # past 7 days

        income_records = await self.client.get_income_history_async(
            symbol="BTCUSDT",
            income_type=None,
            start_time=start_time,
            end_time=now,
            limit=50,
            recv_window=5000,
        )

        self.assertIsInstance(income_records, list)
        if income_records:
            self.assertIsInstance(income_records[0], dict)
            self.assertIn("symbol", income_records[0])
            self.assertIn("incomeType", income_records[0])


if __name__ == "__main__":
    unittest.main()

