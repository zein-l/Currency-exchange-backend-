from firebase_config import firestore_db

def sync_transaction_to_firestore(transaction):
    try:
        doc_data = {
            "user_id": transaction.user_id,
            "usd_amount": transaction.usd_amount,
            "lbp_amount": transaction.lbp_amount,
            "usd_to_lbp": transaction.usd_to_lbp,
            "added_date": transaction.added_date.isoformat()
        }

        firestore_db.collection("transactions").add(doc_data)
        print("✅ Transaction synced to Firestore")

    except Exception as e:
        print(f"❌ Firestore sync failed: {str(e)}")
