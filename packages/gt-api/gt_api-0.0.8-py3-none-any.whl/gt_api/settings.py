from . import generic
from .client import Client


@Client._register_endpoint
def update_preset_settings(preset_id, settings, auth_token=None):
    data = generic.encode_encdata({"presetId": preset_id, "settings": settings})
    print(data)
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/settings/updatePresetSettingsV2.php",
            "POST",
            auth_token,
            json={"enc": data},
        )
    )
