"""
Google Places API Client for extracting place data.

This module provides a comprehensive client for interacting with the Google
Places API (New), including methods for place details, nearby search, text
search, autocomplete, and place photos.

Based on the Google Places API documentation:
https://developers.google.com/maps/documentation/places/web-service/client-library-examples
"""

import asyncio
import logging
import os
from typing import Any, Optional

from pydantic import BaseModel, Field

try:
    from google.maps import places_v1  # type: ignore[import-untyped]
    from google.api_core.exceptions import GoogleAPIError  # type: ignore[import-untyped]
except ImportError:
    places_v1 = None  # type: ignore[assignment]
    GoogleAPIError = Exception

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlaceSearchParams(BaseModel):
    """Parameters for place search operations."""

    location: Optional[dict[str, float]] = None  # {"lat": float, "lng": float}
    radius: int | None = Field(
        None, ge=100, le=100000, description="In meters"
    )  # In meters
    included_types: Optional[list[str]] = None
    excluded_types: Optional[list[str]] = None
    max_result_count: Optional[int] = None
    language_code: Optional[str] = None
    region_code: Optional[str] = None


class PlacePhoto(BaseModel):
    """
    Represents a place photo from Google Maps Places API.

    Photos provide visual information about places and are available through
    Place Details Essentials (IDs Only) SKU for Place Details,
    Text Search Pro SKU for Text Search, and Nearby Search Pro SKU for Nearby Search.
    """

    name: str = Field(
        ...,
        description="The resource name of the photo in the format 'places/{place_id}/photos/{photo_reference}'. "
        "This serves as the unique identifier for the photo and can be used to retrieve the photo media.",
    )
    width_px: int = Field(
        ...,
        description="The maximum width in pixels of the photo. This represents the original width "
        "of the photo as stored by Google Maps.",
    )
    height_px: int = Field(
        ...,
        description="The maximum height in pixels of the photo. This represents the original height "
        "of the photo as stored by Google Maps.",
    )
    photo_uri: Optional[str] = Field(
        None,
        description="The URI for accessing the photo. When provided, this is a direct link to the photo "
        "that can be used to display or download the image. May be None if the photo URI "
        "hasn't been requested or generated.",
    )


class PlaceDetails(BaseModel):
    """
    Represents detailed information about a place from Google Maps Places API.

    This class contains comprehensive place data that can be retrieved through
    Place Details, Text Search, and Nearby Search operations. Different fields
    require different SKUs (Essentials, Pro, Enterprise, Enterprise + Atmosphere).
    """

    place_id: str = Field(
        ...,
        description="The unique identifier for a place. This is a textual identifier that "
        "uniquely identifies a place and can be used to retrieve place details. "
        "Available with Place Details Essentials (IDs Only), Text Search Essentials (IDs Only), "
        "and Nearby Search Pro SKUs.",
    )
    name: Optional[str] = Field(
        None,
        description="The human-readable name of the place. This is the primary display name "
        "as it appears in Google Maps. Available with Place Details Essentials (IDs Only), "
        "Text Search Essentials (IDs Only), and Nearby Search Pro SKUs.",
    )
    formatted_address: Optional[str] = Field(
        None,
        description="A string containing the human-readable address of this place. Often this "
        "address is equivalent to the postal address. Available with Place Details Essentials, "
        "Text Search Pro, and Nearby Search Pro SKUs.",
    )
    phone_number: Optional[str] = Field(
        None,
        description="The place's phone number in national format. For international format, "
        "use international_phone_number. Available with Place Details Enterprise, "
        "Text Search Enterprise, and Nearby Search Enterprise SKUs.",
    )
    website_uri: Optional[str] = Field(
        None,
        description="The authoritative website for this place, such as a business's homepage. "
        "Available with Place Details Enterprise, Text Search Enterprise, "
        "and Nearby Search Enterprise SKUs.",
    )
    rating: Optional[float] = Field(
        None,
        ge=1.0,
        le=5.0,
        description="The place's rating, from 1.0 to 5.0, based on aggregated user reviews. "
        "If no rating is available, this field will be None. Available with "
        "Place Details Enterprise, Text Search Enterprise, and Nearby Search Enterprise SKUs.",
    )
    user_rating_count: Optional[int] = Field(
        None,
        ge=0,
        description="The total number of ratings that the place has received. Available with "
        "Place Details Enterprise, Text Search Enterprise, and Nearby Search Enterprise SKUs.",
    )
    location: Optional[dict[str, float]] = Field(
        None,
        description="The latitude and longitude coordinates of the place in the format "
        "{'lat': float, 'lng': float}. Available with Place Details Essentials, "
        "Text Search Pro, and Nearby Search Pro SKUs.",
    )
    types: Optional[list[str]] = Field(
        None,
        description="An array of types for this place (e.g., ['restaurant', 'food', 'establishment']). "
        "These types are used to categorize the place and can be used for filtering. "
        "Available with Place Details Essentials, Text Search Pro, and Nearby Search Pro SKUs.",
    )
    photos: Optional[list[PlacePhoto]] = Field(
        None,
        description="An array of photo objects, each containing a reference to an image associated "
        "with the place. Photos can provide visual context about the business or location. "
        "Available with Place Details Essentials (IDs Only), Text Search Pro, "
        "and Nearby Search Pro SKUs.",
    )
    opening_hours: Optional[dict[str, Any]] = Field(
        None,
        description="Information about the place's opening hours, including current status (open/closed) "
        "and weekly schedule. Contains 'open_now' boolean and 'periods' array with opening "
        "and closing times for each day. Available with Place Details Enterprise, "
        "Text Search Enterprise, and Nearby Search Enterprise SKUs.",
    )
    price_level: Optional[str] = Field(
        None,
        description="The price level of the place, from 0 (free) to 4 (very expensive). "
        "This provides a general indication of the cost of services or goods. "
        "Available with Place Details Enterprise, Text Search Enterprise, "
        "and Nearby Search Enterprise SKUs.",
    )
    reviews: Optional[list[dict[str, Any]]] = Field(
        None,
        description="An array of up to five reviews, sorted by relevance. Each review contains "
        "rating, text, author information, and publication time. Available with "
        "Place Details Enterprise + Atmosphere, Text Search Enterprise + Atmosphere, "
        "and Nearby Search Enterprise + Atmosphere SKUs.",
    )
    editorial_summary: Optional[str] = Field(
        None,
        description="A brief editorial summary of the place, providing a concise description "
        "of what the place is and what it offers. This field provides official descriptive "
        "content about the place from Google's editorial team.",
    )


