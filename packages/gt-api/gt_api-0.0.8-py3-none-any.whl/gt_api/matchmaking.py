from .client import Client
from . import generic


@Client._register_endpoint
def get_ranked_matchmaking_games(uid, offset=0, auth_token=None):
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/matchmaking/getRankedMatchmakingGames",
            "GET",
            auth_token,
            params={"uid": uid, "offset": offset},
        )
    )


@Client._register_endpoint
def get_game_history_details(lobby_id, auth_token=None):
    return generic.process_response(
        generic.geotastic_api_request(
            "https://backend01.geotastic.net/v1/matchmaking/getGameHistoryDetails.php",
            "GET",
            auth_token,
            params={"lobbyId": lobby_id},
        )
    )
