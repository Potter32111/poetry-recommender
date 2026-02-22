import subprocess
import time
import os

def log(msg):
    with open("build_process.log", "a", encoding="utf-8") as f:
        f.write(f"{time.ctime()}: {msg}\n")
    print(msg)

def run():
    log("Starting Docker Compose Build in background...")
    # Use -d and --build to ensure everything is rebuilt and started
    with open("docker_output.log", "w", encoding="utf-8") as out:
        process = subprocess.Popen(
            ["docker", "compose", "up", "-d", "--build"],
            stdout=out,
            stderr=out,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
        log(f"Process started with PID {process.pid}")
        
        while True:
            retcode = process.poll()
            if retcode is not None:
                log(f"Process finished with return code {retcode}")
                break
            time.sleep(10)
            log("Still building...")

if __name__ == "__main__":
    if os.path.exists("build_process.log"):
        os.remove("build_process.log")
    run()
