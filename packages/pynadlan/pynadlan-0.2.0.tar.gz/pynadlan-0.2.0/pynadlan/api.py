import httpx
from typing import Any, Optional, Union
from urllib.parse import quote
from .locations import CITIES, CITIES_AND_NEIGHBORHOODS


async def _fetch_histograms(query: str) -> dict[str, Any]:
    """
    Fetch histogram data from dirobot for a given query (city/neighborhood).

    Returns the parsed JSON payload.
    """
    query = query.replace(", ", "_")
    encoded_query = quote(query, safe="")
    url = f"https://dirobot.co.il/api/analysis/histograms/{encoded_query}"

    # Keep an independent short-lived client for this endpoint
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


def _latest_value(points: list[dict[str, Any]]) -> Optional[Union[int, float]]:
    if not points:
        return None
    # Points are chronological; take the last value
    last_point = points[-1]
    return last_point.get("value")


def _extract_latest_by_prefix(payload: dict[str, Any], prefix: str, rooms: list[int] | None) -> dict[str, Optional[Union[int, float]]]:
    """
    From the histograms payload, extract the latest value for each histogram_type
    that starts with the given prefix (e.g., "sell_" or "rent_").

    If rooms is provided, only include keys for those room counts (e.g., 2..6).
    """
    histograms: list[dict[str, Any]] = payload.get("real_estate_histograms", [])

    latest: dict[str, Optional[Union[int, float]]] = {}

    # Build the set of expected keys when rooms are specified
    expected_keys: Optional[set] = None
    if rooms is not None:
        expected_keys = {f"{prefix}{room}_price" for room in rooms}

    for item in histograms:
        h_type = item.get("histogram_type")
        if not isinstance(h_type, str):
            continue
        if not h_type.startswith(prefix):
            continue

        # Only keep room-specific price series (e.g., sell_2_price) and not aggregated ones
        if not h_type.endswith("_price"):
            continue

        if expected_keys is not None and h_type not in expected_keys:
            continue

        value = _latest_value(item.get("histogram_points", []))
        latest[h_type] = value

    # If rooms were specified but some keys were missing from the payload, include them as None
    if expected_keys is not None:
        for key in expected_keys:
            latest.setdefault(key, None)

    return latest


async def get_avg_prices(query: str, rooms: Optional[Union[int, list[int]]] = None) -> dict[str, Optional[Union[int, float]]]:
    """
    Return latest sell prices per room type for the given query.

    - query: city or neighborhood string (Hebrew/English supported)
    - rooms: optional single room count (e.g., 3) or list of room counts (e.g., [3,4])

    Example return (rooms unspecified):
    {"sell_2_price": 2500000, "sell_3_price": 3200000, ...}
    """
    rooms_list: Optional[list[int]]
    if rooms is None:
        rooms_list = None
    elif isinstance(rooms, int):
        rooms_list = [rooms]
    else:
        rooms_list = list(rooms)

    payload = await _fetch_histograms(query)
    return _extract_latest_by_prefix(payload, prefix="sell_", rooms=rooms_list)


async def get_rent_prices(query: str, rooms: Optional[Union[int, list[int]]] = None) -> dict[str, Optional[Union[int, float]]]:
    """
    Return latest rent prices per room type for the given query.

    - query: city or neighborhood string (Hebrew/English supported)
    - rooms: optional single room count (e.g., 3) or list of room counts (e.g., [3,4])

    Example return (rooms unspecified):
    {"rent_2_price": 6500, "rent_3_price": 7500, ...}
    """
    rooms_list: Optional[list[int]]
    if rooms is None:
        rooms_list = None
    elif isinstance(rooms, int):
        rooms_list = [rooms]
    else:
        rooms_list = list(rooms)

    payload = await _fetch_histograms(query)
    return _extract_latest_by_prefix(payload, prefix="rent_", rooms=rooms_list)


def get_autocomplete_lists() -> dict[str, list[str]]:
    """
    Return static autocomplete lists for cities and for cities+neighborhoods.
    Structure:
    {
        "cities": [...],
        "cities_and_neighborhoods": [...]
    }
    """
    return {
        "cities": list(CITIES),
        "cities_and_neighborhoods": list(CITIES_AND_NEIGHBORHOODS),
    }


