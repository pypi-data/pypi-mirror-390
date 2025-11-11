from typing import Any, Dict, Optional

from .client import Client


def _normalize_flag(value: Optional[Any]) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, (int, float)):
        return 1 if int(value) != 0 else 0
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes"}:
            return 1
        if lowered in {"0", "false", "no"}:
            return 0
    raise ValueError("Boolean-like value expected")

class Campaign:
    """
    Get the campaign information and set the campaign information
    """
    def __init__(self, client: Client):
        self.client = client

    def get_templates(self):
        """
        Get the templates

        Returns
        -------
        json
            the templates
        """
        return self.client.get("GetTemplates")
    
    def update_template(
        self,
        template_id: int,
        *,
        description: Optional[str] = None,
        caller_id: Optional[str] = None,
        incoming_policy: Optional[str] = None,
        customer_default: Optional[bool] = None,
        max_active_channels: Optional[int] = None,
        max_bridged_channels: Optional[int] = None,
        originate_timeout: Optional[int] = None,
        vm_detect: Optional[bool] = None,
        filter_enabled: Optional[bool] = None,
        max_dial_attempts: Optional[int] = None,
        redial_wait: Optional[int] = None,
        redial_policy: Optional[str] = None,
        yemot_context: Optional[str] = None,
        bridge_to: Optional[str] = None,
        play_private_msg: Optional[bool] = None,
        remove_request: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update a telephony template with given parameters.

        Parameters
        ----------
        template_id : int
            ID of the template to update
        description : str, optional
            Description of the template
        caller_id : str, optional
            Caller ID associated with this template
        incoming_policy : str, optional
            Incoming policy, one of: 'OPEN', 'BLACKLIST', 'WHITELIST', 'BLOCKED'
        customer_default : bool or int, optional
            Whether this template is the default for the customer
        max_active_channels : int, optional
            The maximum active channels allowed
        max_bridged_channels : int, optional
            The maximum bridged channels allowed
        originate_timeout : int, optional
            Timeout (in seconds) when originating a call
        vm_detect : bool or int, optional
            Voicemail detection enabled flag
        filter_enabled : bool or int, optional
            Whether filtering is enabled
        max_dial_attempts : int, optional
            Maximum dial attempts
        redial_wait : int, optional
            How many seconds to wait before redialing
        redial_policy : str, optional
            Redial policy, one of: 'NONE', 'CONGESTIONS', 'FAILED'
        yemot_context : str, optional
            YEMOT context, one of: 'SIMPLE', 'REPEAT', 'MESSAGE', 'VOICEMAIL', 'BRIDGE'
        bridge_to : int, optional
            ID to bridge calls to
        play_private_msg : bool or int, optional
            Whether to play a private message
        remove_request : str, optional
            Removal request type, 'SILENT' or 'WITH_MESSAGE'

        Returns
        -------
        Any
            Response from the client post request
        """
        
        if not isinstance(template_id, int):
            return "The template_id must be a integer"
        
        if incoming_policy not in [None, 'OPEN', 'BLACKLIST', 'WHITELIST', 'BLOCKED']:
            return "The incoming_policy must be one of the following: 'OPEN', 'BLACKLIST', 'WHITELIST', 'BLOCKED'"
        
        if max_active_channels and not isinstance(max_active_channels, int):
            return "The max_active_channels must be a integer"

        if max_bridged_channels and not isinstance(max_bridged_channels, int):
            return "The max_bridged_channels must be a integer"
        
        if originate_timeout and not isinstance(originate_timeout, int):
            return "The originate_timeout must be a integer"
        
        if max_dial_attempts and not isinstance(max_dial_attempts, int):
            return "The max_dial_attempts must be a integer"

        if redial_wait and not isinstance(redial_wait, int):
            return "The redial_wait must be a integer"
        
        if redial_policy not in [None, 'NONE', 'CONGESTIONS', 'FAILED']:
            return "The redial_policy must be one of the following: 'NONE', 'CONGESTIONS', 'FAILED'"

        if yemot_context not in [None, 'SIMPLE', 'REPEAT', 'MESSAGE', 'VOICEMAIL', 'BRIDGE', 'OTHER']:
            return "The yemot_context must be one of the following: 'SIMPLE', 'REPEAT', 'MESSAGE', 'VOICEMAIL', 'BRIDGE'"

        if remove_request not in [None, 'SILENT', 'WITH_MESSAGE']:
            return "The remove_request must be one of the following: 'SILENT', 'WITH_MESSAGE'"

        data = {
            "templateId": template_id,
            "description": description,
            "callerId": caller_id,
            "incomingPolicy": incoming_policy,
            "customerDefault": _normalize_flag(customer_default),
            "maxActiveChannels": max_active_channels,
            "maxBridgedChannels": max_bridged_channels,
            "originateTimeout": originate_timeout,
            "vmDetect": _normalize_flag(vm_detect),
            "filterEnabled": _normalize_flag(filter_enabled),
            "maxDialAttempts": max_dial_attempts,
            "redialWait": redial_wait,
            "redialPolicy": redial_policy,
            "yemotContext": yemot_context,
            "bridgeTo": bridge_to,
            "playPrivateMsg": _normalize_flag(play_private_msg),
            "removeRequest": remove_request,
        }
        return self.client.post("UpdateTemplate", data=data)
    
    def upload_template_file(
        self,
        file_path: str,
        template_name: Optional[str],
        file_type: str,
        convert_audio: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Upload the template file

        Parameters
        ----------
        file_path : string
            path to the file to upload
        template_name : string, optional
            template identifier or phone number for PRIVATE_MSG files, defaults to "Default"
        file_type : string
            one of 'VOICE', 'SMS', 'BRIDGE', 'PRIVATE_FIRST', 'PRIVATE_MSG'
        convert_audio : bool or int, optional
            truthy to request server-side audio conversion

        Returns
        -------
        json
            the response of the upload
        """
        name = template_name or "Default"
        if file_type not in ['VOICE', 'SMS', 'BRIDGE', 'PRIVATE_FIRST', 'PRIVATE_MSG']:
            return "The type must be one of the following: 'VOICE', 'SMS', 'BRIDGE' - for a msg befor bridge, 'PRIVATE_FIRST', 'PRIVATE_MSG'"

        if not file_path:
            return "The file is required"

        if file_type == 'VOICE':
            path = f'{name}.wav'
        if file_type == 'SMS':
            path = f'{name}.tts'
        if file_type == 'BRIDGE':
            path = f'{name}-MoreInfo.wav'
        if file_type == 'PRIVATE_FIRST':
            path = f'{name}-First.wav'
        if file_type == 'PRIVATE_MSG':
            path = f'PrivateMsg/{name}.wav'

        data = {
            "path": path,
            "convertAudio": _normalize_flag(convert_audio) if convert_audio is not None else None,
        }

        return self.client.post_file("UploadFile", file_path=file_path, data=data)

    def download_template_file(self, name: Optional[str], file_type: str) -> bytes:
        """
        Download the template file

        Parameters
        ----------
        name : string, optional
            the template id or phone number if using PRIVATE_MSG, defaults to "Default"
        file_type : string
            one of: 'VOICE', 'SMS', 'BRIDGE', 'PRIVATE_FIRST', 'PRIVATE_MSG'

        Returns
        -------
        bytes
            raw file content
        """
        if name == None:
            name = "Default"
        if file_type not in ['VOICE', 'SMS', 'BRIDGE', 'PRIVATE_FIRST', 'PRIVATE_MSG']:
            return "The type must be one of the following: 'VOICE', 'SMS', 'BRIDGE' - for a msg befor bridge, 'PRIVATE_FIRST', 'PRIVATE_MSG'"
        
        if file_type == 'VOICE':
            path = f'{name}.wav'
        if file_type == 'SMS':
            path = f'{name}.tts'
        if file_type == 'BRIDGE':
            path = f'{name}-MoreInfo.wav'
        if file_type == 'PRIVATE_FIRST':
            path = f'{name}-First.wav'
        if file_type == 'PRIVATE_MSG':
            path = f'PrivateMsg/{name}.wav'
        
        return self.client.download("DownloadFile", {"path": path})

    def downlaoad_template_file(self, name: Optional[str], type: str) -> bytes:  # pragma: no cover - backwards compat
        """Backward compatible alias for ``download_template_file``."""

        return self.download_template_file(name, type)

    # TODO: Implement the FileAction method and GetTextFile method and UploadTextFile method

    def create_template(self, description: str) -> Dict[str, Any]:
        """
        Create a new template the details of the template will be generated from the default template to change the details use the update_template method

        Parameters
        ----------
        description : string
            the description of the template

        Returns
        -------
        dict
            response payload containing the new template id
        """
        return self.client.get("CreateTemplate", {"description": description})
    
    def delete_template(self, template_id: int) -> Dict[str, Any]:
        """
        Delete the template by the template id

        Parameters
        ----------
        template_id : int
            the template id

        Returns
        -------
        json
            success message
        """
        if not isinstance(template_id, int):
            return "The template_id must be a integer"
        
        return self.client.get("DeleteTemplate", {"templateId": template_id})
    
    def get_template_entries(self, template_id: int) -> Dict[str, Any]:
        """
        Get the template entries

        Parameters
        ----------
        template_id : int
            the template id

        Returns
        -------
        json
            the template entries
        """
        if not isinstance(template_id, int):
            return "The template_id must be a integer"
        
        return self.client.get("GetTemplateEntries", {"templateId": template_id})
    
    def update_template_entry(
        self,
        template_id: int,
        *,
        rowid: Optional[int] = None,
        phone: Optional[str] = None,
        name: Optional[str] = None,
        more_info: Optional[str] = None,
        blocked: Optional[bool] = False,
    ) -> Dict[str, Any]:
        """
        Update a template entry or create a new one

        Parameters
        ----------
        template_id : int
            the template id
        rowid : int, optional
            if not given or not fund will crate a new entry, by default None
        phone : string, optional
            the entry phone, by default None
        name : string, optional
            the name, by default None
        more_info : string, optional
            mor details, by default None
        blocked : bool or int, optional
            to add the user in blocked list, by default False

        Returns
        -------
        json
            the response of the request
        """
        if not isinstance(template_id, int):
            return "The template_id must be a integer"
        
        if rowid and not isinstance(rowid, int):
            return "The rowid must be a integer"
        
        data = {
            "templateId": template_id,
            "rowid": rowid,
            "phone": phone,
            "name": name,
            "moreInfo": more_info,
            "blocked": _normalize_flag(blocked),
        }
        return self.client.post("UpdateTemplateEntry", data=data)
    


        