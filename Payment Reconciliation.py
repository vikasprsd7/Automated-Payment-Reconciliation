import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set seed for reproducibility — everyone gets same "random" data
np.random.seed(42)
random.seed(42)

# Configuration
num_transactions = 100
start_date = datetime(2024, 1, 15)

# Generate transaction IDs
transaction_ids = []
for i in range(1001, 1001 + num_transactions):
    txn_id = "TXN" + str(i).zfill(5)
    transaction_ids.append(txn_id)

# Check first few IDs
print("Sample transaction IDs:", transaction_ids[:5])

# Generate random amounts (typical e-commerce range)
amount_options = [299, 499, 799, 999, 1499, 1999, 2499, 3999]
amounts = np.random.choice(amount_options, size=num_transactions)

print("Sample amounts:", amounts[:10])

# Generate timestamps spread over 3 days
timestamps = []
for i in range(num_transactions):
    random_days = random.randint(0, 2)
    random_hours = random.randint(9, 21)
    random_minutes = random.randint(0, 59)

    timestamp = start_date + timedelta(days=random_days, hours=random_hours, minutes=random_minutes)
    timestamps.append(timestamp)

print("Sample timestamps:", timestamps[:3])

# Generate payment methods
method_options = ['UPI', 'Card', 'NetBanking', 'Wallet']
method_weights = [0.5, 0.3, 0.1, 0.1]  # UPI is 50%, Card is 30%, etc. Probability distribution (weights)

payment_methods = np.random.choice(method_options, size=num_transactions, p=method_weights)

print("Sample payment methods:", payment_methods[:10])


# Create the internal ledger DataFrame
internal_ledger = pd.DataFrame({
    'transaction_id': transaction_ids,
    'amount': amounts,
    'timestamp': timestamps,
    'payment_method': payment_methods,
    'status': 'SUCCESS'  # All recorded as success in our system
})

print(f"Internal ledger created with {len(internal_ledger)} transactions")
internal_ledger.head(10)

# Start with a copy of internal ledger
gateway_export = internal_ledger.copy()

print(f"Starting gateway export with {len(gateway_export)} transactions")

# Randomly select 5 transactions to remove from gateway
missing_indices = np.random.choice(gateway_export.index, size=5, replace=False)

# Store the IDs before removing (for our reference)
missing_txn_ids = []
for idx in missing_indices:
    txn_id = internal_ledger.loc[idx, 'transaction_id']
    missing_txn_ids.append(txn_id)

print(f"Will remove these transaction IDs: {missing_txn_ids}")

# Remove them from gateway
gateway_export = gateway_export.drop(missing_indices)

print(f"Gateway now has {len(gateway_export)} transactions")


# Select 3 random transactions to modify amounts
mismatch_indices = np.random.choice(gateway_export.index, size=3, replace=False)

# Modify each one
fee_options = [10, 20, 50, 100]

for idx in mismatch_indices:
    original_amount = gateway_export.loc[idx, 'amount']
    fee_deducted = random.choice(fee_options)
    new_amount = original_amount - fee_deducted
    gateway_export.loc[idx, 'amount'] = new_amount

    txn_id = gateway_export.loc[idx, 'transaction_id']
    print(f"{txn_id}: ₹{original_amount} -> ₹{new_amount} (fee: ₹{fee_deducted})")

# Create 2 extra transactions that only exist in gateway
extra_transaction_1 = {
    'transaction_id': 'TXN99901',
    'amount': 1599,
    'timestamp': start_date + timedelta(hours=14),
    'payment_method': 'UPI',
    'status': 'SUCCESS'
}

extra_transaction_2 = {
    'transaction_id': 'TXN99902',
    'amount': 2999,
    'timestamp': start_date + timedelta(days=1, hours=10),
    'payment_method': 'Card',
    'status': 'SUCCESS'
}

# Create DataFrame for extra transactions
extra_transactions = pd.DataFrame([extra_transaction_1, extra_transaction_2])

# Add to gateway export
gateway_export = pd.concat([gateway_export, extra_transactions], ignore_index=True)

print(f"Added extra transactions: TXN99901, TXN99902")
print(f"Gateway now has {len(gateway_export)} transactions")

# Select 2 transactions to change status
# Exclude the last 2 rows (our extra transactions)
available_indices = gateway_export.index[:-2].tolist()
status_change_indices = np.random.choice(available_indices, size=2, replace=False)

for idx in status_change_indices:
    txn_id = gateway_export.loc[idx, 'transaction_id']
    gateway_export.loc[idx, 'status'] = 'FAILED'
    print(f"{txn_id}: Status changed to FAILED")

# Final dataset sizes
print(f"\n{'='*50}")
print(f"Internal Ledger: {len(internal_ledger)} transactions")
print(f"Gateway Export: {len(gateway_export)} transactions")
print(f"{'='*50}")

### Quick Data Inspection

