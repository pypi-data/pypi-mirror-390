"""civic_lib_geo/us_constants.py.

US State Code Constants for Civic Interconnect

This module defines reusable mappings and lookup records for U.S. state information,
including:

- 2-letter abbreviations
- Full state names
- FIPS codes
- Multiple lookup formats (by name, abbr, FIPS, lowercase)
- Pre-built record dictionaries and choice lists for UI/display

These constants are used to standardize geodata processing and support consistent reporting.
"""

from dataclasses import dataclass

__all__ = [
    "US_STATE_CODES",
    "US_STATE_ABBR_TO_NAME",
    "US_STATE_ABBR_TO_FIPS",
    "US_STATE_FIPS_TO_ABBR",
    "US_STATE_NAME_TO_ABBR",
    "US_STATE_RECORDS",
    "US_STATE_RECORDS_BY_ABBR",
    "US_STATE_RECORDS_BY_NAME",
    "US_STATE_RECORDS_BY_FIPS",
    "get_state_record_by_abbr",
    "get_state_record_by_name",
    "get_state_record_by_fips",
    "get_state_record_by_any",
    "list_state_choices",
    "list_state_choices_by_fips",
]


# List of all valid 2-letter U.S. state abbreviations
US_STATE_CODES = [
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
]

# Mapping of state abbreviation to full name
US_STATE_ABBR_TO_NAME = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
}

# Mapping of state abbreviation to FIPS code
# FIPS codes are 2-digit codes assigned by the U.S. Census Bureau
US_STATE_ABBR_TO_FIPS = {
    "AL": "01",
    "AK": "02",
    "AZ": "04",
    "AR": "05",
    "CA": "06",
    "CO": "08",
    "CT": "09",
    "DE": "10",
    "FL": "12",
    "GA": "13",
    "HI": "15",
    "ID": "16",
    "IL": "17",
    "IN": "18",
    "IA": "19",
    "KS": "20",
    "KY": "21",
    "LA": "22",
    "ME": "23",
    "MD": "24",
    "MA": "25",
    "MI": "26",
    "MN": "27",
    "MS": "28",
    "MO": "29",
    "MT": "30",
    "NE": "31",
    "NV": "32",
    "NH": "33",
    "NJ": "34",
    "NM": "35",
    "NY": "36",
    "NC": "37",
    "ND": "38",
    "OH": "39",
    "OK": "40",
    "OR": "41",
    "PA": "42",
    "RI": "44",
    "SC": "45",
    "SD": "46",
    "TN": "47",
    "TX": "48",
    "UT": "49",
    "VT": "50",
    "VA": "51",
    "WA": "53",
    "WV": "54",
    "WI": "55",
    "WY": "56",
}

# Map FIPS codes to state abbreviations
US_STATE_FIPS_TO_ABBR = {v: k for k, v in US_STATE_ABBR_TO_FIPS.items()}

# Map full state names to abbreviations
US_STATE_NAME_TO_ABBR = {v: k for k, v in US_STATE_ABBR_TO_NAME.items()}

# Map full state names to FIPS codes
US_STATE_RECORDS = [
    {
        "abbr": abbr,
        "name": US_STATE_ABBR_TO_NAME[abbr],
        "fips": US_STATE_ABBR_TO_FIPS[abbr],
    }
    for abbr in US_STATE_CODES
]

# Pre-built records by FIPS code for each state with abbr, name, and FIPS code
US_STATE_RECORDS_BY_FIPS = {record["fips"]: record for record in US_STATE_RECORDS}

# Pre-built records by 2-letter state abbreviation (e.g. MN) for each state with abbr, name, and FIPS code
US_STATE_RECORDS_BY_ABBR = {record["abbr"]: record for record in US_STATE_RECORDS}

# Pre-built records by full state name (e.g. Minnesota) for each state with abbr, name, and FIPS code
US_STATE_RECORDS_BY_NAME = {record["name"]: record for record in US_STATE_RECORDS}

# Pre-built records by lowercase full state name (e.g. "minnesota") for each state
US_STATE_RECORDS_BY_NAME_LOWER = {record["name"].lower(): record for record in US_STATE_RECORDS}

