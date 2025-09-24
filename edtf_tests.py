from edtf import parse_edtf, struct_time_to_date

# sample dates in LOC EDTF formats
# parsing using https://pypi.org/project/edtf/
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

print('Converting to upper and lower strict dates...')
for date in date_samples:
    date_structured = parse_edtf(date)
    print(date, date_structured.lower_strict()[:3], date_structured.upper_strict()[:3])


print('Converting to datetime...')
for date in date_samples:
    date_structured = parse_edtf(date)
    lower_datetime_format = struct_time_to_date(date_structured.lower_strict())
    upper_datetime_format = struct_time_to_date(date_structured.upper_strict())
    #print(date, date_edtf.lower_strict()[:3], date_edtf.upper_strict()[:3])
    print(date, upper_datetime_format, lower_datetime_format)



