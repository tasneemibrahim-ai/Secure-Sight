import argparse
import os
import posixpath
import sys
import time

import paramiko


REMOTE_PROJECT_DIR = "/home/secure-sight/Code/extracted_features_merged"
REMOTE_BACKUP_ROOT = "/home/secure-sight/Code/backup_previous_runs"
DATASET_DIRS = {"Normal_Videos", "Anomaly_Videos"}

# Only these locations are eligible for backup+delete.
# We intentionally do NOT touch any extracted_features_* directories to avoid deleting cached features that might
# actually be the dataset or expensive to regenerate.
REMOTE_OUTPUT_CANDIDATES = [
    "/home/secure-sight/Code/runs",
    "/home/secure-sight/Code/run",
    "/home/secure-sight/Code/logs",
    "/home/secure-sight/Code/log",
    "/home/secure-sight/Code/outputs",
    "/home/secure-sight/Code/output",
    "/home/secure-sight/Code/checkpoints",
    "/home/secure-sight/Code/checkpoint",
    "/home/secure-sight/Code/eval",
    "/home/secure-sight/Code/evaluation",
    "/home/secure-sight/Code/results",
    "/home/secure-sight/Code/result",
    "/home/secure-sight/Code/tensorboard",
    "/home/secure-sight/tasnim/outputs",
    "/home/secure-sight/tasnim/evaluation",
    "/home/secure-sight/tasnim/train_log.txt",
]


def _connect(host: str, username: str, password: str) -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, look_for_keys=False)
    return client


def _run(ssh: paramiko.SSHClient, command: str, *, timeout_s: int = 3600) -> tuple[int, str, str]:
    stdin, stdout, stderr = ssh.exec_command(command, get_pty=True, timeout=timeout_s)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    rc = stdout.channel.recv_exit_status()
    return rc, out, err


def _safe_write(text: str, *, stream: str = "stdout") -> None:
    data = text.encode("utf-8", errors="replace")
    if stream == "stderr":
        sys.stderr.buffer.write(data)
        sys.stderr.buffer.flush()
    else:
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()


def _remote_quote(s: str) -> str:
    return "'" + s.replace("'", "'\"'\"'") + "'"


def inventory_only(ssh: paramiko.SSHClient) -> None:
    cmds = [
        "set -euo pipefail",
        f"cd {_remote_quote(REMOTE_PROJECT_DIR)}",
        "echo '=== HOST ==='",
        "hostname && whoami && pwd",
        "echo '=== TOP-LEVEL CONTENTS ==='",
        "ls -la",
        "echo '=== TOP-LEVEL DIR SIZES (excluding dataset dirs) ==='",
        "for d in */ ; do "
        "  dn=${d%/}; "
        f"  if [ \"$dn\" = 'Normal_Videos' ] || [ \"$dn\" = 'Anomaly_Videos' ]; then continue; fi; "
        "  du -sh \"$dn\" 2>/dev/null || true; "
        "done",
        "echo '=== CANDIDATE OUTPUT DIRS/FILES (heuristic) ==='",
        "python3 - <<'PY'\n"
        "import os\n"
        "DATASET = {'Normal_Videos','Anomaly_Videos'}\n"
        "patterns = (\n"
        "  'run','runs','output','outputs','log','logs','checkpoint','checkpoints',\n"
        "  'eval','evaluation','result','results','cache','caches','tensorboard'\n"
        ")\n"
        "items = []\n"
        "for name in sorted(os.listdir('.')):\n"
        "  if name in DATASET: continue\n"
        "  lower = name.lower()\n"
        "  if any(p in lower for p in patterns):\n"
        "    items.append(name)\n"
        "print('\\n'.join(items) if items else '(none found)')\n"
        "PY",
    ]
    rc, out, err = _run(ssh, "bash -lc " + _remote_quote("\n".join(cmds)), timeout_s=3600)
    _safe_write(out)
    if err.strip():
        _safe_write(err, stream="stderr")
    if rc != 0:
        raise SystemExit(f"Inventory failed (rc={rc}).")


def probe_server_layout(ssh: paramiko.SSHClient) -> None:
    cmds = [
        "set -euo pipefail",
        "echo '=== HOME ==='",
        "pwd || true",
        "echo '=== WHOAMI/HOST ==='",
        "whoami && hostname",
        "echo '=== LS ~ ==='",
        "ls -la ~",
        "echo '=== LS ~/Code ==='",
        "ls -la ~/Code || true",
        "echo '=== FIND SECURESIGHT-LIKE DIRS (shallow) ==='",
        "python3 - <<'PY'\n"
        "import os\n"
        "roots = [os.path.expanduser('~'), os.path.expanduser('~/Code')]\n"
        "targets = []\n"
        "for root in roots:\n"
        "  if not os.path.isdir(root):\n"
        "    continue\n"
        "  for name in os.listdir(root):\n"
        "    p = os.path.join(root, name)\n"
        "    if os.path.isdir(p) and any(k in name.lower() for k in ('securesight','secure','sight','anomaly','ucf','crime','efficient','extract')):\n"
        "      targets.append(p)\n"
        "print('\\n'.join(sorted(set(targets))) if targets else '(none)')\n"
        "PY",
    ]
    rc, out, err = _run(ssh, "bash -lc " + _remote_quote("\n".join(cmds)), timeout_s=3600)
    _safe_write(out)
    if err.strip():
        _safe_write(err, stream="stderr")
    if rc != 0:
        raise SystemExit(f"Probe failed (rc={rc}).")


