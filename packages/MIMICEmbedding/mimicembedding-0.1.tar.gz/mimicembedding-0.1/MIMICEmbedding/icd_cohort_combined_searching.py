
import os, re
import pandas as pd
import numpy as np
from importlib.resources import files

# PATHS (edit base_dir if needed)

with files("MIMICEmbedding.mappings").joinpath("diagnoses_icd.csv.gz").open("rb") as f:
    dx = pd.read_csv(f, compression="gzip")

def icd_combined_search(tags):
    print("Searching for ICD tags:", tags)

    codes_str = tags
    versions  = (9, 10)  # Include both ICD-9 and ICD-10
    scope     = "hadm"

    dx["icd_code"] = dx["icd_code"].astype(str).str.replace(".", "", regex=False)
    ver = dx["icd_version"].isin(versions)

    codes = [c.strip().upper().replace(".", "") for c in codes_str.split(",") if c.strip()]
    print("Parsed codes:", codes)

    flags = []
    for i, c in enumerate(codes):
        col = f"f{i}"
        if "-" in c:
            m = re.match(r"^([A-Z])(\d{2})-(\1)(\d{2})$", c)
            if not m:
                print(f"Bad range format: {c}")
                continue
            L, n1, _, n2 = m.groups()
            lo, hi = f"{L}{n1}", f"{L}{n2}"
            fam3 = dx["icd_code"].str.slice(0, 3)
            dx[col] = (ver & fam3.ge(lo) & fam3.le(hi)).astype(np.uint8)
        else:
            if c.endswith("*"):
                dx[col] = (ver & dx["icd_code"].str.startswith(c[:-1])).astype(np.uint8)
            else:
                dx[col] = (ver & (dx["icd_code"] == c)).astype(np.uint8)
        flags.append(col)

    keys = ["hadm_id", "subject_id"] if scope == "hadm" else ["subject_id"]
    agg = dx.groupby(keys, dropna=False)[flags].max().reset_index()
    mask = agg[flags].astype(bool).any(axis=1)  # Match any code

    cohort_ids = agg.loc[mask, keys].drop_duplicates().reset_index(drop=True)
    print(f"Matched {len(cohort_ids)} {'admissions' if scope == 'hadm' else 'subjects'}")
    return cohort_ids