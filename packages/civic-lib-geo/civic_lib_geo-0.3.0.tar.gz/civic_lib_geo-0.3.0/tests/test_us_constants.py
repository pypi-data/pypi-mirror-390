"""
tests/test_constants.py

Test suite for US state constants in civic_lib_geo.us_constants.
"""

import civic_lib_geo.us_constants as c


def test_state_codes_length():
    assert len(c.US_STATE_CODES) == 50


def test_state_code_validity():
    for code in c.US_STATE_CODES:
        assert code in c.US_STATE_ABBR_TO_NAME
        assert code in c.US_STATE_ABBR_TO_FIPS


def test_fips_mappings_bidirectional():
    for abbr, fips in c.US_STATE_ABBR_TO_FIPS.items():
        assert c.US_STATE_FIPS_TO_ABBR[fips] == abbr


def test_name_abbr_mappings_bidirectional():
    for abbr, name in c.US_STATE_ABBR_TO_NAME.items():
        assert c.US_STATE_NAME_TO_ABBR[name] == abbr


def test_record_structure():
    for record in c.US_STATE_RECORDS:
        assert "abbr" in record
        assert "name" in record
        assert "fips" in record


def test_choices_structure():
    for abbr, name in c.US_STATE_CHOICES:
        assert abbr in c.US_STATE_CODES
        assert name == c.US_STATE_ABBR_TO_NAME[abbr]


def test_lowercase_keys_exist():
    for record in c.US_STATE_RECORDS:
        assert record["abbr"].lower() in c.US_STATE_RECORDS_BY_ABBR_LOWER
        assert record["name"].lower() in c.US_STATE_RECORDS_BY_NAME_LOWER
        assert record["fips"].lower() in c.US_STATE_RECORDS_BY_FIPS_LOWER


def test_resolve_state_tokens_one_word():
    # Test with abbreviation
    tokens: c.StateTokens = c.get_state_tokens("MN")
    assert tokens.abbr_uppercase == "MN"
    assert tokens.abbr_lowercase == "mn"
    assert tokens.fips == "27"
    assert tokens.iso_dir_name == "mn"
    assert tokens.legacy_dir_name_lowercase_with_underscores
    assert tokens.full_name == "Minnesota"


def test_resolve_state_tokens_two_words():
    # Test with abbreviation
    tokens: c.StateTokens = c.get_state_tokens("NY")
    assert tokens.abbr_uppercase == "NY"
    assert tokens.abbr_lowercase == "ny"
    assert tokens.fips == "36"
    assert tokens.iso_dir_name == "ny"
    assert tokens.legacy_dir_name_lowercase_with_underscores == "new_york"
    assert tokens.full_name == "New York"
