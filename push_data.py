import json
import os
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from postgrest.exceptions import APIError
from supabase import Client, create_client

from Network_Security.exception import NetworkSecurityException
from Network_Security.logger import logger

load_dotenv(override=True)

SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").strip().strip('"').strip("'") or None
SUPABASE_KEY = (os.getenv("SUPABASE_KEY") or "").strip().strip('"').strip("'") or None
SUPABASE_TABLE = os.getenv("SUPABASE_TABLE", "network_data")
INSERT_BATCH_SIZE = 500
SCHEMA_FILE = Path(__file__).resolve().parent / "supabase_schema.sql"


def _csv_path() -> Path:
    filename = "phisingData.csv"
    data_dir = Path(os.getenv("DATA_DIR", "Network_Data"))
    candidates = [
        data_dir / filename,
        Path("Network_Data") / filename,
        Path("data") / filename,
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(f"{filename} not found. Looked in: {candidates}")


def _sql_editor_url() -> str:
    host = (SUPABASE_URL or "").replace("https://", "").replace("http://", "")
    project_ref = host.split(".")[0]
    return f"https://supabase.com/dashboard/project/{project_ref}/sql/new"


def _missing_table_message() -> str:
    return (
        f"Table 'public.{SUPABASE_TABLE}' does not exist yet.\n\n"
        "Create it once, then rerun this script:\n"
        f"  1. Open {_sql_editor_url()}\n"
        f"  2. Paste the SQL from {SCHEMA_FILE}\n"
        "  3. Click Run\n"
        "  4. python push_data.py"
    )


def _rls_blocked_message() -> str:
    return (
        f"Row Level Security is blocking inserts into '{SUPABASE_TABLE}'.\n\n"
        "Run this in the SQL editor, then rerun the script:\n"
        f"  {_sql_editor_url()}\n\n"
        f"  alter table {SUPABASE_TABLE} disable row level security;\n"
        f"  grant select, insert on table {SUPABASE_TABLE} to anon, authenticated;"
    )


def _supabase_error_message(error: APIError) -> str:
    if error.code == "PGRST205":
        return _missing_table_message()
    if error.code == "42501":
        return _rls_blocked_message()
    return f"Supabase request failed: {error}"


def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    try:
        client.table(SUPABASE_TABLE).select("id").limit(1).execute()
    except APIError as e:
        raise ConnectionError(_supabase_error_message(e)) from e
    logger.info("Connected to Supabase table '%s'", SUPABASE_TABLE)
    return client


class NetworkDataExtract:
    def csv_to_json(self, file_path: str | Path) -> list[dict]:
        try:
            data = pd.read_csv(file_path)
            data.reset_index(drop=True, inplace=True)
            return json.loads(data.to_json(orient="records"))
        except Exception as e:
            raise NetworkSecurityException(e)

    def insert_data_supabase(
        self,
        records: list[dict],
        table: str,
        client: Client | None = None,
    ) -> int:
        try:
            supabase = client or get_supabase_client()
            inserted = 0
            for start in range(0, len(records), INSERT_BATCH_SIZE):
                batch = records[start : start + INSERT_BATCH_SIZE]
                supabase.table(table).insert(batch).execute()
                inserted += len(batch)
                logger.info("Inserted %s / %s records", inserted, len(records))
            return inserted
        except APIError as e:
            raise ConnectionError(_supabase_error_message(e)) from e
        except Exception as e:
            raise NetworkSecurityException(e)


if __name__ == "__main__":
    try:
        logger.info("SUPABASE_URL loaded: %s", bool(SUPABASE_URL))
        client = get_supabase_client()
        file_path = _csv_path()
        extractor = NetworkDataExtract()
        records = extractor.csv_to_json(file_path)
        logger.info("Converted %s records from %s", len(records), file_path)
        inserted = extractor.insert_data_supabase(
            records, SUPABASE_TABLE, client=client
        )
        logger.info("Inserted %s records into %s", inserted, SUPABASE_TABLE)
    except ConnectionError as e:
        logger.error("%s", e)
        sys.exit(1)
    except Exception as e:
        raise NetworkSecurityException(e)
