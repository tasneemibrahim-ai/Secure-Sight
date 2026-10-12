import paramiko
import sys
import os

def execute_remote(command):
    host = "10.55.205.205"
    user = "secure-sight"
    pw = "S#SiT#$38337"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=pw)
        stdin, stdout, stderr = client.exec_command(command)
        out = stdout.read().decode()
        err = stderr.read().decode()
        if out: print(out)
        if err: print(err)
    finally:
        client.close()

def upload_file(local_path, remote_path):
    host = "10.55.205.205"
    user = "secure-sight"
    pw = "S#SiT#$38337"
    
    transport = paramiko.Transport((host, 22))
    transport.connect(username=user, password=pw)
    sftp = paramiko.SFTPClient.from_transport(transport)
    try:
        sftp.put(local_path, remote_path)
        print(f"Uploaded {local_path} to {remote_path}")
    finally:
        sftp.close()
        transport.close()

if __name__ == "__main__":
    if sys.argv[1] == "upload":
        upload_file(sys.argv[2], sys.argv[3])
    else:
        execute_remote(sys.argv[1])
