import re
import hashlib
from pathlib import Path
import pandas as pd
import streamlit as st


# -----------------------------
# APP CONFIGURATION
# -----------------------------
st.set_page_config(
    page_title="Axeom Studio Dashboard",
    page_icon="🎬",
    layout="wide"
)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "cleaned_data"
UPLOAD_DIR = BASE_DIR / "uploads"

REPORTING_DATE = pd.Timestamp("2026-10-06")


# -----------------------------
# DATA LOADING AND FILE UPLOADS
# -----------------------------
UPLOAD_DIR.mkdir(exist_ok=True)

DATASET_SCHEMAS = {
    "bookings": {"booking_id", "date", "client_name", "status"},
    "invoices": {"invoice_no", "bill_to", "due", "amount", "status"},
    "payments": {"payment_id", "date", "payer", "amount"},
    "leads": {"lead_id", "created", "business", "source", "status"},
    "production_board": {"video_id", "client", "title", "editor", "stage"},
    "team": {"name", "role", "joined", "pay"},
    "costs": {"item", "cost"}
}


def identify_dataset(filename, columns):
    stem = Path(filename).stem.lower()

    for dataset in DATASET_SCHEMAS:
        if stem == dataset or stem.endswith("_" + dataset):
            return dataset

    matches = [
        name
        for name, required in DATASET_SCHEMAS.items()
        if required.issubset(set(columns))
    ]

    return matches[0] if len(matches) == 1 else None


def clean_uploaded_csv(df):
    df = df.copy()

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
    )

    df = df.dropna(how="all")

    for column in df.select_dtypes(include="object").columns:
        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    return df.drop_duplicates()

# -----------------------------
# SAFE DATASET MERGING
# -----------------------------

RECORD_ID_COLUMNS = {
    "bookings": "booking_id",
    "invoices": "invoice_no",
    "payments": "payment_id",
    "leads": "lead_id",
    "production_board": "video_id",
    "team": "name",
    "costs": "item"
}


def merge_uploaded_dataset(dataset, existing_df, new_df):

    existing_df = clean_uploaded_csv(existing_df)
    new_df = clean_uploaded_csv(new_df)

    id_column = RECORD_ID_COLUMNS.get(dataset)

    if not id_column or id_column not in new_df.columns:
        combined = pd.concat(
            [existing_df, new_df],
            ignore_index=True,
            sort=False
        ).drop_duplicates()

        return combined, 0, 0, 0

    if existing_df.empty:
        return new_df.drop_duplicates(), len(new_df), 0, 0

    if id_column not in existing_df.columns:
        return existing_df, 0, 0, len(new_df)

    existing_df = existing_df.copy()
    new_df = new_df.copy()

    existing_df[id_column] = existing_df[id_column].astype(str).str.strip()
    new_df[id_column] = new_df[id_column].astype(str).str.strip()

    # Ignore blank IDs rather than treating all blank IDs
    # as the same record.
    valid_new = new_df[
        new_df[id_column].ne("")
        & new_df[id_column].ne("nan")
    ]

    blank_id_rows = new_df[
        ~(
            new_df[id_column].ne("")
            & new_df[id_column].ne("nan")
        )
    ]

    existing_by_id = existing_df.set_index(
        id_column,
        drop=False
    )

    additions = []
    conflicts = []
    duplicates = 0

    for _, new_row in valid_new.iterrows():

        record_id = new_row[id_column]

        if record_id not in existing_by_id.index:
            additions.append(new_row)
            continue

        old_rows = existing_by_id.loc[record_id]

        if isinstance(old_rows, pd.Series):
            old_rows = old_rows.to_frame().T

        same_record = False

        for _, old_row in old_rows.iterrows():

            old_values = old_row.reindex(new_row.index).fillna("").astype(str)
            new_values = new_row.fillna("").astype(str)

            if old_values.equals(new_values):
                same_record = True
                break

        if same_record:
            duplicates += 1

        else:
            conflicts.append(new_row)

    # Keep conflicting records separate for owner review.
    if conflicts:

        conflict_df = pd.DataFrame(conflicts)

        conflict_path = UPLOAD_DIR / "upload_conflicts.csv"

        if conflict_path.exists():

            previous_conflicts = pd.read_csv(conflict_path)

            conflict_df = pd.concat(
                [previous_conflicts, conflict_df],
                ignore_index=True,
                sort=False
            )

        conflict_df = conflict_df.drop_duplicates()

        conflict_df.to_csv(
            conflict_path,
            index=False
        )

    # Add only genuinely new records.
    additions_df = pd.DataFrame(additions)

    # Rows without IDs are retained, but cannot be safely
    # deduplicated by a record identifier.
    additions_df = pd.concat(
        [additions_df, blank_id_rows],
        ignore_index=True,
        sort=False
    )

    combined = pd.concat(
        [existing_df, additions_df],
        ignore_index=True,
        sort=False
    )

    combined = combined.drop_duplicates()

    return (
        combined,
        len(additions_df),
        duplicates,
        len(conflicts)
    )


