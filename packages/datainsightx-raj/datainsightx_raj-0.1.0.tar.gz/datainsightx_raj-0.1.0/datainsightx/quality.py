# datainsightx/quality.py

import pandas as pd
import numpy as np
from pandas.api import types as ptypes
from typing import Dict, Any, Tuple

def missing_value_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns columns with missing values and their counts + percentages.
    """
    missing_count = df.isnull().sum()
    missing_percent = (missing_count / len(df)) * 100
    report = pd.DataFrame({
        'Missing Values': missing_count,
        'Percentage': missing_percent.round(2)
    })
    report = report[report['Missing Values'] > 0].sort_values(by='Percentage', ascending=False)
    return report


def duplicate_report(df: pd.DataFrame, subset: list = None, keep: str = 'first') -> pd.DataFrame:
    """
    Detect duplicates in the DataFrame.

    Parameters:
        df: pandas DataFrame
        subset: list of columns to consider for duplicate detection. If None, use all columns.
        keep: 'first' or 'last' — which duplicate to keep (pandas' drop_duplicates semantics).

    Returns:
        A DataFrame with:
            - total_rows: total rows in original df
            - duplicate_count: number of rows that are duplicates (excluding the kept one)
            - duplicate_percent: percentage of duplicate rows
        and sample duplicated rows (up to 5) as extra info in a dict-like structure.
    """
    total_rows = len(df)
    if subset is None:
        subset = df.columns.tolist()

    # boolean Series where True indicates a duplicate row (according to subset)
    duplicates_mask = df.duplicated(subset=subset, keep=keep)
    duplicate_count = int(duplicates_mask.sum())
    duplicate_percent = round((duplicate_count / total_rows) * 100, 2) if total_rows > 0 else 0.0

    # sample up to 5 duplicated rows for inspection
    sample_duplicates = df[duplicates_mask].head(5).copy()

    summary = pd.DataFrame({
        'total_rows': [total_rows],
        'duplicate_count': [duplicate_count],
        'duplicate_percent': [duplicate_percent]
    })

    # Attach sample as attribute for convenience (not typical for DataFrames but handy here)
    summary.attrs['sample_duplicates'] = sample_duplicates

    return summary


def validate_schema(df: pd.DataFrame, expected_schema: Dict[str, str]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Validate that DataFrame columns and dtypes match an expected schema.

    Parameters:
        df: pandas DataFrame
        expected_schema: dict mapping column_name -> expected_type_string
            example: {'id': 'int', 'name': 'str', 'price': 'float'}

    Returns:
        (report_df, details)
        report_df: DataFrame with rows for each expected column showing status.
        details: dict with 'missing_columns', 'extra_columns', and 'type_mismatches' for easy programmatic use.
    """
    # Normalize inputs
    expected_cols = set(expected_schema.keys())
    actual_cols = set(df.columns.tolist())

    missing_columns = list(expected_cols - actual_cols)
    extra_columns = list(actual_cols - expected_cols)

    rows = []
    type_mismatches = {}

    for col, exp_type in expected_schema.items():
        if col not in df.columns:
            rows.append({
                'column': col,
                'expected_type': exp_type,
                'actual_type': None,
                'status': 'missing'
            })
            continue

        actual_series = df[col]
        actual_type = str(actual_series.dtype)

        # Use pandas type checks for common categories
        match = False
        exp = exp_type.lower()
        if exp in ('int', 'integer'):
            match = ptypes.is_integer_dtype(actual_series.dropna())
        elif exp in ('float', 'double'):
            match = ptypes.is_float_dtype(actual_series.dropna())
        elif exp in ('str', 'string', 'object'):
            match = ptypes.is_string_dtype(actual_series.dropna()) or ptypes.is_object_dtype(actual_series.dropna())
        elif exp in ('bool', 'boolean'):
            match = ptypes.is_bool_dtype(actual_series.dropna())
        elif exp in ('datetime', 'datetime64'):
            match = ptypes.is_datetime64_any_dtype(actual_series.dropna())
        elif exp == 'numeric':
            match = ptypes.is_numeric_dtype(actual_series.dropna())
        else:
            # fallback: compare dtype names directly
            match = exp in actual_type

        status = 'ok' if match else 'type_mismatch'
        rows.append({
            'column': col,
            'expected_type': exp_type,
            'actual_type': actual_type,
            'status': status
        })
        if status == 'type_mismatch':
            type_mismatches[col] = {'expected': exp_type, 'actual': actual_type}

    report_df = pd.DataFrame(rows).set_index('column')

    details = {
        'missing_columns': missing_columns,
        'extra_columns': extra_columns,
        'type_mismatches': type_mismatches
    }

    return report_df, details


def compare_datasets(df_ref: pd.DataFrame, df_new: pd.DataFrame, numeric_threshold: float = 0.1) -> Dict[str, Any]:
    """
    Compare two datasets (reference vs new) to detect data drift.

    For numeric columns: compute mean and std differences and relative change in mean.
    For categorical columns: compute total variation distance between category distributions.

    Parameters:
        df_ref: reference DataFrame (older or baseline)
        df_new: new DataFrame to compare
        numeric_threshold: relative change threshold (as a fraction) to mark 'significant drift' in mean.

    Returns:
        A dictionary with per-column drift metrics and a summary.
    """
    cols = set(df_ref.columns).intersection(set(df_new.columns))
    numeric_cols = []
    categorical_cols = []

    for c in cols:
        if ptypes.is_numeric_dtype(df_ref[c]) and ptypes.is_numeric_dtype(df_new[c]):
            numeric_cols.append(c)
        else:
            categorical_cols.append(c)

    numeric_report = {}
    for c in numeric_cols:
        # drop NA for stats
        a = df_ref[c].dropna().astype(float)
        b = df_new[c].dropna().astype(float)

        if len(a) == 0 or len(b) == 0:
            numeric_report[c] = {'note': 'not enough data'}
            continue

        mean_a, std_a = float(a.mean()), float(a.std(ddof=0))
        mean_b, std_b = float(b.mean()), float(b.std(ddof=0))

        # relative mean change (avoid div by zero)
        if abs(mean_a) < 1e-9:
            rel_change = float('inf') if mean_b != 0 else 0.0
        else:
            rel_change = abs((mean_b - mean_a) / mean_a)

        numeric_report[c] = {
            'ref_mean': round(mean_a, 6),
            'ref_std': round(std_a, 6),
            'new_mean': round(mean_b, 6),
            'new_std': round(std_b, 6),
            'relative_mean_change': round(rel_change, 6),
            'drift_flag': rel_change > numeric_threshold
        }

    categorical_report = {}
    for c in categorical_cols:
        a = df_ref[c].fillna('__MISSING__').astype(str)
        b = df_new[c].fillna('__MISSING__').astype(str)

        # value counts normalized
        p = a.value_counts(normalize=True)
        q = b.value_counts(normalize=True)

        # align index union
        all_idx = p.index.union(q.index)
        p_all = p.reindex(all_idx, fill_value=0.0)
        q_all = q.reindex(all_idx, fill_value=0.0)

        # total variation distance (L1 / 2)
        tvd = 0.5 * np.abs(p_all - q_all).sum()

        # top changes
        top_ref = p.head(5).to_dict()
        top_new = q.head(5).to_dict()

        categorical_report[c] = {
            'tvd': round(float(tvd), 6),
            'top_ref_categories': top_ref,
            'top_new_categories': top_new,
            'drift_flag': float(tvd) > 0.1  # arbitrary threshold; can be tuned
        }

    summary = {
        'numeric': numeric_report,
        'categorical': categorical_report,
        'numeric_cols_checked': len(numeric_cols),
        'categorical_cols_checked': len(categorical_cols)
    }

    return summary
