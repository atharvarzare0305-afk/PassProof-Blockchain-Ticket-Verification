from pathlib import Path
import shutil

import qrcode
import streamlit as st

from blockchain import (
    add_block,
    create_genesis_block,
    find_ticket_events,
    load_chain,
    save_chain,
    ticket_status,
    validate_chain,
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LEDGER_PATH = DATA_DIR / "ledger.json"
BACKUP_PATH = DATA_DIR / "demo_ledger.json"

st.set_page_config(
    page_title="PassProof",
    page_icon="🎟️",
    layout="wide",
)

st.title("🎟️ PassProof")
st.caption("Blockchain-Based Event Ticket Verification System")

chain = load_chain(LEDGER_PATH)

# Keep a clean demo ledger as a restore point.
if not BACKUP_PATH.exists():
    save_chain(BACKUP_PATH, chain)

valid, errors = validate_chain(chain)

with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Choose a module",
        [
            "Dashboard",
            "Issue Ticket",
            "Verify Entry",
            "Blockchain Explorer",
            "Security Lab",
        ],
    )

    st.divider()
    st.write(f"**Blocks:** {len(chain)}")
    st.write("**Chain:** " + ("Healthy ✅" if valid else "Modified ⚠️"))


if page == "Dashboard":
    st.subheader("Dashboard")

    issued = sum(
        1 for b in chain
        if b.get("data", {}).get("type") == "TICKET_ISSUED"
    )
    used = sum(
        1 for b in chain
        if b.get("data", {}).get("type") == "ENTRY_GRANTED"
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tickets Issued", issued)
    c2.metric("Entries Used", used)
    c3.metric("Available", max(issued - used, 0))
    c4.metric("Ledger Blocks", len(chain))

    st.divider()

    if valid:
        st.success("Ledger integrity check passed. No tampering detected.")
    else:
        st.error("Ledger integrity check failed.")
        for error in errors:
            st.write(f"- {error}")

    st.info(
        "PassProof records ticket issuance and entry as append-only events. "
        "Each block contains a SHA-256 hash and the previous block's hash."
    )


elif page == "Issue Ticket":
    st.subheader("Issue Ticket")

    with st.form("issue_ticket"):
        name = st.text_input("Attendee Name")
        event = st.text_input("Event Name", value="SVVV Tech Fest 2026")
        category = st.selectbox(
            "Category",
            ["Student", "Faculty", "Guest", "Other"],
        )
        submitted = st.form_submit_button("Generate Ticket")

    if submitted:
        if not name.strip():
            st.warning("Please enter the attendee name.")
        else:
            clean_name = name.strip()
            ticket_id = (
                f"PP-{clean_name.upper().replace(' ', '-')[:12]}-"
                f"{len(chain):03d}"
            )

            if find_ticket_events(chain, ticket_id):
                st.error("A ticket with this generated ID already exists.")
            else:
                data = {
                    "type": "TICKET_ISSUED",
                    "ticket_id": ticket_id,
                    "attendee_name": clean_name,
                    "event_name": event.strip(),
                    "category": category,
                    "status": "Issued",
                }

                add_block(chain, data)
                save_chain(LEDGER_PATH, chain)

                qr_path = BASE_DIR / "assets"
                qr_path.mkdir(exist_ok=True)
                image_path = qr_path / f"{ticket_id}.png"
                qrcode.make(ticket_id).save(image_path)

                st.success(f"Ticket created successfully: {ticket_id}")
                st.image(image_path, caption="Ticket QR Code", width=220)
                st.code(ticket_id)
                st.info("Ticket issuance has been recorded as a new block.")


elif page == "Verify Entry":
    st.subheader("Verify Entry")

    ticket_id = st.text_input(
        "Enter Ticket ID",
        placeholder="Example: PP-ATHARV-001",
    ).strip()

    if st.button("Check Ticket"):
        if not ticket_id:
            st.warning("Please enter a Ticket ID.")
        else:
            status, events = ticket_status(chain, ticket_id)
            st.session_state["checked_ticket"] = ticket_id
            st.session_state["checked_status"] = status
            st.session_state["checked_events"] = events

    checked_ticket = st.session_state.get("checked_ticket")
    status = st.session_state.get("checked_status")
    events = st.session_state.get("checked_events", [])

    if checked_ticket and status:
        if status == "Invalid":
            st.error("INVALID TICKET ❌")
        elif status == "Used":
            st.warning("TICKET ALREADY USED ⚠️")
            st.write("A previous ENTRY_GRANTED event already exists.")
        else:
            st.success("VALID TICKET — ENTRY CAN BE GRANTED ✅")

            if st.button("Grant Entry"):
                data = {
                    "type": "ENTRY_GRANTED",
                    "ticket_id": checked_ticket,
                    "status": "Used",
                }
                add_block(chain, data)
                save_chain(LEDGER_PATH, chain)
                st.session_state.pop("checked_ticket", None)
                st.session_state.pop("checked_status", None)
                st.session_state.pop("checked_events", None)
                st.success(
                    "Entry recorded successfully. The ticket is now marked as Used."
                )
                st.rerun()

        if events:
            st.write("Ticket history:")
            st.json(events)


elif page == "Blockchain Explorer":
    st.subheader("Blockchain Explorer")

    if not valid:
        st.error("Chain integrity failure detected.")
        for error in errors:
            st.write(f"- {error}")

    for block in chain:
        event_type = block.get("data", {}).get("type", "UNKNOWN")
        with st.expander(f"Block {block['index']} — {event_type}"):
            st.write("**Timestamp:**", block["timestamp"])
            st.write("**Previous Hash:**")
            st.code(block["previous_hash"])
            st.write("**Hash:**")
            st.code(block["hash"])
            st.write("**Data:**")
            st.json(block["data"])


elif page == "Security Lab":
    st.subheader("Security Lab")

    st.write(
        "Change a block's stored data without recalculating its hash. "
        "The integrity checker will then detect a hash mismatch or broken link."
    )

    if valid:
        st.success("Current ledger is healthy.")
    else:
        st.error("Current ledger is already modified.")

    non_genesis = list(range(1, len(chain)))

    if non_genesis:
        selected = st.selectbox(
            "Select a non-genesis block",
            non_genesis,
        )

        if st.button("Simulate Tampering"):
            tampered_chain = load_chain(LEDGER_PATH)
            tampered_chain[selected]["data"]["tampered"] = True
            tampered_chain[selected]["data"]["demo_note"] = (
                "This block was intentionally changed for demonstration."
            )
            save_chain(LEDGER_PATH, tampered_chain)
            st.error(
                f"Block {selected} was modified for the demo. "
                "Open Dashboard to see the integrity failure."
            )
            st.rerun()
    else:
        st.info("Issue at least one ticket to create a non-genesis block.")

    st.divider()

    if st.button("Restore Clean Demo Ledger"):
        clean_chain = load_chain(BACKUP_PATH)
        save_chain(LEDGER_PATH, clean_chain)
        st.success("Clean demo ledger restored.")
        st.rerun()
