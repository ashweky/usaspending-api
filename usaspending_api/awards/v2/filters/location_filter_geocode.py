import logging

from django.conf import settings
from django.db.models import Q
from itertools import chain
from typing import Optional, List

from usaspending_api.awards.models.temp import TempEsTransactionHit, TempEsTransactionHitManager, DEFAULT_CHUNK_SIZE
from usaspending_api.common.elasticsearch.client import es_client_query, es_scan
from django.db.models import Q

from usaspending_api.common.exceptions import InvalidParameterException
from usaspending_api.common.helpers.dict_helpers import upper_case_dict_values

logger = logging.getLogger(__name__)
ALL_FOREIGN_COUNTRIES = "FOREIGN"


def geocode_filter_locations(scope: str, values: list, use_matview: bool = False) -> Q:
    """
    Function filter querysets on location table
    scope- place of performance or recipient location mappings
    values- array of location requests
    returns queryset
    """
    or_queryset = Q()

    # Accounts for differences between matview queries and regular queries
    q_str, country_code = return_query_string(use_matview)

    # creates a dictionary with all of the locations organized by country
    # Counties and congressional districts are nested under state codes
    nested_values = create_nested_object(values)

    # In this for-loop a django Q filter object is created from the python dict
    for country, state_zip in nested_values.items():
        country_qs = None
        if country != ALL_FOREIGN_COUNTRIES:
            country_qs = Q(**{q_str.format(scope, country_code) + "__exact": country})
        state_qs = Q()

        for state_zip_key, location_values in state_zip.items():

            if state_zip_key == "city":
                state_inner_qs = Q(**{q_str.format(scope, "city_name") + "__in": location_values})
            elif state_zip_key == "zip":
                state_inner_qs = Q(**{q_str.format(scope, "zip5") + "__in": location_values})
            else:
                state_inner_qs = Q(**{q_str.format(scope, "state_code") + "__exact": state_zip_key.upper()})
                county_qs = Q()
                district_qs = Q()
                city_qs = Q()

                if location_values["county"]:
                    county_qs = Q(**{q_str.format(scope, "county_code") + "__in": location_values["county"]})
                if location_values["district"]:
                    district_qs = Q(**{q_str.format(scope, "congressional_code") + "__in": location_values["district"]})
                if location_values["city"]:
                    city_qs = Q(**{q_str.format(scope, "city_name") + "__in": location_values["city"]})
                state_inner_qs &= county_qs | district_qs | city_qs

            state_qs |= state_inner_qs
        if country_qs:
            or_queryset |= country_qs & state_qs
        else:
            or_queryset |= state_qs
    return or_queryset


def validate_location_keys(values):
    """ Validate that the keys provided are sufficient and match properly. """
    for v in values:
        if ("country" not in v) or (("district" in v or "county" in v) and "state" not in v):
            location_error_handling(v.keys())


def create_nested_object(values):
    """ Makes sure keys provided are valid """
    validate_location_keys(values)

    nested_locations = {}
    for v in values:
        upper_case_dict_values(v)
        city = v.get("city")
        country = v.get("country")
        county = v.get("county")
        district = v.get("district")
        state = v.get("state")
        zip = v.get("zip")
        # First level in location filtering in country
        # All location requests must have a country otherwise there will be a key error
        if nested_locations.get(country) is None:
            nested_locations[country] = {}

        # Initialize the list
        if zip and not nested_locations[country].get("zip"):
            nested_locations[country]["zip"] = []

        if city and not nested_locations[country].get("city"):
            nested_locations[country]["city"] = []

        # Second level of filtering is zip and state
        # Requests must have a country+zip or country+state combination
        if zip:
            # Appending zips so we don't overwrite
            nested_locations[country]["zip"].append(zip)

        # If we have a state, add it to the list
        if state and nested_locations[country].get(state) is None:
            nested_locations[country][state] = {"county": [], "district": [], "city": []}

        # Based on previous checks, there will always be a state if either of these exist
        if county:
            nested_locations[country][state]["county"].extend(get_fields_list("county", county))

        if district:
            nested_locations[country][state]["district"].extend(get_fields_list("district", district))

        if city and state:
            nested_locations[country][state]["city"].append(city)
        elif city:
            nested_locations[country]["city"].append(city)

    return nested_locations


def location_error_handling(fields):
    """ Raise the relevant error for location keys. """
    # Request must have country, and can only have 3 fields, and must have state if there is county or district
    if "country" not in fields:
        raise InvalidParameterException("Invalid filter:  Missing necessary location field: country.")

    if "state" not in fields and ("county" in fields or "district" in fields):
        raise InvalidParameterException("Invalid filter:  Missing necessary location field: state.")


