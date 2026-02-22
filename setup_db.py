import subprocess
import time
import socket
import sys

def check_port(host="localhost", port=5432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0

def log(msg):
    with open("setup.log", "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)

def main():
    log("================== NEW RUN ==================")
    log("Starting docker compose build...")
    # Hide stdout/stderr to completely bypass any windows terminal truncation / pipe issues that were aborting the process
    res_compose = subprocess.run(
        ["docker", "compose", "up", "-d", "--build"], 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL
    )
    if res_compose.returncode != 0:
        log(f"Docker compose failed with code {res_compose.returncode}")
        # Could just be pulling images. Try again.
        log("Trying again...")
        time.sleep(2)
        subprocess.run(["docker", "compose", "up", "-d", "--build"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    log("Waiting for DB to be ready on port 5432...")
    attempts = 0
    while not check_port() and attempts < 60:
        time.sleep(2)
        attempts += 1
    
    if attempts >= 60:
        log("Timeout waiting for DB port.")
        sys.exit(1)

    log("DB is up. Waiting 10s for Postgres configuration/restart...")
    time.sleep(10)

    log("Generating Alembic migrations...")
    res1 = subprocess.run(
        ["docker", "compose", "exec", "-T", "backend", "alembic", "revision", "--autogenerate", "-m", "Add pgvector"], 
        capture_output=True, text=True
    )
    log(f"Alembic revision output:\n{res1.stdout}\nError:\n{res1.stderr}")

    log("Applying Alembic migrations...")
    res2 = subprocess.run(
        ["docker", "compose", "exec", "-T", "backend", "alembic", "upgrade", "head"], 
        capture_output=True, text=True
    )
    log(f"Alembic upgrade output:\n{res2.stdout}\nError:\n{res2.stderr}")

    log("Setup complete.")

if __name__ == "__main__":
    main()
