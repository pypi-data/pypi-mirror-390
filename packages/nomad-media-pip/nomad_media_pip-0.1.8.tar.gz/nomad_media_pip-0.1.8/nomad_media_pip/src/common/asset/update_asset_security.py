"""
This module contains the function to updateAssetSecurity.

Functions:
    _updateSecurity: Update Asset Security.
"""

from nomad_media_pip.src.helpers.send_request import _send_request


def _update_asset_security(
    self, 
    id: str, 
    inherit_security: bool, 
    security_groups: list[dict], 
    security_users: list[dict]
) -> dict | None:
    """
    Update Asset Security.

    Args:
        id (str): The id of the asset to apply the security to.
        inherit_security (bool): Whether or not to inherit the security from parent.
        security_groups (list[dict]): The security groups to update the asset with.
        security_users (list[dict]): The security users to update the asset with.

    Returns:
        dict: The JSON response from the server if the request is successful.
        None: If the request fails or the response cannot be parsed as JSON.
    """

    api_url: str = f"{self.config["serviceApiUrl"]}/admin/security/{id}/update"
    
    body = {
	  	"inheritSecurity": inherit_security,
	  	"securityGroups": security_groups,
	  	"securityUsers": security_users
	  }
    return _send_request(self, "Update Asset Security", api_url, "POST", None, body)