class GooglePlacesClient:
    """
    Google Places API client for extracting place data.

    This client provides methods for:
    - Place Details (New)
    - Nearby Search (New)
    - Text Search (New)
    - Autocomplete (New)
    - Place Photos (New)
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Google Places client.

        Args:
            api_key: Google Places API key. If not provided, will try to get from
                    environment variable GOOGLE_PLACES_API_KEY or use
                    Application Default Credentials.
        """
        if places_v1 is None:
            raise ImportError(
                "google-maps-places library is not installed. "
                "Please install it with: pip install google-maps-places"
            )

        self.api_key = api_key or os.getenv("GOOGLE_PLACES_API_KEY")

        if self.api_key:
            # Use API key authentication
            from google.api_core import client_options

            options = client_options.ClientOptions(api_key=self.api_key)
            self.client = places_v1.PlacesAsyncClient(client_options=options)
        else:
            # Use Application Default Credentials
            self.client = places_v1.PlacesAsyncClient()
            logger.warning(
                "No API key provided. Using Application Default Credentials. "
                "Make sure ADC is properly configured."
            )

    async def get_place_details(
        self, place_id: str, fields: Optional[list[str]] = None
    ) -> Optional[PlaceDetails]:
        """
        Get detailed information about a place.

        Args:
            place_id: The place ID to get details for
            fields: list of fields to include in response. If None, includes
                   basic fields. Available fields: name, formatted_address,
                   phone_number, website_uri, rating, user_rating_count,
                   location, types, photos, opening_hours, price_level,
                   reviews, etc.

        Returns:
            PlaceDetails object with place information, or None if not found
        """
        try:
            # Default fields if none specified
            if fields is None:
                fields = [
                    "name",
                    "formatted_address",
                    "phone_number",
                    "website_uri",
                    "rating",
                    "user_rating_count",
                    "location",
                    "types",
                    "photos",
                ]

            field_mask = ",".join(fields)
            place_name = f"places/{place_id}"

            request = places_v1.GetPlaceRequest(name=place_name)  # type: ignore[attr-defined]

            response = await self.client.get_place(  # type: ignore[misc]
                request=request, metadata=[("x-goog-fieldmask", field_mask)]
            )

            return self._convert_place_to_details(response, place_id)

        except GoogleAPIError as e:
            logger.error(f"Error getting place details for {place_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting place details: {e}")
            return None

    async def nearby_search(self, params: PlaceSearchParams) -> list[PlaceDetails]:
        """
        Search for places near a location.

        Args:
            params: PlaceSearchParams with search criteria

        Returns:
            list of PlaceDetails objects
        """
        try:
            if not params.location:
                raise ValueError("Location is required for nearby search")

            # Build the basic location restriction
            location_restriction = {
                "circle": {
                    "center": {
                        "latitude": params.location["lat"],
                        "longitude": params.location["lng"],
                    },
                    "radius": params.radius or 1000,  # Default 1km radius
                }
            }

            # Build the request data step by step
            request_data: dict[str, Any] = {
                "location_restriction": location_restriction
            }

            if params.included_types:
                request_data["included_types"] = params.included_types
            if params.excluded_types:
                request_data["excluded_primary_types"] = params.excluded_types
            if params.max_result_count:
                request_data["max_result_count"] = min(params.max_result_count, 20)
            if params.language_code:
                request_data["language_code"] = params.language_code
            if params.region_code:
                request_data["region_code"] = params.region_code

            request = places_v1.SearchNearbyRequest(**request_data)  # type: ignore[attr-defined]

            # Set field mask for response
            field_mask = (
                "places.id,places.displayName,places.formattedAddress,"
                "places.location,places.rating,places.userRatingCount,places.types,places.photos,places.editorialSummary"
            )

            response = await self.client.search_nearby(  # type: ignore[misc]
                request=request, metadata=[("x-goog-fieldmask", field_mask)]
            )

            results: list[PlaceDetails] = []
            for place in response.places:
                place_details = self._convert_place_to_details(place)
                if place_details:
                    results.append(place_details)

            return results

        except GoogleAPIError as e:
            logger.error(f"Error in nearby search: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in nearby search: {e}")
            return []

    async def text_search(
        self, text_query: str, params: Optional[PlaceSearchParams] = None
    ) -> list[PlaceDetails]:
        """
        Search for places using a text query.

        Args:
            text_query: The text query to search for
                       (e.g., "restaurants in New York")
            params: Optional PlaceSearchParams for additional filtering

        Returns:
            list of PlaceDetails objects
        """
        try:
            request_data: dict[str, Any] = {"text_query": text_query}

            if params:
                if params.max_result_count:
                    max_count = min(params.max_result_count, 20)
                    request_data["max_result_count"] = max_count
                if params.language_code:
                    request_data["language_code"] = params.language_code
                if params.region_code:
                    request_data["region_code"] = params.region_code
                if params.included_types:
                    request_data["included_types"] = params.included_types
                if params.location:
                    # Add location bias
                    radius = params.radius or 50000  # Default 50km for bias
                    location_bias = {
                        "circle": {
                            "center": {
                                "latitude": params.location["lat"],
                                "longitude": params.location["lng"],
                            },
                            "radius": radius,
                        }
                    }
                    request_data["location_bias"] = location_bias

            request = places_v1.SearchTextRequest(**request_data)  # type: ignore[attr-defined]

            # Set field mask for response
            field_mask = (
                "places.id,places.displayName,places.formattedAddress,"
                "places.location,places.rating,places.userRatingCount,places.types,places.photos,places.editorialSummary"
            )

            response = await self.client.search_text(  # type: ignore[misc]
                request=request, metadata=[("x-goog-fieldmask", field_mask)]
            )

            results: list[PlaceDetails] = []
            for place in response.places:
                place_details = self._convert_place_to_details(place)
                if place_details:
                    results.append(place_details)

            return results

        except GoogleAPIError as e:
            logger.error(f"Error in text search: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in text search: {e}")
            return []

    async def autocomplete(
        self,
        input_text: str,
        location: Optional[dict[str, float]] = None,
        radius: Optional[int] = None,
        language_code: Optional[str] = None,
        region_code: Optional[str] = None,
        included_types: Optional[list[str]] = None,
    ) -> list[dict[str, Any]]:
        """
        Get autocomplete suggestions for place queries.

        Args:
            input_text: The input text to get suggestions for
            location: Optional location for bias {"lat": float, "lng": float}
            radius: Optional radius in meters for location bias
            language_code: Optional language code for results
            region_code: Optional region code for results
            included_types: Optional list of place types to include

        Returns:
            list of autocomplete suggestions
        """
        try:
            request_data: dict[str, Any] = {"input": input_text}

            if location:
                request_data["location_bias"] = {
                    "circle": {
                        "center": {
                            "latitude": location["lat"],
                            "longitude": location["lng"],
                        },
                        "radius": radius or 50000,  # Default 50km radius
                    }
                }

            if language_code:
                request_data["language_code"] = language_code
            if region_code:
                request_data["region_code"] = region_code
            if included_types:
                request_data["included_types"] = included_types

            request = places_v1.AutocompletePlacesRequest(**request_data)  # type: ignore[attr-defined]

            response = await self.client.autocomplete_places(request=request)  # type: ignore[misc]

            suggestions: list[dict[str, Any]] = []
            for suggestion in response.suggestions:
                if hasattr(suggestion, "place_prediction"):
                    suggestions.append(
                        {
                            "place_id": suggestion.place_prediction.place_id,
                            "text": suggestion.place_prediction.text.text,
                            "structured_formatting": {
                                "main_text": suggestion.place_prediction.structured_format.main_text.text,
                                "secondary_text": suggestion.place_prediction.structured_format.secondary_text.text,
                            }
                            if suggestion.place_prediction.structured_format
                            else None,
                        }
                    )

            return suggestions

        except GoogleAPIError as e:
            logger.error(f"Error in autocomplete: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in autocomplete: {e}")
            return []

    async def get_place_photo(
        self,
        place_id: str,
        max_width_px: int = 800,
        max_height_px: Optional[int] = None,
    ) -> Optional[str]:
        """
        Get a photo URI for a place.

        Args:
            place_id: The place ID to get photo for
            max_width_px: Maximum width in pixels (default: 800)
            max_height_px: Optional maximum height in pixels

        Returns:
            Photo URI string, or None if no photo available
        """
        try:
            # First get place details to find photo references
            place_name = f"places/{place_id}"
            request = places_v1.GetPlaceRequest(name=place_name)  # type: ignore[attr-defined]

            response = await self.client.get_place(  # type: ignore[misc]
                request=request, metadata=[("x-goog-fieldmask", "photos")]
            )

            if not response.photos or len(response.photos) == 0:
                logger.info(f"No photos found for place: {place_id}")
                return None

            # Get the first photo
            first_photo = response.photos[0]
            photo_media_name = f"{first_photo.name}/media"

            # Build photo request
            photo_request_data: dict[str, Any] = {
                "name": photo_media_name,
                "max_width_px": max_width_px,
            }

            if max_height_px:
                photo_request_data["max_height_px"] = max_height_px

            photo_request = places_v1.GetPhotoMediaRequest(**photo_request_data)  # type: ignore[attr-defined]

            photo_response = await self.client.get_photo_media(photo_request)  # type: ignore[misc]

            return photo_response.photo_uri

        except GoogleAPIError as e:
            logger.error(f"Error getting place photo for {place_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting place photo: {e}")
            return None

    def _convert_place_to_details(
        self, place_response: Any, place_id: Optional[str] = None
    ) -> Optional[PlaceDetails]:
        """Convert API response to PlaceDetails object."""
        try:
            # Extract place ID
            if place_id:
                extracted_place_id = place_id
            elif hasattr(place_response, "id"):
                extracted_place_id = place_response.id
            elif hasattr(place_response, "name"):
                # Extract place ID from name like "places/ChIJaXQRs6lZwokRY6EFpJnhNNE"
                extracted_place_id = (
                    place_response.name.split("/")[-1]
                    if "/" in place_response.name
                    else place_response.name
                )
            else:
                extracted_place_id = "unknown"

            # Extract location
            location = None
            if hasattr(place_response, "location") and place_response.location:
                location = {
                    "lat": place_response.location.latitude,
                    "lng": place_response.location.longitude,
                }

            # Extract photos
            photos: list[PlacePhoto] = []
            if hasattr(place_response, "photos") and place_response.photos:
                for photo in place_response.photos:
                    photos.append(
                        PlacePhoto(
                            name=photo.name,
                            width_px=photo.width_px,
                            height_px=photo.height_px,
                            photo_uri=None,  # URI not available in basic photo response
                        )
                    )

            # Extract opening hours
            opening_hours: Optional[dict[str, Any]] = None
            if (
                hasattr(place_response, "current_opening_hours")
                and place_response.current_opening_hours
            ):
                opening_hours = {
                    "open_now": getattr(
                        place_response.current_opening_hours, "open_now", None
                    ),
                    "periods": [],
                }
                if hasattr(place_response.current_opening_hours, "periods"):
                    for period in place_response.current_opening_hours.periods:
                        opening_hours["periods"].append(
                            {
                                "open": {
                                    "day": period.open.day,
                                    "time": period.open.time,
                                }
                                if period.open
                                else None,
                                "close": {
                                    "day": period.close.day,
                                    "time": period.close.time,
                                }
                                if period.close
                                else None,
                            }
                        )

            # Extract reviews
            reviews: list[dict[str, Any]] = []
            if hasattr(place_response, "reviews") and place_response.reviews:
                for review in place_response.reviews:
                    reviews.append(
                        {
                            "rating": getattr(review, "rating", None),
                            "text": getattr(review.text, "text", None)
                            if hasattr(review, "text")
                            else None,
                            "author_name": getattr(
                                review, "author_attribution", {}
                            ).get("display_name", None)
                            if hasattr(review, "author_attribution")
                            else None,
                            "time": getattr(review, "publish_time", None),
                        }
                    )

            return PlaceDetails(
                place_id=extracted_place_id,
                name=getattr(place_response.display_name, "text", None)
                if hasattr(place_response, "display_name")
                and place_response.display_name
                else None,
                formatted_address=getattr(place_response, "formatted_address", None),
                phone_number=getattr(place_response, "national_phone_number", None),
                website_uri=getattr(place_response, "website_uri", None),
                rating=self._convert_rating(getattr(place_response, "rating", None)),
                user_rating_count=getattr(place_response, "user_rating_count", None),
                location=location,
                types=list(getattr(place_response, "types", [])),
                photos=photos if photos else None,
                opening_hours=opening_hours,
                price_level=self._convert_price_level(
                    getattr(place_response, "price_level", None)
                ),
                reviews=reviews if reviews else None,
                editorial_summary=self._extract_editorial_summary(place_response),
            )

        except Exception as e:
            logger.error(f"Error converting place response to details: {e}")
            return None

    def _convert_price_level(self, price_level: Any) -> Optional[str]:
        """Convert price level enum to string."""
        if price_level is None:
            return None

        # Handle enum values from the API
        if hasattr(price_level, "name"):
            # Convert enum name to a more readable format
            price_level_name = price_level.name
            if price_level_name == "PRICE_LEVEL_UNSPECIFIED":
                return None
            elif price_level_name == "PRICE_LEVEL_FREE":
                return "FREE"
            elif price_level_name == "PRICE_LEVEL_INEXPENSIVE":
                return "INEXPENSIVE"
            elif price_level_name == "PRICE_LEVEL_MODERATE":
                return "MODERATE"
            elif price_level_name == "PRICE_LEVEL_EXPENSIVE":
                return "EXPENSIVE"
            elif price_level_name == "PRICE_LEVEL_VERY_EXPENSIVE":
                return "VERY_EXPENSIVE"
            else:
                return str(price_level_name)

        # Handle numeric values (0-4 scale)
        if isinstance(price_level, int):
            price_map = {
                0: None,  # Unspecified
                1: "INEXPENSIVE",
                2: "MODERATE",
                3: "EXPENSIVE",
                4: "VERY_EXPENSIVE",
            }
            return price_map.get(price_level)

        # Handle string values (already converted)
        if isinstance(price_level, str):
            return price_level

        # Fallback - convert to string
        return str(price_level)

    def _convert_rating(self, rating: Any) -> Optional[float]:
        """Convert rating to valid float or None."""
        if rating is None:
            return None

        try:
            rating_float = float(rating)
            # Google Places ratings should be between 1.0 and 5.0
            # If rating is 0, it means no rating is available
            if rating_float == 0.0:
                return None
            # Ensure rating is within valid range
            if rating_float < 1.0 or rating_float > 5.0:
                logger.warning(f"Invalid rating value: {rating_float}, returning None")
                return None
            return rating_float
        except (ValueError, TypeError):
            logger.warning(f"Could not convert rating to float: {rating}")
            return None

    def _extract_editorial_summary(self, place_response: Any) -> Optional[str]:
        """Extract editorial summary from place response."""
        try:
            if (
                hasattr(place_response, "editorial_summary")
                and place_response.editorial_summary
            ):
                # The editorial summary might have a text field
                if hasattr(place_response.editorial_summary, "text"):
                    return place_response.editorial_summary.text
                # Or it might be a string directly
                elif isinstance(place_response.editorial_summary, str):
                    return place_response.editorial_summary
            return None
        except Exception as e:
            logger.debug(f"Could not extract editorial summary: {e}")
            return None

    async def close(self):
        """Close the client connection."""
        # The PlacesAsyncClient doesn't have a close method in the current version
        # This is kept for future compatibility
        try:
            if hasattr(self.client, "close"):
                await self.client.close()
        except Exception as e:
            logger.debug(f"Client close method not available or failed: {e}")


