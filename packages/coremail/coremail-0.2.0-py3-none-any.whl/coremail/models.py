from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, model_validator


class BaseResponse(BaseModel):
    code: int
    message: Optional[str] = None


class TokenResponse(BaseModel):
    code: int
    result: str


class AuthenticateResponse(BaseModel):
    code: int
    message: Optional[str] = None


class SessionInfoResponse(BaseModel):
    code: int
    result: str
    message: Optional[str] = None


class SessionInfoResult(BaseModel):
    uid: str
    domain_id: str
    org_id: str


class SessionVariableResponse(BaseModel):
    code: int
    result: str
    message: Optional[str] = None


class UserExistResponse(BaseModel):
    code: int
    result: str
    message: Optional[str] = None


class UserAttributeQuery(BaseModel):
    # User identification attributes
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    domain_name: Optional[str] = None
    alias: Optional[str] = None
    
    # Password attributes
    password: Optional[str] = None
    password_expired: Optional[bool] = None
    password_change_date: Optional[str] = None
    password_change_cycle: Optional[int] = None
    password_change_next_time: Optional[bool] = None
    password_lock_date: Optional[str] = None
    password_lock_cycle: Optional[int] = None
    password_lock_next_time: Optional[bool] = None
    password_lock_time: Optional[int] = None
    password_lock_count: Optional[int] = None
    password_lock_interval: Optional[int] = None
    password_lock_admin: Optional[bool] = None
    password_lock_enabled: Optional[bool] = None
    
    # Storage attributes
    quota_mb: Optional[int] = None
    quota_used_mb: Optional[float] = None
    quota_used_percent: Optional[float] = None
    mailsize_limit_mb: Optional[int] = None
    receive_size_limit_mb: Optional[int] = None
    send_size_limit_mb: Optional[int] = None
    
    # Limitation attributes
    receive_limit_count: Optional[int] = None
    send_limit_count: Optional[int] = None
    receive_limit_cycle: Optional[str] = None
    send_limit_cycle: Optional[str] = None
    receive_limit_enabled: Optional[bool] = None
    send_limit_enabled: Optional[bool] = None
    receive_limit_time: Optional[str] = None
    send_limit_time: Optional[str] = None
    receive_limit_exception: Optional[str] = None
    send_limit_exception: Optional[str] = None
    receive_limit_white_list: Optional[str] = None
    send_limit_white_list: Optional[str] = None
    receive_limit_black_list: Optional[str] = None
    send_limit_black_list: Optional[str] = None
    
    # Mail retention attributes
    mail_days_keep: Optional[int] = None
    receive_mail_days_keep: Optional[int] = None
    send_mail_days_keep: Optional[int] = None
    receive_mail_days_keep_enabled: Optional[bool] = None
    send_mail_days_keep_enabled: Optional[bool] = None
    
    # Forwarding attributes
    forward_type: Optional[int] = None
    forward_addr: Optional[str] = None
    forward_backup: Optional[bool] = None
    
    # Auto-reply attributes
    auto_reply_enabled: Optional[bool] = None
    auto_reply_subject: Optional[str] = None
    auto_reply_message: Optional[str] = None
    auto_reply_date_start: Optional[str] = None
    auto_reply_date_end: Optional[str] = None
    auto_reply_holidays_enabled: Optional[bool] = None
    auto_reply_holidays_list: Optional[str] = None
    auto_reply_vacation_enabled: Optional[bool] = None
    auto_reply_vacation_message: Optional[str] = None
    auto_reply_vacation_date_start: Optional[str] = None
    auto_reply_vacation_date_end: Optional[str] = None
    
    # Mail filtering attributes
    mail_filter_enabled: Optional[bool] = None
    mail_filter_rules: Optional[str] = None
    mail_filter_white_list: Optional[str] = None
    mail_filter_black_list: Optional[str] = None
    
    # User status attributes
    user_enabled: Optional[bool] = None
    admin_enabled: Optional[bool] = None
    admin_privileges: Optional[str] = None
    admin_domains: Optional[str] = None
    
    # Date attributes
    create_date: Optional[str] = None
    modify_date: Optional[str] = None
    last_login_date: Optional[str] = None
    last_login_ip: Optional[str] = None
    login_count: Optional[int] = None
    login_fail_count: Optional[int] = None
    login_fail_date: Optional[str] = None
    login_fail_ip: Optional[str] = None
    login_fail_lock: Optional[bool] = None
    login_fail_lock_time: Optional[int] = None
    login_fail_lock_count: Optional[int] = None
    login_fail_lock_interval: Optional[int] = None
    login_fail_lock_admin: Optional[bool] = None
    login_fail_lock_enabled: Optional[bool] = None