def load_data():
    files = {}

    for dataset in DATASET_SCHEMAS:
        uploaded_path = UPLOAD_DIR / f"{dataset}.csv"
        original_path = DATA_DIR / f"{dataset}.csv"

        path = (
            uploaded_path
            if uploaded_path.exists()
            else original_path
        )

        if path.exists():
            files[dataset] = pd.read_csv(path)

    messages_path = UPLOAD_DIR / "messages.txt"

    if not messages_path.exists():
        messages_path = BASE_DIR / "data" / "messages.txt"

    if messages_path.exists():
        files["messages"] = messages_path.read_text(
            encoding="utf-8",
            errors="replace"
        )

    return files


# -----------------------------
# MAIN PAGE FILE UPLOAD
# -----------------------------

def get_file_hash(file_bytes):
    return hashlib.sha256(file_bytes).hexdigest()


# Remember processed files to prevent repeated uploads
# during Streamlit reruns.
if "processed_uploads" not in st.session_state:
    st.session_state.processed_uploads = set()


st.header("Update data")

uploaded_files = st.file_uploader(
    "Add new files",
    type=["csv", "txt"],
    accept_multiple_files=True,
    key="dataset_uploader"
)


if uploaded_files:

    for file in uploaded_files:

        try:

            file_bytes = file.getvalue()
            file_hash = get_file_hash(file_bytes)

            # Prevent processing the same file again
            # when Streamlit reruns the application.
            if file_hash in st.session_state.processed_uploads:
                st.info(
                f"{file.name}: already processed in this session."
                )
                continue

            # -----------------------------
            # TEXT FILES: APPEND MESSAGES
            # -----------------------------

            if file.name.lower().endswith(".txt"):

                messages = file_bytes.decode(
                    "utf-8",
                    errors="replace"
                ).strip()

                messages_path = UPLOAD_DIR / "messages.txt"

                # Preserve original messages if no uploaded
                # messages file exists yet.
                if messages_path.exists():

                    existing_messages = messages_path.read_text(
                        encoding="utf-8",
                        errors="replace"
                    )

                else:

                    original_messages = BASE_DIR / "data" / "messages.txt"

                    existing_messages = (
                        original_messages.read_text(
                            encoding="utf-8",
                            errors="replace"
                        )
                        if original_messages.exists()
                        else ""
                    )

                if messages and messages not in existing_messages:

                    combined_messages = (
                        existing_messages.rstrip()
                        + "\n\n"
                        + messages
                    )

                    messages_path.write_text(
                        combined_messages,
                        encoding="utf-8"
                    )

                    st.success(
                        f"Added messages from {file.name}"
                    )

                else:

                    st.info(
                        f"No new message content in {file.name}"
                    )

                st.session_state.processed_uploads.add(file_hash)

            # -----------------------------
            # CSV FILES: APPEND NEW RECORDS
            # -----------------------------

            elif file.name.lower().endswith(".csv"):

                df = pd.read_csv(
                    pd.io.common.BytesIO(file_bytes)
                )

                df = clean_uploaded_csv(df)

                dataset = identify_dataset(
                    file.name,
                    df.columns
                )

                if dataset is None:

                    st.error(
                        f"Could not identify dataset: {file.name}"
                    )

                    continue

                missing = (
                    DATASET_SCHEMAS[dataset]
                    - set(df.columns)
                )

                if missing:

                    st.error(
                        f"{file.name} is missing: "
                        f"{', '.join(sorted(missing))}"
                    )

                    continue

                uploaded_path = UPLOAD_DIR / f"{dataset}.csv"
                original_path = DATA_DIR / f"{dataset}.csv"

                # Read the current dataset, preserving
                # previously uploaded records.
                if uploaded_path.exists():

                    existing_df = pd.read_csv(uploaded_path)

                elif original_path.exists():

                    existing_df = pd.read_csv(original_path)

                else:

                    existing_df = pd.DataFrame()

                existing_df = clean_uploaded_csv(existing_df)

                old_count = len(existing_df)

                # Combine old and new records.
                  # Safely merge incoming records with existing data.
                (
                    combined_df,
                     added_count,
                     duplicate_count,
                     conflict_count
                    ) = merge_uploaded_dataset(
                       dataset,
                        existing_df,
                      df
                    )

                combined_df.to_csv(
                    uploaded_path,
                    index=False
                )

                st.session_state.processed_uploads.add(file_hash)

                st.success(
                    f"{dataset}: {added_count} new records added. "
                    f"{duplicate_count} duplicates ignored. "
                    f"Total records: {len(combined_df)}"
                )

                if conflict_count:

                    st.warning(
                        f"{conflict_count} conflicting records "
                        "were saved for owner review. "
                        "Existing records were not overwritten."
                    )


               
               

        except Exception as error:

            st.error(
                f"Could not process {file.name}: {error}"
            )


