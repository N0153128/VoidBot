import git
from typing import Any, Dict, List
from pytonapi.rest.client import TonapiRestClient
from config import *
import asyncio


class Motd:
    def __init__(self, api_key: str, **kwargs) -> None:
        self._client = TonapiRestClient(api_key=api_key, **kwargs)
        self.rates_json: Dict[str, Any] = {}
        self.gbp_rate: float = 0.0
        self.balance: float = 0.0
        self._initialized = False

    async def initialize(self) -> None:
        """Fetch rates and balance. Called lazily on first begin_push."""
        self.rates_json = await self.get_prices(
            tokens=['TON', 'EQBCFwW8uFUh-amdRmNY9NyeDEaeDYXd9ggJGsicpqVcHq7B'],
            currencies=['TON', 'GBP'],
        )
        self.gbp_rate = self.rates_json['rates']['TON']['prices']['GBP']
        self.balance = await self.get_balance()
        self._initialized = True

    def get_git_commits(self, path: str) -> str:
        repo = git.Repo(path)
        return repo.git.rev_list('--count', 'HEAD')

    async def get_balance(self) -> float:
        account = await self._client.accounts.get_account(account_id=ACCOUNT_ID)
        balance = account.balance
        # 0.x returned a Balance model with .to_amount(); 2.x returns raw nanotons
        if hasattr(balance, 'to_amount'):
            return balance.to_amount()
        return round(int(balance) / 1e9, 2)

    async def get_prices(self, tokens: List[str], currencies: List[str]) -> Dict[str, Any]:
        return await self._client.rates.get_rates(tokens=tokens, currencies=currencies)

    def get_payload(self) -> str:
        payload = f'''
            24 have passed, wake up.
            Current Weather:
            # Highest temperature today:
            # Rain possibility:

            Ton coins holding: {self.balance}
            Ton Pirce: {round(self.gbp_rate, 2)}
            current balance: {round(self.balance*self.gbp_rate, 2)}

            Commits for Void Bot: {self.get_git_commits(VOID_BOT)}
            Commits for ALTNET: {self.get_git_commits(ALTNET)}
            Commits for DigiRunner: {self.get_git_commits(DIGIRUNNER)}
            Commits for N0153.tech: {self.get_git_commits(N0153WEB)}\n
            Commits for UAKAWAI: {self.get_git_commits(UAKAWAI)}\n

            '''
        return payload

    async def begin_push(self, item) -> str:
        if not self._initialized:
            await self.initialize()
        return self.get_payload()

# motd = Motd(API_KEY)
# asyncio.run(motd.initialize())
# print(motd.get_payload())
