
import pandas as pd
from pathlib import Path

ROOT = Path("data/quickstart")
TZ = "Europe/Vienna"


def load(name):
    path = ROOT / name
    if not path.exists():
        print(f"\nMISSING FILE: {name}")
        return None
    return pd.read_csv(path)


def numeric_summary(df):
    df = df.copy()
    df["numeric_value"] = pd.to_numeric(
        df["value"], errors="coerce"
    )

    return df.groupby(["asset_id", "metric"]).agg(
        total_records=("value", "size"),
        numeric_records=("numeric_value", "count"),
        min_value=("numeric_value", "min"),
        max_value=("numeric_value", "max"),
        mean_value=("numeric_value", "mean"),
    )


def section(title):
    print(f"\n{'=' * 15} {title} {'=' * 15}")


# --------------------------------------------------
# BOOKINGS / OCCUPANCY SURGES
# --------------------------------------------------

section("BOOKINGS")

bk = load("bookings.csv")

if bk is not None:
    print("Columns:", bk.columns.tolist())

    if {"arrival_utc", "room_id"}.issubset(bk.columns):
        bk["arrival_utc"] = pd.to_datetime(
            bk["arrival_utc"], utc=True, errors="coerce"
        )

        if "status" in bk.columns:
            bk = bk[bk["status"] == "confirmed"]

        bk["arrival_day"] = (
            bk["arrival_utc"]
            .dt.tz_convert(TZ)
            .dt.date
        )

        arrivals = (
            bk.groupby("arrival_day")["room_id"]
            .nunique()
            .sort_values(ascending=False)
        )

        print("\nMaximum arrivals/day:", arrivals.max())
        print("\nTop arrival days:")
        print(arrivals.head(10).to_string())

        print("\nDays with >= 20 arrivals:")
        print(arrivals[arrivals >= 20].to_string())


# --------------------------------------------------
# STAFFING
# --------------------------------------------------

section("STAFF ROSTER")

ro = load("staff_roster.csv")

if ro is not None:
    print("Columns:", ro.columns.tolist())

    if {"role", "status"}.issubset(ro.columns):
        print("\nStaff records by role/status:")
        print(
            ro.groupby(["role", "status"])
            .size()
            .to_string()
        )

        sick = ro[
            (ro["role"] == "cleaner")
            & (ro["status"] == "sick")
        ]

        print("\nSick cleaner records:")

        if sick.empty:
            print("None")
        else:
            cols = [
                c for c in [
                    "resource_id",
                    "start_utc",
                    "end_utc",
                    "status_known_utc"
                ]
                if c in sick.columns
            ]
            print(sick[cols].to_string(index=False))


# --------------------------------------------------
# EQUIPMENT
# --------------------------------------------------

section("EQUIPMENT")

eq = load("equipment.csv")

if eq is not None:
    print("Columns:", eq.columns.tolist())

    if {"asset_id", "metric", "value"}.issubset(eq.columns):
        print("\nEquipment metric summary:")
        print(numeric_summary(eq).round(2).to_string())

        # Textual status readings
        statuses = eq[
            eq["metric"].astype(str).str.contains(
                "status", case=False, na=False
            )
        ]

        if not statuses.empty:
            print("\nEquipment status values:")
            print(
                statuses.groupby(
                    ["asset_id", "metric", "value"]
                ).size().to_string()
            )

        eq["timestamp_utc"] = pd.to_datetime(
            eq["timestamp_utc"],
            utc=True,
            errors="coerce"
        )

        eq["numeric_value"] = pd.to_numeric(
            eq["value"], errors="coerce"
        )

        # AHU filter pressure
        ahu = eq[
            (eq["asset_id"] == "AHU1")
            & (eq["metric"] == "filter_dp_pa")
        ].copy()

        if not ahu.empty:
            daily = (
                ahu.set_index("timestamp_utc")
                ["numeric_value"]
                .resample("1D")
                .median()
            )

            print("\nAHU1 daily median filter pressure (Pa):")
            print(daily.round(1).to_string())

            print("\nAHU pressure change:")
            print("First daily median:", daily.iloc[0])
            print("Last daily median:", daily.iloc[-1])

        # Heat pump
        hp = eq[
            (eq["asset_id"] == "HP1")
            & (
                eq["metric"].isin([
                    "heat_output_kw",
                    "electric_kw"
                ])
            )
        ]

        if not hp.empty:
            pivot = hp.pivot_table(
                index="timestamp_utc",
                columns="metric",
                values="numeric_value",
                aggfunc="median"
            )

            if {
                "heat_output_kw",
                "electric_kw"
            }.issubset(pivot.columns):

                pivot = pivot[
                    pivot["electric_kw"] > 0.5
                ].copy()

                pivot["cop"] = (
                    pivot["heat_output_kw"]
                    / pivot["electric_kw"]
                )

                print("\nHP1 daily median COP:")
                print(
                    pivot["cop"]
                    .resample("1D")
                    .median()
                    .round(2)
                    .to_string()
                )


# --------------------------------------------------
# LOGISTICS
# --------------------------------------------------

section("LOGISTICS")

lg = load("logistics.csv")

if lg is not None:
    print("Columns:", lg.columns.tolist())

    if {"asset_id", "metric", "value"}.issubset(lg.columns):
        print("\nLogistics metric summary:")
        print(numeric_summary(lg).round(2).to_string())

        lg["numeric_value"] = pd.to_numeric(
            lg["value"], errors="coerce"
        )

        for asset, g in lg.groupby("asset_id"):
            if asset == "WASTE_MAIN":
                threshold = 85
                hits = g[g.numeric_value >= threshold]

            elif str(asset).startswith("WASTE_F"):
                threshold = 90
                hits = g[g.numeric_value >= threshold]

            elif asset == "VEND1":
                threshold = 15
                hits = g[g.numeric_value <= threshold]

            else:
                continue

            print(
                f"{asset}: {len(hits)} readings "
                f"crossing threshold {threshold}"
            )


section("DIAGNOSTICS COMPLETE")
