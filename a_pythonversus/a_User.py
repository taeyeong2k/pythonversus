from dataclasses import dataclass
from typing import Optional, Dict, Any, TYPE_CHECKING

from a_pythonversus import Utils
from a_pythonversus.a_Match import Match

if TYPE_CHECKING:
    from a_pythonversus import a_MvsAPI


@dataclass
class User:
    api: 'a_MvsAPI'
    account_id: Optional[str] = None
    username: Optional[str] = None
    profile_data: Optional[Dict[str, Any]] = None
    account_data: Optional[Dict[str, Any]] = None

    @classmethod
    async def from_id(cls, api: 'a_MvsAPI', account_id: str) -> 'User':
        user = cls(api=api, account_id=account_id)
        await user.fetch_data()
        return user

    @classmethod
    async def from_username(cls, api: 'a_MvsAPI', username: str) -> 'User':
        account_id = await api.user_api.get_id_from_username(username)
        return await cls.from_id(api, account_id)

    def user_summary(self):
        summary = f"username: {self.username}\n"
        summary += f"account_id: {self.account_id}"
        return summary

    async def fetch_data(self) -> None:
        if not self.account_id:
            raise ValueError("Account ID is required to fetch data")

        self.account_data = await self.api.user_api.get_player_account(self.account_id)
        self.profile_data = await self.api.user_api.get_player_profile(self.account_id)
        self.username = self.account_data["identity"]["alternate"]["wb_network"][0]["username"]

    async def refresh_profile(self):
        self.profile_data = await self.api.user_api.get_player_profile(self.account_id)

    # Rank Information
    async def get_rank_data(self, account_id: str, gamemode: str, character: str = "all", season: int = 2) -> Dict[
        str, Any]:
        endpoint = f"leaderboards/ranked_season{season}_{gamemode}_{character}/score-and-rank/{account_id}"
        return await self.api.user_api.request(endpoint)

    # async def get_highest_ranked_character(self, gamemode: str) -> ''

    async def get_elo(self, gamemode: str, character: str = "all") -> float:
        rank_data = await self.get_rank_data(gamemode, character)
        elo = rank_data["score"]
        return elo

    async def get_rank_str(self, gamemode: str, character: str = "all") -> str:
        return Utils.elo_to_rank(await self.get_elo(gamemode, character))

    async def get_most_recent_match_id(self):
        match = await self.api.match_api.get_user_matches(self.account_id, 1)
        match_id = match["matches"][0]["id"]
        return match_id

    async def get_most_recent_match(self) -> Optional["Match"]:
        match_id = await self.get_most_recent_match_id()
        # match = await self.api.match_api.get_match_by_id(match_id)
        # Once Match class is complete, instantiate and return a Match object
        match = await Match.from_id(self.api, match_id)
        return match

    def __post_init__(self):
        if not self.api:
            raise ValueError("MvsAPIWrapper instance is required")
