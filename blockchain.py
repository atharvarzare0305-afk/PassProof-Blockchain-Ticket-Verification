import hashlib
import json
from datetime import datetime
from pathlib import Path


def calculate_hash(index, timestamp, data, previous_hash):
    payload = json.dumps(
        {
            "index": index,
            "timestamp": timestamp,
            "data": data,
            "previous_hash": previous_hash,
        },
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def create_genesis_block():
    timestamp = datetime.now().isoformat(timespec="seconds")
    data = {"type": "GENESIS"}
    block = {
        "index": 0,
        "timestamp": timestamp,
        "data": data,
        "previous_hash": "0" * 64,
    }
    block["hash"] = calculate_hash(
        block["index"], block["timestamp"], block["data"], block["previous_hash"]
    )
    return block


def load_chain(path: Path):
    if not path.exists() or path.stat().st_size == 0:
        chain = [create_genesis_block()]
        save_chain(path, chain)
        return chain

    try:
        chain = json.loads(path.read_text(encoding="utf-8"))
        if not chain:
            chain = [create_genesis_block()]
            save_chain(path, chain)
        return chain
    except (json.JSONDecodeError, OSError):
        chain = [create_genesis_block()]
        save_chain(path, chain)
        return chain


def save_chain(path: Path, chain):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(chain, indent=2), encoding="utf-8")


def add_block(chain, data):
    previous = chain[-1]
    block = {
        "index": previous["index"] + 1,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "data": data,
        "previous_hash": previous["hash"],
    }
    block["hash"] = calculate_hash(
        block["index"],
        block["timestamp"],
        block["data"],
        block["previous_hash"],
    )
    chain.append(block)
    return block


def validate_chain(chain):
    errors = []

    if not chain:
        return False, ["Ledger is empty."]

    for i, block in enumerate(chain):
        expected_hash = calculate_hash(
            block["index"],
            block["timestamp"],
            block["data"],
            block["previous_hash"],
        )

        if block.get("hash") != expected_hash:
            errors.append(f"Block {i}: hash mismatch.")

        if i == 0:
            if block.get("previous_hash") != "0" * 64:
                errors.append("Genesis block has an invalid previous hash.")
        elif block.get("previous_hash") != chain[i - 1].get("hash"):
            errors.append(f"Block {i}: previous-hash link is broken.")

    return len(errors) == 0, errors


def find_ticket_events(chain, ticket_id):
    return [
        block for block in chain
        if block.get("data", {}).get("ticket_id") == ticket_id
    ]


def ticket_status(chain, ticket_id):
    events = find_ticket_events(chain, ticket_id)

    if not events:
        return "Invalid", events

    issued = any(
        b.get("data", {}).get("type") == "TICKET_ISSUED"
        for b in events
    )
    used = any(
        b.get("data", {}).get("type") == "ENTRY_GRANTED"
        for b in events
    )

    if not issued:
        return "Invalid", events
    if used:
        return "Used", events
    return "Issued", events