def backup_and_clean(ssh: paramiko.SSHClient) -> None:
    ts = time.strftime("%Y%m%d_%H%M%S")
    backup_dir = posixpath.join(REMOTE_BACKUP_ROOT, f"backup_{ts}")
    # Server-side: determine candidate items, copy them to backup, verify, then delete originals.
    cmds = [
        "set -euo pipefail",
        f"cd {_remote_quote(REMOTE_PROJECT_DIR)}",
        f"mkdir -p {_remote_quote(REMOTE_BACKUP_ROOT)}",
        f"mkdir -p {_remote_quote(backup_dir)}",
        "echo '=== BACKUP TARGET DIR ==='",
        f"echo {_remote_quote(backup_dir)}",
        "python3 - <<'PY'\n"
        "import os, json, sys\n"
        "DATASET = {'Normal_Videos','Anomaly_Videos'}\n"
        "patterns = (\n"
        "  'run','runs','output','outputs','log','logs','checkpoint','checkpoints',\n"
        "  'eval','evaluation','result','results','cache','caches','tensorboard'\n"
        ")\n"
        "items = []\n"
        "for name in sorted(os.listdir('.')):\n"
        "  if name in DATASET: continue\n"
        "  lower = name.lower()\n"
        "  if any(p in lower for p in patterns):\n"
        "    items.append(name)\n"
        "print(json.dumps(items))\n"
        "PY",
        "echo '=== ITEMS TO BACKUP (excluding dataset) ==='",
        "ITEMS_JSON=$(python3 - <<'PY'\n"
        "import os, json\n"
        "DATASET = {'Normal_Videos','Anomaly_Videos'}\n"
        "patterns = (\n"
        "  'run','runs','output','outputs','log','logs','checkpoint','checkpoints',\n"
        "  'eval','evaluation','result','results','cache','caches','tensorboard'\n"
        ")\n"
        "items = []\n"
        "for name in sorted(os.listdir('.')):\n"
        "  if name in DATASET: continue\n"
        "  lower = name.lower()\n"
        "  if any(p in lower for p in patterns):\n"
        "    items.append(name)\n"
        "print(json.dumps(items))\n"
        "PY"
        ")",
        "python3 - <<'PY'\n"
        "import json, os\n"
        "items = json.loads(os.environ['ITEMS_JSON'])\n"
        "print('\\n'.join(items) if items else '(none)')\n"
        "PY",
        "if [ \"$(python3 - <<'PY'\n"
        "import json, os\n"
        "items = json.loads(os.environ['ITEMS_JSON'])\n"
        "print(len(items))\n"
        "PY"
        ")\" -eq 0 ]; then echo 'Nothing to backup/clean.'; exit 0; fi",
        "echo '=== COPYING TO BACKUP (cp -a) ==='",
        f"python3 - <<'PY'\n"
        f"import json, os, subprocess, sys\n"
        f"backup_dir = {backup_dir!r}\n"
        f"items = json.loads(os.environ['ITEMS_JSON'])\n"
        f"for it in items:\n"
        f"  subprocess.check_call(['cp','-a',it,backup_dir])\n"
        f"print('Copied', len(items), 'items to', backup_dir)\n"
        f"PY",
        "echo '=== VERIFY BACKUP EXISTS ==='",
        f"python3 - <<'PY'\n"
        f"import json, os, sys\n"
        f"backup_dir = {backup_dir!r}\n"
        f"items = json.loads(os.environ['ITEMS_JSON'])\n"
        f"missing = [it for it in items if not os.path.exists(os.path.join(backup_dir, it))]\n"
        f"if missing:\n"
        f"  print('Missing in backup:', missing)\n"
        f"  sys.exit(2)\n"
        f"print('Backup verification OK')\n"
        f"PY",
        "echo '=== DELETING ORIGINALS (rm -rf) ==='",
        "python3 - <<'PY'\n"
        "import json, os, subprocess\n"
        "items = json.loads(os.environ['ITEMS_JSON'])\n"
        "for it in items:\n"
        "  subprocess.check_call(['rm','-rf',it])\n"
        "print('Deleted originals:', len(items))\n"
        "PY",
        "echo '=== POST-CLEAN TOP-LEVEL CONTENTS ==='",
        "ls -la",
        "echo '=== DONE ==='",
    ]
    rc, out, err = _run(ssh, "bash -lc " + _remote_quote("\n".join(cmds)), timeout_s=6 * 3600)
    sys.stdout.write(out)
    if err.strip():
        sys.stderr.write(err)
    if rc != 0:
        raise SystemExit(f"Backup/clean failed (rc={rc}).")


