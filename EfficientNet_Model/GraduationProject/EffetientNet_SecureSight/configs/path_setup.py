"""
Resolve evaluation / report directories from environment (server-safe defaults).
"""

import os


def get_code_root() -> str:
    return os.environ.get(
        "SECURESIGHT_CODE_ROOT",
        os.path.dirname(os.path.abspath(__file__)),
    )


def get_output_root() -> str:
    return os.environ.get(
        "SECURESIGHT_OUTPUT_ROOT",
        os.path.join(get_code_root(), "output"),
    )


def get_evaluation_base_dir() -> str:
    base = os.environ.get("SECURESIGHT_EVAL_BASE")
    if base:
        return base
    local_eval = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evaluation")
    if os.path.exists(local_eval):
        return local_eval
    return os.path.join(get_output_root(), "evaluation")


def get_evaluation_report_dir() -> str:
    return os.path.join(get_evaluation_base_dir(), "report")
