from pathlib import Path

import ctl
from ctl import _ctl_native


def test_signature_identity(identity_ctl):
    sig = _ctl_native.signature(str(identity_ctl))
    names = [p["name"] for p in sig["inputs"]]
    assert names == ["rIn", "gIn", "bIn"]
    assert all(p["varying"] for p in sig["inputs"])
    assert all(p["type"] == "float" for p in sig["inputs"])
    assert [p["name"] for p in sig["outputs"]] == ["rOut", "gOut", "bOut"]


def test_signature_required_param(required_param_ctl):
    sig = _ctl_native.signature(str(required_param_ctl))
    scale = next(p for p in sig["inputs"] if p["name"] == "scale")
    assert scale["varying"] is False
    assert scale["has_default"] is False


def test_python_signature_dataclass(identity_ctl):
    sig = ctl.signature(identity_ctl)
    assert [p.name for p in sig.inputs] == ["rIn", "gIn", "bIn"]
    assert all(p.varying for p in sig.inputs)
    assert sig.path == str(Path(identity_ctl).resolve())


def test_python_signature_accepts_str(identity_ctl):
    sig = ctl.signature(str(identity_ctl))
    assert sig.outputs[0].name == "rOut"


def test_python_signature_pretty_print(identity_ctl, capsys):
    sig = ctl.signature(identity_ctl)
    print(sig)
    captured = capsys.readouterr().out
    assert "rIn" in captured
    assert "varying" in captured
