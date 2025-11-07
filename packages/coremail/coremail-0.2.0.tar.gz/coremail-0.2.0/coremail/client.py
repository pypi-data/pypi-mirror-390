"""
Coremail API Client
"""
import os
import time
import requests
from typing import Optional, Dict, Any
from cachetools import TTLCache
from dotenv import load_dotenv
from .models import (
    TokenResponse, AuthenticateResponse, GetAttrsResponse, ChangeAttrsResponse, 
    CreateResponse, DeleteResponse, ListResponse, ListDomainsResponse, 
    GetDomainAttrsResponse, ChangeDomainAttrsResponse, AdminResponse,
    LogResponse, SearchResponse, GroupResponse, SystemConfigResponse,
    UserExistResponse, AddAliasResponse, DeleteAliasResponse, GetAliasResponse,
    SessionInfoResponse, SessionVariableResponse, GetUserAliasResponse,
    GetOrgInfoResponse, GetOrgListResponse, GetDomainListResponse,
    GetUnitAttrsResponse, RequestTokenParams, UserLoginParams, UserLoginExParams,
    UserExistParams, AuthenticateParams, SesTimeOutParams, SesRefreshParams,
    GetSessionVarParams, UserLogoutParams, SetSessionVarParams, AddSmtpAliasParams,
    DelSmtpAliasParams, GetSmtpAliasParams, GetAttrsParams, ChangeAttrsParams,
    CreateParams, DeleteParams, GetOrgInfoParams, AlterOrgParams,
    AddOrgDomainParams, DelOrgDomainParams, AddOrgCosParams, AlterOrgCosParams,
    DelOrgCosParams, GetOrgCosUserParams, AddUnitParams, DelUnitParams,
    GetUnitAttrsParams, SetUnitAttrsParams, RenameUserParams, MoveUserParams,
    UserAttributeQuery, DomainAttributeQuery, UserAttributes, OrgAttributeQuery,
    OrgAttributes, UnitAttributes, ContactAttributes, ContactAttributeQuery,
    BaseResponse, SessionResponse, CreateObjectResponse, GetObjAttrsResponse,
    SetObjAttrsResponse, DeleteObjResponse, DomainExistResponse, AddDomainResponse,
    DelDomainResponse, AddDomainAliasResponse, GetDomainAliasResponse,
    DelDomainAliasResponse, GetOrgListByDomainResponse, MailInfoAttributes,
    ListMailInfosResponse, GetNewMailInfosResponse, SmtpTransportResponse,
    SetAdminTypeResponse, GetAdminTypeResponse, RenameUserResponse, MoveUserResponse,
    AddOrgResponse, AddOrgDomainResponse, DelOrgDomainResponse, AddOrgCosResponse,
    DelOrgCosResponse, GetOrgCosUserResponse, AddUnitResponse, DelUnitResponse,
    UnitAttributeQuery, DomainAttributes
)

# Load environment variables
load_dotenv()

