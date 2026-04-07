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










































































