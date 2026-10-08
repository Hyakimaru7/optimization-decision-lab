"""Strict JSON input helpers for the optional decision support tools."""
import argparse
import json
import math
import sys
from pathlib import Path
from check_linear_solution import number, reject_unknown


def obj(value, fields, name):
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    reject_unknown(value, fields, name)
    if set(value) != set(fields):
        raise ValueError(f"{name} requires {sorted(set(fields) - set(value))}")
    return value


def label(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a nonempty string")
    return value


def labels(value, name, nonempty=False):
    if not isinstance(value, list) or (nonempty and not value):
        raise ValueError(f"{name} must be an array" + (" with entries" if nonempty else ""))
    result = [label(x, name) for x in value]
    if len(result) != len(set(result)):
        raise ValueError(f"{name} must be unique")
    return result


def nonnegative(value, name):
    v = number(value, name)
    if v < 0:
        raise ValueError(f"{name} must be nonnegative")
    return v


def total(values):
    v = math.fsum(values)
    if not math.isfinite(v):
        raise ValueError("nonfinite arithmetic; rescale inputs")
    return v


def cli(function, success):
    parser = argparse.ArgumentParser(description=function.__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        result = function(json.loads(args.input.read_text(encoding="utf-8")))
        print(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2))
        return 0 if success(result) else 1
    except (OSError, ValueError, TypeError, OverflowError) as error:
        print(json.dumps({"status": "invalid_input", "error": str(error)}, ensure_ascii=False))
        return 2
