"""
One-off SFTP sync: pull evaluation outputs from the SecureSight server into ./evaluation/.
Requires: pip install paramiko

Environment:
  SSH_PASS       Password for SSH (do not commit; prefer SSH keys).
  SSH_HOST       Default 10.55.205.205
  SSH_PORT       Default 22
  SSH_USER       Default secure-sight
  REMOTE_EVAL    Override remote evaluation dir (single path).
"""

from __future__ import annotations

import os
import stat
import sys
from pathlib import Path

import paramiko

HOST = os.environ.get("SSH_HOST", "10.55.205.205")
PORT = int(os.environ.get("SSH_PORT", "22"))
USER = os.environ.get("SSH_USER", "secure-sight")
LOCAL_EVAL = Path(__file__).resolve().parent / "evaluation"


def _is_dir(attr: paramiko.SFTPAttributes) -> bool:
    return stat.S_ISDIR(attr.st_mode)


def sftp_pull_tree(sftp: paramiko.SFTPClient, remote_dir: str, local_dir: Path) -> None:
    local_dir.mkdir(parents=True, exist_ok=True)
    for attr in sftp.listdir_attr(remote_dir):
        name = attr.filename
        if name in (".", ".."):
            continue
        rp = f"{remote_dir.rstrip('/')}/{name}"
        lp = local_dir / name
        if _is_dir(attr):
            sftp_pull_tree(sftp, rp, lp)
        else:
            sftp.get(rp, str(lp))


def main() -> int:
    password = os.environ.get("SSH_PASS")
    if not password:
        print("Set SSH_PASS to the SSH password for this one-off sync.", file=sys.stderr)
        return 1

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, port=PORT, username=USER, password=password, timeout=30)

    override = os.environ.get("REMOTE_EVAL", "").strip()
    if override:
        cand = [override]
    else:
        stdin, stdout, stderr = client.exec_command(
            "ls -d /home/secure-sight/Code/output/evaluation "
            "/home/secure-sight/Code/tasnim/evaluation "
            "/home/secure-sight/Code/evaluation 2>/dev/null"
        )
        cand = [x.strip() for x in stdout.read().decode().splitlines() if x.strip()]
    err = stderr.read().decode()
    if err:
        print(err, file=sys.stderr)

    remote_sources = []
    for path in cand:
        stdin, stdout, stderr = client.exec_command(f"test -d '{path}' && echo OK")
        if stdout.read().decode().strip() == "OK":
            remote_sources.append(path)

    if not remote_sources:
        stdin, stdout, stderr = client.exec_command(
            "find /home/secure-sight -maxdepth 6 -type d -name detailed_results 2>/dev/null | head -5"
        )
        hints = stdout.read().decode().strip().splitlines()
        print("Could not find evaluation dirs. find hints:", hints, file=sys.stderr)
        client.close()
        return 2

    print("Remote evaluation roots:", remote_sources)
    sftp = client.open_sftp()

    for rs in remote_sources:
        name = rs.replace("/", "_").strip("_")[-80:] or "remote"
        dest = LOCAL_EVAL
        # If remote path ends with .../evaluation, merge contents into LOCAL_EVAL
        if rs.rstrip("/").endswith("/evaluation"):
            for attr in sftp.listdir_attr(rs):
                if attr.filename in (".", ".."):
                    continue
                rp = f"{rs.rstrip('/')}/{attr.filename}"
                lp = dest / attr.filename
                if _is_dir(attr):
                    sftp_pull_tree(sftp, rp, lp)
                else:
                    dest.mkdir(parents=True, exist_ok=True)
                    sftp.get(rp, str(lp))
        else:
            sub = dest / name
            sftp_pull_tree(sftp, rs, sub)

    sftp.close()
    client.close()
    print(f"Pulled into: {LOCAL_EVAL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