async def get_cities_summary(min_deals: int = 10) -> dict[str, Any]:
    """
    Fetch cities summary with median prices and deal counts from dirobot API.

    Args:
        min_deals: Minimum number of deals to include a city (default: 10)

    Returns:
        Dictionary containing:
        - average_price_overall: Overall average price across all cities
        - cities: List of city objects with:
            - city_name: Name of the city (Hebrew)
            - date_range: Date range of deals (e.g., "2023-10-15 to 2025-08-27")
            - medianPrice: Median price for the city
            - total_deals: Total number of deals
        - generated_at: Timestamp of data generation
        - total_cities: Total number of cities in response
        - total_deals_all_cities: Total deals across all cities

    Example return:
    {
        "average_price_overall": 0,
        "cities": [
            {
                "city_name": "ירושלים",
                "date_range": "2023-10-15 to 2025-08-27",
                "medianPrice": 2838515,
                "total_deals": 5795
            },
            ...
        ],
        "generated_at": "2025-10-12T22:00:50.433169",
        "total_cities": 303,
        "total_deals_all_cities": 88081
    }
    """
    url = f"https://api.dirobot.co.il/api/v2/cities-summary?min_deals={min_deals}"

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://www.dirobot.co.il',
        'pragma': 'no-cache',
        'referer': 'https://www.dirobot.co.il/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()


async def get_neighborhoods_summary(city: str, min_deals: int = 3) -> dict[str, Any]:
    """
    Fetch neighborhoods summary for a specific city with median prices and deal counts.

    Args:
        city: City name in Hebrew (e.g., "רעננה", "תל אביב יפו")
        min_deals: Minimum number of deals to include a neighborhood (default: 3)

    Returns:
        Dictionary containing:
        - average_median_price_overall: Average of median prices across neighborhoods
        - cities_breakdown: Dictionary mapping city names to their deal counts
        - filters: Applied filters (city and min_deals)
        - generated_at: Timestamp of data generation
        - neighborhoods: List of neighborhood objects with:
            - city: City name (Hebrew)
            - neighborhood: Neighborhood name (Hebrew)
            - date_range: Date range of deals
            - median_price: Median price for the neighborhood
            - total_deals: Total number of deals
            - unique_streets: Number of unique streets with deals
            - file_path: Internal file path reference
            - filename: Internal filename reference
            - original_name: Original compound name
        - total_cities: Total number of cities in the database
        - total_deals_all_neighborhoods: Total deals across all neighborhoods
        - total_neighborhoods: Total number of neighborhoods in the database

    Example return:
    {
        "average_median_price_overall": 2600725.6,
        "cities_breakdown": {"רעננה": 18, "תל אביב יפו": 60, ...},
        "filters": {"city": "רעננה", "min_deals": 3},
        "generated_at": "2025-10-12T21:33:02.139469",
        "neighborhoods": [
            {
                "city": "רעננה",
                "neighborhood": "נווה דוד רמז",
                "date_range": "2023-10-25 to 2025-08-14",
                "median_price": 3222500,
                "total_deals": 234,
                "unique_streets": 14,
                ...
            },
            ...
        ],
        "total_cities": 303,
        "total_deals_all_neighborhoods": 88081,
        "total_neighborhoods": 1652
    }
    """
    # URL-encode the city name
    encoded_city = quote(city, safe="")
    url = f"https://api.dirobot.co.il/api/v2/neighborhoods-summary?city={encoded_city}&min_deals={min_deals}"

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://www.dirobot.co.il',
        'pragma': 'no-cache',
        'referer': 'https://www.dirobot.co.il/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()