class UserAttributes(BaseModel):
    primary_email: Optional[str] = None  # 指å¤-éšè¿ä¸»éè®¢åžåç?
    alias: Optional[List[str]] = None  # æå-éšååå®ä»¶å°ç?
    org_unit_id: Optional[str] = None  # ééåååä¼°è?
    user_status: Optional[int] = None  # ç”³æä¸°çŠ:0-æ©é¥,1-å¹é,2-ç»å,3-ä»£ç,4-éé,100-å»¶è¿åæ
    password: Optional[str] = None  # ç”Žæå¯
    cos_id: Optional[int] = None  # æå¤çº§å¨è®°è?
    quota_delta: Optional[int] = None  # éååè©ä¹¡éè¿(MB)
    nf_quota_delta: Optional[int] = None  # éååç±è¥ä¹¡éè¿(MB)
    privacy_level: Optional[int] = None  # ä¿¡æåç»é–¿èŒåå:0-ä¸-å,2-ç»éçºä,4-ç«™çºä
    user_list_rank: Optional[int] = None  # ¹è®°
    true_name: Optional[str] = None  # å
    nick_name: Optional[str] = None  # ³
    duty: Optional[str] = None  # è¡å
    gender: Optional[str] = None  # ²: "0"-ç, "1"-å
    birthday: Optional[str] = None  # é©
    alt_email: Optional[str] = None  # ¹æä»¶ç®ç?
    mobile_number: Optional[str] = None  # æªéªç
    home_phone: Optional[str] = None  # å®ç®ç”
    company_phone: Optional[str] = None  # å…¬åç”
    fax_number: Optional[str] = None  # å¨ä»¹ç
    province: Optional[str] = None  # ç?/å
    city: Optional[str] = None  # å
    anniversary: Optional[str] = None  # å‘—å¹´ç¬ä¹ç?
    zipcode: Optional[str] = None  # é¦å²è?
    address: Optional[str] = None  # èÁåå?
    homepage: Optional[str] = None  # å…¬åä¸»é¡
    remarks: Optional[str] = None  # å
    user_security_role: Optional[int] = None  # äººåç²è?
    security_level: Optional[int] = None  # æ¯ä¿¡å¯ç?
    sender_security_level: Optional[int] = None  # ååä¿¡å¯ç?
    smsaddr: Optional[str] = None  # ç»éæè™å
    second_auth_type: Optional[int] = None  # äşå·éªå®çą:1-å


class GetAttrsResponse(BaseModel):
    code: int
    result: Optional[Dict[str, Any]] = None  # Raw result from API
    message: Optional[str] = None

    def get_user_attributes(self) -> Optional[UserAttributes]:
        """
        Returns the result as a UserAttributes model for type safety
        """
        if self.result is None:
            return None
        return UserAttributes.model_validate(self.result)

    def get_result_data(self) -> Optional[UserAttributes]:
        """
        Returns the actual result data for direct access
        """
        return self.get_user_attributes()


class ChangeAttrsResponse(BaseModel):
    code: int
    message: Optional[str] = None


class CreateResponse(BaseModel):
    code: int
    message: Optional[str] = None


class DeleteResponse(BaseModel):
    code: int
    message: Optional[str] = None


class GetUserAliasResponse(BaseModel):
    code: int
    result: str
    message: Optional[str] = None

    def get_result_data(self) -> str:
        """
        Returns the actual result data for direct access
        """
        return self.result


class AddAliasResponse(BaseModel):
    code: int
    message: Optional[str] = None


class DeleteAliasResponse(BaseModel):
    code: int
    message: Optional[str] = None


class GetAliasResponse(BaseModel):
    code: int
    result: str  # Comma-separated list of aliases
    message: Optional[str] = None