# Load data after uploads
data = load_data()


st.sidebar.divider()
st.sidebar.subheader("Loaded datasets")

for dataset, df in data.items():

    if isinstance(df, pd.DataFrame):
        st.sidebar.caption(
            f"{dataset}: {len(df)} records"
        )

    else:
        st.sidebar.caption(
            f"{dataset}: loaded"
        )
# -----------------------------
# CLIENT MATCHING
# -----------------------------

mapping_path = BASE_DIR / "master_client_mapping.csv"

DECISIONS_PATH = BASE_DIR / "client_review_decisions.csv"

DECISION_COLUMNS = [
    "dataset",
    "normalized_name",
    "decision",
    "canonical_client_id"
]


# -----------------------------
# LOAD OWNER DECISIONS
# -----------------------------

if DECISIONS_PATH.exists():

    client_decisions = pd.read_csv(
        DECISIONS_PATH
    ).fillna("")

    # Ensure all required columns exist
    for column in DECISION_COLUMNS:

        if column not in client_decisions.columns:
            client_decisions[column] = ""

    client_decisions = client_decisions[
        DECISION_COLUMNS
    ]

else:

    client_decisions = pd.DataFrame(
        columns=DECISION_COLUMNS
    )


def save_client_decisions(decisions):

    decisions[DECISION_COLUMNS].to_csv(
        DECISIONS_PATH,
        index=False
    )


# -----------------------------
# LOAD MASTER CLIENT MAPPING
# -----------------------------

if mapping_path.exists():

    client_mapping = pd.read_csv(
        mapping_path
    ).fillna("")

else:

    client_mapping = pd.DataFrame()


def normalize_name(value):

    if pd.isna(value):
        return ""

    value = str(value).lower().strip()

    return re.sub(r"\s+", " ", value)


# -----------------------------
# SOURCE COLUMNS
# -----------------------------

SOURCE_COLUMNS = {

    "bookings": ["client_name"],

    "invoices": ["bill_to"],

    "payments": ["payer"],

    "leads": ["business", "name"],

    "production_board": ["client"]

}


RECORD_ID_COLUMNS = {

    "bookings": "booking_id",

    "invoices": "invoice_no",

    "payments": "payment_id",

    "leads": "lead_id",

    "production_board": "video_id"

}


# -----------------------------
# BUILD CLIENT LOOKUP
# -----------------------------

def build_client_lookup(dataset):

    """
    Start with verified master mappings.

    Apply owner decisions afterward.

    APPROVED:
        Connect the name to the selected client.

    REJECTED:
        Prevent automatic matching for that name.
    """

    if client_mapping.empty:
        return {}

    required = {
        "source_file",
        "normalized_name",
        "canonical_client_id",
        "review_status"
    }

    if not required.issubset(
        client_mapping.columns
    ):
        return {}

    source_rows = client_mapping[
        (
            client_mapping["source_file"]
            .astype(str)
            .str.lower()
            == f"{dataset}.csv"
        )
        &
        (
            client_mapping["review_status"].isin([
                "VERIFIED_MERGE",
                "VERIFIED_RELATIONSHIP"
            ])
        )
    ]

    possible_matches = {}

    for _, row in source_rows.iterrows():

        name = normalize_name(
            row["normalized_name"]
        )

        client_id = str(
            row["canonical_client_id"]
        ).strip()

        if not name or not client_id:
            continue

        possible_matches.setdefault(
            name,
            set()
        ).add(client_id)


    # Keep only unambiguous automatic matches
    final_lookup = {

        name: next(iter(client_ids))

        for name, client_ids in possible_matches.items()

        if len(client_ids) == 1

    }


    # Get decisions for this dataset
    dataset_decisions = client_decisions[
        client_decisions["dataset"].astype(str)
        == dataset
    ]


    # Validate canonical client IDs
    valid_client_ids = set(
        client_mapping["canonical_client_id"]
        .astype(str)
        .str.strip()
    )


    # -----------------------------
    # APPLY REJECTIONS FIRST
    # -----------------------------

    for _, decision in dataset_decisions.iterrows():

        if str(decision["decision"]).upper() == "REJECTED":

            name = normalize_name(
                decision["normalized_name"]
            )

            if name:
                final_lookup.pop(name, None)


    # -----------------------------
    # APPLY APPROVALS
    # -----------------------------

    for _, decision in dataset_decisions.iterrows():

        if str(decision["decision"]).upper() == "APPROVED":

            name = normalize_name(
                decision["normalized_name"]
            )

            client_id = str(
                decision["canonical_client_id"]
            ).strip()

            if (
                name
                and client_id
                and client_id in valid_client_ids
            ):

                final_lookup[name] = client_id


    return final_lookup


# -----------------------------
# ATTACH CANONICAL CLIENT IDS
# -----------------------------