def get_fields_list(scope, field_value):
    """ List of values to search for; `field_value`, plus possibly variants on it """
    if scope in ["congressional_code", "county_code"]:
        try:
            # Congressional and county codes are not uniform and contain multiple variables
            # In the location table Ex congressional code (01): '01', '1.0', '1'
            return [str(int(field_value)), field_value, str(float(field_value))]
        except ValueError:
            # if filter causes an error when casting to a float or integer
            # Example: 'ZZ' for an area without a congressional code
            pass
    return [field_value]


def return_query_string(use_matview: bool) -> tuple:
    """ Returns query strings based upon if the queryset is for a normalized or de-normalized model """

    if use_matview:  # de-normalized
        # Queries going through the references_location table will not require a join
        # Example "pop__county_code"
        q_str = "{0}_{1}"
        country_code_col = "country_code"  # Matviews use country_code ex: pop_country_code
    else:
        # Queries going through the references_location table will require a join in the filter
        # Example "place_of_performance__county_code"
        q_str = "{0}__{1}"
        country_code_col = "location_country_code"  # References_location table uses the col location_country_code

    return q_str, country_code_col


def create_city_name_queryset(
    scope: str, desired_id_field: str, list_of_cities: list, country_code: str, state_code: Optional[str] = None
) -> Q:
    """
    Given a list of city names and the scope, return a django queryset.
    scope = "pop" or "recipient_location"
    list_of_city_names is a list of strings
    country_code is the country code to limit the query and results from Elasticsearch
    state_code (optional) is the state code if the search should be limited to that state
    """
    matching_awards = set(
        chain(*[get_record_ids_by_city(
            scope, desired_id_field, city, country_code, state_code) for city in list_of_cities]
        )
    )
    result_queryset = Q(pk=None)  # If there are no city results in Elasticsearch, use this always falsey Q filter

    if matching_awards:
        result_queryset = Q(**{desired_id_field + "__in": matching_awards})
    return result_queryset


def get_record_ids_by_city(
    scope: str, desired_id_field: str, city: str, country_code: str, state_code: Optional[str] = None
) -> list:
    """
    Craft an elasticsearch query to return award ids by city or an empty list
    if there were no matches.
    """

    # Search using a "filter" instead of a "query" to leverage ES caching
    query = {
        "bool": {
            "must": [
                {"match": {"{}_city_name.keyword".format(scope): es_sanitize(city).upper()}},
                {"match": {"{}_country_code".format(scope): es_sanitize(country_code)}},
            ]
        }
    }
    if state_code:
        # If a state was provided, include it in the filter to limit hits
        query["bool"]["must"].append({"match": {"{}_state_code".format(scope): es_sanitize(state_code).upper()}})

    search_body = {
        "_source": [desired_id_field],
        "size": 0,
        "query": query,
        "aggs": {"id_groups": {"terms": {"field": desired_id_field, "size": 500000}}},
    }

    return elasticsearch_results(search_body)


def build_temp_es_transaction_hits_by_city(scope: str, city: str, country_code: str,
                                           state_code: Optional[str] = None, es_batch_size=10000,
                                           insert_chunk_size=DEFAULT_CHUNK_SIZE):
    hits = page_es_hits_by_city(scope, city, country_code, state_code, page_size=es_batch_size)
    TempEsTransactionHitManager.add_es_hits_orm(hits, chunk_size=insert_chunk_size)


def page_es_hits_by_city(scope: str, city: str, country_code: str,
                         state_code: Optional[str] = None,
                         page_size: int = 10000) -> list:
    """
    Craft an elasticsearch query to return award ids by city or an empty list
    if there were no matches.
    """
    must_criteria = {
        "must": [
            {"match": {"{}_city_name.keyword".format(scope): es_sanitize(city).upper()}},
            {"match": {"{}_country_code".format(scope): es_sanitize(country_code)}},
        ]
    }
    if state_code:
        # If a state was provided, include it in the filter to limit hits
        must_criteria["must"].append({"match": {"{}_state_code".format(scope): es_sanitize(state_code).upper()}})

    # Search using a "filter" instead of a "query" to leverage ES caching
    search_body = {
        "_source": ["award_id", "transaction_id"],
        "size": 0,
        "query": {
            "bool": {
                "filter": {
                    "bool": must_criteria
                }
            }
        }
    }
    paging_strategy = "search_after"
    aggs = _get_city_search_aggregation(paging_strategy, "transaction_id", search_body, page_size)
    if aggs:
        search_body["aggs"] = aggs

    logger.debug("Start streaming Elasticsearch results using paging strategy [{}] for city, state, country "
                 "= {}, {}, {}".format(paging_strategy, city, state_code, country_code))
    yield from _yield_es_hits(paging_strategy, search_body, page_size)


