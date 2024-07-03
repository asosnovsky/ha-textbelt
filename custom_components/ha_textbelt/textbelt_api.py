import httpx

from datetime import datetime, timedelta
from http import HTTPStatus
from typing import NamedTuple

ErrorStr = str
ApiKey = str


class QuotaState(NamedTuple):
    quota: int | None
    last_update: datetime
    last_error: ErrorStr | None


_quotas: dict[ApiKey, QuotaState | None] = {}


class TextbeltAPI:
    def __init__(self, key: ApiKey, base_url: str = "https://textbelt.com/") -> None:
        self.key = key
        self.client = httpx.AsyncClient(base_url=base_url)
        _quotas[key] = _quotas.get(key, None)

    @property
    def quota(self):
        return _quotas.get(self.key, None)

    @quota.setter
    def quota(self, value: QuotaState):
        _quotas[self.key] = value

    async def get_balance(self) -> tuple[ErrorStr, None] | tuple[None, int]:
        if self.quota is not None:
            if self.quota.quota is not None:
                if datetime.now() - self.quota.last_update < timedelta(minutes=30):
                    return self.quota.last_error, self.quota.quota
            elif datetime.now() - self.quota.last_update < timedelta(minutes=10):
                return self.quota.last_error, self.quota.quota
        err, resp = await self._get_balance()
        if err is None:
            self.quota = QuotaState(resp, datetime.now(), None)
        else:
            self.quota = QuotaState(None, datetime.now(), err)
        return self.quota.last_error, self.quota.quota

    async def _get_balance(self) -> tuple[ErrorStr, None] | tuple[None, int]:
        resp = await self.client.get(f"/quota/{self.key}")
        if resp.status_code == HTTPStatus.OK:
            data = resp.json()
            if data["success"]:
                return None, data["quotaRemaining"]
            return resp.text, None
        return f"Unexpected status code = {resp.status_code} data = {resp.text}", None

    async def send_text(
        self,
        msg: str,
        phone: str,
    ) -> tuple[ErrorStr, None] | tuple[None, dict]:
        resp = await self.client.post(
            "/text",
            json={
                "phone": phone,
                "message": msg,
                "key": self.key,
            },
        )
        if resp.status_code == HTTPStatus.OK:
            data = resp.json()
            if data["success"]:
                if data.get("quotaRemaining", None) is not None:
                    self.quota = QuotaState(
                        data["quotaRemaining"], datetime.now(), None
                    )
                return None, data
            return data["error"], None
        return f"Unexpected status code = {resp.status_code} data = {resp.text}", None
