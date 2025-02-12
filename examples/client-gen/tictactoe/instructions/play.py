from __future__ import annotations
import typing
from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction, AccountMeta
import borsh_construct as borsh
from .. import types
from ..program_id import PROGRAM_ID


class PlayArgs(typing.TypedDict):
    tile: types.tile.Tile


layout = borsh.CStruct("tile" / types.tile.Tile.layout)


class PlayAccounts(typing.TypedDict):
    game: PublicKey
    player: PublicKey


def play(args: PlayArgs, accounts: PlayAccounts) -> TransactionInstruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["game"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["player"], is_signer=True, is_writable=False),
    ]
    identifier = b"\xd5\x9d\xc1\x8e\xe48\xf8\x96"
    encoded_args = layout.build(
        {
            "tile": args["tile"].to_encodable(),
        }
    )
    data = identifier + encoded_args
    return TransactionInstruction(keys, PROGRAM_ID, data)