# Convenience functions for common use cases
async def search_restaurants_nearby(
    lat: float, lng: float, radius: int = 1000, api_key: Optional[str] = None
) -> list[PlaceDetails]:
    """
    Search for restaurants near a location.

    Args:
        lat: Latitude
        lng: Longitude
        radius: Search radius in meters (default: 1000)
        api_key: Optional API key

    Returns:
        list of restaurant PlaceDetails
    """
    client = GooglePlacesClient(api_key)
    try:
        params = PlaceSearchParams(
            location={"lat": lat, "lng": lng},
            radius=radius,
            included_types=["restaurant"],
        )
        return await client.nearby_search(params)
    finally:
        await client.close()


async def search_places_by_text(
    query: str, api_key: Optional[str] = None
) -> list[PlaceDetails]:
    """
    Search for places using text query.

    Args:
        query: Text query (e.g., "coffee shops in Prague")
        api_key: Optional API key

    Returns:
        list of PlaceDetails
    """
    client = GooglePlacesClient(api_key)
    try:
        return await client.text_search(query)
    finally:
        await client.close()


async def get_place_info(
    place_id: str, api_key: Optional[str] = None
) -> Optional[PlaceDetails]:
    """
    Get detailed information about a specific place.

    Args:
        place_id: Google Places place ID
        api_key: Optional API key

    Returns:
        PlaceDetails object or None
    """
    client = GooglePlacesClient(api_key)
    try:
        return await client.get_place_details(place_id)
    finally:
        await client.close()


