"""
jd_auth_client.py
=================
OAuth2 client for JD (京东) 自研商家授权。

说明（要点）：
- 使用 code 换取 access_token（GET 请求到 open-oauth.jd.com/oauth2/access_token）
- 使用 refresh_token 刷新（GET 请求到 open-oauth.jd.com/oauth2/refresh_token）
- 将 token 持久化到数据库（表名：jd_tokens），仅保存最新一条
- 自动在到期前 1 天刷新（京东建议在到期前一天刷新）
- 兼容多进程/多线程（使用 WhisperDB 的连接管理）
"""

import json
import datetime as dt
from typing import Optional
import time
import logging

import requests
from ..whisper_db import WhisperDB

class JDAuthClient:
    """Minimal OAuth2 client for JD (自研商家)."""

    ACCESS_URL = "https://open-oauth.jd.com/oauth2/access_token"
    REFRESH_URL = "https://open-oauth.jd.com/oauth2/refresh_token"

    def __init__(self, app_key: str, app_secret: str):
        self.app_key = app_key
        self.app_secret = app_secret
        # Load latest token if present
        self.token: Optional[dict] = self._load_latest_token()

    def _ensure_datetime(self, value):
        """Normalize value to timezone-aware UTC datetime. Accepts datetime/str/int/None."""
        if value is None:
            return None
        if isinstance(value, dt.datetime):
            return value if value.tzinfo else value.replace(tzinfo=dt.timezone.utc)
        if isinstance(value, (int, float)):
            return dt.datetime.fromtimestamp(value, tz=dt.timezone.utc)
        if isinstance(value, str):
            try:
                dtobj = dt.datetime.fromisoformat(value)
                return dtobj if dtobj.tzinfo else dtobj.replace(tzinfo=dt.timezone.utc)
            except Exception:
                formats = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S")
                for fmt in formats:
                    try:
                        dtobj = dt.datetime.strptime(value, fmt)
                        return dtobj.replace(tzinfo=dt.timezone.utc)
                    except Exception:
                        continue
        return value

    def _parse_expiry_to_datetime(self, val):
        """
        Parse various forms of expiry:
        - datetime -> ensure tz
        - numeric -> if large treat as epoch ms/epoch s, else treat as seconds from now
        - for JD responses we typically get expires_in (seconds)
        """
        if val is None:
            return None
        if isinstance(val, dt.datetime):
            return val if val.tzinfo else val.replace(tzinfo=dt.timezone.utc)
        if isinstance(val, (int, float)):
            num = int(val)
        elif isinstance(val, str):
            try:
                num = int(val)
            except Exception:
                try:
                    num = int(float(val))
                except Exception:
                    parsed = self._ensure_datetime(val)
                    if isinstance(parsed, dt.datetime):
                        return parsed
                    return None
        else:
            return None

        now = dt.datetime.now(dt.timezone.utc)
        # if looks like epoch ms
        if num > 10**12:
            return dt.datetime.fromtimestamp(num / 1000.0, tz=dt.timezone.utc)
        if num > 10**9:
            return dt.datetime.fromtimestamp(num, tz=dt.timezone.utc)
        # otherwise treat as relative seconds
        return now + dt.timedelta(seconds=num)

    # ------------------------- DB helpers --------------------------- #
    def _load_latest_token(self) -> Optional[dict]:
        """Load latest token row from jd_tokens table."""
        with WhisperDB() as db:
            with db.connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id, access_token, refresh_token, access_expires, refresh_expires, created_at FROM jd_tokens WHERE app_key = %s ORDER BY id DESC LIMIT 1",
                    (self.app_key,),
                )
                row = cursor.fetchone()
                if row:
                    token = {
                        "id": row[0],
                        "access_token": row[1],
                        "refresh_token": row[2],
                        "access_expires": self._ensure_datetime(row[3]),
                        "refresh_expires": self._ensure_datetime(row[4]),
                        "created_at": self._ensure_datetime(row[5]),
                    }
                    self.token = token
                    return token
                return None

    # ------------------------- Public API ------------------------------------ #
    def fetch_token_with_auth_code(self, auth_code: str) -> None:
        """Use authorization code to obtain access_token (grant_type=authorization_code)."""
        params = {
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "grant_type": "authorization_code",
            "code": auth_code,
        }
        self._request_and_save(self.ACCESS_URL, params)

    def get_access_token(self) -> str:
        """Return a valid access_token. If necessary, refresh or exchange a recent auth_code."""
        now = dt.datetime.now(dt.timezone.utc)

        # If refresh_token missing or expired -> try using a recent auth_code or raise
        refresh_exp = self._ensure_datetime(self.token.get("refresh_expires")) if self.token else None
        if (self.token is None) or (refresh_exp is None) or (now >= refresh_exp):
            recent_code = None
            try:
                with WhisperDB() as db:
                    with db.connection.cursor() as cursor:
                        cursor.execute(
                            """
                            SELECT auth_code
                            FROM jd_auth_codes
                            WHERE app_key = %s and created_at > NOW() - INTERVAL 10 MINUTE
                            ORDER BY created_at DESC
                            LIMIT 1
                            """,
                            (self.app_key,),
                        )
                        row = cursor.fetchone()
                        if row:
                            recent_code = row[0]
            except Exception as exc:
                logging.error("Unable to query auth_code table: %s", exc)

            if recent_code:
                logging.info("Using recent auth_code to obtain new tokens...")
                self.fetch_token_with_auth_code(recent_code)
            else:
                logging.warning("refresh_token & auth_code both expired; manual re-auth required.")
                raise RuntimeError("需要重新授权.")

        # If access_token is within 1 day of expiry (recommended) refresh it
        if self._is_access_expired():
            self._refresh_token()

        return self.token["access_token"]

    # -------------------- Token refresh / storage --------------------------- #
    def _is_access_expired(self) -> bool:
        """Consider access token expired if within 1 day of expiry or missing."""
        if not self.token:
            return True
        access_exp = self._ensure_datetime(self.token.get("access_expires"))
        if not access_exp:
            return True
        return dt.datetime.now(dt.timezone.utc) >= access_exp - dt.timedelta(days=1)

    def _refresh_token(self) -> None:
        """Refresh token using JD refresh endpoint."""
        params = {
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.token["refresh_token"],
        }
        self._request_and_save(self.REFRESH_URL, params)

    def _request_and_save(self, url: str, params: dict) -> None:
        """Perform GET request to JD OAuth endpoints and persist the returned tokens."""
        max_attempts = 3
        backoff = 1
        body = None
        for attempt in range(1, max_attempts + 1):
            try:
                logging.debug("Request URL: %s params: %s", url, json.dumps(params, ensure_ascii=False))
                resp = requests.get(url, params=params, timeout=10)
                resp.raise_for_status()
                body = resp.json()
                break
            except requests.exceptions.RequestException as exc:
                logging.warning("Request attempt %d failed: %s", attempt, exc)
                if attempt < max_attempts:
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                else:
                    logging.error("All request attempts failed.")
                    raise
            except ValueError as exc:
                logging.error("Failed to decode JSON response: %s", exc)
                raise

        logging.debug("Response body: %s", json.dumps(body, ensure_ascii=False))

        # JD returns access_token on success. On error typically returns error fields.
        access_token = body.get("access_token")
        refresh_token = body.get("refresh_token")
        expires_in = body.get("expires_in")  # seconds
        xid = body.get("xid") or body.get("openId") or body.get("x_id")  # best-effort

        if not access_token or not refresh_token:
            logging.error("Token response missing access_token or refresh_token: %s", body)
            raise RuntimeError("Invalid token response from JD: %s" % json.dumps(body, ensure_ascii=False))

        now = dt.datetime.now(dt.timezone.utc)
        access_expires = self._parse_expiry_to_datetime(expires_in) or now
        # JD may not return refresh_expires; set a conservative long expiry (1 year) when missing
        refresh_expires = None
        # if response contains refresh_expires or refresh_expires_in, parse it
        if "refresh_expires" in body:
            refresh_expires = self._parse_expiry_to_datetime(body.get("refresh_expires"))
        elif "refresh_expires_in" in body:
            refresh_expires = self._parse_expiry_to_datetime(body.get("refresh_expires_in"))
        if refresh_expires is None:
            refresh_expires = now + dt.timedelta(days=365)

        canonical = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "access_expires": access_expires,
            "refresh_expires": refresh_expires,
            "xid": xid,
        }

        self._save_token(canonical)

    def _save_token(self, data: dict) -> None:
        """Persist token pair to jd_tokens and update in-memory copy."""
        now = dt.datetime.now(dt.timezone.utc)
        access_token = data["access_token"]
        refresh_token = data["refresh_token"]
        access_expires = data.get("access_expires") or now
        refresh_expires = data.get("refresh_expires") or (now + dt.timedelta(days=365))

        with WhisperDB() as db:
            with db.connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO jd_tokens (
                        app_key, xid, access_token,
                        refresh_token, access_expires, refresh_expires, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        self.app_key,
                        data.get("xid"),
                        access_token,
                        refresh_token,
                        access_expires,
                        refresh_expires,
                        now,
                    ),
                )
                last_id = cursor.lastrowid
            db.commit()

        self.token = {
            "id": last_id,
            "app_key": self.app_key,
            "xid": data.get("xid"),
            "access_token": access_token,
            "refresh_token": refresh_token,
            "access_expires": access_expires,
            "refresh_expires": refresh_expires,
            "created_at": now,
        }
