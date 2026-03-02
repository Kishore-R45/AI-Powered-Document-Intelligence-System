"""
reset_data.py — Wipe all InfoVault Mobile data from MongoDB and Pinecone.
Run from the backend directory:
    python reset_data.py
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─── MongoDB ────────────────────────────────────────────────────────────────

def reset_mongodb():
    from pymongo import MongoClient

    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri)

    # Extract DB name from URI (infovault_mobile)
    db_name = mongo_uri.split("/")[-1].split("?")[0]
    db = client[db_name]

    collections = db.list_collection_names()
    if not collections:
        print(f"[MongoDB] No collections found in '{db_name}' — already empty.")
    else:
        print(f"[MongoDB] Dropping {len(collections)} collections from '{db_name}':")
        for col in collections:
            db.drop_collection(col)
            print(f"  ✓ Dropped: {col}")
        print(f"[MongoDB] Done — all data cleared.\n")

    client.close()


# ─── Pinecone ────────────────────────────────────────────────────────────────

def reset_pinecone():
    from pinecone import Pinecone

    api_key    = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME", "infovault-mobile")

    pc = Pinecone(api_key=api_key)

    # Check the index exists
    existing = [i.name for i in pc.list_indexes()]
    if index_name not in existing:
        print(f"[Pinecone] Index '{index_name}' does not exist — nothing to clear.\n")
        return

    index = pc.Index(index_name)
    stats = index.describe_index_stats()
    total = stats.get("total_vector_count", 0) or sum(
        ns.get("vector_count", 0) for ns in (stats.get("namespaces") or {}).values()
    )
    print(f"[Pinecone] Index '{index_name}' has {total} vectors.")

    if total == 0:
        print(f"[Pinecone] Already empty — nothing to delete.\n")
        return

    # Delete all vectors by deleting each namespace (or use deleteAll)
    namespaces = list((stats.get("namespaces") or {}).keys())
    if namespaces:
        for ns in namespaces:
            index.delete(delete_all=True, namespace=ns)
            print(f"  ✓ Cleared namespace: '{ns}'")
    else:
        # Default (empty-string) namespace
        index.delete(delete_all=True)
        print(f"  ✓ Cleared default namespace")

    print(f"[Pinecone] Done — all vectors deleted.\n")


# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print(" InfoVault Mobile — Data Reset")
    print("=" * 50)
    confirm = input("\n⚠  This will PERMANENTLY DELETE all users, documents,\n   chats, notifications, and embeddings.\n   Type YES to continue: ").strip()

    if confirm != "YES":
        print("Aborted.")
        exit(0)

    print()
    try:
        reset_mongodb()
    except Exception as e:
        print(f"[MongoDB] ERROR: {e}\n")

    try:
        reset_pinecone()
    except Exception as e:
        print(f"[Pinecone] ERROR: {e}\n")

    print("=" * 50)
    print(" Reset complete. Start fresh!")
    print("=" * 50)