### Before any reconciliation, always inspect your data.

print("=== Internal Ledger Summary ===")
print(f"Date range: {internal_ledger['timestamp'].min()} to {internal_ledger['timestamp'].max()}")
print(f"Total amount: ₹{internal_ledger['amount'].sum():,}")
print(f"\nPayment method distribution:")
print(internal_ledger['payment_method'].value_counts())

print("\n=== Gateway Export Summary ===")
print(f"Date range: {gateway_export['timestamp'].min()} to {gateway_export['timestamp'].max()}")
print(f"Total amount: ₹{gateway_export['amount'].sum():,}")
print(f"\nStatus distribution:")
print(gateway_export['status'].value_counts())

# Get all transaction IDs from both sources
ledger_ids = set(internal_ledger['transaction_id'])
gateway_ids = set(gateway_export['transaction_id'])

print(f"Unique IDs in Ledger: {len(ledger_ids)}")
print(f"Unique IDs in Gateway: {len(gateway_ids)}")

# Find IDs in ledger but not in gateway
missing_in_gateway = ledger_ids - gateway_ids

print(f"\nTransactions in Ledger but NOT in Gateway: {len(missing_in_gateway)}")
print(f"Transaction IDs: {missing_in_gateway}")

# Get full details of missing transactions
# We need to filter the ledger for these IDs

missing_in_gateway_list = list(missing_in_gateway)
missing_in_gateway_df = internal_ledger[internal_ledger['transaction_id'].isin(missing_in_gateway_list)].copy()

# Add a column to mark the issue type
missing_in_gateway_df['issue_type'] = 'MISSING_IN_GATEWAY'

# Calculate total value at risk
total_missing_value = missing_in_gateway_df['amount'].sum()
print(f"\nTotal value at risk: ₹{total_missing_value:,}")

missing_in_gateway_df

# Find IDs in gateway but not in ledger
missing_in_ledger = gateway_ids - ledger_ids

print(f"Transactions in Gateway but NOT in Ledger: {len(missing_in_ledger)}")
print(f"Transaction IDs: {missing_in_ledger}")

# Get full details
missing_in_ledger_list = list(missing_in_ledger)
missing_in_ledger_df = gateway_export[gateway_export['transaction_id'].isin(missing_in_ledger_list)].copy()

# Add issue type
missing_in_ledger_df['issue_type'] = 'MISSING_IN_LEDGER'

# Calculate total unrecorded value
total_unrecorded_value = missing_in_ledger_df['amount'].sum()
print(f"\nTotal unrecorded value: ₹{total_unrecorded_value:,}")

missing_in_ledger_df

# Find common transactions (present in both)
common_ids = ledger_ids & gateway_ids

print(f"Transactions present in both: {len(common_ids)}")

# Get data for common transactions from both sources
common_ids_list = list(common_ids)

ledger_common = internal_ledger[internal_ledger['transaction_id'].isin(common_ids_list)].copy()
gateway_common = gateway_export[gateway_export['transaction_id'].isin(common_ids_list)].copy()

print(f"Ledger common records: {len(ledger_common)}")
print(f"Gateway common records: {len(gateway_common)}")

# Merge on transaction_id to compare side by side
comparison = ledger_common.merge(
    gateway_common[['transaction_id', 'amount', 'status']],
    on='transaction_id',
    suffixes=('_ledger', '_gateway')
)

print(f"Merged comparison table: {len(comparison)} rows")
comparison.head()

# Calculate the difference between ledger and gateway amounts
comparison['amount_diff'] = comparison['amount_ledger'] - comparison['amount_gateway']

# Find rows where there's a difference
amount_mismatches = comparison[comparison['amount_diff'] != 0].copy()

print(f"Transactions with amount mismatch: {len(amount_mismatches)}")

if len(amount_mismatches) > 0:
    total_discrepancy = amount_mismatches['amount_diff'].sum()
    print(f"Total discrepancy: ₹{total_discrepancy:,}")

    # Show details
    print("\nMismatch details:")
    print(amount_mismatches[['transaction_id', 'amount_ledger', 'amount_gateway', 'amount_diff']])

# Find status mismatches in our comparison table
status_mismatches = comparison[comparison['status_ledger'] != comparison['status_gateway']].copy()

print(f"Transactions with status mismatch: {len(status_mismatches)}")

if len(status_mismatches) > 0:
    print("\n⚠️  CRITICAL — We think SUCCESS but gateway says otherwise:")
    print(status_mismatches[['transaction_id', 'amount_ledger', 'status_ledger', 'status_gateway']])


# Part B: Build the Final Report

# Prepare amount mismatches for the report
amount_mismatch_report = amount_mismatches[['transaction_id', 'amount_ledger', 'amount_gateway', 'amount_diff']].copy()
amount_mismatch_report['issue_type'] = 'AMOUNT_MISMATCH'
amount_mismatch_report.columns = ['transaction_id', 'ledger_amount', 'gateway_amount', 'difference', 'issue_type']

