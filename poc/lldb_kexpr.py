"""LLDB command: kexpr

Inside LLDB:
    command script import /absolute/path/to/lldb_kexpr.py
    kexpr x + y * factor
"""

from __future__ import annotations
import os
import sys

try:
    import lldb
except ImportError as exc:
    raise RuntimeError("This module must be imported by an LLDB Python environment") from exc

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from kexpr_core import KExprError, SafeKotlinEvaluator

_INTEGER_HINTS = (
    "int", "long", "short", "byte",
    "uint", "ulong", "ushort", "ubyte",
    "int8", "int16", "int32", "int64",
    "uint8", "uint16", "uint32", "uint64",
)
_FLOAT_HINTS = ("float", "double")
_BOOL_HINTS = ("bool", "boolean")


def _convert_primitive(value):
    type_name = (value.GetTypeName() or "").lower()
    raw = value.GetValue()

    if any(h in type_name for h in _BOOL_HINTS):
        if raw is not None:
            s = raw.strip().lower()
            if s in ("true", "1"):
                return True
            if s in ("false", "0"):
                return False
        return bool(value.GetValueAsUnsigned())

    if any(h in type_name for h in _FLOAT_HINTS):
        if raw is None:
            raise ValueError("floating-point value unavailable")
        return float(raw)

    if any(h in type_name for h in _INTEGER_HINTS):
        if raw is not None:
            try:
                return int(raw, 0)
            except ValueError:
                pass
        return int(value.GetValueAsSigned())

    raise ValueError(f"unsupported type: {type_name}")


def _collect_frame_primitives(frame):
    env = {}
    values = frame.GetVariables(True, True, False, True)

    for index in range(values.GetSize()):
        value = values.GetValueAtIndex(index)
        name = value.GetName()
        if not name:
            continue
        try:
            env[name] = _convert_primitive(value)
        except Exception:
            continue

    return env


def _selected_frame(debugger):
    target = debugger.GetSelectedTarget()
    if not target or not target.IsValid():
        raise KExprError("No valid target is selected")

    process = target.GetProcess()
    if not process or not process.IsValid():
        raise KExprError("No valid process is selected")

    thread = process.GetSelectedThread()
    if not thread or not thread.IsValid():
        raise KExprError("No valid thread is selected")

    frame = thread.GetSelectedFrame()
    if not frame or not frame.IsValid():
        raise KExprError("No valid stack frame is selected")

    return frame


def kexpr(debugger, command, result, internal_dict):
    expression = command.strip()
    if not expression:
        result.SetError("usage: kexpr <Kotlin-like expression>")
        return

    try:
        frame = _selected_frame(debugger)
        env = _collect_frame_primitives(frame)
        if not env:
            raise KExprError("No supported primitive locals/arguments are available")

        value = SafeKotlinEvaluator(env).evaluate(expression)
        rendered = "true" if value is True else "false" if value is False else repr(value)
        result.AppendMessage(rendered)
    except Exception as exc:
        result.SetError(str(exc))


def kexpr_vars(debugger, command, result, internal_dict):
    try:
        frame = _selected_frame(debugger)
        env = _collect_frame_primitives(frame)
        if not env:
            result.AppendMessage("<no supported primitive values>")
            return

        for name in sorted(env):
            value = env[name]
            rendered = "true" if value is True else "false" if value is False else repr(value)
            result.AppendMessage(f"{name} = {rendered}")
    except Exception as exc:
        result.SetError(str(exc))


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand("command script add -f lldb_kexpr.kexpr kexpr")
    debugger.HandleCommand("command script add -f lldb_kexpr.kexpr_vars kexpr-vars")
    print("Installed commands: kexpr, kexpr-vars")
