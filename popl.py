#!/usr/bin/env python3

import argparse
import os
import sys
import subprocess
import json
import venv

def get_venv_executables(venv_dir):
    if os.name == 'nt':  # Windows
        pip_executable = os.path.join(venv_dir, 'Scripts', 'pip.exe')
        python_executable = os.path.join(venv_dir, 'Scripts', 'python.exe')
    else:  # Unix-like systems (Linux, macOS)
        pip_executable = os.path.join(venv_dir, 'bin', 'pip')
        python_executable = os.path.join(venv_dir, 'bin', 'python')
    return python_executable, pip_executable


parser = argparse.ArgumentParser(prog='popl', description='A pip wrapper acting like npm')
subparsers = parser.add_subparsers(dest='command')

init_parser = subparsers.add_parser('init', help='Initialize a new popl project')
init_parser.add_argument('--import', dest="do_import", action='store_true', help='import requirements from requirements.txt into popl.json. Only necessary if you want to delete or clean requirements.txt')

def popl_init(do_import):
    project_file = 'popl.json'
    requirements_file = 'requirements.txt'
    venv_dir = os.path.join(os.getcwd(), '.venv')

    # if project file and virtual environment already exist, do nothing
    if os.path.exists(project_file) and os.path.exists(venv_dir):
        print('Project already initialized.')
        return
    
    # virtual environment setup
    if not os.path.exists(venv_dir):
        # Create virtual environment
        venv.create(venv_dir, with_pip=True)
        print('Initialized empty popl virtual environment.')
    else:
        print('Virtual environment already exists. Skipping creation.')
    
    # project file setup
    if not os.path.exists(project_file):
        project_data = {
            'name': os.path.basename(os.getcwd()),
            'dependencies': {}
        }
        with open(project_file, 'w') as f:
            json.dump(project_data, f, indent=4)
        print('Initialized empty popl.json.')
    else:
        print('popl.json found. skipping creation.')
    
    # requirements file setup
    if not os.path.exists(requirements_file):
        if do_import:
            # print warning message
            print('warning: --import flag is set but requirements.txt not found. Ignoring flag.')

        with open(requirements_file, 'w') as f:
            f.write('# this is your requirements lock file\n')
            print('Initialized empty requirements.txt.')
    else:
        if do_import:
            # print notice
            print('Importing requirements from requirements.txt into popl.json.')
            with open(requirements_file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if not line.startswith('#'):
                        project_data['dependencies'][line.strip()] = line.strip()
            # merge dependencies, favoring popl.json
            with open(project_file, 'w') as f:
                json.dump(project_data, f, indent=4)
            print('Imported requirements from requirements.txt into popl.json.')
        else:
            print('requirements.txt found. Use `popl install` to install dependencies.')
    


def init_from_requirements(requirements_file, write_to_popl_dependencies=False):
    project_file = 'popl.json'
    project_data = {
        'name': os.path.basename(os.getcwd()),
        'dependencies': [],
        'comment': "Note: core dependencies could not be determined from requirements.txt. 'popl install' still works though.",
        'from_requirements_no_core_dependencies': True
    }

    # Read dependencies from requirements.txt
    if write_to_popl_dependencies:
        with open(requirements_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if not line.startswith('#'):
                    project_data['dependencies'].append(line.strip())
        
    # Create popl.json with dependencies from requirements.txt
    with open(project_file, 'w') as f:
        json.dump(project_data, f, indent=4)
    print('Initialized popl project from requirements.txt.')

install_parser = subparsers.add_parser('install', help='Install packages')
install_parser.add_argument('packages', nargs='*', help='Packages to install')
install_parser.add_argument('--global', dest='global_install', action='store_true', help='Install globally')
install_parser.add_argument('pip_args', nargs=argparse.REMAINDER, help='Additional arguments for pip')

def popl_install(packages, global_install, pip_args, project_file=None, save=True, update_lock=True):
    # Ensure project is initialized
    project_file = find_project_file() if not project_file else project_file
    if not project_file:
        # check if requirements.txt exists and initialize from it
        if os.path.exists('requirements.txt'):
            popl_init({'skip_confirmation': False})
        else:
            print('Error: No popl project found. Run popl init first.')
            sys.exit(1)

    # Load project data
    with open(project_file, 'r') as f:
        project_data = json.load(f)

    # Define local packages directory
    local_packages_dir = os.path.join(os.path.dirname(project_file), 'local_packages')

    if not packages:
        # install all dependencies from requirements.txt
        if os.path.exists('requirements.txt'):
            with open('requirements.txt', 'r') as f:
                locked_packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                popl_install(locked_packages, False, pip_args, project_file, save=False, update_lock=False)

        # Install all additional dependencies from popl.json, pip will ignore already installed packages
        desired_packages = list(project_data['dependencies'].values())
        popl_install(desired_packages, False, pip_args, project_file, save=False, update_lock=True)
        return

    # Install packages globally
    if global_install:
        subprocess.run([sys.executable, '-m', 'pip', 'install'] + packages + pip_args)
        return

    # Install packages locally
    venv_dir = os.path.join(os.path.dirname(project_file), '.venv')
    _, pip_executable = get_venv_executables(venv_dir)
    if not os.path.exists(pip_executable):
        print('Error: Virtual environment not found. Run popl init again.')
        sys.exit(1)
    # Install packages using the virtual environment's pip
    pip_args = [pip_executable, 'install'] + packages + pip_args
    subprocess.run(pip_args)

    # Update project dependencies if new packages were provided
    if save:
        for package in packages:
            package_name = package.split('==')[0]
            project_data['dependencies'][package_name] = package

    # Save updated project data
    with open(project_file, 'w') as f:
        json.dump(project_data, f, indent=4)

    # Update requirements.txt
    # Capture the current state of installed packages using pip freeze
    result = subprocess.run([pip_executable, 'freeze'], capture_output=True, text=True)
    if result.returncode != 0:
        print('Error: Unable to update requirements.txt.')
        return
    with open('requirements.txt', 'w') as f:
        f.write(result.stdout)


def find_project_file():
    current_dir = os.getcwd()
    while True:
        project_file = os.path.join(current_dir, 'popl.json')
        if os.path.exists(project_file):
            return project_file
        new_dir = os.path.dirname(current_dir)
        if new_dir == current_dir:
            return None
        current_dir = new_dir

def setup_environment():
    project_file = find_project_file()
    if not project_file:
        print('Error: No popl project found.')
        sys.exit(1)
    local_packages_dir = os.path.join(os.path.dirname(project_file), 'local_packages')
    sys.path.insert(0, local_packages_dir)

run_parser = subparsers.add_parser('run', help='Run a python script with popl environment')
run_parser.add_argument('-m', '--module', dest='module_mode', action='store_true', help='Run as a module (python -m)')
run_parser.add_argument('script', help='Script or module to run')
run_parser.add_argument('script_args', nargs=argparse.REMAINDER, help='Arguments for the script')


def popl_run(module_mode, script, script_args):
    project_file = find_project_file()
    if not project_file:
        print('Error: No popl project found.')
        sys.exit(1)
    venv_dir = os.path.join(os.path.dirname(project_file), '.venv')
    python_executable, _ = get_venv_executables(venv_dir)
    if not os.path.exists(python_executable):
        print('Error: Virtual environment not found. Run popl init again.')
        sys.exit(1)
    
    # Prepare the command
    # Handle running a module with -m
    if module_mode:
        # Prepare the command to run the module
        command = [python_executable, '-m', script] + script_args
    else:
        # Handle running a Python script file
        script_path = os.path.abspath(script)
        if not os.path.exists(script_path):
            print(f'Error: Script {script} not found.')
            sys.exit(1)
        # Prepare the command
        command = [python_executable, script_path] + script_args
    
    # Execute the script or module
    subprocess.run(command)

exec_parser = subparsers.add_parser('exec', help='Execute a command in the popl environment')
exec_parser.add_argument('exec_command', nargs=argparse.REMAINDER, help='Command to execute in the popl environment')

def popl_exec(command_args):
    if not command_args:
        print('Error: No command provided to execute.')
        sys.exit(1)

    project_file = find_project_file()
    if not project_file:
        print('Error: No popl project found.')
        sys.exit(1)

    venv_dir = os.path.join(os.path.dirname(project_file), '.venv')
    python_executable, _ = get_venv_executables(venv_dir)
    if not os.path.exists(python_executable):
        print('Error: Virtual environment not found. Run popl init again.')
        sys.exit(1)

    # Prepare the environment variables to simulate activation
    if os.name == 'nt':
        venv_bin_dir = os.path.join(venv_dir, 'Scripts')
    else:
        venv_bin_dir = os.path.join(venv_dir, 'bin')

    env = os.environ.copy()
    env['PATH'] = venv_bin_dir + os.pathsep + env.get('PATH', '')

    # Include any necessary environment variables specific to virtual environments
    env['VIRTUAL_ENV'] = venv_dir

    # Execute the command
    subprocess.run(command_args, env=env, shell=True)



def main():
    args = parser.parse_args()
    if args.command == 'init':
        popl_init(args.do_import)
    elif args.command == 'install':
        popl_install(args.packages, args.global_install, args.pip_args)
    elif args.command == 'run':
        popl_run(args.module_mode, args.script, args.script_args)
    elif args.command == 'exec':
        popl_exec(args.exec_command)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