# Example usage
if __name__ == "__main__":

    async def example_usage():
        """Example usage of the Google Places client."""

        # Initialize client (make sure to set GOOGLE_PLACES_API_KEY environment variable)
        client = GooglePlacesClient()

        try:
            # Example 1: Search for restaurants nearby
            print("1. Searching for restaurants near Olomouc center...")
            restaurants = await client.nearby_search(
                PlaceSearchParams(
                    location={"lat": 50.0755, "lng": 14.4378},  # Prague center
                    radius=1000,
                    included_types=["restaurant", "cafe"],
                    max_result_count=5,
                )
            )

            for restaurant in restaurants[:3]:  # Show first 3
                print(f"  - {restaurant.name} ({restaurant.rating}⭐)")
                print(f"    Address: {restaurant.formatted_address}")

            # Example 2: Text search
            print("\n2. Text search for 'Tips around Olomouc'...")
            coffee_shops = await client.text_search(
                "Tips around Olomouc",
                PlaceSearchParams(max_result_count=20, radius=5000),
            )

            for shop in coffee_shops:
                print(f"  - {shop.name}")
                print(f"    Address: {shop.formatted_address}")

            # Example 3: Autocomplete
            print("\n3. Autocomplete for 'Starbucks'...")
            suggestions = await client.autocomplete("Olomouc")

            for suggestion in suggestions[:3]:  # Show first 3
                print(f"  - {suggestion['text']}")

            # Example 4: Get place details
            if restaurants:
                place_id = restaurants[0].place_id
                print(f"\n4. Getting details for place: {place_id}")

                details = await client.get_place_details(
                    place_id,
                    fields=[
                        "name",
                        "formatted_address",
                        "international_phone_number",
                        "website_uri",
                        "photos",
                    ],
                )

                if details:
                    print(f"  Name: {details.name}")
                    print(f"  Address: {details.formatted_address}")
                    print(f"  Phone: {details.phone_number}")
                    print(f"  Website: {details.website_uri}")
                    print(f"  Photos: {len(details.photos) if details.photos else 0}")

                    # Example 5: Get place photo
                    print(f"\n5. Getting photo for place: {place_id}")
                    photo_uri = await client.get_place_photo(place_id)
                    if photo_uri:
                        print(f"  Photo URI: {photo_uri}")

        finally:
            await client.close()

    # Run the example
    asyncio.run(example_usage())
