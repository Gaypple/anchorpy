import json
from pathlib import Path
from anchorpy import Idl, Program
from solana.publickey import PublicKey


def test_idls() -> None:
    idls = []
    programs = []
    for path in Path("tests/idls/").iterdir():
        with path.open() as f:
            data = json.load(f)
        idl = Idl.from_json(data)
        idls.append(idl)
        program = Program(idl, PublicKey(1))
        programs.append(program)
    assert idls


def test_jet_enum() -> None:
    path = Path("tests/idls/jet.json")
    with path.open() as f:
        data = json.load(f)
    idl = Idl.from_json(data)
    program = Program(idl, PublicKey(1))
    expired_err = program.type["CacheInvalidError"].Expired
    assert expired_err(msg="hi").msg == "hi"


def test_switchboard_tuple() -> None:
    path = Path("tests/idls/switchboard.json")
    with path.open() as f:
        data = json.load(f)
    idl = Idl.from_json(data)
    program = Program(idl, PublicKey(1))  # noqa: F841


def test_clientgen_example() -> None:
    path = Path("tests/idls/clientgen_example_program.json")
    with path.open() as f:
        data = json.load(f)
    Idl.from_json(data)