def attach_client_ids(dataset, df):

    if df.empty or dataset not in SOURCE_COLUMNS:
        return df

    lookup = build_client_lookup(dataset)

    columns = SOURCE_COLUMNS[dataset]

    def find_client(row):

        # Leads: use business name first.
        # Only use contact name if business is missing.
        if dataset == "leads":

            business = normalize_name(
                row.get("business", "")
            )

            contact = normalize_name(
                row.get("name", "")
            )

            name = business if business else contact

            return lookup.get(name, "")

        # Other datasets
        matched_ids = set()

        for column in columns:

            if column in df.columns:

                name = normalize_name(
                    row.get(column, "")
                )

                if name in lookup:
                    matched_ids.add(lookup[name])

        # Never guess if multiple clients match
        if len(matched_ids) == 1:
            return next(iter(matched_ids))

        return ""

    df = df.copy()

    df["canonical_client_id"] = df.apply(
        find_client,
        axis=1
    )

    return df


# Apply matching to loaded datasets
for dataset in SOURCE_COLUMNS:

    if dataset in data:

        data[dataset] = attach_client_ids(
            dataset,
            data[dataset]
        )
# -----------------------------
# FIND UNLINKED CLIENT RECORDS
# -----------------------------

def get_unlinked_records():

    records = []

    for dataset, name_columns in SOURCE_COLUMNS.items():

        df = data.get(
            dataset,
            pd.DataFrame()
        )

        if (
            df.empty
            or "canonical_client_id" not in df.columns
        ):
            continue

        id_column = RECORD_ID_COLUMNS[dataset]

        for _, row in df.iterrows():

            if str(
                row.get("canonical_client_id", "")
            ).strip():

                continue

            names = []

            for column in name_columns:

                if column in df.columns:

                    value = str(
                        row.get(column, "")
                    ).strip()

                    if value and value.lower() != "nan":

                        names.append(value)

            if not names:
                continue


            # For leads, use business as the
            # primary client name.
            # If business is missing, use contact name.
            if dataset == "leads":

                primary_name = str(
                    row.get("business", "")
                ).strip()

                if (
                    not primary_name
                    or primary_name.lower() == "nan"
                ):

                    primary_name = str(
                        row.get("name", "")
                    ).strip()

            else:

                primary_name = names[0]


            normalized = normalize_name(
                primary_name
            )

            if not normalized:
                continue

            records.append({

                "dataset": dataset,

                "record_id": row.get(
                    id_column,
                    ""
                ),

                "client_name": " / ".join(
                    dict.fromkeys(names)
                ),

                "normalized_name": normalized

            })


    if not records:

        return pd.DataFrame(
            columns=[
                "dataset",
                "normalized_name",
                "client_name",
                "records"
            ]
        )


    result = pd.DataFrame(records)

    return (
        result.groupby(
            ["dataset", "normalized_name"],
            as_index=False
        )
        .agg(
            client_name=("client_name", "first"),
            records=("record_id", "count")
        )
        .sort_values(
            ["dataset", "client_name"]
        )
    )


unlinked_records = get_unlinked_records()


# -----------------------------
# CLIENT DIRECTORY HELPERS
# -----------------------------

def get_client_records(client_id):

    if client_mapping.empty:
        return set()

    group = client_mapping[
        client_mapping["canonical_client_id"].astype(str)
        == str(client_id)
    ]

    aliases = set()

    for column in [
        "original_name",
        "normalized_name"
    ]:

        if column in group.columns:

            aliases.update(

                normalize_name(value)

                for value in group[column].dropna()

                if str(value).strip()

            )

    return aliases


def filter_client_records(
    df,
    columns,
    aliases,
    client_id=None
):

    if df.empty:
        return df

    # Prefer canonical IDs
    if (
        client_id is not None
        and "canonical_client_id" in df.columns
    ):

        return df[
            df["canonical_client_id"].astype(str)
            == str(client_id)
        ]


    # Fallback to exact normalized names
    result = pd.Series(
        False,
        index=df.index
    )

    for column in columns:

        if column in df.columns:

            result |= (
                df[column]
                .fillna("")
                .astype(str)
                .apply(normalize_name)
                .isin(aliases)
            )

    return df[result]


# -----------------------------
# DASHBOARD HEADER
# -----------------------------

st.title("🎬 Axeom Studio")

st.caption(
    "Business operations dashboard | "
    "Reporting date: October 6, 2026"
)

st.divider()

# -----------------------------
# FINANCIAL RECONCILIATION
# -----------------------------
invoices = data.get(
    "invoices",
    pd.DataFrame()
)
payments = data.get(
    "payments",
    pd.DataFrame()
)

finance_summary = {
    "invoice_total": 0,
    "paid_invoice_total": 0,
    "unpaid_invoice_total": 0,
    "partial_invoice_total": 0,
    "payment_total": 0,
    "matched_payment_total": 0,
    "unmatched_payment_total": 0,
    "paid_without_reference": 0,
    "unpaid_with_payment": 0
}

