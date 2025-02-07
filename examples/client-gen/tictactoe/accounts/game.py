import typing
from dataclasses import dataclass
from base64 import b64decode
from solana.publickey import PublicKey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
import borsh_construct as borsh
from anchorpy.coder.accounts import ACCOUNT_DISCRIMINATOR_SIZE
from anchorpy.error import AccountInvalidDiscriminator
from anchorpy.utils.rpc import get_multiple_accounts
from anchorpy.borsh_extension import BorshPubkey
from ..program_id import PROGRAM_ID
from .. import types


class GameJSON(typing.TypedDict):
    players: list[str]
    turn: int
    board: list[list[typing.Optional[types.sign.SignJSON]]]
    state: types.game_state.GameStateJSON


@dataclass
class Game:
    discriminator: typing.ClassVar = b"\x1bZ\xa6}Jdy\x12"
    layout: typing.ClassVar = borsh.CStruct(
        "players" / BorshPubkey[2],
        "turn" / borsh.U8,
        "board" / borsh.Option(types.sign.layout)[3][3],
        "state" / types.game_state.layout,
    )
    players: list[PublicKey]
    turn: int
    board: list[list[typing.Optional[types.sign.SignKind]]]
    state: types.game_state.GameStateKind

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: PublicKey,
        commitment: typing.Optional[Commitment] = None,
    ) -> typing.Optional["Game"]:
        resp = await conn.get_account_info(address, commitment=commitment)
        info = resp["result"]["value"]
        if info is None:
            return None
        if info["owner"] != str(PROGRAM_ID):
            raise ValueError("Account does not belong to this program")
        bytes_data = b64decode(info["data"][0])
        return cls.decode(bytes_data)

    @classmethod
    async def fetch_multiple(
        cls,
        conn: AsyncClient,
        addresses: list[PublicKey],
        commitment: typing.Optional[Commitment] = None,
    ) -> typing.List[typing.Optional["Game"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["Game"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != PROGRAM_ID:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "Game":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = Game.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            players=dec.players,
            turn=dec.turn,
            board=list(
                map(
                    lambda item: list(
                        map(
                            lambda item: (
                                None if item is None else types.sign.from_decoded(item)
                            ),
                            item,
                        )
                    ),
                    dec.board,
                )
            ),
            state=types.game_state.from_decoded(dec.state),
        )

    def to_json(self) -> GameJSON:
        return {
            "players": list(map(lambda item: str(item), self.players)),
            "turn": self.turn,
            "board": list(
                map(
                    lambda item: list(
                        map(
                            lambda item: (None if item is None else item.to_json()),
                            item,
                        )
                    ),
                    self.board,
                )
            ),
            "state": self.state.to_json(),
        }

    @classmethod
    def from_json(cls, obj: GameJSON) -> "Game":
        return cls(
            players=list(map(lambda item: PublicKey(item), obj["players"])),
            turn=obj["turn"],
            board=list(
                map(
                    lambda item: list(
                        map(
                            lambda item: (
                                None if item is None else types.sign.from_json(item)
                            ),
                            item,
                        )
                    ),
                    obj["board"],
                )
            ),
            state=types.game_state.from_json(obj["state"]),
        )