print(f"Amount mismatch records: {len(amount_mismatch_report)}")
amount_mismatch_report

# Prepare missing in gateway for the report
missing_gateway_report = missing_in_gateway_df[['transaction_id', 'amount']].copy()
missing_gateway_report['gateway_amount'] = 0
missing_gateway_report['difference'] = missing_gateway_report['amount']
missing_gateway_report['issue_type'] = 'MISSING_IN_GATEWAY'
missing_gateway_report.columns = ['transaction_id', 'ledger_amount', 'gateway_amount', 'difference', 'issue_type']

print(f"Missing in gateway records: {len(missing_gateway_report)}")
missing_gateway_report

# Prepare missing in ledger for the report
missing_ledger_report = missing_in_ledger_df[['transaction_id', 'amount']].copy()
missing_ledger_report['ledger_amount'] = 0
missing_ledger_report['gateway_amount'] = missing_ledger_report['amount']
missing_ledger_report['difference'] = -missing_ledger_report['amount']  # Negative because we're under
missing_ledger_report['issue_type'] = 'MISSING_IN_LEDGER'
missing_ledger_report = missing_ledger_report[['transaction_id', 'ledger_amount', 'gateway_amount', 'difference', 'issue_type']]

print(f"Missing in ledger records: {len(missing_ledger_report)}")
missing_ledger_report

# Combine all issues into one report
reconciliation_report = pd.concat([
    missing_gateway_report,
    missing_ledger_report,
    amount_mismatch_report
], ignore_index=True)

print(f"\n=== RECONCILIATION REPORT ===")
print(f"Total issues found: {len(reconciliation_report)}")

# Count by issue type
print(f"\nBy issue type:")
print(reconciliation_report['issue_type'].value_counts())

# Combine all issues into one report
reconciliation_report = pd.concat([
    missing_gateway_report,
    missing_ledger_report,
    amount_mismatch_report
], ignore_index=True)

print(f"\n=== RECONCILIATION REPORT ===")
print(f"Total issues found: {len(reconciliation_report)}")

# Count by issue type
print(f"\nBy issue type:")
print(reconciliation_report['issue_type'].value_counts())

# Sort by absolute difference (biggest issues first)
reconciliation_report['abs_difference'] = reconciliation_report['difference'].abs()
reconciliation_report = reconciliation_report.sort_values('abs_difference', ascending=False)
reconciliation_report = reconciliation_report.drop('abs_difference', axis=1)

# Reset index for clean display
reconciliation_report = reconciliation_report.reset_index(drop=True)

print("\nFull report (sorted by impact):")
reconciliation_report

# Calculate summary statistics
total_ledger = internal_ledger['amount'].sum()
total_gateway_success = gateway_export[gateway_export['status'] == 'SUCCESS']['amount'].sum()

## Summmary Report

# Build summary dictionary
summary = {}
summary['Total Transactions in Ledger'] = len(internal_ledger)
summary['Total Transactions in Gateway'] = len(gateway_export)
summary['Matched Transactions'] = len(common_ids) - len(amount_mismatches)
summary['Total Issues Found'] = len(reconciliation_report)
summary['Missing in Gateway (Count)'] = len(missing_in_gateway)
summary['Missing in Gateway (Value)'] = missing_in_gateway_df['amount'].sum()
summary['Missing in Ledger (Count)'] = len(missing_in_ledger)
summary['Missing in Ledger (Value)'] = missing_in_ledger_df['amount'].sum()
summary['Amount Mismatches (Count)'] = len(amount_mismatches)

if len(amount_mismatches) > 0:
    summary['Amount Mismatches (Net Diff)'] = amount_mismatches['amount_diff'].sum()
else:
    summary['Amount Mismatches (Net Diff)'] = 0

summary['Ledger Total'] = total_ledger
summary['Gateway Total (SUCCESS only)'] = total_gateway_success

# Display as DataFrame
summary_df = pd.DataFrame(list(summary.items()), columns=['Metric', 'Value'])
summary_df


# The bottom line
net_difference = total_ledger - total_gateway_success

print(f"\n{'='*50}")
print(f"BOTTOM LINE")
print(f"{'='*50}")
print(f"We think we have: ₹{total_ledger:,}")
print(f"Gateway confirms: ₹{total_gateway_success:,}")
print(f"Net difference:   ₹{net_difference:,}")
print(f"{'='*50}")

if net_difference > 0:
    print(f"\n⚠️  We are OVER-REPORTING by ₹{net_difference:,}")
    print("    Action: Investigate missing gateway records")
elif net_difference < 0:
    print(f"\n⚠️  We are UNDER-REPORTING by ₹{abs(net_difference):,}")
    print("    Action: Investigate extra gateway transactions")
else:
    print("\n✅ Perfectly reconciled!")

























