def inventory_outputs(ssh: paramiko.SSHClient) -> None:
    candidates = " ".join(_remote_quote(p) for p in REMOTE_OUTPUT_CANDIDATES)
    cmds = [
        "set -euo pipefail",
        "echo '=== OUTPUT INVENTORY (only known output paths) ==='",
        f"for p in {candidates}; do "
        "  if [ -e \"$p\" ]; then "
        "    echo \"--- $p ---\"; "
        "    ls -la \"$p\" | head -n 50 || true; "
        "    du -sh \"$p\" 2>/dev/null || true; "
        "  fi; "
        "done",
    ]
    rc, out, err = _run(ssh, "bash -lc " + _remote_quote("\n".join(cmds)), timeout_s=3600)
    _safe_write(out)
    if err.strip():
        _safe_write(err, stream="stderr")
    if rc != 0:
        raise SystemExit(f"Output inventory failed (rc={rc}).")


def backup_and_clean_outputs(ssh: paramiko.SSHClient) -> None:
    ts = time.strftime("%Y%m%d_%H%M%S")
    backup_dir = posixpath.join(REMOTE_BACKUP_ROOT, f"backup_{ts}")
    candidates = " ".join(_remote_quote(p) for p in REMOTE_OUTPUT_CANDIDATES)
    cmds = [
        "set -euo pipefail",
        f"mkdir -p {_remote_quote(REMOTE_BACKUP_ROOT)}",
        f"mkdir -p {_remote_quote(backup_dir)}",
        "echo '=== BACKUP TARGET DIR ==='",
        f"echo {_remote_quote(backup_dir)}",
        "echo '=== COPYING (cp -a) THEN DELETING (rm -rf) ==='",
        f"for p in {candidates}; do "
        "  if [ -e \"$p\" ]; then "
        "    base=$(basename \"$p\"); "
        "    echo \"Backing up $p -> " + backup_dir + "/$base\"; "
        f"    cp -a \"$p\" {_remote_quote(backup_dir)}/ || exit 2; "
        f"    if [ ! -e {_remote_quote(backup_dir)}/$base ]; then echo \"Backup missing for $p\"; exit 3; fi; "
        "    rm -rf \"$p\"; "
        "    echo \"Deleted $p\"; "
        "  fi; "
        "done",
        "echo '=== POST-CLEAN LS ~/Code (top) ==='",
        "ls -la ~/Code | head -n 200",
        "echo '=== DONE ==='",
    ]
    rc, out, err = _run(ssh, "bash -lc " + _remote_quote("\n".join(cmds)), timeout_s=6 * 3600)
    _safe_write(out)
    if err.strip():
        _safe_write(err, stream="stderr")
    if rc != 0:
        raise SystemExit(f"Output backup/clean failed (rc={rc}).")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="10.55.205.205")
    ap.add_argument("--username", default="secure-sight")
    ap.add_argument("--password_env", default="SECURESIGHT_SSH_PASSWORD")
    ap.add_argument("--probe", action="store_true", help="Probe server layout for code directories.")
    ap.add_argument("--inventory", action="store_true", help="Only inventory; no backup/clean.")
    ap.add_argument("--backup_clean", action="store_true", help="Backup then clean old runs/logs/checkpoints/eval/caches.")
    ap.add_argument("--inventory_outputs", action="store_true", help="Inventory known output paths under ~/Code.")
    ap.add_argument("--backup_clean_outputs", action="store_true", help="Backup then clean known output paths under ~/Code.")
    ap.add_argument("--exec", default=None, help="Run an arbitrary remote command (bash -lc).")
    ap.add_argument("--upload", nargs=2, metavar=("LOCAL_PATH", "REMOTE_PATH"), help="Upload a local file to remote path via SFTP.")
    args = ap.parse_args()

    password = os.environ.get(args.password_env)
    if not password:
        raise SystemExit(f"Missing env var {args.password_env} (SSH password).")

    ssh = _connect(args.host, args.username, password)
    try:
        if args.upload:
            local_path, remote_path = args.upload
            sftp = ssh.open_sftp()
            try:
                # Ensure remote parent exists
                parent = posixpath.dirname(remote_path.rstrip("/"))
                if parent:
                    rc, _, _ = _run(ssh, "bash -lc " + _remote_quote(f"mkdir -p {parent}"), timeout_s=3600)
                    if rc != 0:
                        raise SystemExit(f"Failed to create remote directory: {parent}")
                sftp.put(local_path, remote_path)
                print(f"Uploaded {local_path} -> {remote_path}")
            finally:
                sftp.close()
            return
        if args.exec:
            rc, out, err = _run(ssh, "bash -lc " + _remote_quote(args.exec), timeout_s=6 * 3600)
            _safe_write(out)
            if err.strip():
                _safe_write(err, stream="stderr")
            raise SystemExit(rc)
        if args.probe:
            probe_server_layout(ssh)
            return
        if args.inventory_outputs:
            inventory_outputs(ssh)
            return
        if args.backup_clean_outputs:
            backup_and_clean_outputs(ssh)
            return
        if args.backup_clean:
            backup_and_clean(ssh)
        else:
            inventory_only(ssh)
    finally:
        ssh.close()


if __name__ == "__main__":
    main()
