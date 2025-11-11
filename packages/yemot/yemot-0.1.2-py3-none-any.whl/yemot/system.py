from typing import Any, Dict, Optional

from .client import Client

class System:
    """
    Get the system information and set the system information
    """
    def __init__(self, client: Client):
        self.client = client

    def system_info(self):
        """
        Get the system information

        Returns
        -------
        json
            the system information
        """
        return self.client.get("GetSession")
    
    def set_system_info(
        self,
        *,
        name: Optional[str] = None,
        email: Optional[str] = None,
        organization: Optional[str] = None,
        contact_name: Optional[str] = None,
        phones: Optional[str] = None,
        invoice_name: Optional[str] = None,
        invoice_address: Optional[str] = None,
        fax: Optional[str] = None,
        access_password: Optional[str] = None,
        record_password: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Set the system information you can set some of the parameters or all of them to set the system information

        Parameters
        ----------
        name : string, optional
            the name of the user, by default None
        email : string, optional
            the users email, by default None
        organization : string, optional
            the name of your organiztion, by default None
        contact_name : string, optional
            the contact user, by default None
        phones : string, optional
            the users phone, by default None
        invoice_name : string, optional
            the name for the invoice, by default None
        invoice_address : string, optional
            the email for the invoice, by default None
        fax : string, optional
            the fax number, by default None
        access_password : string, optional
            the main password, by default None
        record_password : string, optional
            the password for limited access, by default None

        Returns
        -------
        json
            the new system information
        """
        data = {
            "name": name,
            "email": email,
            "organization": organization,
            "contactName": contact_name,
            "phones": phones,
            "invoiceName": invoice_name,
            "invoiceAddress": invoice_address,
            "fax": fax,
            "accessPassword": access_password,
            "recordPassword": record_password,
        }
        return self.client.post("SetCustomerDetails", data)
    
    def set_password(self, new_password: str) -> Dict[str, Any]:
        """
        Set the new password

        Parameters
        ----------
        new_password : string
            the new password

        Returns
        -------
        json
            the new password
        """
        payload = {
            "password": self.client.password,
            "newPassword": str(new_password),
        }
        response = self.client.post("SetPassword", payload)
        self.client.password = str(new_password)
        return response

    def get_transactions(
        self,
        from_id: Optional[int] = None,
        limit: Optional[int] = 100,
        filter_: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get the transactions of the units in the system

        Parameters
        ----------
        first : string, optional
            the number to start, by default None
        limit : str, optional
            how meny to show, by default '100'
        filter : string, optional
            the filter for example: "campaigns", by default None

        Returns
        -------
        json
            the transactions of the units
        """
        return self.client.get(
            "GetTransactions",
            {"from": from_id, "limit": limit, "filter": filter_},
        )

    def transfer_units(self, amount: int, destination: str) -> Dict[str, Any]:
        """
        Transfer units to another account

        Parameters
        ----------
        amount : int
            the amount of units
        destination : string
            the destination account

        Returns
        -------
        json
            the response of the transfer
        """
        if amount <= 0:
            raise ValueError("amount must be a positive integer")
        payload = {
            "amount": amount,
            "destination": destination,
        }
        return self.client.get("TransferUnits", payload)
    
    def get_incoming_calls(self):
        """
        Get the incoming calls

        Returns
        -------
        json
            the incoming calls
        """
        return self.client.get("GetIncomingCalls")
    
    def upload_file(
        self,
        *,
        file_path: Optional[str] = None,
        file: Optional[str] = None,
        path: str,
        convert_audio: Optional[Any] = False,
        auto_numbering: Optional[Any] = False,
        tts: Optional[Any] = False,
    ) -> Dict[str, Any]:
        """
        Upload file to the system

        Parameters
        ----------
        file_path : string, optional
            absolute or relative path to the file on disk. Alias ``file`` is accepted for backwards compatibility.
        path : string
            full target path in the system (must start with ``ivr2:``)
        convert_audio : bool or int, optional
            set truthy value to request server-side wav conversion, falsy to skip
        auto_numbering : bool or str, optional
            truthy to let the server assign incremental filenames (path must end with ``/``)
        tts : bool or int, optional
            mark the uploaded file as TTS when using auto numbering

        Returns
        -------
        json
            the response of the upload
        """
        resolved_file_path = file_path or file
        if not resolved_file_path:
            raise ValueError("file_path is required")
        if not path:
            raise ValueError("path is required")
        if not path.startswith("ivr2:"):
            raise ValueError("path must start with 'ivr2:'")

        def _flag(value: Optional[Any], *, true_false: bool = False) -> Optional[Any]:
            if value is None:
                return None
            if isinstance(value, str):
                lowered = value.strip().lower()
                if lowered in {"1", "true", "yes"}:
                    return "true" if true_false else 1
                if lowered in {"0", "false", "no"}:
                    return "false" if true_false else 0
            if isinstance(value, bool):
                return str(value).lower() if true_false else (1 if value else 0)
            if isinstance(value, (int, float)):
                flag = int(value) != 0
                if true_false:
                    return "true" if flag else "false"
                return 1 if flag else 0
            raise ValueError("Unsupported flag value")

        data = {
            "path": path,
            "convertAudio": _flag(convert_audio),
            "autoNumbering": _flag(auto_numbering, true_false=True),
            "tts": _flag(tts),
        }

        return self.client.post_file(
            "UploadFile",
            file_path=resolved_file_path,
            data=data,
        )
    
    def upload_file_big(self, file=None, path=None, convert_audio=None, auto_numbering=None, tts=None):
        """
        Upload file this is for uploading a file what is over 50MB not redy yet
        """
        # TODO: Implement this method

        # split the file to parts and upload each part in the first part generate a qquuid and send it to the server
        # the parameter what i need to send in each part is 
        # qquuid - the generated qquuid
        # qqpartindex - the part index
        # qqpartbyteoffset - the part byte offset
        # qqchunksize - the chunk size
        # qqtotalparts - the total parts
        # qqtotalfilesize - the total file size in bytes
        # qqfilename - the file name
        # qqfile - the file
        # uploader - yemot-admin
        return "Not implemented"
    
    def download_file(self, path: str) -> bytes:
        """
        Download file from the system

        Parameters
        ----------
        path : string
            the path to the file in the system starting with ivr2:

        Returns
        -------
        bytes
            raw file content
        """
        if not path:
            raise ValueError("path is required")
        return self.client.download("DownloadFile", {"path": path})