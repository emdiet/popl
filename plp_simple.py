#!/usr/bin/env python3

import argparse
import os
import sys
import subprocess
import json

parser = argparse.ArgumentParser(prog='plp', description='A pip wrapper acting like npm')
subparsers = parser.add_subparsers(dest='command')

init_parser = subparsers.add_parser('init', help='Initialize a new plp project')

def plp_init():
    project_file = 'plp.json'
    if os.path.exists(project_file):
        print('Project already initialized.')
        return
    project_data = {
        'name': os.path.basename(os.getcwd()),
        'dependencies': {}
    }
    with open(project_file, 'w') as f:
        json.dump(project_data, f, indent=4)
    print('Initialized empty plp project.')

install_parser = subparsers.add_parser('install', help='Install packages')
install_parser.add_argument('packages', nargs='*', help='Packages to install')
install_parser.add_argument('--global', action='store_true', help='Install globally')

def plp_install(packages, global_install):
    if global_install:
        subprocess.run([sys.executable, '-m', 'pip', 'install'] + packages)
        return

    # Ensure project is initialized
    project_file = find_project_file()
    if not project_file:
        print('Error: No plp project found. Run plp init first.')
        sys.exit(1)

    # Load project data
    with open(project_file, 'r') as f:
        project_data = json.load(f)

    # Define local packages directory
    local_packages_dir = os.path.join(os.path.dirname(project_file), 'local_packages')

    # Install packages locally
    pip_args = [sys.executable, '-m', 'pip', 'install', '--target', local_packages_dir] + packages
    subprocess.run(pip_args)

    # Update project dependencies
    for package in packages:
        package_name = package.split('==')[0]
        project_data['dependencies'][package_name] = package

    # Save updated project data
    with open(project_file, 'w') as f:
        json.dump(project_data, f, indent=4)

def find_project_file():
    current_dir = os.getcwd()
    while True:
        project_file = os.path.join(current_dir, 'plp.json')
        if os.path.exists(project_file):
            return project_file
        new_dir = os.path.dirname(current_dir)
        if new_dir == current_dir:
            return None
        current_dir = new_dir

def setup_environment():
    project_file = find_project_file()
    if not project_file:
        print('Error: No plp project found.')
        sys.exit(1)
    local_packages_dir = os.path.join(os.path.dirname(project_file), 'local_packages')
    sys.path.insert(0, local_packages_dir)

run_parser = subparsers.add_parser('run', help='Run a script with plp environment')
run_parser.add_argument('script', help='Script to run')
run_parser.add_argument('script_args', nargs=argparse.REMAINDER, help='Arguments for the script')

def plp_run(script, script_args):
    setup_environment()
    script_path = os.path.abspath(script)
    if not os.path.exists(script_path):
        print(f'Error: Script {script} not found.')
        sys.exit(1)
    # Prepare the command
    command = [sys.executable, script_path] + script_args
    # Execute the script
    subprocess.run(command, env=os.environ)

def plp_install(packages, global_install):
    # Ensure project is initialized
    project_file = find_project_file()
    if not project_file:
        print('Error: No plp project found. Run plp init first.')
        sys.exit(1)

    # Load project data
    with open(project_file, 'r') as f:
        project_data = json.load(f)

    # Define local packages directory
    local_packages_dir = os.path.join(os.path.dirname(project_file), 'local_packages')

    if not packages:
        # Install all dependencies from plp.json
        packages = list(project_data['dependencies'].values())

    if global_install:
        subprocess.run([sys.executable, '-m', 'pip', 'install'] + packages)
        return

    # Install packages locally
    pip_args = [sys.executable, '-m', 'pip', 'install', '--target', local_packages_dir] + packages
    subprocess.run(pip_args)

    # Update project dependencies if new packages were provided
    for package in packages:
        package_name = package.split('==')[0]
        project_data['dependencies'][package_name] = package

    # Save updated project data
    with open(project_file, 'w') as f:
        json.dump(project_data, f, indent=4)

def main():
    args = parser.parse_args()
    if args.command == 'init':
        plp_init()
    elif args.command == 'install':
        plp_install(args.packages, args.global)
    elif args.command == 'run':
        plp_run(args.script, args.script_args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
