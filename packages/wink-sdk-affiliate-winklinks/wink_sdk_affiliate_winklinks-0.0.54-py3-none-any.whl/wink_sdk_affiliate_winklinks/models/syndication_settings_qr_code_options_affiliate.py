# coding: utf-8

"""
    Wink API

     # Introduction  Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.  Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.   # Integrations  We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.   # Intended Audience  Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.  - Hotel chains  - Hotel brands  - Travel tech companies  - Destination sites  - Integrators  - Aggregators  - Destination management companies  - Travel agencies  - OTAs   ## APIs  Not every integrator needs every API. For that reason, we have separated APIs into context.  ### Test API   - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.  ### Common APIs  - [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account. - [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.  ### Consume APIs Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.   - [Configuration](/customization-client): A single endpoint to retrieve whitelabel + customization information for the booking customization.  - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.  - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..  - [Booking](/booking): All APIs related to creating bookings on the platform.  - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.   ### Produce APIs  Produce endpoints are for developers who want to create and manage travel inventory.   #### Property  - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.  - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.  - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.  - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.  - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.  - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.  - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.   #### Affiliate  - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.  - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.  - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.  - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.  - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.   #### Rate provider  - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.   ### Taxonomy APIs  Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.   - [Reference](/reference): All APIs related to retrieving platform-supported taxonomies.   ### Insight APIs  Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.   - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.   ### Payment APIs  Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant payment widget for all other entities.   - [TripPay](/payment): All APIs related to TripPay account management, booking, mapping and integration features.   ## SDKs  We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).   - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)   ## Usage  These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.   ## Versioning  We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.   ## Release history  - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md    # WinkLinks API The WinkLinks API exposes endpoints to manage WinkLink entries, categories and settings. This API lets you:  1. Entries: Manage WinkLinks entries. 2. Categories: Manage WinkLinks tags. 2. Settings: Configure WinkLinks account.  Browse the endpoints in the left navigation bar to get started.  

    The version of the OpenAPI document: 30.28.1
    Contact: bjorn@wink.travel
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from typing import Optional, Set
from typing_extensions import Self

class SyndicationSettingsQrCodeOptionsAffiliate(BaseModel):
    """
    SyndicationSettingsQrCodeOptionsAffiliate
    """ # noqa: E501
    image_identifier: Optional[StrictStr] = Field(default=None, description="Custom image ID for subscribers", alias="imageIdentifier")
    shape: Optional[StrictStr] = Field(default='SQUARE', description="QR code shape")
    dots_type: Optional[StrictStr] = Field(default='SQUARE', description="QR code shape", alias="dotsType")
    dots_round_size: Optional[StrictBool] = Field(default=True, description="Dots round size", alias="dotsRoundSize")
    dots_gradient_type: Optional[StrictStr] = Field(default='LINEAR', description="Dots gradient", alias="dotsGradientType")
    dots_gradient_rotation: Optional[StrictInt] = Field(default=0, description="Dots gradient rotation", alias="dotsGradientRotation")
    dots_start_color: Optional[StrictStr] = Field(default=None, description="Dots primary color", alias="dotsStartColor")
    dots_end_color: Optional[StrictStr] = Field(default=None, description="Dots gradient color", alias="dotsEndColor")
    corner_square_type: Optional[StrictStr] = Field(default='SQUARE', description="Corner square type", alias="cornerSquareType")
    corner_square_gradient_type: Optional[StrictStr] = Field(default='LINEAR', description="Corners square gradient", alias="cornerSquareGradientType")
    corner_square_gradient_rotation: Optional[StrictInt] = Field(default=0, description="Corners square gradient rotation", alias="cornerSquareGradientRotation")
    corner_square_start_color: Optional[StrictStr] = Field(default=None, description="Corner square primary color", alias="cornerSquareStartColor")
    corner_square_end_color: Optional[StrictStr] = Field(default=None, description="Corner square gradient color", alias="cornerSquareEndColor")
    corner_dot_type: Optional[StrictStr] = Field(default='SQUARE', description="Corner dot type", alias="cornerDotType")
    corner_dot_gradient_type: Optional[StrictStr] = Field(default='LINEAR', description="Corners dot gradient", alias="cornerDotGradientType")
    corner_dot_gradient_rotation: Optional[StrictInt] = Field(default=0, description="Corners dot gradient rotation", alias="cornerDotGradientRotation")
    corner_dot_start_color: Optional[StrictStr] = Field(default=None, description="Corner dot primary color", alias="cornerDotStartColor")
    corner_dot_end_color: Optional[StrictStr] = Field(default=None, description="Corner dot gradient color", alias="cornerDotEndColor")
    background_round: Optional[StrictInt] = Field(default=0, description="Corner square type", alias="backgroundRound")
    background_gradient_type: Optional[StrictStr] = Field(default='LINEAR', description="Corners square gradient", alias="backgroundGradientType")
    background_gradient_rotation: Optional[StrictInt] = Field(default=0, description="Corners square gradient rotation", alias="backgroundGradientRotation")
    background_start_color: Optional[StrictStr] = Field(default=None, description="Corner square primary color", alias="backgroundStartColor")
    background_end_color: Optional[StrictStr] = Field(default=None, description="Corner square gradient color", alias="backgroundEndColor")
    __properties: ClassVar[List[str]] = ["imageIdentifier", "shape", "dotsType", "dotsRoundSize", "dotsGradientType", "dotsGradientRotation", "dotsStartColor", "dotsEndColor", "cornerSquareType", "cornerSquareGradientType", "cornerSquareGradientRotation", "cornerSquareStartColor", "cornerSquareEndColor", "cornerDotType", "cornerDotGradientType", "cornerDotGradientRotation", "cornerDotStartColor", "cornerDotEndColor", "backgroundRound", "backgroundGradientType", "backgroundGradientRotation", "backgroundStartColor", "backgroundEndColor"]

    @field_validator('shape')
    def shape_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['SQUARE', 'CIRCLE']):
            raise ValueError("must be one of enum values ('SQUARE', 'CIRCLE')")
        return value

    @field_validator('dots_type')
    def dots_type_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['DOTS', 'ROUNDED', 'CLASSY', 'CLASSY_ROUNDED', 'SQUARE', 'EXTRA_ROUNDED']):
            raise ValueError("must be one of enum values ('DOTS', 'ROUNDED', 'CLASSY', 'CLASSY_ROUNDED', 'SQUARE', 'EXTRA_ROUNDED')")
        return value

    @field_validator('dots_gradient_type')
    def dots_gradient_type_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['LINEAR', 'RADIAL']):
            raise ValueError("must be one of enum values ('LINEAR', 'RADIAL')")
        return value

    @field_validator('corner_square_type')
    def corner_square_type_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['SQUARE', 'EXTRA_ROUNDED', 'DOT']):
            raise ValueError("must be one of enum values ('SQUARE', 'EXTRA_ROUNDED', 'DOT')")
        return value

    @field_validator('corner_square_gradient_type')
    def corner_square_gradient_type_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['LINEAR', 'RADIAL']):
            raise ValueError("must be one of enum values ('LINEAR', 'RADIAL')")
        return value

    @field_validator('corner_dot_type')
    def corner_dot_type_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['SQUARE', 'DOT']):
            raise ValueError("must be one of enum values ('SQUARE', 'DOT')")
        return value

    @field_validator('corner_dot_gradient_type')
    def corner_dot_gradient_type_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['LINEAR', 'RADIAL']):
            raise ValueError("must be one of enum values ('LINEAR', 'RADIAL')")
        return value

    @field_validator('background_gradient_type')
    def background_gradient_type_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['LINEAR', 'RADIAL']):
            raise ValueError("must be one of enum values ('LINEAR', 'RADIAL')")
        return value

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of SyndicationSettingsQrCodeOptionsAffiliate from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of SyndicationSettingsQrCodeOptionsAffiliate from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "imageIdentifier": obj.get("imageIdentifier"),
            "shape": obj.get("shape") if obj.get("shape") is not None else 'SQUARE',
            "dotsType": obj.get("dotsType") if obj.get("dotsType") is not None else 'SQUARE',
            "dotsRoundSize": obj.get("dotsRoundSize") if obj.get("dotsRoundSize") is not None else True,
            "dotsGradientType": obj.get("dotsGradientType") if obj.get("dotsGradientType") is not None else 'LINEAR',
            "dotsGradientRotation": obj.get("dotsGradientRotation") if obj.get("dotsGradientRotation") is not None else 0,
            "dotsStartColor": obj.get("dotsStartColor"),
            "dotsEndColor": obj.get("dotsEndColor"),
            "cornerSquareType": obj.get("cornerSquareType") if obj.get("cornerSquareType") is not None else 'SQUARE',
            "cornerSquareGradientType": obj.get("cornerSquareGradientType") if obj.get("cornerSquareGradientType") is not None else 'LINEAR',
            "cornerSquareGradientRotation": obj.get("cornerSquareGradientRotation") if obj.get("cornerSquareGradientRotation") is not None else 0,
            "cornerSquareStartColor": obj.get("cornerSquareStartColor"),
            "cornerSquareEndColor": obj.get("cornerSquareEndColor"),
            "cornerDotType": obj.get("cornerDotType") if obj.get("cornerDotType") is not None else 'SQUARE',
            "cornerDotGradientType": obj.get("cornerDotGradientType") if obj.get("cornerDotGradientType") is not None else 'LINEAR',
            "cornerDotGradientRotation": obj.get("cornerDotGradientRotation") if obj.get("cornerDotGradientRotation") is not None else 0,
            "cornerDotStartColor": obj.get("cornerDotStartColor"),
            "cornerDotEndColor": obj.get("cornerDotEndColor"),
            "backgroundRound": obj.get("backgroundRound") if obj.get("backgroundRound") is not None else 0,
            "backgroundGradientType": obj.get("backgroundGradientType") if obj.get("backgroundGradientType") is not None else 'LINEAR',
            "backgroundGradientRotation": obj.get("backgroundGradientRotation") if obj.get("backgroundGradientRotation") is not None else 0,
            "backgroundStartColor": obj.get("backgroundStartColor"),
            "backgroundEndColor": obj.get("backgroundEndColor")
        })
        return _obj


