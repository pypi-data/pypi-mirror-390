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
