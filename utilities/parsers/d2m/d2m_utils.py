import os
import subprocess


# dont call this from the code directly, made to be run only on a docker build
def initial_setup():
    work_dir = os.path.dirname(os.path.abspath(__file__))
    command = ["npx", "--yes", "d2m@latest", "-h"]
    install_run = subprocess.run(command, capture_output=True, text=True, cwd=work_dir)
    if install_run.returncode != 0:
        print(f"Cannot install d2m. Error: {install_run.stderr}")
        exit(1)
    print("Sucessfully installed d2m.")