# PassProof – Blockchain-Based Event Ticket Verification System

## Project Overview

PassProof is a lightweight blockchain-based event ticket verification system designed to issue unique tickets, record check-in events, and make unauthorized changes to ticket records detectable.

The system uses a hash-linked ledger where each block contains its own SHA-256 hash and the hash of the previous block.

## Problem Statement

Traditional ticket records can be copied, edited, or reused. This can lead to duplicate tickets, repeat entry, altered records, and difficulty in maintaining a reliable audit trail.

PassProof addresses these problems by recording ticket issuance and entry actions as blockchain-style events.

## Objectives

- Develop a hash-linked blockchain ledger for ticket issuance and check-in events.
- Ensure data integrity using SHA-256 hashing and previous-hash linking.
- Detect unauthorized changes through chain validation.
- Prevent duplicate entry by recording successful check-ins.
- Provide a simple dashboard and visible blockchain audit trail.

## Main Features

- Unique ticket generation
- QR-based ticket identification
- Ticket verification
- Duplicate check-in prevention
- SHA-256 cryptographic hashing
- Previous-hash blockchain linking
- Blockchain Explorer
- Chain integrity validation
- Tamper detection demonstration
- Local-first operation

## System Workflow

**Issue Ticket → Record Issuance → Verify Ticket → Check In → Record Entry**

Every important action is recorded as a new event instead of silently overwriting previous records.

## Blockchain Concept

Each block contains:

- Block index
- Timestamp
- Event data
- Previous block hash
- Current block SHA-256 hash

Changing the data of a block changes its calculated hash and can therefore be detected during chain validation.

## Technology Stack

- Python
- Streamlit
- SHA-256 / hashlib
- JSON
- QR Code

## Application Modules

1. Dashboard
2. Issue Ticket
3. Verify Entry
4. Blockchain Explorer
5. Security Lab

## Project Scope

This project is a classroom demonstration of blockchain fundamentals. It focuses on hashing, hash chaining, append-only event history, integrity validation, and duplicate check-in prevention.

It does not claim to implement a distributed public blockchain, peer-to-peer network, distributed consensus, or production-grade identity and payment security.

## Team Members

- **Atharv Arzare** – 23100BTCSFBI14614
- **Ketan Agrawal** – 23100BTCSFBI14620
- **Kirtan Jaiswal** – 23100BTCSFBI14621

## Course

**BTIBM721 – Introduction to Blockchain**

**Course Teacher:** Prof. Rohit Choubey

**Shri Vaishnav Institute of Information Technology (SVIIT)**

## Project Documents

- Project Synopsis – `PassProof_Project_Synopsis.docx`
- Project Presentation – `PassProof_Presentation.pptx`
