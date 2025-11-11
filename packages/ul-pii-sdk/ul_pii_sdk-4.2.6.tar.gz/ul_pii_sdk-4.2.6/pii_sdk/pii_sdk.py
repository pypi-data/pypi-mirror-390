import json

from uuid import UUID
from typing import List

from ul_api_utils.internal_api.internal_api import InternalApi
from ul_api_utils.internal_api.internal_api_response import InternalApiResponse

from pii_sdk.pii_sdk_config import PiiSdkConfig
from pii_sdk.types.api_ogranization import ApiOrganization, ApiOrganizationAvailableEvents
from pii_sdk.types.api_user import ApiUserEventsToSendEmail, ApiUserAllowedEvents
from pii_sdk.utils.internal_api_error_handler import internal_api_error_handler
from pii_sdk.types.api_ogranization import ApiUserListResponse, ApiOrganizationUserEmails


class PiiSdk:
    def __init__(self, config: PiiSdkConfig) -> None:
        self._config = config
        self._api = InternalApi(self._config.api_url, default_auth_token=self._config.api_token)

    @internal_api_error_handler
    def get_organization_by_id(self, organization_id: UUID) -> InternalApiResponse[ApiOrganization]:
        return self._api.request_get(f'/organizations/{organization_id}').typed(ApiOrganization).check()

    @internal_api_error_handler
    def get_organization_by_name(self, organization_name: str) -> InternalApiResponse[List[ApiOrganization]]:       # type: ignore
        return self._api.request_get(
            '/organizations',
            q={"filter": '[{"name":"organization_data","op":"has","val":{"name":"name","op": "==","val": "%s"}}]' % organization_name},
        ).typed(List[ApiOrganization]).check()

    @internal_api_error_handler
    def get_organizations_by_id_list(self, organization_ids: List[UUID]) -> InternalApiResponse[List[ApiOrganization]]:     # type: ignore
        organization_ids_str = json.dumps([str(org_id) for org_id in organization_ids])
        return self._api.request_get(
            '/organizations',
            q={"filter": '[{"name":"id","op": "in","val": %s}]' % organization_ids_str},
        ).typed(List[ApiOrganization]).check()

    @internal_api_error_handler
    def get_organizations(self) -> InternalApiResponse[List[ApiOrganization]]:      # type: ignore
        return self._api.request_get('/organizations').typed(List[ApiOrganization]).check()

    @internal_api_error_handler
    def get_organizations_available_events(self, organization_id: UUID) -> InternalApiResponse[ApiOrganizationAvailableEvents]:
        return self._api.request_get(f'/organizations/{organization_id}/available_events').typed(ApiOrganizationAvailableEvents).check()
    
    @internal_api_error_handler
    def get_organizations_users_list(self, organization_id: UUID) -> InternalApiResponse[List[ApiUserListResponse]]:     # type: ignore
        return self._api.request_get(f'/organizations/{organization_id}/users/list').typed(List[ApiUserListResponse]).check()

    @internal_api_error_handler
    def get_user_send_event_email_list(self, user_id: UUID) -> InternalApiResponse[ApiUserEventsToSendEmail]:
        return self._api.request_get(f'/users/{user_id}/events_to_send_email').typed(ApiUserEventsToSendEmail).check()

    @internal_api_error_handler
    def get_organization_users_emails_by_events(self, organization_id: UUID, events: List[str]) -> InternalApiResponse[ApiOrganizationUserEmails]:
        return self._api.request_get(
            f'/organizations/{organization_id}/users/emails-by-events',
            q={"events": events},
        ).typed(ApiOrganizationUserEmails).check()

    @internal_api_error_handler
    def get_user_allowed_events(self, user_id: UUID) -> InternalApiResponse[ApiUserAllowedEvents]:
        return self._api.request_get(f'/users/{user_id}/allowed_events').typed(ApiUserAllowedEvents).check()