class OrgAttributeQuery(BaseModel):
    org_name: Optional[str] = None
    domain_name: Optional[str] = None
    org_status: Optional[int] = None
    org_expiry_date: Optional[str] = None
    cos_info: Optional[str] = None
    total_users: Optional[int] = None
    used_users: Optional[int] = None
    used_quota_delta: Optional[int] = None
    used_mail_quota_delta: Optional[int] = None
    used_nf_quota_delta: Optional[int] = None


class OrgAttributes(BaseModel):
    org_name: Optional[str] = None
    domain_name: Optional[str] = None
    org_status: Optional[int] = None
    org_expiry_date: Optional[str] = None
    cos_info: Optional[str] = None
    total_users: Optional[int] = None
    used_users: Optional[int] = None
    used_quota_delta: Optional[int] = None
    used_mail_quota_delta: Optional[int] = None
    used_nf_quota_delta: Optional[int] = None
    cos_id: Optional[Union[int, List[int]]] = None
    num_of_classes: Optional[Union[int, List[int]]] = None
    res_grp_id: Optional[str] = None
    org_assignable_quota: Optional[int] = None
    org_options: Optional[int] = None
    org_active_options: Optional[int] = None
    org_address: Optional[str] = None
    org_phone_number: Optional[str] = None
    org_contact: Optional[str] = None
    org_access_level: Optional[int] = None
    org_access_user: Optional[str] = None
    org_deny_user: Optional[str] = None
    org_access_user_l1: Optional[str] = None
    email_allow_user: Optional[str] = None


class GetOrgInfoResponse(BaseModel):
    code: int
    result: Optional[OrgAttributes] = None
    message: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def validate_result(cls, values):
        if isinstance(values, dict):
            result_data = values.get('result')
            if result_data and isinstance(result_data, dict):
                # Convert the result dict to OrgAttributes model
                values['result'] = OrgAttributes.model_validate(result_data)
        return values

    def get_result_data(self) -> Optional[OrgAttributes]:
        """
        Returns the actual result data for direct access
        """
        return self.result


class GetOrgListResponse(BaseModel):
    code: int
    result: str  # Comma-separated list of org IDs
    message: Optional[str] = None

    def get_result_data(self) -> str:
        """
        Returns the actual result data for direct access
        """
        return self.result


class UnitAttributeQuery(BaseModel):
    parent_org_unit_id: Optional[str] = None
    org_unit_name: Optional[str] = None
    org_unit_list_rank: Optional[int] = None
    user_count: Optional[int] = None
    abook_user_count: Optional[int] = None


class AddOrgResponse(BaseModel):
    code: int
    message: Optional[str] = None


class AddOrgDomainResponse(BaseModel):
    code: int
    message: Optional[str] = None


class DelOrgDomainResponse(BaseModel):
    code: int
    message: Optional[str] = None


class AddOrgCosResponse(BaseModel):
    code: int
    message: Optional[str] = None


class DelOrgCosResponse(BaseModel):
    code: int
    message: Optional[str] = None


class GetOrgCosUserResponse(BaseModel):
    code: int
    result: str  # Comma-separated list of user IDs
    message: Optional[str] = None


class AddUnitResponse(BaseModel):
    code: int
    message: Optional[str] = None


class DelUnitResponse(BaseModel):
    code: int
    message: Optional[str] = None


class ContactAttributes(BaseModel):
    org_id: Optional[str] = None
    org_unit_id: Optional[str] = None
    obj_class: Optional[int] = None
    obj_email: Optional[str] = None
    obj_creation_date: Optional[str] = None
    privacy_level: Optional[int] = None
    obj_list_rank: Optional[int] = None
    true_name: Optional[str] = None
    nick_name: Optional[str] = None
    duty: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[str] = None
    alt_email: Optional[str] = None
    mobile_number: Optional[str] = None
    home_phone: Optional[str] = None
    company_phone: Optional[str] = None
    fax_number: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    anniversary: Optional[str] = None
    zipcode: Optional[str] = None
    address: Optional[str] = None
    homepage: Optional[str] = None
    remarks: Optional[str] = None


