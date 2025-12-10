import pandas as pd
import matplotlib.pyplot as plt
import ast
from pathlib import Path

# ============================================================
# 0. Config
# ============================================================

CSV_PATH = Path("dref3_export.csv")          # change if needed
OUTPUT_DIR = Path("figures_multi_ops")
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================
# 1. Load & basic preprocessing
# ============================================================

df = pd.read_csv(CSV_PATH)

# --- Date parsing ---
date_cols = [
    "date_of_disaster",
    "date_of_appeal_request_from_ns",
    "date_of_approval",
    "date_of_summary_publication",
    "start_date_of_operation",
    "end_date_of_operation",
    "modified_at",
]
for col in date_cols:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

# --- population_disaggregation parsing if present ---
def parse_dict(x):
    if pd.isna(x):
        return {}
    if isinstance(x, dict):
        return x
    try:
        return ast.literal_eval(x)
    except Exception:
        return {}

if "population_disaggregation" in df.columns:
    df["population_disaggregation"] = df["population_disaggregation"].apply(parse_dict)

# Make sure numeric fields are numeric (robustness)
for col in ["amount_approved", "total_approved", "people_affected", "people_targeted", "people_assisted"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# ============================================================
# 2. Funding over time (monthly)
# ============================================================

# Use date_of_disaster as the reference time; fallback to start_date_of_operation
if "date_of_disaster" in df.columns:
    df["ref_date"] = df["date_of_disaster"]
elif "start_date_of_operation" in df.columns:
    df["ref_date"] = df["start_date_of_operation"]
else:
    df["ref_date"] = pd.NaT

funding_time = df.dropna(subset=["ref_date", "total_approved"]).copy()
if not funding_time.empty:
    funding_time["year_month"] = funding_time["ref_date"].dt.to_period("M").dt.to_timestamp()
    funding_monthly = funding_time.groupby("year_month")["total_approved"].sum().sort_index()

    plt.figure(figsize=(14, 7))
    plt.plot(funding_monthly.index[-20:], funding_monthly.values[-20:], marker="o")
    plt.xlabel("Month")
    plt.ylabel("Total Approved (CHF)")
    plt.title("Total Approved Funding Over Time (All Operations)")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "funding_over_time.png", dpi=1200)
    plt.close()

# ============================================================
# 3. Scatter: Funding vs People Targeted
# ============================================================

# scatter_df = df.dropna(subset=["total_approved", "people_targeted"]).copy()

# if not scatter_df.empty:
#     plt.figure(figsize=(10, 8))
#     plt.scatter(scatter_df["people_targeted"], scatter_df["total_approved"])
#     plt.xlabel("People Targeted")
#     plt.ylabel("Total Approved (CHF)")
#     plt.title("Funding vs People Targeted (All Operations)")
#     plt.tight_layout()
#     plt.savefig(OUTPUT_DIR / "funding_vs_people_scatter.png", dpi=1200)
#     plt.close()

# ============================================================
# 4. Operations by disaster type
# ============================================================

if "disaster_definition" in df.columns:
    disaster_counts = df["disaster_definition"].fillna("Unknown").value_counts()

    plt.figure(figsize=(16, 9))
    disaster_counts.sort_values()[-10:].plot(kind="barh")
    plt.xlabel("Number of Operations")
    plt.ylabel("Disaster Type")
    plt.title("Number of Operations by Disaster Type")
    plt.subplots_adjust(left=0.25)  # more space for y-title and labels
    plt.savefig(OUTPUT_DIR / "operations_by_disaster_type.png", dpi=1200)
    plt.close()

# ============================================================
# 5. Sector usage counts (how many operations use each sector)
# ============================================================

# Boolean sector columns: sector_* where type is bool or 0/1-like
sector_bool_cols = [
    c for c in df.columns
    if c.startswith("sector_")
    and not c.endswith("_budget")
    and not c.endswith("_people_targeted")
]

# convert to bool in case they are 0/1
sector_bool_df = df[sector_bool_cols].copy()
for c in sector_bool_cols:
    sector_bool_df[c] = sector_bool_df[c].astype(bool)

sector_usage = sector_bool_df.sum().sort_values(ascending=True)

def clean_sector_name(col):
    name = col.replace("sector_", "")
    name = name.replace("_", " ").title()
    return name

sector_usage.index = [clean_sector_name(c) for c in sector_usage.index]

plt.figure(figsize=(16, 9))
sector_usage[-10:].plot(kind="barh")
plt.xlabel("Number of Operations Using Sector")
plt.ylabel("Sector")
plt.title("Sector Usage Across All Operations")
plt.subplots_adjust(left=0.35)  # more room for long sector names
plt.savefig(OUTPUT_DIR / "sector_usage_counts.png", dpi=1200)
plt.close()

# ============================================================
# 6. Sector usage by region (heatmap)
# ============================================================

if "region" in df.columns and not df["region"].isna().all():
    # make a long-form table: rows = operations, columns = sector + region
    heat_df = sector_bool_df.copy()
    heat_df["region"] = df["region"].fillna("Unknown")

    # group by region, sum booleans => count operations per region using sector
    sector_by_region = heat_df.groupby("region")[sector_bool_cols].sum().T

    # clean index and columns
    sector_by_region.index = [clean_sector_name(c) for c in sector_by_region.index]

    regions = sector_by_region.columns
    sectors = sector_by_region.index
    data = sector_by_region.values

    plt.figure(figsize=(16, 9))
    plt.imshow(data, aspect="auto")
    plt.colorbar(label="Number of Operations")
    plt.xticks(range(len(regions)), regions, rotation=45, ha="right")
    plt.yticks(range(len(sectors)), sectors)
    plt.title("Sector Usage by Region (Number of Operations)")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "sector_usage_by_region_heatmap.png", dpi=1200)
    plt.close()

print("Figures saved to:", OUTPUT_DIR.resolve())
