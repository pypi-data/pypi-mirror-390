from enum import Enum
from typing import Any, Dict, List, Optional

from pytz import all_timezones
from ul_api_utils.api_resource.api_response import JsonApiResponsePayload
from ul_api_utils.api_resource.api_response_payload_alias import ApiBaseUserModelPayloadResponse
from pydantic import BaseModel, UUID4

from ul_api_utils.validators.custom_fields import PgTypeShortStrAnnotation
from pii_sdk.types.enums.organization_user_state import OrganizationUserState
from datetime import datetime



TimeZonesEnum = Enum('tz_type', {tz_name.lower().replace('/', '_'): tz_name for tz_name in all_timezones})       # type: ignore


class ApiOrganizationData(BaseModel):
    admin_notes: Optional[str] = None
    name: str
    available_permissions: List[int]
    timezones: List[TimeZonesEnum]


class ApiOrganization(ApiBaseUserModelPayloadResponse):
    admin_notes: Optional[str] = None
    organization_data: ApiOrganizationData
    frontend_settings: Dict[str, Any]
    teams_count: int
    users_count: int

class ApiOrganizationAvailableEvents(JsonApiResponsePayload):
    available_events: list[str]


class ApiUserListResponse(JsonApiResponsePayload):
    """Упрощенная модель ответа для списков пользователей организации"""
    
    id: UUID4
    date_created: datetime
    date_modified: datetime
    is_alive: bool
    
    # Основная информация о пользователе
    is_superuser: bool
    
    # Данные пользователя (только основные поля)
    email: PgTypeShortStrAnnotation
    first_name: Optional[PgTypeShortStrAnnotation] = None
    last_name: Optional[PgTypeShortStrAnnotation] = None
    nick_name: Optional[PgTypeShortStrAnnotation] = None
    
    # Статус в организации
    organization_user_state: OrganizationUserState
    organization_user_notes: Optional[str] = None
    
    # Количество команд пользователя в организации
    teams_count: int = 0


class ApiOrganizationUserEmails(JsonApiResponsePayload):
    emails: list[str]
