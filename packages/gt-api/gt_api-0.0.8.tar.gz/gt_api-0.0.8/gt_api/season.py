from . import generic
from .client import Client


@Client._register_endpoint
def get_season(auth_token=None):
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/season/getSeason.php", "GET", auth_token
        )
    )


@Client._register_endpoint
def get_current_user_statistics(uid, auth_token=None):
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/season/getCurrentUserStatistics.php",
            "GET",
            auth_token,
            params={"uid": uid},
        )
    )


@Client._register_endpoint
def get_season_progress_leaderboard(id, auth_token=None):
    return generic.process_response(
        generic.geotastic_api_request(
            "https://backend01.geotastic.net/v1/season/getSeasonProgressLeaderboard.php",
            "GET",
            auth_token,
            params={"id": id},
        )
    )


@Client._register_endpoint
def get_all_matchmaking(auth_token=None):
    return generic.process_response(
        generic.geotastic_api_request(
            "https://backend01.geotastic.net/v1/season/getAllMatchmaking.php",
            "GET",
            auth_token,
        )
    )
