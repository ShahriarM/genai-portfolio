"""Week 8 — Tool use: the three tools.

Each tool has two parts: a Python function that does the work, and a schema (name, description,
input_schema) that tells the model what the tool is for and what arguments it takes. The model
never runs anything: it asks for a call, agent.py runs the function and sends the result back.

Every function takes model-written input, so every function checks it. A tool that is given bad
input raises ValueError with a message the model can act on; agent.py returns it as an error result.
"""
import ast
import json
import math
import operator
import sqlite3
from functools import lru_cache
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

DB = Path(__file__).resolve().parent / "loans.db"      # built by make_data.py
MAX_ROWS = 200                                          # most rows sql_query returns
FEATURES = ["fico", "dti", "ltv"]


# ---------------------------------------------------------------- calculator
_BINARY = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
           ast.Pow: operator.pow, ast.Mod: operator.mod, ast.FloorDiv: operator.floordiv}
_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_FUNCS = {"sqrt": math.sqrt, "exp": math.exp, "log": math.log, "abs": abs, "round": round, "min": min, "max": max}


def _eval(node):
    """Walk the parsed expression and allow only numbers, arithmetic and a few named functions."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY:
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("exponent too large")            # 9**9**9 would hang the process
        return _BINARY[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY:
        return _UNARY[type(node.op)](_eval(node.operand))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _FUNCS and not node.keywords:
        return _FUNCS[node.func.id](*[_eval(a) for a in node.args])
    raise ValueError(f"not allowed in an expression: {ast.dump(node)[:60]}")


def calculator(expression: str) -> str:
    """Evaluate an arithmetic expression. Never eval(): the text comes from the model."""
    if len(expression) > 2000:
        raise ValueError("expression too long")
    try:
        tree = ast.parse(expression.replace("$", "").replace("^", "**"), mode="eval")   # commas stay: they separate arguments
    except SyntaxError as e:
        raise ValueError(f"not a valid arithmetic expression ({e.msg}). Write numbers without thousands separators: 1000000, not 1,000,000")
    if isinstance(tree.body, ast.Tuple):
        raise ValueError("write numbers without thousands separators: 1000000, not 1,000,000")
    try:
        return repr(_eval(tree.body))
    except ZeroDivisionError:
        raise ValueError("division by zero")


# ----------------------------------------------------------------- sql_query
def _connect():
    return sqlite3.connect(f"file:{DB}?mode=ro", uri=True)     # read-only at the database level


def sql_query(query: str) -> str:
    """Run one read-only SELECT on the loans table; at most MAX_ROWS rows come back."""
    q = query.strip().rstrip(";").strip()
    if ";" in q:
        raise ValueError("only one statement is allowed")
    if not q.lower().startswith(("select", "with")):
        raise ValueError("only SELECT queries are allowed")
    con = _connect()
    try:
        cur = con.execute(q)
        rows = cur.fetchmany(MAX_ROWS + 1)
        columns = [d[0] for d in cur.description]
    except sqlite3.Error as e:
        raise ValueError(f"SQL error: {e}")
    finally:
        con.close()
    out = {"columns": columns, "rows": [list(r) for r in rows[:MAX_ROWS]], "row_count": min(len(rows), MAX_ROWS)}
    if len(rows) > MAX_ROWS:
        out["truncated"] = f"more than {MAX_ROWS} rows; only the first {MAX_ROWS} are shown. Aggregate in SQL instead."
    return json.dumps(out)


# -------------------------------------------------------------------- get_pd
@lru_cache(maxsize=1)
def _pd_model():
    """Logistic regression of default on FICO, DTI and LTV, fitted once on the whole loans table."""
    con = _connect()
    data = np.array(con.execute(f"SELECT {', '.join(FEATURES)}, defaulted FROM loans").fetchall(), dtype=float)
    con.close()
    return make_pipeline(StandardScaler(), LogisticRegression()).fit(data[:, :3], data[:, 3])


def get_pd(loan_ids: list | None = None, fico: float | None = None, dti: float | None = None, ltv: float | None = None) -> str:
    """PD for loans in the table (by loan_ids) or for one hypothetical loan (fico, dti, ltv)."""
    model = _pd_model()
    if loan_ids:
        ids = sorted({int(i) for i in loan_ids})
        con = _connect()
        marks = ",".join("?" * len(ids))
        rows = con.execute(f"SELECT loan_id, {', '.join(FEATURES)} FROM loans WHERE loan_id IN ({marks})", ids).fetchall()
        con.close()
        if not rows:
            raise ValueError("none of those loan_ids exist; loan_id runs from 1 to 500")
        found = [r[0] for r in rows]
        pds = model.predict_proba(np.array([r[1:] for r in rows], dtype=float))[:, 1]
        out = {"n_loans": len(found), "mean_pd": round(float(pds.mean()), 6),
               "min_pd": round(float(pds.min()), 6), "max_pd": round(float(pds.max()), 6)}
        if len(found) <= 20:
            out["pd_by_loan"] = {str(i): round(float(p), 6) for i, p in zip(found, pds)}
        missing = sorted(set(ids) - set(found))
        if missing:
            out["missing_loan_ids"] = missing
        return json.dumps(out)
    if None in (fico, dti, ltv):
        raise ValueError("give either loan_ids, or all three of fico, dti and ltv")
    if not (300 <= fico <= 850 and 0 <= dti <= 1.5 and 0 <= ltv <= 2):
        raise ValueError("out of range: fico is 300-850; dti and ltv are ratios such as 0.34 and 0.78, not percentages")
    pd_ = model.predict_proba(np.array([[fico, dti, ltv]], dtype=float))[0, 1]
    return json.dumps({"pd": round(float(pd_), 6), "inputs": {"fico": fico, "dti": dti, "ltv": ltv}})


# What the model sees. The description is how the model decides when and how to call a tool.
TOOLS = [
    {
        "name": "calculator",
        "description": "Evaluate one arithmetic expression and return the number. Supports + - * / ** % and "
                       "parentheses, and sqrt, exp, log, abs, round, min, max. Use it for every calculation; "
                       "do not do arithmetic yourself. Write numbers plainly, without commas or currency signs. "
                       "Example: \"(a + b) / 2\" with your own numbers in place of a and b.",
        "input_schema": {
            "type": "object",
            "properties": {"expression": {"type": "string", "description": "Numbers and operators only, no variables"}},
            "required": ["expression"],
        },
    },
    {
        "name": "sql_query",
        "description": "Run one read-only SQLite SELECT on the loan portfolio and get the rows as JSON. "
                       "Table `loans` (500 rows): loan_id INTEGER, amount REAL (original balance in dollars), "
                       "fico INTEGER (520-850), dti REAL (debt-to-income ratio, e.g. 0.34), ltv REAL (loan-to-value "
                       f"ratio, e.g. 0.78), term INTEGER (years: 15, 20, 30), state TEXT (two letters), defaulted "
                       f"INTEGER (1 = defaulted). At most {MAX_ROWS} rows are returned, so aggregate with COUNT, SUM "
                       "and AVG where you can. The table has no PD column: use get_pd for PDs.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "A single SELECT statement"}},
            "required": ["query"],
        },
    },
    {
        "name": "get_pd",
        "description": "Probability of default (PD) from a logistic regression on FICO, DTI and LTV. Two ways to "
                       "call it. (1) loan_ids: a list of loan_id values from the loans table; returns the number of "
                       "loans, the mean, minimum and maximum PD, and each loan's PD when there are 20 or fewer. "
                       "(2) fico, dti and ltv for one hypothetical loan; returns its PD. PDs are fractions: 0.05 is 5%.",
        "input_schema": {
            "type": "object",
            "properties": {
                "loan_ids": {"type": "array", "items": {"type": "integer"}, "description": "loan_id values, e.g. from sql_query"},
                "fico": {"type": "number", "description": "Credit score, 300-850"},
                "dti": {"type": "number", "description": "Debt-to-income as a ratio, e.g. 0.34"},
                "ltv": {"type": "number", "description": "Loan-to-value as a ratio, e.g. 0.78"},
            },
        },
    },
]

FUNCTIONS = {"calculator": calculator, "sql_query": sql_query, "get_pd": get_pd}
