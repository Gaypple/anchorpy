from __future__ import annotations
import typing
from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction, AccountMeta
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class CreateArgs(typing.TypedDict):
    authority: PublicKey


layout = borsh.CStruct("authority" / BorshPubkey)


class CreateAccounts(typing.TypedDict):
    counter: PublicKey
    rent: PublicKey


def create(args: CreateArgs, accounts: CreateAccounts) -> TransactionInstruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["counter"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["rent"], is_signer=False, is_writable=False),
    ]
    identifier = b"\x18\x1e\xc8(\x05\x1c\x07w"
    encoded_args = layout.build(
        {
            "authority": args["authority"],
        }
    )
    data = identifier + encoded_args
    return TransactionInstruction(keys, PROGRAM_ID, data)
