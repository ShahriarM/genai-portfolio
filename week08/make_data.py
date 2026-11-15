"""Week 8 — Tool use: build the small SQLite table of loan data that the SQL tool queries.

The data is SYNTHETIC: 500 made-up loans drawn from simple distributions with a fixed seed.
Default is simulated from a known logistic relationship, so the PD model fitted later has
something real to recover. Nothing here describes actual borrowers or any bank's portfolio.

    python make_data.py        # writes loans.db (overwrites it)
"""
import sqlite3
from pathlib import Path

import numpy as np

DB = Path(__file__).resolve().parent / "loans.db"
N = 500
rng = np.random.default_rng(8)

fico = np.clip(rng.normal(700, 60, N), 520, 850).round().astype(int)
dti = np.clip(rng.normal(0.34, 0.10, N), 0.05, 0.65).round(3)            # debt-to-income ratio
ltv = np.clip(rng.normal(0.78, 0.12, N), 0.30, 1.05).round(3)            # loan-to-value ratio
amount = (np.clip(rng.lognormal(12.3, 0.55, N), 40_000, 1_500_000) / 1000).round() * 1000
term = rng.choice([15, 20, 30], N, p=[0.2, 0.15, 0.65])                  # years
state = rng.choice(["PA", "OH", "NJ", "NY", "FL", "TX"], N)

# True default process: worse credit, more debt and less equity raise the odds of default
logit = -3.2 - 0.012 * (fico - 700) + 4.0 * (dti - 0.34) + 3.0 * (ltv - 0.78)
defaulted = (rng.random(N) < 1 / (1 + np.exp(-logit))).astype(int)

con = sqlite3.connect(DB)
con.execute("DROP TABLE IF EXISTS loans")
con.execute("""CREATE TABLE loans (
    loan_id   INTEGER PRIMARY KEY,
    amount    REAL,     -- original balance in dollars
    fico      INTEGER,  -- credit score, 520-850
    dti       REAL,     -- debt-to-income ratio, e.g. 0.34
    ltv       REAL,     -- loan-to-value ratio, e.g. 0.78
    term      INTEGER,  -- years: 15, 20 or 30
    state     TEXT,     -- two-letter state
    defaulted INTEGER   -- 1 if the loan defaulted, else 0
)""")
con.executemany("INSERT INTO loans VALUES (?,?,?,?,?,?,?,?)",
                [(i + 1, float(amount[i]), int(fico[i]), float(dti[i]), float(ltv[i]), int(term[i]), str(state[i]), int(defaulted[i]))
                 for i in range(N)])
con.commit()
n, d, big, avg = con.execute("SELECT COUNT(*), SUM(defaulted), SUM(amount > 300000), AVG(amount) FROM loans").fetchone()
print(f"{DB.name}: {n} loans, {d} defaults ({d / n:.1%}), {big} over $300k, average amount ${avg:,.0f}")
con.close()