class ContactAttributeQuery(BaseModel):
    org_id: Optional[str] = None
    org_unit_id: Optional[str] = None
    obj_class: Optional[int] = None
    obj_email: Optional[str] = None
    obj_creation_date: Optional[str] = None
    privacy_level: Optional[int] = None
    obj_list_rank: Optional[int] = None
    true_name: Optional[str] = None
    nick_name: Optional[str] = None
    duty: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[str] = None
    alt_email: Optional[str] = None
    mobile_number: Optional[str] = None
    home_phone: Optional[str] = None
    company_phone: Optional[str] = None
    fax_number: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    anniversary: Optional[str] = None
    zipcode: Optional[str] = None
    address: Optional[str] = None
    homepage: Optional[str] = None
    remarks: Optional[str] = None


class CreateObjectResponse(BaseModel):
    code: int
    result: Optional[Dict[str, str]] = None  # Contains obj_uid
    message: Optional[str] = None


class GetObjAttrsResponse(BaseModel):
    code: int
    result: Optional[ContactAttributes] = None
    message: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def validate_result(cls, values):
        if isinstance(values, dict):
            result_data = values.get('result')
            if result_data and isinstance(result_data, dict):
                # Convert the result dict to ContactAttributes model
                values['result'] = ContactAttributes.model_validate(result_data)
        return values

    def get_result_data(self) -> Optional[ContactAttributes]:
        """
        Returns the actual result data for direct access
        """
        return self.result


class SetObjAttrsResponse(BaseModel):
    code: int
    message: Optional[str] = None


class DeleteObjResponse(BaseModel):
    code: int
    message: Optional[str] = None


class DomainExistResponse(BaseModel):
    code: int
    result: Optional[str] = None  # Domain name if exists
    message: Optional[str] = None

    def get_result_data(self) -> Optional[str]:
        """
        Returns the actual result data for direct access
        """
        return self.result


class AddDomainResponse(BaseModel):
    code: int
    message: Optional[str] = None


class DelDomainResponse(BaseModel):
    code: int
    message: Optional[str] = None


class AddDomainAliasResponse(BaseModel):
    code: int
    message: Optional[str] = None


class GetDomainAliasResponse(BaseModel):
    code: int
    result: str  # Comma-separated list of domain aliases
    message: Optional[str] = None


class DelDomainAliasResponse(BaseModel):
    code: int
    message: Optional[str] = None


class GetOrgListByDomainResponse(BaseModel):
    code: int
    result: str  # Comma-separated list of organization IDs
    message: Optional[str] = None


class MailInfoAttributes(BaseModel):
    mid: str
    msid: int
    fid: int
    flag: int
    from_addr: str = Field(alias="from")
    to: str
    subject: str
    size: int
    date: str


class ListMailInfosResponse(BaseModel):
    code: int
    result: Optional[Dict[str, List[MailInfoAttributes]]] = None  # Contains "mail" key with list of mails
    message: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def validate_result(cls, values):
        if isinstance(values, dict):
            result_data = values.get('result')
            if result_data and isinstance(result_data, dict) and 'mail' in result_data:
                # Process the mail list by validating each item as MailInfoAttributes
                mail_list = result_data.get('mail', [])
                validated_mail_list = [MailInfoAttributes.model_validate(item) for item in mail_list]
                result_data['mail'] = validated_mail_list
                values['result'] = result_data
        return values


class GetNewMailInfosResponse(BaseModel):
    code: int
    result: Optional[Dict[str, List[MailInfoAttributes]]] = None  # Contains "mail" key with list of mails
    message: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def validate_result(cls, values):
        if isinstance(values, dict):
            result_data = values.get('result')
            if result_data and isinstance(result_data, dict) and 'mail' in result_data:
                # Process the mail list by validating each item as MailInfoAttributes
                mail_list = result_data.get('mail', [])
                validated_mail_list = [MailInfoAttributes.model_validate(item) for item in mail_list]
                result_data['mail'] = validated_mail_list
                values['result'] = result_data
        return values


class SmtpTransportResponse(BaseModel):
    code: int
    message: Optional[str] = None


class SetAdminTypeResponse(BaseModel):
    code: int
    message: Optional[str] = None


class GetAdminTypeResponse(BaseModel):
    code: int
    result: str  # Format: "admin_type=...&role_id=..."
    message: Optional[str] = None


class RenameUserResponse(BaseModel):
    code: int
    message: Optional[str] = None


class MoveUserResponse(BaseModel):
    code: int
    message: Optional[str] = None