def _yield_es_hits(paging_strategy, search_body, page_size=None):
    if paging_strategy == "search_after":
        search_body["sort"] = search_body["_source"]
        yield from _yield_query_results_with_search_after(page_size, search_body)
    elif paging_strategy == "scroll":
        yield from _yield_query_results_with_scroll(page_size, search_body)
    elif paging_strategy == "partition":
        yield from _yield_query_results_with_partition(search_body)


def _get_city_search_aggregation(paging_strategy, desired_id_field, search_body, page_size=10000):
    if paging_strategy == "search_after" or paging_strategy == "scroll": return {}
    elif paging_strategy == "partition":
        cardinality_agg = {
            "total_hit_count": {
                "cardinality": {
                    "field": desired_id_field
                }
            }
        }
        total_hit_query = search_body.copy()
        total_hit_query["aggs"] = cardinality_agg
        total_hit_result = es_client_query(body=total_hit_query,
                                           index="{}*".format(settings.TRANSACTIONS_INDEX_ROOT),
                                           retries=5)
        total_hit_count = total_hit_result["aggregations"]["total_hit_count"]["value"]
        # +1 to round up the fraction and +1 more because cardinality counts aren't precise.
        num_partitions = (total_hit_count // page_size) + 3

        return {
                "id_groups": {
                    "terms": {
                        "field": desired_id_field,
                        "size": page_size,
                        "include": {
                            "partition": 0,
                            "num_partitions": num_partitions
                        },
                    }
                }
            }
    else:
        raise ValueError("Unrecognized paging strategy")


def _yield_query_results_with_partition(search_body):
    had_values = False
    page_size = search_body["aggs"]["id_groups"]["terms"]["size"]
    num_partitions = search_body["aggs"]["id_groups"]["terms"]["include"]["num_partitions"]
    for partition in range(0, num_partitions):
        search_body["aggs"]["id_groups"]["terms"]["include"]["partition"] = partition
        logger.debug("ES STARTING REQUEST (_search) with body: {}".format(search_body))
        result = es_client_query(body=search_body, index="{}*".format(settings.TRANSACTIONS_INDEX_ROOT), retries=5)
        if result and result["aggregations"]["id_groups"]["buckets"]:
            had_values = True
            logger.debug("ES RECEIVED RESPONSE: Streaming batch of {} "
                         "transaction hits from Elasticsearch".format(page_size))
            yield from (TempEsTransactionHit(award_id=hit["key"],
                                             transaction_id=hit["key"])
                        for hit in result["aggregations"]["id_groups"]["buckets"])
    if not had_values:
        logger.info("No transaction hits from Elasticsearch for search")


def _yield_query_results_with_scroll(page_size, search_body):
    for hit in es_scan(index="{}*".format(settings.TRANSACTIONS_INDEX_ROOT), body=search_body, batch_size=page_size):
        yield TempEsTransactionHit(award_id=hit["_source"]["award_id"],
                                   transaction_id=hit["_source"]["transaction_id"])


def _yield_query_results_with_search_after(page_size, search_body):
    search_after = None
    search_body["size"] = page_size
    while True:
        logger.debug("ES STARTING REQUEST (_search) with body: {}".format(search_body))
        result = es_client_query(body=search_body, index="{}*".format(settings.TRANSACTIONS_INDEX_ROOT), retries=5)
        if result and result["hits"]["total"] and result["hits"]["hits"]:
            logger.debug("ES RECEIVED RESPONSE: Streaming batch of {} "
                         "transaction hits from Elasticsearch".format(page_size))
            yield from (TempEsTransactionHit(award_id=hit["_source"]["award_id"],
                                             transaction_id=hit["_source"]["transaction_id"])
                        for hit in result["hits"]["hits"])
            search_after = result["hits"]["hits"][-1]["sort"]
            search_body["search_after"] = search_after
        else:
            if search_after is None:
                logger.info("No transaction hits from Elasticsearch for search")
            break


def elasticsearch_results(body: dict) -> list:
    """
    Run provided query and return a list of award ids or an empty list if there
    were no hits.
    """
    hits = es_client_query(body=body, index="{}*".format(settings.TRANSACTIONS_INDEX_ROOT), retries=5)

    if hits and hits["hits"]["total"]:
        return [result["key"] for result in hits["aggregations"]["id_groups"]["buckets"]]
    else:
        return []