# Pre-built records by lowercase 2-letter abbreviation (e.g. "mn") for each state
US_STATE_RECORDS_BY_ABBR_LOWER = {record["abbr"].lower(): record for record in US_STATE_RECORDS}

# Pre-built records by lowercase FIPS code (e.g. "27") for each state
US_STATE_RECORDS_BY_FIPS_LOWER = {record["fips"].lower(): record for record in US_STATE_RECORDS}

# List of (abbreviation, full name) tuples (e.g. ("MN", "Minnesota")), useful for UI selection
US_STATE_CHOICES = [(abbr, US_STATE_ABBR_TO_NAME[abbr]) for abbr in US_STATE_CODES]

# List of (FIPS, full name) tuples (e.g. ("27", "Minnesota")), useful for UI selection
US_STATE_CHOICES_BY_FIPS = [(record["fips"], record["name"]) for record in US_STATE_RECORDS]


def get_state_record_by_abbr(abbr: str) -> dict | None:
    """Return state record by 2-letter abbreviation (e.g., 'MN')."""
    return US_STATE_RECORDS_BY_ABBR.get(abbr.upper())


def get_state_record_by_name(name: str) -> dict | None:
    """Return state record by full name (e.g., 'Minnesota')."""
    return US_STATE_RECORDS_BY_NAME.get(name)


def get_state_record_by_fips(fips: str) -> dict | None:
    """Return state record by FIPS code (e.g., '27')."""
    return US_STATE_RECORDS_BY_FIPS.get(fips)


def get_state_record_by_any(value: str) -> dict | None:
    """Return state record by abbr, name, or FIPS code (case-insensitive)."""
    value = value.strip().lower()
    return (
        US_STATE_RECORDS_BY_ABBR_LOWER.get(value)
        or US_STATE_RECORDS_BY_NAME_LOWER.get(value)
        or US_STATE_RECORDS_BY_FIPS_LOWER.get(value)
    )


def list_state_choices() -> list[tuple[str, str]]:
    """Return list of (abbr, name) tuples for all states (for dropdowns/UI)."""
    return US_STATE_CHOICES


def list_state_choices_by_fips() -> list[tuple[str, str]]:
    """Return list of (FIPS, name) tuples for all states (for dropdowns/UI)."""
    return US_STATE_CHOICES_BY_FIPS


def get_state_dir_name(state_abbr: str) -> str:
    """Return the standardized directory name for a state (full lowercase name with underscores).

    DEPRECATED: Use get_state_tokens().legacy_dir_name_lowercase_with_underscores or .iso_dir_name instead.
    """
    name = US_STATE_ABBR_TO_NAME[state_abbr]
    return name.lower().replace(" ", "_")


@dataclass(frozen=True)
class StateTokens:
    """Canonical state identifiers with all representations."""

    abbr_uppercase: str  # 'MN'
    abbr_lowercase: str  # 'mn'
    fips: str  # '27'
    full_name: str  # 'Minnesota'

    @property
    def legacy_dir_name_lowercase_with_underscores(self) -> str:
        """Legacy directory name (full state name lowercase with underscores)."""
        return self.full_name.lower().replace(" ", "_")

    @property
    def iso_dir_name(self) -> str:
        """ISO-standardized directory name (lowercase abbreviation)."""
        return self.abbr_lowercase


def get_state_tokens(value: str | None) -> StateTokens:
    """Get all canonical forms of a state identifier.

    Args:
        value: Any state identifier - 'MN', 'mn', 'Minnesota', '27', etc.

    Returns:
        StateTokens with all canonical forms

    Examples:
        >>> tokens = get_state_tokens('Minnesota')
        >>> tokens.abbr_uppercase
        'MN'
        >>> tokens.iso_dir_name
        'mn'
        >>> tokens.legacy_dir_name_lowercase_with_underscores
        'minnesota'
    """
    rec = get_state_record_by_any(value or "")
    if not rec or "abbr" not in rec:
        raise ValueError(f"Unrecognized state: {value!r}")

    return StateTokens(
        abbr_uppercase=rec["abbr"],
        abbr_lowercase=rec["abbr"].lower(),
        fips=rec["fips"],
        full_name=rec["name"],
    )
