import inspect
import threading
import time
from datetime import datetime, timedelta, timezone
from time import sleep
from typing import Tuple

import ntplib
import requests
from dateutil import parser
from .env_vars import PRINT_CONFIGURATION_STATUSES


def is_log_argument_supported():
    try:
        signature = inspect.signature(print)
        return "log" in signature.parameters
    except (TypeError, ValueError) as err:
        return False


# Determine if the `log` argument is supported
PRINT_ARGS = {"log": False} if is_log_argument_supported() else {}


class TimeSync:
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = cls()  # Initialize singleton
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):  # Avoid reinitialization
            return
        if PRINT_CONFIGURATION_STATUSES:
            print("Configurating global time lock", **PRINT_ARGS)
        self.sync_utc_datetime, self.local_time_ms = self._fetch_utc_time()
        self._initialized = True
        if PRINT_CONFIGURATION_STATUSES:
            print("Configurating global time lock...DONE", **PRINT_ARGS)

    def _fetch_utc_time(self) -> Tuple[datetime, int]:
        try:
            return self._fetch_with_retries(self._fetch_ntp_time)
        except Exception as e:
            if PRINT_CONFIGURATION_STATUSES:
                print(f"NTP sync failed: {e}. Falling back to HTTP APIs.", **PRINT_ARGS)
            return self._fetch_with_retries(self._fetch_utc_time_from_apis)

    def _fetch_with_retries(
        self, fetch_func, retries=3, backoff_factor=1
    ) -> Tuple[datetime, int]:
        for attempt in range(retries):
            try:
                return fetch_func()
            except Exception as e:
                if PRINT_CONFIGURATION_STATUSES:
                    print(f"Attempt {attempt + 1} failed: {e}", **PRINT_ARGS)
                sleep(backoff_factor * (2**attempt))
        raise Exception("All retries failed")

    def _fetch_ntp_time(self) -> Tuple[datetime, int]:
        client = ntplib.NTPClient()
        response = client.request("pool.ntp.org", version=3)
        utc_datetime = datetime.utcfromtimestamp(response.tx_time).replace(
            tzinfo=timezone.utc
        )
        local_time_ms = int(time.time() * 1000)
        if PRINT_CONFIGURATION_STATUSES:
            print("Time successfully synced using NTP.", **PRINT_ARGS)
        return utc_datetime, local_time_ms

    def _fetch_utc_time_from_apis(self) -> Tuple[datetime, int]:
        apis = [
            "https://worldtimeapi.org/api/timezone/Etc/UTC",
            "http://worldclockapi.com/api/json/utc/now",
        ]
        for api in apis:
            try:
                response = requests.get(api, timeout=5)
                response.raise_for_status()
                data = response.json()
                if "datetime" in data:
                    utc_datetime = parser.isoparse(data["datetime"])
                elif "currentDateTime" in data:
                    utc_datetime = parser.isoparse(data["currentDateTime"])
                else:
                    raise ValueError("Unexpected API response format")
                local_time_ms = int(time.time() * 1000)
                if PRINT_CONFIGURATION_STATUSES:
                    print(f"Time successfully synced using {api}.", **PRINT_ARGS)
                return utc_datetime, local_time_ms
            except Exception as e:
                if PRINT_CONFIGURATION_STATUSES:
                    print(f"Failed to fetch time from {api}: {e}", **PRINT_ARGS)
        if PRINT_CONFIGURATION_STATUSES:
            print("All time sources failed. Falling back to system time.", **PRINT_ARGS)
        utc_datetime = datetime.now(timezone.utc)
        local_time_ms = int(time.time() * 1000)
        return utc_datetime, local_time_ms

    def get_utc_time_in_ms(self) -> int:
        current_local_time_ms = int(time.time() * 1000)
        elapsed_ms = current_local_time_ms - self.local_time_ms
        current_utc_datetime = self.sync_utc_datetime + timedelta(
            milliseconds=elapsed_ms
        )
        return int(current_utc_datetime.timestamp() * 1000)
