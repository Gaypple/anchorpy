from __future__ import annotations
from solana.transaction import TransactionInstruction, AccountMeta
from ..program_id import PROGRAM_ID


def cause_error() -> TransactionInstruction:
    keys: list[AccountMeta] = []
    identifier = b"Ch%\x11\x02\x9bD\x11"
    encoded_args = b""
    data = identifier + encoded_args
    return TransactionInstruction(keys, PROGRAM_ID, data)