async def get_city_timeseries(
    city: str,
    property_type: str = "apartment",
    time_range: str = "1year"
) -> dict[str, Any]:
    """
    Fetch historical timeseries data for a city showing price trends over time by room count.

    Args:
        city: City name in Hebrew (e.g., "רעננה", "תל אביב יפו")
        property_type: Type of property (default: "apartment")
        time_range: Time range for data - options: "1year", "2years", "all" (default: "1year")

    Returns:
        Dictionary containing:
        - city: City name (Hebrew)
        - filters: Applied filters (property_type, room_category, time_range)
        - metadata: Data statistics
            - totalDataPoints: Total number of data points
            - totalRoomCategories: Number of room categories
        - summaries: Summary statistics per room category with:
            - avgPrice: Average price over time period
            - dataPointsCount: Number of data points
            - latestMonth: Most recent month (Hebrew)
            - latestPrice: Most recent price
            - latestYear: Most recent year
            - maxPrice: Maximum price in period
            - minPrice: Minimum price in period
            - totalTransactions: Total number of transactions
        - timeSeriesByRooms: Time series data per room category, each with monthly data points:
            - askingPrice: Average asking price
            - avgDaysExisted: Average days listings existed
            - existingListingsCount: Count of existing listings
            - growth: Price growth percentage
            - marketValue: Market value (median transaction price)
            - medianRentPrice: Median rent price
            - month: Month name (Hebrew)
            - year: Year
            - newListingsCount: Count of new listings
            - rentListingCount: Count of rental listings
            - totalListingsCount: Total listing count
            - transactionCount: Number of transactions

    Example return:
    {
        "city": "רעננה",
        "filters": {
            "property_type": "Apartment",
            "room_category": "All Rooms",
            "time_range": "שנה"
        },
        "metadata": {
            "totalDataPoints": 45,
            "totalRoomCategories": 5
        },
        "summaries": {
            "3 חדרים": {
                "avgPrice": 2705846.0,
                "dataPointsCount": 10,
                "latestMonth": "אוג",
                "latestPrice": 2740000,
                "latestYear": 2025,
                ...
            },
            ...
        },
        "timeSeriesByRooms": {
            "3 חדרים": [
                {
                    "month": "אוג",
                    "year": 2025,
                    "marketValue": 2740000,
                    "askingPrice": 2959393,
                    "growth": -5.5,
                    "transactionCount": 5,
                    ...
                },
                ...
            ],
            ...
        }
    }
    """
    # URL-encode the city name
    encoded_city = quote(city, safe="")
    url = f"https://api.dirobot.co.il/api/v2/city-timeseries/{encoded_city}?property_type={property_type}&time_range={time_range}"

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://www.dirobot.co.il',
        'pragma': 'no-cache',
        'referer': 'https://www.dirobot.co.il/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

async def get_street_deals(
    city_street: str,
    per_page: int = 10000
) -> dict[str, Any]:
    """
    Fetch detailed transaction/deal data for a specific street in a city.

    Args:
        city_street: Combined city and street name in format "city_street" (Hebrew, e.g., "רמת גן_רות")
        per_page: Maximum number of deals to return per page (default: 10000)

    Returns:
        Dictionary containing:
        - city: City name (Hebrew)
        - street: Street name (Hebrew)
        - cityStreet: Combined city_street identifier
        - deals: List of transaction objects with:
            - buildYear: Year building was constructed
            - buildingMR: Building identifier number
            - floor: Floor number
            - houseNumber: Street number
            - neighborhood: Neighborhood name (Hebrew)
            - price: Sale price in ILS
            - propertyType: Type of property
            - rooms: Number of rooms
            - saleDate: Date of sale (YYYY-MM-DD)
            - squareMeters: Property size
            - streetName: Street name
        - summary: Aggregated statistics:
            - avgPrice: Average price across all deals
            - medianPrice: Median price
            - totalDeals: Total number of transactions
            - dateRange: Date range of deals
            - avgSquareMeters: Average property size
            - avgPricePerSquareMeter: Average price per sqm
        - filters: Applied filters (per_page)
        - metadata: Data generation timestamp
        - pagination: Pagination information (currentPage, totalPages, totalRecords)

    Example return:
    {
        "city": "רמת גן",
        "street": "רות",
        "cityStreet": "רמת גן_רות",
        "deals": [
            {
                "buildYear": 1998,
                "buildingMR": 123456,
                "floor": 3,
                "houseNumber": "15",
                "neighborhood": "בורסה",
                "price": 3500000,
                "propertyType": "דירת גן",
                "rooms": 4,
                "saleDate": "2024-05-15",
                "squareMeters": 120,
                "streetName": "רות"
            },
            ...
        ],
        "summary": {
            "avgPrice": 3200000,
            "medianPrice": 3150000,
            "totalDeals": 45,
            "dateRange": "2023-01-10 to 2025-08-20",
            "avgSquareMeters": 110,
            "avgPricePerSquareMeter": 29090
        },
        "filters": {"per_page": 10000},
        "metadata": {"generated_at": "2025-10-12T22:00:50.433169"},
        "pagination": {
            "currentPage": 1,
            "totalPages": 1,
            "totalRecords": 45
        }
    }
    """
    # URL-encode the city_street parameter
    encoded_city_street = quote(city_street, safe="")
    url = f"https://api.dirobot.co.il/api/v2/street-deals/{encoded_city_street}?per_page={per_page}"

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://www.dirobot.co.il',
        'pragma': 'no-cache',
        'referer': 'https://www.dirobot.co.il/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
