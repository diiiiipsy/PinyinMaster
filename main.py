import subprocess

def run_script(script_name):
    result = subprocess.run(['python', script_name], capture_output=True, text=True, check=True)
    print(result.stdout)

def run_script_silently(script_name):
    subprocess.run(['python', script_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

if __name__ == "__main__":
    run_script_silently('./src/processor.py')
    run_script('./src/test.py')