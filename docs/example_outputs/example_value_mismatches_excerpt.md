# Example `value_mismatches.csv` excerpt

Example only (illustrative):

```csv
key,source_field,target_field,source_value,target_value,comparator,reason
1004,email,email,alice@oldco.com,alice@newco.co,string,exact_string_mismatch
1007,balance,balance,42.10,42.60,number,absolute_tolerance_exceeded
```

Use the real generated CSV as authoritative evidence for your run.
