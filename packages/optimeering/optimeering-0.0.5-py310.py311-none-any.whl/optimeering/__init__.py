# coding: utf-8

# flake8: noqa

"""
    Optimeering

"""  # noqa: E501

__version__ = "0.0.2"

# import apis into sdk package
from optimeering.api.access_api import AccessApi
from optimeering.api.predictions_api import PredictionsApi
from optimeering.api_client import OptimeeringClient

# import OptimeeringClient
from optimeering.api_response import ApiResponse
from optimeering.azure_authentication import AzureAuth
from optimeering.configuration import Configuration
from optimeering.exceptions import (
    ApiAttributeError,
    ApiException,
    ApiKeyError,
    ApiTypeError,
    ApiValueError,
    OpenApiException,
)

# import models into sdk package
from optimeering.models.access_key_created import AccessKeyCreated
from optimeering.models.access_key_list_key_response import AccessKeyListKeyResponse
from optimeering.models.access_key_post_response import AccessKeyPostResponse
from optimeering.models.access_post_key import AccessPostKey
from optimeering.models.event_time_end import EventTimeEnd
from optimeering.models.event_time_start import EventTimeStart
from optimeering.models.expires_at import ExpiresAt
from optimeering.models.http_validation_error import HTTPValidationError
from optimeering.models.max_event_time import MaxEventTime
from optimeering.models.predictions_data import PredictionsData
from optimeering.models.predictions_data_list import PredictionsDataList
from optimeering.models.predictions_event import PredictionsEvent
from optimeering.models.predictions_series import PredictionsSeries
from optimeering.models.predictions_series_list import PredictionsSeriesList
from optimeering.models.predictions_value import PredictionsValue
from optimeering.models.predictions_version import PredictionsVersion
from optimeering.models.predictions_version_list import PredictionsVersionList
from optimeering.models.validation_error import ValidationError
from optimeering.models.validation_error_loc_inner import ValidationErrorLocInner
from optimeering.models.versioned_series import VersionedSeries

# add to __all__
__all__ = [
    "AccessApi",
    "PredictionsApi",
    "ApiResponse",
    "AzureAuth",
    "OptimeeringClient",
    "Configuration",
    "OpenApiException",
    "ApiTypeError",
    "ApiValueError",
    "ApiKeyError",
    "ApiAttributeError",
    "ApiException",
    "AccessKeyCreated",
    "AccessKeyListKeyResponse",
    "AccessKeyPostResponse",
    "AccessPostKey",
    "EventTimeEnd",
    "EventTimeStart",
    "ExpiresAt",
    "HTTPValidationError",
    "MaxEventTime",
    "PredictionsData",
    "PredictionsDataList",
    "PredictionsEvent",
    "PredictionsSeries",
    "PredictionsSeriesList",
    "PredictionsValue",
    "PredictionsVersion",
    "PredictionsVersionList",
    "ValidationError",
    "ValidationErrorLocInner",
    "VersionedSeries",
]