class UnitAttributes(BaseModel):
    parent_org_unit_id: Optional[str] = None
    org_unit_name: Optional[str] = None
    org_unit_list_rank: Optional[int] = None
    user_count: Optional[int] = None
    abook_user_count: Optional[int] = None


class GetUnitAttrsResponse(BaseModel):
    code: int
    result: Optional[UnitAttributes] = None
    message: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def validate_result(cls, values):
        if isinstance(values, dict):
            result_data = values.get('result')
            if result_data and isinstance(result_data, dict):
                # Convert the result dict to UnitAttributes model
                values['result'] = UnitAttributes.model_validate(result_data)
        return values

    def get_result_data(self) -> Optional[UnitAttributes]:
        """
        Returns the actual result data for direct access
        """
        return self.result


class ListResponse(BaseModel):
    code: int
    result: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class ListDomainsResponse(BaseModel):
    code: int
    result: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

    def get_result_data(self) -> Optional[Dict[str, Any]]:
        """
        Returns the actual result data for direct access
        """
        return self.result


class DomainAttributes(BaseModel):
    domain_name: Optional[str] = None
    domain_alias: Optional[str] = None
    quota_mb: Optional[int] = None
    max_users: Optional[int] = None
    user_count: Optional[int] = None
    enabled: Optional[bool] = None
    create_date: Optional[str] = None
    modify_date: Optional[str] = None
    mail_size_limit_mb: Optional[int] = None
    receive_size_limit_mb: Optional[int] = None
    send_size_limit_mb: Optional[int] = None
    receive_limit_count: Optional[int] = None
    send_limit_count: Optional[int] = None
    receive_limit_cycle: Optional[str] = None
    send_limit_cycle: Optional[str] = None
    receive_limit_enabled: Optional[bool] = None
    send_limit_enabled: Optional[bool] = None
    admin_user_id: Optional[str] = None
    admin_email: Optional[str] = None
    description: Optional[str] = None


class GetDomainAttrsResponse(BaseModel):
    code: int
    result: Optional[DomainAttributes] = None
    message: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def validate_result(cls, values):
        if isinstance(values, dict):
            result_data = values.get('result')
            if result_data and isinstance(result_data, dict):
                # Convert the result dict to DomainAttributes model
                values['result'] = DomainAttributes.model_validate(result_data)
        return values

    def get_result_data(self) -> Optional[DomainAttributes]:
        """
        Returns the actual result data for direct access
        """
        return self.result


class ChangeDomainAttrsResponse(BaseModel):
    code: int
    message: Optional[str] = None


class AdminResponse(BaseModel):
    code: int
    result: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class SearchResponse(BaseModel):
    code: int
    result: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class LogResponse(BaseModel):
    code: int
    result: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class GroupResponse(BaseModel):
    code: int
    message: Optional[str] = None


class SystemConfigResponse(BaseModel):
    code: int
    result: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class RequestTokenParams(BaseModel):
    app_id: str
    secret: str


class UserLoginParams(BaseModel):
    token: str = Field(alias="_token")
    user_at_domain: str


class UserLoginExParams(BaseModel):
    token: str = Field(alias="_token")
    user_at_domain: str
    attrs: Optional[str] = None


class UserExistParams(BaseModel):
    token: str = Field(alias="_token")
    user_at_domain: str


class AuthenticateParams(BaseModel):
    token: str = Field(alias="_token")
    user_at_domain: str
    password: str


class SesTimeOutParams(BaseModel):
    token: str = Field(alias="_token")
    ses_id: str


class SesRefreshParams(BaseModel):
    token: str = Field(alias="_token")
    ses_id: str


class GetSessionVarParams(BaseModel):
    token: str = Field(alias="_token")
    ses_id: str
    ses_key: str


class UserLogoutParams(BaseModel):
    token: str = Field(alias="_token")
    ses_id: str


class SetSessionVarParams(BaseModel):
    token: str = Field(alias="_token")
    ses_id: str
    ses_key: str
    ses_var: str


class AddSmtpAliasParams(BaseModel):
    token: str = Field(alias="_token")
    user_at_domain: str
    alias_user_at_domain: str


class DelSmtpAliasParams(BaseModel):
    token: str = Field(alias="_token")
    user_at_domain: str
    alias_user_at_domain: str