if not invoices.empty:

    finance = invoices.copy()

    finance["amount"] = pd.to_numeric(
        finance["amount"],
        errors="coerce"
    ).fillna(0)

    finance["status"] = (
        finance["status"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    finance_summary["invoice_total"] = finance["amount"].sum()

    finance_summary["paid_invoice_total"] = finance.loc[
        finance["status"] == "paid", "amount"
    ].sum()

    finance_summary["unpaid_invoice_total"] = finance.loc[
        finance["status"] == "unpaid", "amount"
    ].sum()

    finance_summary["partial_invoice_total"] = finance.loc[
        finance["status"] == "partial", "amount"
    ].sum()


if not payments.empty and not invoices.empty:

    payment_data = payments.copy()

    payment_data["amount"] = pd.to_numeric(
        payment_data["amount"],
        errors="coerce"
    ).fillna(0)

    finance_summary["payment_total"] = (
        payment_data["amount"].sum()
    )

    # Match payments using explicit invoice references only.
    invoice_numbers = set(
        invoices["invoice_no"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    payment_data["reference"] = (
        payment_data["reference"]
        .fillna("")
        .astype(str)
        .str.strip()
        if "reference" in payment_data.columns
        else ""
    )

    payment_data["matched"] = (
        payment_data["reference"].isin(invoice_numbers)
    )

    finance_summary["matched_payment_total"] = (
        payment_data.loc[
            payment_data["matched"], "amount"
        ].sum()
    )

    finance_summary["unmatched_payment_total"] = (
        payment_data.loc[
            ~payment_data["matched"], "amount"
        ].sum()
    )

    matched_invoice_numbers = set(
        payment_data.loc[
            payment_data["matched"], "reference"
        ]
    )

    finance_summary["paid_without_reference"] = len(
        invoices[
            (invoices["status"].astype(str).str.lower() == "paid")
            & (~invoices["invoice_no"].astype(str).isin(
                matched_invoice_numbers
            ))
        ]
    )

    finance_summary["unpaid_with_payment"] = len(
        invoices[
            (invoices["status"].astype(str).str.lower() == "unpaid")
            & (invoices["invoice_no"].astype(str).isin(
                matched_invoice_numbers
            ))
        ]
    )
# -----------------------------
# INVOICE-LEVEL RECONCILIATION
# -----------------------------

invoice_reconciliation = pd.DataFrame()

if not invoices.empty and not payments.empty:

    invoice_check = invoices.copy()
    payment_check = payments.copy()

    invoice_check["amount"] = pd.to_numeric(
        invoice_check["amount"],
        errors="coerce"
    ).fillna(0)

    payment_check["amount"] = pd.to_numeric(
        payment_check["amount"],
        errors="coerce"
    ).fillna(0)

    invoice_check["invoice_no"] = (
        invoice_check["invoice_no"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    if "reference" in payment_check.columns:

        payment_check["reference"] = (
            payment_check["reference"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        matched_payments = (
            payment_check[
                payment_check["reference"].isin(
                    invoice_check["invoice_no"]
                )
            ]
            .groupby("reference")["amount"]
            .sum()
            .reset_index()
            .rename(columns={
                "reference": "invoice_no",
                "amount": "matched_payment_amount"
            })
        )

    else:

        matched_payments = pd.DataFrame(
            columns=[
                "invoice_no",
                "matched_payment_amount"
            ]
        )

    invoice_reconciliation = invoice_check[
        ["invoice_no", "bill_to", "amount", "status"]
    ].merge(
        matched_payments,
        on="invoice_no",
        how="left"
    )

    invoice_reconciliation["matched_payment_amount"] = (
        invoice_reconciliation["matched_payment_amount"]
        .fillna(0)
    )

    invoice_reconciliation["difference"] = (
        invoice_reconciliation["amount"]
        - invoice_reconciliation["matched_payment_amount"]
    )
    # -----------------------------
# POTENTIAL UNBILLED BOOKINGS
# -----------------------------

booking_billing_review = pd.DataFrame()

bookings = data.get(
    "bookings",
    pd.DataFrame()
)

if not bookings.empty and not invoices.empty:

    booking_check = bookings.copy()
    invoice_check = invoices.copy()

    # Extract booking references from invoice memos.
    invoiced_booking_ids = set()

    if "memo" in invoice_check.columns:

        for memo in invoice_check["memo"].fillna("").astype(str):

            references = re.findall(
                r"B\d{3}",
                memo.upper()
            )

            invoiced_booking_ids.update(references)

    # Find completed bookings without an explicit
    # booking reference in any invoice memo.
    booking_check["price"] = pd.to_numeric(
        booking_check["price"],
        errors="coerce"
    ).fillna(0)

    booking_check["booking_id"] = (
        booking_check["booking_id"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    completed = booking_check[
        booking_check["status"]
        .astype(str)
        .str.lower()
        .eq("completed")
    ].copy()

    booking_billing_review = completed[
        ~completed["booking_id"].isin(invoiced_booking_ids)
    ].copy()

    booking_billing_review["review_reason"] = (
        "No explicit booking reference found in invoice memos"
    )

    booking_billing_review["billing_review"] = (
        booking_billing_review["price"].apply(
            lambda price:
                "Check retainer or bundled billing"
                if price == 0
                else "Check whether separately invoiced"
        )
    )
     
    def reconciliation_status(row):

        status = str(row["status"]).lower().strip()

        if row["matched_payment_amount"] == 0:
            if status == "paid":
                return "Paid status — no matched reference"
            return "No matched payment reference"

        if row["difference"] < 0:
            return "Matched payments exceed invoice"

        if row["difference"] == 0:
            return "Fully matched by reference"

        return "Partially matched by reference"

    invoice_reconciliation["reconciliation_result"] = (
        invoice_reconciliation.apply(
            reconciliation_status,
            axis=1
        )
    )
    
# -----------------------------
# MONDAY PRIORITIES
# -----------------------------

st.header("Monday priorities")

invoices = data.get(
    "invoices",
    pd.DataFrame()
)

production = data.get(
    "production_board",
    pd.DataFrame()
)

leads = data.get(
    "leads",
    pd.DataFrame()
)


 overdue_count = 0
overdue_amount = 0
reconciled_overdue_count = 0
reconciled_overdue_amount = 0

if (
    not invoices.empty
    and {"due", "amount", "status", "invoice_no"}.issubset(invoices.columns)
):

    invoices = invoices.copy()

    invoices["due"] = pd.to_datetime(
        invoices["due"],
        errors="coerce"
    )

    invoices["amount"] = pd.to_numeric(
        invoices["amount"],
        errors="coerce"
    ).fillna(0)

    invoices["invoice_no"] = (
        invoices["invoice_no"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    overdue = invoices[
        (invoices["due"] < REPORTING_DATE)
        &
        (
            invoices["status"]
            .astype(str)
            .str.lower()
            .str.strip()
            .isin(["unpaid", "partial"])
        )
    ].copy()

    overdue_count = len(overdue)
    overdue_amount = overdue["amount"].sum()

    overdue["matched_payment_amount"] = 0

    if not invoice_reconciliation.empty:

        payment_matches = invoice_reconciliation[
            ["invoice_no", "matched_payment_amount"]
        ].copy()

        overdue = overdue.drop(
            columns=["matched_payment_amount"]
        ).merge(
            payment_matches,
            on="invoice_no",
            how="left"
        )

    overdue["matched_payment_amount"] = (
        overdue["matched_payment_amount"]
        .fillna(0)
    )

    overdue["remaining_balance"] = (
        overdue["amount"]
        - overdue["matched_payment_amount"]
    ).clip(lower=0)

    outstanding = overdue[
        overdue["remaining_balance"] > 0
    ]

    reconciled_overdue_count = len(outstanding)

    reconciled_overdue_amount = (
        outstanding["remaining_balance"].sum()
    )


pending_videos = 0

if (
    not production.empty
    and "stage" in production.columns
):

    pending_videos = len(
        production[
            production["stage"]
            .astype(str)
            .str.lower()
            != "delivered"
        ]
    )


unanswered_leads = 0

if (
    not leads.empty
    and "first_reply" in leads.columns
):

    unanswered_leads = (
        leads["first_reply"].isna()
        |
        leads["first_reply"]
        .astype(str)
        .str.strip()
        .eq("")
    ).sum()


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Status-based overdue",
    overdue_count,
    help="Invoices marked unpaid or partial with a due date before the reporting date."
)

col1.caption(
    f"Invoice face value: ${overdue_amount:,.0f}"
)

col2.metric(
    "Reconciled outstanding",
    reconciled_overdue_count,
    help="Overdue invoice balances after deducting payments matched by exact invoice reference."
)

col2.caption(
    f"Remaining balance: ${reconciled_overdue_amount:,.0f}"
)

col3.metric(
    "Videos not delivered",
    pending_videos
)

col4.metric(
    "Leads without reply date",
    unanswered_leads
)

st.caption(
    "Reconciled figures use exact invoice-number payment references. "
    "Unreferenced payments are not automatically allocated."
)

st.divider()


# -----------------------------
# NAVIGATION
# -----------------------------

st.header("Operations")

tab1, tab2, tab3, tab4 = st.tabs([
    "Clients",
    "Money",
    "Production",
    "Leads"
])

# -----------------------------
# CLIENT DIRECTORY
# -----------------------------

with tab1:

    st.subheader("Client directory")

    required_client_columns = {

        "canonical_client_id",

        "canonical_client_name"

    }

    if (
        client_mapping.empty
        or not required_client_columns.issubset(
            client_mapping.columns
        )
    ):

        st.warning(
            "Master client mapping not found "
            "or missing required columns."
        )

    else:

        clients = (

            client_mapping[
                [
                    "canonical_client_id",
                    "canonical_client_name"
                ]
            ]

            .drop_duplicates()

            .sort_values(
                "canonical_client_name"
            )
         
        )
        st.metric("Total clients", len(clients))


        selected = st.selectbox(

            "Select a client",

            clients["canonical_client_id"].tolist(),

            format_func=lambda x: clients.loc[

                clients["canonical_client_id"] == x,

                "canonical_client_name"

            ].iloc[0]

        )


        group = client_mapping[
            client_mapping["canonical_client_id"]
            == selected
        ]

        aliases = get_client_records(selected)


        st.markdown(
            f"### {group['canonical_client_name'].iloc[0]}"
        )


        st.write("**Other names used:**")

        st.write(

            ", ".join(
                sorted(set(group["original_name"]) - {""})
            )

            if "original_name" in group.columns

            else "Not available"

        )


        st.write("**Email addresses:**")

        st.write(

            ", ".join(
                sorted(set(group["email"]) - {""})
            )

            if "email" in group.columns

            else "Not available"

        )


        st.write("**Mapping review status:**")

        st.write(

            ", ".join(
                sorted(set(group["review_status"]) - {""})
            )

            if "review_status" in group.columns

            else "Not available"

        )


        st.divider()


        sections = [

            ("Bookings", "bookings", ["client_name"]),

            ("Invoices", "invoices", ["bill_to"]),

            ("Payments", "payments", ["payer"]),

            ("Leads", "leads", ["business", "name"]),

            ("Production", "production_board", ["client"])

        ]


        for title, key, columns in sections:

            st.markdown(
                f"#### {title}"
            )

            df = data.get(
                key,
                pd.DataFrame()
            )

            matched = filter_client_records(
                df,
                columns,
                aliases,
                selected
            )

            if matched.empty:

                st.caption(
                    "No directly linked records."
                )

            else:

                st.dataframe(
                    matched,
                    use_container_width=True
                )
                
    # -----------------------------
    # NEEDS ATTENTION
    # -----------------------------

    st.divider()

    st.subheader("Needs attention")

    st.caption(
        "These records could not be confidently linked "
        "to an existing client. Review the reason before "
        "making any matching decisions."
    )

    reviewed = set(
        zip(
            client_decisions["dataset"].astype(str),
            client_decisions["normalized_name"].astype(str)
        )
    )

    if unlinked_records.empty:
        pending_reviews = unlinked_records
    else:
        pending_reviews = unlinked_records[
            ~unlinked_records.apply(
                lambda row: (
                    row["dataset"],
                    row["normalized_name"]
                ) in reviewed,
                axis=1
            )
        ]

    if pending_reviews.empty:

        st.success("No unresolved client records.")

    else:

        st.metric(
            "Records requiring attention",
            len(pending_reviews)
        )

        def explain_matching_problem(row):

            if client_mapping.empty:
                return (
                    "Mapping unavailable",
                    "Check the master client mapping."
                )

            matches = client_mapping[
                (
                    client_mapping["source_file"]
                    .astype(str).str.lower()
                    == f"{row['dataset']}.csv"
                )
                &
                (
                    client_mapping["normalized_name"]
                    .apply(normalize_name)
                    == row["normalized_name"]
                )
            ]

            if matches.empty:
                return (
                    "No mapping entry",
                    "Verify the business identity manually."
                )

            statuses = sorted(
                set(matches["review_status"].astype(str)) - {""}
            )

            explanations = {
                "REVIEW_REQUIRED_SHARED_EMAIL": (
                    "Shared email",
                    "Multiple businesses may use this email. "
                    "Verify their identities before linking."
                ),
                "REVIEW_REQUIRED_POSSIBLE_DUPLICATE": (
                    "Possible duplicate",
                    "Check whether this name belongs to "
                    "an existing client."
                ),
                "REVIEW_REQUIRED_BOTH": (
                    "Multiple concerns",
                    "Shared-email and possible-duplicate "
                    "concerns require verification."
                ),
                "PROVISIONAL": (
                    "Provisional match",
                    "The relationship has not been verified. "
                    "Check the client identity."
                )
            }

            problems = [
                explanations[status]
                for status in statuses
                if status in explanations
            ]

            if not problems:
                return (
                    ", ".join(statuses) if statuses
                    else "Unverified match",
                    "Review the source record manually."
                )

            if len(problems) == 1:
                return problems[0]

            return (
                "Multiple concerns",
                " ".join(problem[1] for problem in problems)
            )

        # Table headings
        header = st.columns([1.1, 1.5, 0.6, 1.4, 2.5])

        header[0].markdown("**Dataset**")
        header[1].markdown("**Record name**")
        header[2].markdown("**Count**")
        header[3].markdown("**Problem**")
        header[4].markdown("**Recommended action**")

        st.divider()

        for _, row in pending_reviews.iterrows():

            problem, recommendation = explain_matching_problem(row)

            columns = st.columns([1.1, 1.5, 0.6, 1.4, 2.5])

            columns[0].write(row["dataset"])
            columns[1].write(row["client_name"])
            columns[2].write(int(row["records"]))
            columns[3].write(problem)
            columns[4].write(recommendation)

            st.divider()

    # -----------------------------
    # REVIEW HISTORY
    # -----------------------------

    with st.expander("Previously reviewed decisions"):

        if client_decisions.empty:

            st.caption("No decisions have been made yet.")

        else:

            st.dataframe(
                client_decisions,
                use_container_width=True,
                hide_index=True
            )

            for index, decision in client_decisions.iterrows():

                col1, col2 = st.columns([4, 1])

                col1.write(
                    f"**{decision['normalized_name']}** — "
                    f"{decision['dataset']} — "
                    f"{decision['decision']}"
                )

                if col2.button(
                    "Undo",
                    key=f"undo_{index}"
                ):

                    client_decisions = client_decisions.drop(
                        index
                    ).reset_index(drop=True)

                    save_client_decisions(client_decisions)

                    st.rerun()


    # -----------------------------
    # UPLOAD CONFLICTS
    # -----------------------------

    conflict_path = UPLOAD_DIR / "upload_conflicts.csv"

    if conflict_path.exists():

        conflicts = pd.read_csv(conflict_path).fillna("")

        with st.expander(
            f"Upload conflicts requiring review ({len(conflicts)})"
        ):

            st.warning(
                "These incoming records have an existing ID "
                "but different data. Original records were preserved."
            )

            st.dataframe(
                conflicts,
                use_container_width=True,
                hide_index=True
            )

# -----------------------------
# MONEY
# -----------------------------

with tab2:

    st.subheader("Financial overview")

    # Financial summary metrics
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total invoiced",
        f"${finance_summary['invoice_total']:,.2f}"
    )

    col2.metric(
        "Recorded as paid",
        f"${finance_summary['paid_invoice_total']:,.2f}"
    )

    col3.metric(
        "Recorded as unpaid",
        f"${finance_summary['unpaid_invoice_total']:,.2f}"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Partial invoices",
        f"${finance_summary['partial_invoice_total']:,.2f}"
    )

    col2.metric(
        "Payments received",
        f"${finance_summary['payment_total']:,.2f}"
    )

    col3.metric(
        "Payments without invoice reference",
        f"${finance_summary['unmatched_payment_total']:,.2f}"
    )

    st.divider()

    # Reconciliation warnings
    st.subheader("Reconciliation checks")

    col1, col2 = st.columns(2)

    col1.metric(
        "Paid invoices without matched payment reference",
        finance_summary["paid_without_reference"]
    )

    col2.metric(
        "Unpaid invoices with matched payment reference",
        finance_summary["unpaid_with_payment"]
    )

    st.warning(
        "These are reconciliation exceptions, not confirmed "
        "accounting errors. Some payments may be bulk payments, "
        "and some invoice statuses may not have been updated."
    )

    st.divider()

    # Invoice records
    st.subheader("Invoice register")

    if not invoices.empty:

        st.dataframe(
            invoices,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No invoice data found.")

    st.divider()
    st.divider()

# Invoice-level reconciliation
st.subheader("Invoice-level reconciliation")
st.divider()

st.subheader("Potential unbilled bookings")

if not booking_billing_review.empty:

    st.metric(
        "Bookings without explicit invoice references",
        len(booking_billing_review)
    )

    st.metric(
        "Associated booking value",
        f"${booking_billing_review['price'].sum():,.2f}"
    )

    st.warning(
        "These bookings have no explicit booking ID in invoice "
        "memos. This does not prove they are unbilled. "
        "Check retainers, bundled invoices, and invoices "
        "without booking references."
    )

    st.dataframe(
        booking_billing_review[
            [
                "booking_id",
                "client_name",
                "service",
                "price",
                "review_reason",
                "billing_review"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

else:

    st.success(
        "All completed bookings have explicit invoice references."
    )
if not invoice_reconciliation.empty:

    st.caption(
        "Only exact invoice-number references are matched. "
        "Other payments remain unallocated."
    )

    st.dataframe(
        invoice_reconciliation,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "Invoice-level reconciliation is unavailable. "
        "Check that invoice and payment data are loaded."
    )
    # Payment records
    st.subheader("Payment register")

    if not payments.empty:

        st.dataframe(
            payments,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No payment data found.")

# -----------------------------
# PRODUCTION
# -----------------------------

with tab3:

    st.subheader("Production board")

    if not production.empty:

        st.dataframe(
            production,
            use_container_width=True
        )

    else:

        st.warning(
            "No production data found."
        )


# -----------------------------
# LEADS
# -----------------------------

with tab4:

    st.subheader("Lead pipeline")

    if not leads.empty:

        st.dataframe(
            leads,
            use_container_width=True
        )

    else:

        st.warning(
            "No lead data found."
        )


 
# -----------------------------
# FOOTER
# -----------------------------

st.caption(
    "Axeom internal operations | "
    "Recommendations require owner approval."
)                                