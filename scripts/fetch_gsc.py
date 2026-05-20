import os
import json
from datetime import date, timedelta
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SITE_URL = "sc-domain:reicoachingwithfrank.com"

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "docs" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

creds = Credentials(
    None,
    refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
    token_uri="https://oauth2.googleapis.com/token",
    client_id=os.environ["GOOGLE_CLIENT_ID"],
    client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
    scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
)

creds.refresh(Request())

service = build("searchconsole", "v1", credentials=creds)

end_date = date.today() - timedelta(days=2)
start_date = date(2026, 4, 3)


def query_gsc(dimensions=None, row_limit=25000):
    request = {
        "startDate": start_date.isoformat(),
        "endDate": end_date.isoformat(),
        "rowLimit": row_limit,
        "startRow": 0,
    }

    if dimensions:
        request["dimensions"] = dimensions

    response = service.searchanalytics().query(
        siteUrl=SITE_URL,
        body=request
    ).execute()

    return response.get("rows", [])


def save_json(filename, data):
    with open(DATA_DIR / filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


summary_rows = query_gsc()

summary = {
    "site": SITE_URL,
    "start_date": start_date.isoformat(),
    "end_date": end_date.isoformat(),
    "clicks": 0,
    "impressions": 0,
    "ctr": 0,
    "position": 0,
}

if summary_rows:
    row = summary_rows[0]
    summary["clicks"] = row.get("clicks", 0)
    summary["impressions"] = row.get("impressions", 0)
    summary["ctr"] = row.get("ctr", 0)
    summary["position"] = row.get("position", 0)


pages = []
for row in query_gsc(["page"]):
    pages.append({
        "page": row["keys"][0],
        "clicks": row.get("clicks", 0),
        "impressions": row.get("impressions", 0),
        "ctr": row.get("ctr", 0),
        "position": row.get("position", 0),
    })


queries = []
for row in query_gsc(["query"]):
    queries.append({
        "query": row["keys"][0],
        "clicks": row.get("clicks", 0),
        "impressions": row.get("impressions", 0),
        "ctr": row.get("ctr", 0),
        "position": row.get("position", 0),
    })


daily = []
for row in query_gsc(["date"], row_limit=1000):
    daily.append({
        "date": row["keys"][0],
        "clicks": row.get("clicks", 0),
        "impressions": row.get("impressions", 0),
        "ctr": row.get("ctr", 0),
        "position": row.get("position", 0),
    })


page_daily = []
for row in query_gsc(["page", "date"], row_limit=25000):
    page_daily.append({
        "page": row["keys"][0],
        "date": row["keys"][1],
        "clicks": row.get("clicks", 0),
        "impressions": row.get("impressions", 0),
        "ctr": row.get("ctr", 0),
        "position": row.get("position", 0),
    })


save_json("summary.json", summary)
save_json("pages.json", pages)
save_json("queries.json", queries)
save_json("daily.json", daily)
save_json("page_daily.json", page_daily)

print("GSC export complete")
