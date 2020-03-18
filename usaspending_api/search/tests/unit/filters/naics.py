from usaspending_api.search.elasticsearch.filters.naics import NaicsCodes


def test_primative_naics_filter():
    assert NaicsCodes._query_string(["11"], []) == "(11*)"


def test_two_positive_sibling_naics():
    assert NaicsCodes._query_string(["11", "22"], []) == "(11*) OR (22*)"


def test_two_negative_sibling_naics():
    assert NaicsCodes._query_string([], ["11", "22"]) == "(NOT 11*) AND (NOT 22*)"


def test_simple_positive_hierarchy():
    assert NaicsCodes._query_string(["11", "1111"], []) == "(11*) AND ((1111*))"


def test_simple_negative_hierarchy():
    assert NaicsCodes._query_string([], ["11", "1111"]) == "(NOT 11*) OR ((NOT 1111*))"


def test_positive_to_negative_cross_hierarchy():
    assert NaicsCodes._query_string(["11"], ["1111"]) == "(11*) AND ((NOT 1111*))"


def test_negative_to_positive_cross_hierarchy():
    assert NaicsCodes._query_string(["1111"], ["11"]) == "(NOT 11*) OR ((1111*))"
