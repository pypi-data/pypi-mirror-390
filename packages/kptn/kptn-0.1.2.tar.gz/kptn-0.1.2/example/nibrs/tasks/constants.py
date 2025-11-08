DEMOGRAPHICS_TABLE_LIST = [
    "3a",
    "3b",
    "4a",
    "4b",
    "DM7",
    "DM9",
    "5a",
    "5b",
    "GV2a",
    "DM10",
    "3aunclear",
    "3aclear",
    "3bunclear",
    "3bclear",
]

DEMOGRAPHIC_COLUMN_NUMBERS = {
    "3a":33,
    "3b":33,
    "4a":61,
    "4b":61,
    "DM7":54,
    "DM9":54,
    "5a":71,
    "5b":71,
    "GV2a":13,
    "DM10":4,
    "3aunclear":33,
    "3aclear":33,
    "3bunclear":33,
    "3bclear":33,
}

TABLE_LIST = [
    "1a",
    "1b",
    "1c",
    "2a",
    "2b",
    "2c",
    "3a",
    "3b",
    "3c",
    "4a",
    "4b",
    "LEOKA",
    "DM1",
    "DM2",
    "DM3",
    "DM4",
    "DM5",
    "DM6",
    "DM7",
    "DM8",
    "DM9",
    "DM10",
    "5a",
    "5b",
    "GV1a",
    "GV2a",
    "3aunclear",
    "3aclear",
    "3bunclear",
    "3bclear",
    "YT1",
    "YT2",
    "GV3a",
]

NON_DEMOGRAPHICS_TABLE_LIST = [
    t for t in TABLE_LIST if t not in DEMOGRAPHICS_TABLE_LIST
]

STATES = [
    "AL",  # Alabama
    "AK",  # Alaska
    "AZ",  # Arizona
    "AR",  # Arkansas
    "CA",  # California
    "CO",  # Colorado
    "CT",  # Connecticut
    "DE",  # Delaware
    "DC",  # District of Columbia
    "FL",  # Florida
    "GA",  # Georgia
    "HI",  # Hawaii
    "ID",  # Idaho
    "IL",  # Illinois
    "IN",  # Indiana
    "IA",  # Iowa
    "KS",  # Kansas
    "KY",  # Kentucky
    "LA",  # Louisiana
    "ME",  # Maine
    "MD",  # Maryland
    "MA",  # Massachusetts
    "MI",  # Michigan
    "MN",  # Minnesota
    "MS",  # Mississippi
    "MO",  # Missouri
    "MT",  # Montana
    "NB",  # Nebraska
    "NV",  # Nevada
    "NH",  # New Hampshire
    "NJ",  # New Jersey
    "NM",  # New Mexico
    "NY",  # New York
    "NC",  # North Carolina
    "ND",  # North Dakota
    "OH",  # Ohio
    "OK",  # Oklahoma
    "OR",  # Oregon
    "PA",  # Pennsylvania
    "RI",  # Rhode Island
    "SC",  # South Carolina
    "SD",  # South Dakota
    "TN",  # Tennessee
    "TX",  # Texas
    "UT",  # Utah
    "VT",  # Vermont
    "VA",  # Virginia
    "WA",  # Washington
    "WV",  # West Virginia
    "WI",  # Wisconsin
    "WY",  # Wyoming
]

RSCRIPT_ENV = "env LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2"