class CoremailClient:
    """
    Coremail API Client for authentication and token management.
    """
    
    def __init__(self, base_url: Optional[str] = None, app_id: Optional[str] = None, secret: Optional[str] = None):
        """
        Initialize the Coremail client.
        
        :param base_url: Base URL for the Coremail API
        :param app_id: Application ID for authentication
        :param secret: Secret key for authentication
        """
        self.base_url = base_url or os.getenv('COREMAIL_BASE_URL', 'http://mail.ynu.edu.cn:9900/apiws/v3')
        self.app_id = app_id or os.getenv('COREMAIL_APP_ID')
        self.secret = secret or os.getenv('COREMAIL_SECRET')
        self.session = requests.Session()
        
        # Use TTLCache for token caching (1 hour = 3600 seconds)
        self.token_cache: TTLCache = TTLCache(maxsize=1, ttl=3600)
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json'
        })

    def _handle_response(self, response, expected_model):
        """
        Helper method to handle API responses and validate with Pydantic models
        """
        response.raise_for_status()
        data = response.json()
        result = expected_model.model_validate(data)
        
        if result.code != 0:
            raise Exception(f"API Error {result.code}: {result.message or 'Unknown error'}")
            
        return result

    def _handle_response_data_only(self, response, expected_model, result_accessor_func=None):
        """
        Helper method to handle API responses and return only the result data
        """
        response.raise_for_status()
        data = response.json()
        result = expected_model.model_validate(data)
        
        if result.code != 0:
            raise Exception(f"API Error {result.code}: {result.message or 'Unknown error'}")
        
        # Return just the result data depending on the response type
        if result_accessor_func:
            return result_accessor_func(result)
        elif hasattr(result, 'get_result_data'):
            return result.get_result_data()
        elif hasattr(result, 'result') and result.result is not None:
            return result.result
        else:
            # Return True for success if there's no specific result data
            return True

    def _handle_boolean_response(self, response, expected_model):
        """
        Helper method to handle API responses that should return boolean success/failure
        """
        response.raise_for_status()
        data = response.json()
        result = expected_model.model_validate(data)
        
        if result.code != 0:
            raise Exception(f"API Error {result.code}: {result.message or 'Unknown error'}")
        
        # Return True for success if there's no error
        return True
    
    def requestToken(self) -> str:
        """
        Request a new authentication token.
        
        :return: Authentication token
        """
        # Check if we have a valid cached token
        if 'token' in self.token_cache:
            return self.token_cache['token']
        
        url = f"{self.base_url}/requestToken"
        
        payload = {
            "app_id": self.app_id,
            "secret": self.secret
        }
        
        response = self.session.post(url, json=payload)
        result = self._handle_response(response, TokenResponse)
        
        # Cache the token
        self.token_cache['token'] = result.result
        
        return result.result
    
    def authenticate(self, user_at_domain: str, password: str = "") -> bool:
        """
        Authenticate a user.
        
        :param user_at_domain: User identifier in format "user@domain"
        :param password: User password
        :return: True if authentication is successful, False otherwise
        """
        # Ensure we have a valid token (this will refresh if needed)
        token = self.requestToken()
        
        url = f"{self.base_url}/authenticate"
        
        payload = {
            "_token": token,
            "user_at_domain": user_at_domain,
            "password": password
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        
        if result.get('code') != 0:
            raise Exception(f"API Error {result.get('code')}: {result.get('message', 'Authentication failed')}")
        return True
    
    def getAttrs(self, user_at_domain: str, attrs: Optional[Dict[str, Any]] = None) -> UserAttributes:
        """
        Get user attributes.
        
        :param user_at_domain: User identifier in format "user@domain"
        :param attrs: Dictionary of attribute names to retrieve (use None as value for each key), e.g., {"user_id": None, "domain_name": None}. Pass None to retrieve all attributes.
        :return: User attributes model
        """
        # Ensure we have a valid token (this will refresh if needed)
        token = self.requestToken()
        
        url = f"{self.base_url}/getAttrs"
        
        # If attrs is None, get all attributes using a template of all possible attributes set to None
        if attrs is None:
            # Create a dictionary with all UserAttributeQuery fields set to None
            attrs = {field: None for field in UserAttributeQuery.model_fields.keys()}
        
        payload = {
            "_token": token,
            "user_at_domain": user_at_domain,
            "attrs": attrs
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response_data_only(
            response, 
            GetAttrsResponse, 
            result_accessor_func=lambda r: r.get_result_data()
        )
    
    def changeAttrs(self, user_at_domain: str, attrs: Dict[str, Any]) -> bool:
        """
        Change user attributes.
        
        :param user_at_domain: User identifier in format "user@domain"
        :param attrs: Dictionary of attributes to change
        :return: True if successful, False otherwise
        """
        # Ensure we have a valid token (this will refresh if needed)
        token = self.requestToken()
        
        url = f"{self.base_url}/changeAttrs"
        
        payload = {
            "_token": token,
            "user_at_domain": user_at_domain,
            "attrs": attrs
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        
        if result.get('code') != 0:
            raise Exception(f"API Error {result.get('code')}: {result.get('message', 'Change attributes failed')}")
        return True

    def create_user(self, user_at_domain: str, attrs: Dict[str, Any]) -> bool:
        """
        Create a new user.
        
        :param user_at_domain: User identifier in format "user@domain"
        :param attrs: Dictionary of attributes for the new user
        :return: True if successful, False otherwise
        """
        # Ensure we have a valid token (this will refresh if needed)
        token = self.requestToken()
        
        url = f"{self.base_url}/createUser"
        
        payload = {
            "_token": token,
            "user_at_domain": user_at_domain,
            "attrs": attrs
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        
        if result.get('code') == 0:
            return True
        else:
            raise Exception(f"API Error {result.get('code')}: {result.get('message', 'Create user failed')}")
    
    # Keep the old create method for backward compatibility
    def create(self, user_at_domain: str, attrs: UserAttributes) -> CreateResponse:
        """
        Create a new user (backward compatibility method).
        
        :param user_at_domain: User identifier in format "user@domain"
        :param attrs: UserAttributes model of attributes for the new user
        :return: Creation result
        """
        return self.create_user(user_at_domain, attrs)

    def delete(self, user_at_domain: str) -> bool:
        """
        Delete a user.
        
        :param user_at_domain: User identifier in format "user@domain"
        :return: True if successful, False otherwise
        """
        # Ensure we have a valid token (this will refresh if needed)
        token = self.requestToken()
        
        url = f"{self.base_url}/deleteUser"
        
        payload = {
            "_token": token,
            "user_at_domain": user_at_domain,
            "preserve_days": 0  # Immediate deletion
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        
        if result.get('code') != 0:
            raise Exception(f"API Error {result.get('code')}: {result.get('message', 'Delete user failed')}")
        return True

    def list_users(self, domain: Optional[str] = None, attrs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List users in the system or in a specific domain.
        
        :param domain: Optional domain to filter users
        :param attrs: Optional dictionary of attribute names to retrieve (use None as value for each key), e.g., {"user_id": None, "domain_name": None}. Pass None for default attributes.
        :return: Dictionary containing list of users
        """
        # Ensure we have a valid token (this will refresh if needed)
        token = self.requestToken()
        
        url = f"{self.base_url}/list"
        
        payload: Dict[str, Any] = {
            "_token": token
        }
        
        if domain:
            payload["domain"] = domain
            
        if attrs:
            payload["attrs"] = attrs
        else:
            # Default attributes to retrieve
            payload["attrs"] = {
                "user_id": None,
                "user_name": None,
                "domain_name": None,
                "quota_mb": None,
                "user_enabled": None,
                "create_date": None
            }
        
        response = self.session.post(url, json=payload)
        return self._handle_response_data_only(
            response, 
            ListResponse, 
            result_accessor_func=lambda r: r.result
        )

    def listDomains(self, attrs: Optional[Dict[str, Any]] = None) -> str:
        """
        List domains in the system.
        
        :param attrs: Optional attributes to filter or retrieve
        :return: Comma-separated list of domains
        """
        # Ensure we have a valid token (this will refresh if needed)
        token = self.requestToken()
        
        url = f"{self.base_url}/getDomainList"
        
        payload: Dict[str, Any] = {
            "_token": token
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response_data_only(
            response, 
            GetDomainListResponse, 
            result_accessor_func=lambda r: r.get_result_data()
        )

    def getDomainAttrs(self, domain_name: str, attrs: Optional[Dict[str, Any]] = None) -> DomainAttributes:
        """
        Get domain attributes.
        
        :param domain_name: Domain name
        :param attrs: Dictionary of attribute names to retrieve (use None as value for each key), e.g., {"domain_name": None, "quota_mb": None}. Pass None to retrieve all attributes.
        :return: Domain attributes model
        """
        # Ensure we have a valid token (this will refresh if needed)
        token = self.requestToken()
        
        url = f"{self.base_url}/getDomainAttrs"
        
        # If attrs is None, get all attributes using a template of all possible attributes set to None
        if attrs is None:
            # Create a dictionary with all DomainAttributeQuery fields set to None
            attrs = {field: None for field in DomainAttributeQuery.model_fields.keys()}
        
        payload: Dict[str, Any] = {
            "_token": token,
            "domain_name": domain_name,
            "attrs": attrs
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response_data_only(
            response, 
            GetDomainAttrsResponse, 
            result_accessor_func=lambda r: r.result
        )

    def changeDomainAttrs(self, domain_name: str, attrs: Dict[str, Any]) -> bool:
        """
        Change domain attributes.
        
        :param domain_name: Domain name
        :param attrs: Dictionary of attributes to change
        :return: True if successful, False otherwise
        """
        # Ensure we have a valid token (this will refresh if needed)
        token = self.requestToken()
        
        url = f"{self.base_url}/changeDomainAttrs"
        
        payload = {
            "_token": token,
            "domain_name": domain_name,
            "attrs": attrs
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        
        if result.get('code') == 0:
            return True
        else:
            raise Exception(f"API Error {result.get('code')}: {result.get('message', 'Change domain attributes failed')}")

    def admin(self, operation: str, params: Optional[Dict[str, Any]] = None) -> AdminResponse:
        """
        Perform administrative operations.
        
        :param operation: The admin operation to perform
        :param params: Parameters for the operation
        :return: Operation result
        """
        # Ensure we have a valid token (this will refresh if needed)
        token = self.requestToken()
        
        url = f"{self.base_url}/admin"
        
        payload: Dict[str, Any] = {
            "_token": token,
            "operation": operation
        }
        
        if params:
            payload["params"] = params
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, AdminResponse)

    def search(self, user_at_domain: str, search_params: Dict[str, Any]) -> SearchResponse:
        """
        Search messages for a user.
        
        :param user_at_domain: User identifier in format "user@domain"
        :param search_params: Search parameters
        :return: Search result
        """
        # Ensure we have a valid token (this will refresh if needed)
        token = self.requestToken()
        
        url = f"{self.base_url}/search"
        
        payload = {
            "_token": token,
            "user_at_domain": user_at_domain,
            "params": search_params
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, SearchResponse)

    def get_logs(self, log_type: str, start_time: Optional[str] = None, end_time: Optional[str] = None, 
                limit: Optional[int] = None) -> LogResponse:
        """
        Get system logs.
        
        :param log_type: Type of logs to retrieve (e.g., 'login', 'operation', 'error')
        :param start_time: Start time for log search (ISO format)
        :param end_time: End time for log search (ISO format)
        :param limit: Maximum number of logs to return
        :return: Log entries
        """
        # Ensure we have a valid token (this will refresh if needed)
        token = self.requestToken()
        
        url = f"{self.base_url}/getLogs"
        
        payload: Dict[str, Any] = {
            "_token": token,
            "log_type": log_type
        }
        
        if start_time:
            payload["start_time"] = start_time
        if end_time:
            payload["end_time"] = end_time
        if limit:
            payload["limit"] = limit
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, LogResponse)

    def manage_group(self, operation: str, group_name: str, user_at_domain: Optional[str] = None) -> GroupResponse:
        """
        Manage groups (add/remove users, etc.).
        
        :param operation: Group operation ('add', 'remove', 'create', 'delete', 'list')
        :param group_name: Name of the group
        :param user_at_domain: User to add/remove from the group
        :return: Operation result
        """
        # Ensure we have a valid token (this will refresh if needed)
        token = self.requestToken()
        
        url = f"{self.base_url}/manageGroup"
        
        payload: Dict[str, Any] = {
            "_token": token,
            "operation": operation,
            "group_name": group_name
        }
        
        if user_at_domain:
            payload["user_at_domain"] = user_at_domain
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, GroupResponse)

    def get_system_config(self, config_type: Optional[str] = None) -> SystemConfigResponse:
        """
        Get system configuration.
        
        :param config_type: Specific configuration type to retrieve (optional)
        :return: System configuration
        """
        # Ensure we have a valid token (this will refresh if needed)
        token = self.requestToken()
        
        url = f"{self.base_url}/getSystemConfig"
        
        payload: Dict[str, Any] = {
            "_token": token
        }
        
        if config_type:
            payload["config_type"] = config_type
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, SystemConfigResponse)

    def userExist(self, user_at_domain: str) -> UserExistResponse:
        """
        Check if a user exists.
        
        :param user_at_domain: User identifier in format "user@domain"
        :return: Boolean result indicating if user exists
        """
        # Ensure we have a valid token (this will refresh if needed)
        token = self.requestToken()
        
        url = f"{self.base_url}/userExist"
        
        payload: Dict[str, Any] = {
            "_token": token,
            "user_at_domain": user_at_domain
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, UserExistResponse)

    def addSmtpAlias(self, user_at_domain: str, alias_user_at_domain: str) -> bool:
        """
        Add an SMTP alias for a user.
        
        :param user_at_domain: User identifier in format "user@domain"
        :param alias_user_at_domain: Alias email address in format "alias@domain"
        :return: True if successful, False otherwise
        """
        # Ensure we have a valid token (this will refresh if needed)
        token = self.requestToken()
        
        url = f"{self.base_url}/addSmtpAlias"
        
        payload: Dict[str, Any] = {
            "_token": token,
            "user_at_domain": user_at_domain,
            "alias_user_at_domain": alias_user_at_domain
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        
        if result.get('code') == 0:
            return True
        else:
            raise Exception(f"API Error {result.get('code')}: {result.get('message', 'Add alias failed')}")

    def delSmtpAlias(self, user_at_domain: str, alias_user_at_domain: str) -> bool:
        """
        Delete an SMTP alias for a user.
        
        :param user_at_domain: User identifier in format "user@domain"
        :param alias_user_at_domain: Alias email address in format "alias@domain" to be deleted
        :return: True if successful, False otherwise
        """
        # Ensure we have a valid token (this will refresh if needed)
        token = self.requestToken()
        
        url = f"{self.base_url}/delSmtpAlias"
        
        payload: Dict[str, Any] = {
            "_token": token,
            "user_at_domain": user_at_domain,
            "alias_user_at_domain": alias_user_at_domain
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        
        if result.get('code') == 0:
            return True
        else:
            raise Exception(f"API Error {result.get('code')}: {result.get('message', 'Delete alias failed')}")

    def getSmtpAlias(self, user_at_domain: str) -> str:
        """
        Get SMTP aliases for a user.
        
        :param user_at_domain: User identifier in format "user@domain"
        :return: Comma-separated list of aliases for the user
        """
        # Ensure we have a valid token (this will refresh if needed)
        token = self.requestToken()
        
        url = f"{self.base_url}/getSmtpAlias"
        
        payload: Dict[str, Any] = {
            "_token": token,
            "user_at_domain": user_at_domain
        }
        
        response = self.session.post(url, json=payload)
        result = self._handle_response(response, GetAliasResponse)
        return result.result

    # 3.2 登录 section methods
    def userLogin(self, user_at_domain: str) -> SessionResponse:
        """
        User login.
        
        :param user_at_domain: User identifier in format "user@domain"
        :return: Session ID
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/userLogin"
        
        payload = {
            "_token": token,
            "user_at_domain": user_at_domain
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, SessionResponse)

    def userLoginEx(self, user_at_domain: str, attrs: Optional[str] = None) -> SessionResponse:
        """
        User login with additional parameters and return extra information.
        
        :param user_at_domain: User identifier in format "user@domain"
        :param attrs: Additional attributes as URL-encoded string
        :return: Encoded user attributes string
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/userLoginEx"
        
        payload = {
            "_token": token,
            "user_at_domain": user_at_domain
        }
        
        if attrs is not None:
            payload["attrs"] = attrs
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, SessionResponse)

    def sesTimeOut(self, ses_id: str) -> str:
        """
        Check user session and return user information.
        
        :param ses_id: Session ID
        :return: Session info containing uid, domain_id and org_id as a string
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/sesTimeOut"
        
        payload = {
            "_token": token,
            "ses_id": ses_id
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response_data_only(
            response, 
            SessionInfoResponse, 
            result_accessor_func=lambda r: r.result
        )

    def sesRefresh(self, ses_id: str) -> bool:
        """
        Check user session and refresh access time.
        
        :param ses_id: Session ID
        :return: True if successful, False otherwise
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/sesRefresh"
        
        payload = {
            "_token": token,
            "ses_id": ses_id
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        
        if result.get('code') == 0:
            return True
        else:
            raise Exception(f"API Error {result.get('code')}: {result.get('message', 'Session refresh failed')}")

    def getSessionVar(self, ses_id: str, ses_key: str) -> str:
        """
        Get variable from user session.
        
        :param ses_id: Session ID
        :param ses_key: Session variable key to retrieve
        :return: Session variable value
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/getSessionVar"
        
        payload = {
            "_token": token,
            "ses_id": ses_id,
            "ses_key": ses_key
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response_data_only(
            response, 
            SessionVariableResponse, 
            result_accessor_func=lambda r: r.result
        )

    def userLogout(self, ses_id: str) -> bool:
        """
        Logout user session.
        
        :param ses_id: Session ID
        :return: True if successful, False otherwise
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/userLogout"
        
        payload = {
            "_token": token,
            "ses_id": ses_id
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        
        if result.get('code') == 0:
            return True
        else:
            raise Exception(f"API Error {result.get('code')}: {result.get('message', 'User logout failed')}")

    def setSessionVar(self, ses_id: str, ses_key: str, ses_var: str) -> BaseResponse:
        """
        Set variable in user session.
        
        :param ses_id: Session ID
        :param ses_key: Session variable key to set
        :param ses_var: Value to set
        :return: Success response
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/setSessionVar"
        
        payload = {
            "_token": token,
            "ses_id": ses_id,
            "ses_key": ses_key,
            "ses_var": ses_var
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, BaseResponse)

    # 3.3 组织维护 section methods
    def addOrg(self, org_id: str, attrs: Optional[OrgAttributes] = None) -> AddOrgResponse:
        """
        Add an organization.
        
        :param org_id: Organization ID
        :param attrs: Organization attributes
        :return: Success response
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/addOrg"
        
        payload = {
            "_token": token,
            "org_id": org_id,
            "attrs": attrs.model_dump(exclude_unset=True) if attrs else {}
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, AddOrgResponse)

    def getOrgInfo(self, org_id: str, attrs: Optional[Dict[str, Any]] = None) -> OrgAttributes:
        """
        Get organization attributes.
        
        :param org_id: Organization ID
        :param attrs: Dictionary of attribute names to retrieve (use None as value for each key), e.g., {"org_name": None, "org_status": None}. Pass None to retrieve all attributes.
        :return: Organization attributes model
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/getOrgInfo"
        
        # If attrs is None, get all attributes using a template of all possible attributes set to None
        if attrs is None:
            attrs = {field: None for field in OrgAttributeQuery.model_fields.keys()}
        
        payload = {
            "_token": token,
            "org_id": org_id,
            "attrs": attrs
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response_data_only(
            response, 
            GetOrgInfoResponse, 
            result_accessor_func=lambda r: r.get_result_data()
        )

    def alterOrg(self, org_id: str, attrs: OrgAttributes) -> BaseResponse:
        """
        Modify organization attributes.
        
        :param org_id: Organization ID
        :param attrs: Attributes to modify
        :return: Success response
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/alterOrg"
        
        payload = {
            "_token": token,
            "org_id": org_id,
            "attrs": attrs.model_dump(exclude_unset=True)
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, BaseResponse)

    def addOrgDomain(self, org_id: str, domain_name: str) -> AddOrgDomainResponse:
        """
        Add organization domain.
        
        :param org_id: Organization ID
        :param domain_name: Domain name to add
        :return: Success response
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/addOrgDomain"
        
        payload = {
            "_token": token,
            "org_id": org_id,
            "domain_name": domain_name
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, AddOrgDomainResponse)

    def delOrgDomain(self, org_id: str, domain_name: str) -> DelOrgDomainResponse:
        """
        Delete organization domain.
        
        :param org_id: Organization ID
        :param domain_name: Domain name to delete
        :return: Success response
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/delOrgDomain"
        
        payload = {
            "_token": token,
            "org_id": org_id,
            "domain_name": domain_name
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, DelOrgDomainResponse)

    def addOrgCos(self, org_id: str, num_of_classes: int, cos_id: Optional[int] = None, cos_name: Optional[str] = None) -> AddOrgCosResponse:
        """
        Add organization service level.
        
        :param org_id: Organization ID
        :param num_of_classes: Number of users that can be allocated
        :param cos_id: Service level ID
        :param cos_name: Service level name (alternative to cos_id)
        :return: Success response
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/addOrgCos"
        
        payload = {
            "_token": token,
            "org_id": org_id,
            "num_of_classes": num_of_classes
        }
        
        if cos_id is not None:
            payload["cos_id"] = cos_id
        if cos_name is not None:
            payload["cos_name"] = cos_name
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, AddOrgCosResponse)

    def alterOrgCos(self, org_id: str, num_of_classes: int, cos_id: Optional[int] = None, cos_name: Optional[str] = None) -> BaseResponse:
        """
        Update organization service level.
        
        :param org_id: Organization ID
        :param num_of_classes: Number of users that can be allocated
        :param cos_id: Service level ID
        :param cos_name: Service level name (alternative to cos_id)
        :return: Success response
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/alterOrgCos"
        
        payload = {
            "_token": token,
            "org_id": org_id,
            "num_of_classes": num_of_classes
        }
        
        if cos_id is not None:
            payload["cos_id"] = cos_id
        if cos_name is not None:
            payload["cos_name"] = cos_name
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, BaseResponse)

    def delOrgCos(self, org_id: str, cos_id: int) -> DelOrgCosResponse:
        """
        Delete organization service level.
        
        :param org_id: Organization ID
        :param cos_id: Service level ID to delete
        :return: Success response
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/delOrgCos"
        
        payload = {
            "_token": token,
            "org_id": org_id,
            "cos_id": cos_id
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, DelOrgCosResponse)

    def getOrgCosUser(self, org_id: str, cos_id: int) -> GetOrgCosUserResponse:
        """
        List all user IDs under a specific service level in an organization.
        
        :param org_id: Organization ID
        :param cos_id: Service level ID
        :return: Comma-separated list of user IDs
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/getOrgCosUser"
        
        payload = {
            "_token": token,
            "org_id": org_id,
            "cos_id": cos_id
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, GetOrgCosUserResponse)

    def getOrgList(self) -> str:
        """
        Get organization list.
        
        :return: Comma-separated list of organization IDs
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/getOrgList"
        
        payload = {
            "_token": token
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response_data_only(
            response, 
            GetOrgListResponse, 
            result_accessor_func=lambda r: r.get_result_data()
        )

    # 3.4 部门维护 section methods
    def addUnit(self, org_id: str, org_unit_id: str, attrs: UnitAttributes, dont_flush_md: bool = False) -> AddUnitResponse:
        """
        Add a department/unit.
        
        :param org_id: Organization ID
        :param org_unit_id: Unit/department ID
        :param attrs: Unit attributes
        :param dont_flush_md: Whether to ignore flushmd
        :return: Success response
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/addUnit"
        
        payload = {
            "_token": token,
            "org_id": org_id,
            "org_unit_id": org_unit_id,
            "attrs": attrs.model_dump(exclude_unset=True),
            "dont_flush_md": dont_flush_md
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, AddUnitResponse)

    def delUnit(self, org_id: str, org_unit_id: str, dont_flush_md: bool = False) -> DelUnitResponse:
        """
        Delete a department/unit.
        
        :param org_id: Organization ID
        :param org_unit_id: Unit/department ID to delete
        :param dont_flush_md: Whether to ignore flushmd
        :return: Success response
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/delUnit"
        
        payload = {
            "_token": token,
            "org_id": org_id,
            "org_unit_id": org_unit_id,
            "dont_flush_md": dont_flush_md
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, DelUnitResponse)

    def getUnitAttrs(self, org_id: str, org_unit_id: str, attrs: Optional[Dict[str, Any]] = None) -> UnitAttributes:
        """
        Get department/unit attributes.
        
        :param org_id: Organization ID
        :param org_unit_id: Unit/department ID
        :param attrs: Dictionary of attribute names to retrieve (use None as value for each key), e.g., {"org_unit_name": None, "org_unit_list_rank": None}. Pass None to retrieve all attributes.
        :return: Unit attributes model
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/getUnitAttrs"
        
        # If attrs is None, get all attributes using a template of all possible attributes set to None
        if attrs is None:
            attrs = {field: None for field in UnitAttributeQuery.model_fields.keys()}
        
        payload = {
            "_token": token,
            "org_id": org_id,
            "org_unit_id": org_unit_id,
            "attrs": attrs
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response_data_only(
            response, 
            GetUnitAttrsResponse, 
            result_accessor_func=lambda r: r.get_result_data()
        )

    def setUnitAttrs(self, org_id: str, org_unit_id: str, attrs: UnitAttributes, dont_flush_md: bool = False) -> BaseResponse:
        """
        Set department/unit attributes.
        
        :param org_id: Organization ID
        :param org_unit_id: Unit/department ID
        :param attrs: Attributes to set
        :param dont_flush_md: Whether to ignore flushmd
        :return: Success response
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/setUnitAttrs"
        
        payload = {
            "_token": token,
            "org_id": org_id,
            "org_unit_id": org_unit_id,
            "attrs": attrs.model_dump(exclude_unset=True),
            "dont_flush_md": dont_flush_md
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, BaseResponse)

    # 3.5.8 设置用户的管理员身份
    def setAdminType(self, user_at_domain: str, admin_type: str = "OA", role_id: Optional[int] = None, cross_manage_scope: Optional[str] = None) -> bool:
        """
        Set user's administrator type.
        
        :param user_at_domain: User identifier in format "user@domain"
        :param admin_type: Administrator level (default: OA for organization admin)
        :param role_id: Administrator role ID
        :param cross_manage_scope: Management scope for custom admins
        :return: True if successful, False otherwise
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/setAdminType"
        
        attrs = {"admin_type": admin_type}
        if role_id is not None:
            attrs["role_id"] = role_id
        if cross_manage_scope is not None:
            attrs["cross_manage_scope"] = cross_manage_scope
        
        payload = {
            "_token": token,
            "user_at_domain": user_at_domain,
            "attrs": attrs
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        
        if result.get('code') == 0:
            return True
        else:
            raise Exception(f"API Error {result.get('code')}: {result.get('message', 'Set admin type failed')}")

    # 3.5.9 获取用户的管理员身份
    def getAdminType(self, user_at_domain: str) -> GetAdminTypeResponse:
        """
        Get user's administrator type.
        
        :param user_at_domain: User identifier in format "user@domain"
        :return: Administrator type info in format "admin_type=...&role_id=..."
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/getAdminType"
        
        payload = {
            "_token": token,
            "user_at_domain": user_at_domain
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, GetAdminTypeResponse)

    # 3.5.10 修改用户主标识
    def renameUser(self, user_at_domain: str, new_user_id: str) -> bool:
        """
        Rename user.
        
        :param user_at_domain: Current user identifier in format "user@domain"
        :param new_user_id: New user identifier (without domain part)
        :return: True if successful, False otherwise
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/renameUser"
        
        payload = {
            "_token": token,
            "user_at_domain": user_at_domain,
            "new_user_id": new_user_id
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        
        if result.get('code') == 0:
            return True
        else:
            raise Exception(f"API Error {result.get('code')}: {result.get('message', 'Rename user failed')}")

    # 3.5.11 用户跨组织移动
    def moveUser(self, user_at_domain: str, org_id: str, org_unit_id: Optional[str] = None) -> bool:
        """
        Move user to another organization.
        
        :param user_at_domain: User identifier in format "user@domain"
        :param org_id: Target organization ID
        :param org_unit_id: Target unit ID (defaults to root unit)
        :return: True if successful, False otherwise
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/moveUser"
        
        attrs = {"org_id": org_id}
        if org_unit_id is not None:
            attrs["org_unit_id"] = org_unit_id
        
        payload = {
            "_token": token,
            "user_at_domain": user_at_domain,
            "attrs": attrs
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        
        if result.get('code') == 0:
            return True
        else:
            raise Exception(f"API Error {result.get('code')}: {result.get('message', 'Move user failed')}")

    # 3.6 联系人维护 section methods
    def createObj(self, attrs: ContactAttributes) -> CreateObjectResponse:
        """
        Create contact.
        
        :param attrs: Contact attributes
        :return: Object UID
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/createObj"
        
        payload = {
            "_token": token,
            "attrs": attrs.model_dump(exclude_unset=True)
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, CreateObjectResponse)

    def getObjAttrs(self, obj_uid: str, attrs: Optional[Dict[str, Any]] = None) -> GetObjAttrsResponse:
        """
        Get contact attributes.
        
        :param obj_uid: Contact object UID
        :param attrs: Dictionary of attribute names to retrieve (use None as value for each key), e.g., {"true_name": None, "obj_email": None}. Pass None to retrieve all attributes.
        :return: Contact attributes
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/getObjAttrs"
        
        # If attrs is None, get all attributes using a template of all possible attributes set to None
        if attrs is None:
            attrs = {field: None for field in ContactAttributeQuery.model_fields.keys()}
        
        payload = {
            "_token": token,
            "obj_uid": obj_uid,
            "attrs": attrs
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, GetObjAttrsResponse)

    def setObjAttrs(self, obj_uid: str, attrs: ContactAttributes) -> SetObjAttrsResponse:
        """
        Set contact attributes.
        
        :param obj_uid: Contact object UID
        :param attrs: Attributes to set
        :return: Success response
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/setObjAttrs"
        
        payload = {
            "_token": token,
            "obj_uid": obj_uid,
            "attrs": attrs.model_dump(exclude_unset=True)
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, SetObjAttrsResponse)

    def deleteObj(self, obj_uid: str) -> DeleteObjResponse:
        """
        Delete contact.
        
        :param obj_uid: Contact object UID to delete
        :return: Success response
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/deleteObj"
        
        payload = {
            "_token": token,
            "obj_uid": obj_uid
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, DeleteObjResponse)

    # 3.7 域名维护 section methods
    def domainExist(self, domain_name: str) -> DomainExistResponse:
        """
        Check if domain exists.
        
        :param domain_name: Domain name to check
        :return: Domain name if exists, or error if not
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/domainExist"
        
        payload = {
            "_token": token,
            "domain_name": domain_name
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, DomainExistResponse)

    def addDomain25(self, domain_name: str) -> AddDomainResponse:
        """
        Add domain.
        
        :param domain_name: Domain name to add
        :return: Success response
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/addDomain25"
        
        payload = {
            "_token": token,
            "domain_name": domain_name
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, AddDomainResponse)

    def delDomain25(self, domain_name: str) -> DelDomainResponse:
        """
        Delete domain.
        
        :param domain_name: Domain name to delete
        :return: Success response
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/delDomain25"
        
        payload = {
            "_token": token,
            "domain_name": domain_name
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, DelDomainResponse)

    def addDomainAlias(self, domain_name: str, domain_name_alias: str) -> AddDomainAliasResponse:
        """
        Add domain alias.
        
        :param domain_name: Domain name
        :param domain_name_alias: Domain alias to add
        :return: Success response
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/addDomainAlias"
        
        payload = {
            "_token": token,
            "domain_name": domain_name,
            "domain_name_alias": domain_name_alias
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, AddDomainAliasResponse)

    def getDomainAlias(self, domain_name: str) -> GetDomainAliasResponse:
        """
        Get domain aliases.
        
        :param domain_name: Domain name
        :return: Comma-separated list of domain aliases
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/getDomainAlias"
        
        payload = {
            "_token": token,
            "domain_name": domain_name
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, GetDomainAliasResponse)

    def delDomainAlias(self, domain_name: str, domain_name_alias: str) -> DelDomainAliasResponse:
        """
        Delete domain alias.
        
        :param domain_name: Domain name
        :param domain_name_alias: Domain alias to delete
        :return: Success response
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/delDomainAlias"
        
        payload = {
            "_token": token,
            "domain_name": domain_name,
            "domain_name_alias": domain_name_alias
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, DelDomainAliasResponse)

    def getOrgListByDomain(self, domain_name: str) -> GetOrgListByDomainResponse:
        """
        Get organization list by domain.
        
        :param domain_name: Domain name
        :return: Comma-separated list of organization IDs
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/getOrgListByDomain"
        
        payload = {
            "_token": token,
            "domain_name": domain_name
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, GetOrgListByDomainResponse)

    # 3.8 邮件维护 section methods
    def listMailInfos(self, user_at_domain: str, options: Optional[Dict[str, Any]] = None) -> ListMailInfosResponse:
        """
        List user's mail messages.
        
        :param user_at_domain: User identifier in format "user@domain"
        :param options: Options for filtering (limit, fid, skip, order)
        :return: List of mail messages
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/listMailInfos"
        
        payload = {
            "_token": token,
            "user_at_domain": user_at_domain
        }
        
        if options:
            payload["options"] = options
        else:
            # Default options
            payload["options"] = {
                "limit": 10,
                "fid": 1,  # Inbox
                "skip": 0,
                "order": "receivedDate"
            }
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, ListMailInfosResponse)

    def getNewMailInfos(self, user_at_domain: str, options: Optional[Dict[str, Any]] = None) -> GetNewMailInfosResponse:
        """
        Get user's unread mail messages.
        
        :param user_at_domain: User identifier in format "user@domain"
        :param options: Options for filtering (limit, excludeFidList, doubleDecode, format)
        :return: List of unread mail messages
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/getNewMailInfos"
        
        payload = {
            "_token": token,
            "user_at_domain": user_at_domain
        }
        
        if options:
            payload["options"] = options
        else:
            # Default options
            payload["options"] = {
                "limit": 10,
                "excludeFidList": [],
                "doubleDecode": False,
                "format": ""
            }
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, GetNewMailInfosResponse)

    def smtpTransport(self, mail_from: Optional[str] = None, rcpt_to: Optional[str] = None, data: Optional[str] = None, options: Optional[Dict[str, Any]] = None) -> SmtpTransportResponse:
        """
        Send mail through MTA.
        
        :param mail_from: Sender email address
        :param rcpt_to: Recipient email address
        :param data: Mail content in RFC822 format
        :param options: Additional options (remote_ip, X-Coremail-Context)
        :return: Success response
        """
        token = self.requestToken()
        
        url = f"{self.base_url}/smtpTransport"
        
        payload = {
            "_token": token
        }
        
        if mail_from:
            payload["mail_from"] = mail_from
        if rcpt_to:
            payload["rcpt_to"] = rcpt_to
        if data:
            payload["data"] = data
        if options:
            payload["options"] = options
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response, SmtpTransportResponse)

    def refresh_token(self) -> str:
        """
        Refresh the authentication token.
        
        :return: New authentication token
        """
        # Clear the cached token to force a refresh
        self.token_cache.clear()
        return self.requestToken()