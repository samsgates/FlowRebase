from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from .core.compilers import COMPILERS
from .core.digital_twin import DigitalTwinSimulator
from .core.parsers import PARSERS
from .core.proofrun import ProofRunEngine
from .core.uam import UAMProcess


def load_uam(path: str) -> UAMProcess:
    text = Path(path).read_text()
    data = yaml.safe_load(text) if path.endswith((".yaml", ".yml")) else json.loads(text)
    return UAMProcess.model_validate(data)


def write(path: str | None, content: str) -> None:
    if path:
        Path(path).write_text(content)
    else:
        print(content)


def main() -> None:
    parser = argparse.ArgumentParser(prog="flowrebase", description="FlowRebase local UAM developer CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("parse", help="Parse a source automation into UAM JSON")
    p.add_argument("source_type", choices=sorted(PARSERS))
    p.add_argument("input")
    p.add_argument("--name")
    p.add_argument("-o", "--output")

    p = sub.add_parser("validate", help="Validate UAM JSON/YAML")
    p.add_argument("input")

    p = sub.add_parser("compile", help="Compile UAM to a target artifact")
    p.add_argument("target", choices=sorted(COMPILERS))
    p.add_argument("input")
    p.add_argument("-o", "--output")

    p = sub.add_parser("proofrun", help="Replay JSON test cases through UAM")
    p.add_argument("input")
    p.add_argument("cases")

    p = sub.add_parser("simulate", help="Run deterministic digital-twin Monte Carlo simulation")
    p.add_argument("input")
    p.add_argument("--runs", type=int, default=1000)

    args = parser.parse_args()
    if args.command == "parse":
        content = Path(args.input).read_text()
        uam = PARSERS[args.source_type].parse(name=args.name or Path(args.input).stem, content=content)
        write(args.output, json.dumps(uam.model_dump(mode="json"), indent=2))
    elif args.command == "validate":
        uam = load_uam(args.input)
        print(json.dumps({"valid": True, "id": uam.id, "nodes": len(uam.nodes), "edges": len(uam.edges)}, indent=2))
    elif args.command == "compile":
        artifact = COMPILERS[args.target].compile(load_uam(args.input))
        write(args.output, artifact.content)
        if artifact.warnings:
            print(json.dumps({"warnings": artifact.warnings}, indent=2))
    elif args.command == "proofrun":
        cases = json.loads(Path(args.cases).read_text())
        print(json.dumps(ProofRunEngine().run(load_uam(args.input), cases), indent=2))
    elif args.command == "simulate":
        print(json.dumps(DigitalTwinSimulator().simulate(load_uam(args.input), runs=args.runs), indent=2))


if __name__ == "__main__":
    main()
