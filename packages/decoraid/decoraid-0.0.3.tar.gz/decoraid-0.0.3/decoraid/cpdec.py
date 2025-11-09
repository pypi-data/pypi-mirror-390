# cpdec --> check package decorator

import subprocess
import functools
import os
import re

def check_package(package: str, venv_path: str):
    def decorator_check_package(func):
        @functools.wraps(func)
        def wrapper_check_package(*args, **kwargs):
            # Determine the correct activation script based on the OS
            if os.name == 'nt':  # Windows
                activate_script = f"{venv_path}\\Scripts\\activate.bat"
                command = f"cmd /c {activate_script} && pip list"
            else:  # Linux/Unix/Mac
                activate_script = f"{venv_path}/bin/activate"
                command = f"source {activate_script} && pip list"
            
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, executable='/bin/bash' if os.name != 'nt' else None)
                if result.returncode == 0:
                    installed_packages = result.stdout
                    package_pattern = re.compile(rf"{package.replace('==', '==|==').replace('<', '<|==').replace('>', '>|==')}\s.*", re.IGNORECASE)
                    if any(package_pattern.search(line) for line in installed_packages.split('\n')):
                        print(f"{package} is installed in the selected environment here ~ {venv_path}.")
                        return func(*args, **kwargs)
                    else:
                        print(f"{package} is NOT installed in the selected environment here ~ {venv_path}. Function '{func.__name__}' will not be executed.")
                        return None
                else:
                    print(f"Failed to list packages in the virtual environment: {result.stderr}")
                    return None
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                return None

        return wrapper_check_package
    return decorator_check_package


if __name__ == '__main__':
    check_package()

