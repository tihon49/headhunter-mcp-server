import httpx
import os
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

class HHClient:
    BASE_URL = "https://api.hh.ru"

    def __init__(self):
        self.client_id = os.getenv("HH_CLIENT_ID")
        self.client_secret = os.getenv("HH_CLIENT_SECRET")
        self.app_token = os.getenv("HH_APP_TOKEN")
        self.redirect_uri = os.getenv("HH_REDIRECT_URI")
        self.access_token: Optional[str] = os.getenv("HH_ACCESS_TOKEN")
        self.refresh_token: Optional[str] = os.getenv("HH_REFRESH_TOKEN")
        self.token_expires_at: Optional[datetime] = None

    def _get_headers(self, authenticated: bool = False) -> Dict[str, str]:
        headers = {
            "User-Agent": "JobHunter/1.0 (jhunterpro.ru)",
            "HH-User-Agent": "JobHunter/1.0 (jhunterpro.ru)"
        }

        if authenticated and self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        elif not authenticated and self.app_token:
            headers["Authorization"] = f"Bearer {self.app_token}"

        return headers

    async def search_vacancies(
        self,
        text: Optional[str] = None,
        area: Optional[int] = None,
        experience: Optional[str] = None,
        employment: Optional[str] = None,
        schedule: Optional[str] = None,
        salary: Optional[int] = None,
        only_with_salary: bool = False,
        per_page: int = 20,
        page: int = 0
    ) -> Dict[str, Any]:
        params = {
            "text": text,
            "area": area,
            "experience": experience,
            "employment": employment,
            "schedule": schedule,
            "salary": salary,
            "only_with_salary": only_with_salary,
            "per_page": per_page,
            "page": page
        }
        params = {k: v for k, v in params.items() if v is not None}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/vacancies",
                params=params,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()

    async def get_vacancy(self, vacancy_id: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/vacancies/{vacancy_id}",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()

    async def get_employer(self, employer_id: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/employers/{employer_id}",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()

    async def get_similar_vacancies(self, vacancy_id: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/vacancies/{vacancy_id}/similar_vacancies",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()

    async def get_areas(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/areas",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()

    async def get_dictionaries(self) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/dictionaries",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()

    def set_tokens(self, access_token: str, refresh_token: str, expires_in: int):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)

    async def refresh_access_token(self) -> bool:
        if not self.refresh_token:
            return False

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://hh.ru/oauth/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token
                },
                headers=self._get_headers()
            )

            if response.status_code == 200:
                data = response.json()
                self.set_tokens(
                    data["access_token"],
                    data["refresh_token"],
                    data["expires_in"]
                )
                return True
        return False

    async def apply_to_vacancy(
        self,
        vacancy_id: str,
        resume_id: str,
        letter: Optional[str] = None
    ) -> Dict[str, Any]:
        if not self.access_token:
            raise Exception("Authentication required. User must authorize via OAuth.")

        data = {
            "vacancy_id": vacancy_id,
            "resume_id": resume_id
        }
        if letter:
            data["letter"] = letter

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/negotiations",
                json=data,
                headers=self._get_headers(authenticated=True)
            )
            response.raise_for_status()
            return response.json()

    async def get_negotiations(
        self,
        per_page: int = 20,
        page: int = 0
    ) -> Dict[str, Any]:
        if not self.access_token:
            raise Exception("Authentication required.")

        params = {
            "per_page": per_page,
            "page": page
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/negotiations",
                params=params,
                headers=self._get_headers(authenticated=True)
            )
            response.raise_for_status()
            return response.json()

    async def get_resumes(self) -> Dict[str, Any]:
        if not self.access_token:
            raise Exception("Authentication required.")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/resumes/mine",
                headers=self._get_headers(authenticated=True)
            )
            response.raise_for_status()
            return response.json()

    async def get_resume(self, resume_id: str) -> Dict[str, Any]:
        if not self.access_token:
            raise Exception("Authentication required.")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/resumes/{resume_id}",
                headers=self._get_headers(authenticated=True)
            )
            response.raise_for_status()
            return response.json()