class GetSmtpAliasParams(BaseModel):
    token: str = Field(alias="_token")
    user_at_domain: str


class GetAttrsParams(BaseModel):
    token: str = Field(alias="_token")
    user_at_domain: str
    attrs: Optional[Dict[str, Any]] = None


class ChangeAttrsParams(BaseModel):
    token: str = Field(alias="_token")
    user_at_domain: str
    attrs: Dict[str, Any]


class CreateParams(BaseModel):
    token: str = Field(alias="_token")
    user_at_domain: str
    attrs: Dict[str, Any]


class DeleteParams(BaseModel):
    token: str = Field(alias="_token")
    user_at_domain: str
    preserve_days: Optional[int] = 0


class GetOrgInfoParams(BaseModel):
    token: str = Field(alias="_token")
    org_id: str
    attrs: Optional[Dict[str, Any]] = None


class AlterOrgParams(BaseModel):
    token: str = Field(alias="_token")
    org_id: str
    attrs: Dict[str, Any]


class AddOrgDomainParams(BaseModel):
    token: str = Field(alias="_token")
    org_id: str
    domain_name: str


class DelOrgDomainParams(BaseModel):
    token: str = Field(alias="_token")
    org_id: str
    domain_name: str


class AddOrgCosParams(BaseModel):
    token: str = Field(alias="_token")
    org_id: str
    cos_id: Optional[int] = None
    cos_name: Optional[str] = None
    num_of_classes: int


class AlterOrgCosParams(BaseModel):
    token: str = Field(alias="_token")
    org_id: str
    cos_id: Optional[int] = None
    cos_name: Optional[str] = None
    num_of_classes: int


class DelOrgCosParams(BaseModel):
    token: str = Field(alias="_token")
    org_id: str
    cos_id: int


class GetOrgCosUserParams(BaseModel):
    token: str = Field(alias="_token")
    org_id: str
    cos_id: int


class AddUnitParams(BaseModel):
    token: str = Field(alias="_token")
    org_id: str
    org_unit_id: str
    attrs: Dict[str, Any]
    dont_flush_md: Optional[bool] = False


class DelUnitParams(BaseModel):
    token: str = Field(alias="_token")
    org_id: str
    org_unit_id: str
    dont_flush_md: Optional[bool] = False


class GetUnitAttrsParams(BaseModel):
    token: str = Field(alias="_token")
    org_id: str
    org_unit_id: str
    attrs: Optional[Dict[str, Any]] = None


class SetUnitAttrsParams(BaseModel):
    token: str = Field(alias="_token")
    org_id: str
    org_unit_id: str
    attrs: Dict[str, Any]
    dont_flush_md: Optional[bool] = False


class RenameUserParams(BaseModel):
    token: str = Field(alias="_token")
    user_at_domain: str
    new_user_id: str


class MoveUserParams(BaseModel):
    token: str = Field(alias="_token")
    user_at_domain: str
    attrs: Dict[str, Any]


class DomainAttributeQuery(BaseModel):
    domain_name: Optional[str] = None
    domain_alias: Optional[str] = None
    quota_mb: Optional[int] = None
    max_users: Optional[int] = None
    user_count: Optional[int] = None
    enabled: Optional[bool] = None
    create_date: Optional[str] = None
    modify_date: Optional[str] = None
    mail_size_limit_mb: Optional[int] = None
    receive_size_limit_mb: Optional[int] = None
    send_size_limit_mb: Optional[int] = None
    receive_limit_count: Optional[int] = None
    send_limit_count: Optional[int] = None
    receive_limit_cycle: Optional[str] = None
    send_limit_cycle: Optional[str] = None
    receive_limit_enabled: Optional[bool] = None
    send_limit_enabled: Optional[bool] = None
    admin_user_id: Optional[str] = None
    admin_email: Optional[str] = None
    description: Optional[str] = None


class GetDomainListResponse(BaseModel):
    code: int
    result: str
    message: Optional[str] = None

    def get_result_data(self) -> str:
        """
        Returns the actual result data for direct access
        """
        return self.result


class BaseResponse(BaseModel):
    code: int
    message: Optional[str] = None


class SessionResponse(BaseModel):
    code: int
    result: str
    message: Optional[str] = None