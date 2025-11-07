"""
Coremail SDK for Python
A library for interacting with Coremail XT API
"""
from .client import CoremailClient
from .models import *

__version__ = "0.1.0"
__all__ = [
    "CoremailClient",
    "TokenResponse",
    "AuthenticateResponse", 
    "GetAttrsResponse",
    "UserAttributes",
    "CoremailConfig",
    "AddAliasResponse",
    "DeleteAliasResponse",
    "GetAliasResponse",
    "SessionInfoResponse",
    "SessionVariableResponse",
    "GetUserAliasResponse",
    "GetOrgInfoResponse",
    "GetOrgListResponse",
    "GetDomainListResponse",
    "GetUnitAttrsResponse",
    "RequestTokenParams",
    "UserLoginParams",
    "UserLoginExParams",
    "UserExistParams",
    "AuthenticateParams",
    "SesTimeOutParams",
    "SesRefreshParams",
    "GetSessionVarParams",
    "UserLogoutParams",
    "SetSessionVarParams",
    "AddSmtpAliasParams",
    "DelSmtpAliasParams",
    "GetSmtpAliasParams",
    "GetAttrsParams",
    "ChangeAttrsParams",
    "CreateParams",
    "DeleteParams",
    "GetOrgInfoParams",
    "AlterOrgParams",
    "AddOrgDomainParams",
    "DelOrgDomainParams",
    "AddOrgCosParams",
    "AlterOrgCosParams",
    "DelOrgCosParams",
    "GetOrgCosUserParams",
    "AddUnitParams",
    "DelUnitParams",
    "GetUnitAttrsParams",
    "SetUnitAttrsParams",
    "RenameUserParams",
    "MoveUserParams"
]