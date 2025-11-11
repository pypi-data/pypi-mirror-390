from ul_api_utils.api_resource.api_response import JsonApiResponsePayload


class ApiUserEventsToSendEmail(JsonApiResponsePayload):
    events_to_send_email: list[str]


class ApiUserAllowedEvents(JsonApiResponsePayload):
    allowed_events: list[str]
