from edtf import parse_edtf

# sample dates
"""
1962
198X
19XX
[1962..1963] # retain brackets for valid EDTF format
1969-07~
1969-06-20~
1969-06-22
"""


date_samples = ["1962", "198X", "19XX", "[1962..1963]", "1969-07~", "1969-06-20~", "1969-06-22"]

for date in date_samples:
	date_edtf = parse_edtf(date)
	print(date, date_edtf.lower_strict()[:3], date_edtf.upper_strict()[:3])