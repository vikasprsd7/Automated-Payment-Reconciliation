```python
def reconcile_payments(ledger_df, gateway_df, id_column='transaction_id', amount_column='amount'):
    """
    Reconcile two payment datasets and return discrepancy report.

    Parameters:
    -----------
    ledger_df : DataFrame - Internal ledger/records
    gateway_df : DataFrame - External gateway export
    id_column : str - Name of the transaction ID column
    amount_column : str - Name of the amount column

    Returns:
    --------
    dict with 'summary' and individual issue DataFrames
    """

    # Get ID sets
    ledger_ids = set(ledger_df[id_column])
    gateway_ids = set(gateway_df[id_column])

    # =====================
    # 1. Missing in gateway
    # =====================
    missing_in_gateway = ledger_ids - gateway_ids
    missing_in_gateway_list = list(missing_in_gateway)

    missing_gateway_df = ledger_df[ledger_df[id_column].isin(missing_in_gateway_list)].copy()
    missing_gateway_df['issue_type'] = 'MISSING_IN_GATEWAY'
    missing_gateway_df['gateway_amount'] = 0
    missing_gateway_df['difference'] = missing_gateway_df[amount_column]

    # =====================
    # 2. Missing in ledger
    # =====================
    missing_in_ledger = gateway_ids - ledger_ids
    missing_in_ledger_list = list(missing_in_ledger)

    missing_ledger_df = gateway_df[gateway_df[id_column].isin(missing_in_ledger_list)].copy()
    missing_ledger_df['issue_type'] = 'MISSING_IN_LEDGER'
    missing_ledger_df['ledger_amount'] = 0
    missing_ledger_df['difference'] = -missing_ledger_df[amount_column]

    # =====================
    # 3. Amount mismatches
    # =====================
    common_ids = ledger_ids & gateway_ids
    common_ids_list = list(common_ids)

    ledger_common = ledger_df[ledger_df[id_column].isin(common_ids_list)]
    gateway_common = gateway_df[gateway_df[id_column].isin(common_ids_list)]

    merged = ledger_common.merge(
        gateway_common[[id_column, amount_column]],
        on=id_column,
        suffixes=('_ledger', '_gateway')
    )

    merged['difference'] = merged[f'{amount_column}_ledger'] - merged[f'{amount_column}_gateway']
    amount_mismatches = merged[merged['difference'] != 0].copy()
    amount_mismatches['issue_type'] = 'AMOUNT_MISMATCH'

    # =====================
    # Build summary
    # =====================
    summary = {}
    summary['ledger_count'] = len(ledger_df)
    summary['gateway_count'] = len(gateway_df)
    summary['matched_count'] = len(common_ids) - len(amount_mismatches)
    summary['missing_in_gateway_count'] = len(missing_in_gateway)

    if len(missing_gateway_df) > 0:
        summary['missing_in_gateway_value'] = missing_gateway_df[amount_column].sum()
    else:
        summary['missing_in_gateway_value'] = 0

    summary['missing_in_ledger_count'] = len(missing_in_ledger)

    if len(missing_ledger_df) > 0:
        summary['missing_in_ledger_value'] = missing_ledger_df[amount_column].sum()
    else:
        summary['missing_in_ledger_value'] = 0

    summary['amount_mismatch_count'] = len(amount_mismatches)

    if len(amount_mismatches) > 0:
        summary['amount_mismatch_net'] = amount_mismatches['difference'].sum()
    else:
        summary['amount_mismatch_net'] = 0

    summary['total_issues'] = len(missing_in_gateway) + len(missing_in_ledger) + len(amount_mismatches)

    # Return everything
    result = {
        'summary': summary,
        'missing_in_gateway': missing_gateway_df,
        'missing_in_ledger': missing_ledger_df,
        'amount_mismatches': amount_mismatches
    }

    return result
```
