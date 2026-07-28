#!/usr/bin/env python3
"""Validate one Reddit Chrome packet's atomic browser-step ledger."""

import argparse
import json
from pathlib import Path
import sys


STEP_KINDS = {
    "claim", "metadata", "navigate", "read_projection", "fill", "click",
    "submit", "verify", "finalize",
}
FRESH_SNAPSHOT_KINDS = {"fill", "click", "submit", "verify"}
NAVIGATION_OUTCOMES = {"PASS", "TIMEOUT", "ERROR", "UNKNOWN"}


def validate(records):
    if not records:
        raise ValueError("empty browser-step ledger")
    expected_seq = {}
    timeout_readback_required = {}
    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            raise ValueError("record %d is not an object" % index)
        packet_id = record.get("packet_id")
        if not isinstance(packet_id, str) or not packet_id:
            raise ValueError("record %d invalid packet_id" % index)
        step_seq = record.get("step_seq")
        if not isinstance(step_seq, int) or isinstance(step_seq, bool):
            raise ValueError("record %d invalid step_seq" % index)
        next_seq = expected_seq.get(packet_id, 1)
        if step_seq != next_seq:
            raise ValueError("record %d non-contiguous step_seq" % index)
        expected_seq[packet_id] = next_seq + 1
        boundary_kind = record.get("boundary_kind")
        if boundary_kind not in STEP_KINDS:
            raise ValueError("record %d invalid boundary_kind" % index)
        if record.get("boundary_operation_count") != 1:
            raise ValueError("record %d mixed browser boundary" % index)
        if timeout_readback_required.get(packet_id):
            if boundary_kind != "metadata" or record.get("post_timeout_readback") is not True:
                raise ValueError("record %d timeout must be followed by metadata readback" % index)
            timeout_readback_required[packet_id] = False
        if boundary_kind == "navigate":
            if record.get("outcome") not in NAVIGATION_OUTCOMES:
                raise ValueError("record %d navigate requires valid outcome" % index)
            if record["outcome"] == "TIMEOUT":
                timeout_readback_required[packet_id] = True
        if boundary_kind in FRESH_SNAPSHOT_KINDS and record.get("fresh_snapshot") is not True:
            raise ValueError("record %d requires fresh_snapshot" % index)
    if any(timeout_readback_required.values()):
        raise ValueError("timeout missing metadata readback")
    return {"status": "PASS", "packet_count": len(expected_seq), "step_count": len(records)}


def load(path):
    records = []
    for line_number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError("line %d invalid JSON" % line_number) from exc
    return records


def self_test():
    valid = [
        {"packet_id": "p", "step_seq": 1, "boundary_kind": "metadata", "boundary_operation_count": 1},
        {"packet_id": "p", "step_seq": 2, "boundary_kind": "navigate", "boundary_operation_count": 1, "outcome": "PASS"},
        {"packet_id": "p", "step_seq": 3, "boundary_kind": "read_projection", "boundary_operation_count": 1},
        {"packet_id": "p", "step_seq": 4, "boundary_kind": "submit", "boundary_operation_count": 1, "fresh_snapshot": True},
    ]
    assert validate(valid)["status"] == "PASS"
    try:
        validate([{"packet_id": "p", "step_seq": 1, "boundary_kind": "navigate", "boundary_operation_count": 2}])
    except ValueError as exc:
        assert "mixed browser boundary" in str(exc)
    else:
        raise AssertionError("mixed boundary accepted")
    recovery = [
        {"packet_id": "r", "step_seq": 1, "boundary_kind": "navigate", "boundary_operation_count": 1, "outcome": "TIMEOUT"},
        {"packet_id": "r", "step_seq": 2, "boundary_kind": "metadata", "boundary_operation_count": 1, "post_timeout_readback": True},
        {"packet_id": "r", "step_seq": 3, "boundary_kind": "claim", "boundary_operation_count": 1},
        {"packet_id": "r", "step_seq": 4, "boundary_kind": "navigate", "boundary_operation_count": 1, "outcome": "TIMEOUT"},
        {"packet_id": "r", "step_seq": 5, "boundary_kind": "metadata", "boundary_operation_count": 1, "post_timeout_readback": True},
    ]
    assert validate(recovery)["status"] == "PASS"
    try:
        validate([
            {"packet_id": "t", "step_seq": 1, "boundary_kind": "navigate", "boundary_operation_count": 1, "outcome": "TIMEOUT"},
            {"packet_id": "t", "step_seq": 2, "boundary_kind": "navigate", "boundary_operation_count": 1, "outcome": "PASS"},
        ])
    except ValueError as exc:
        assert "timeout must be followed" in str(exc)
    else:
        raise AssertionError("timeout retry accepted")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print(json.dumps({"status": "PASS", "self_test": True}, sort_keys=True))
        return
    if args.input is None:
        parser.error("--input or --self-test is required")
    print(json.dumps(validate(load(args.input)), sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "INVALID", "error": str(exc)}, sort_keys=True))
        sys.exit(2)
