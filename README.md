# plp
plp: python lone projects. pip, but more like npm

## What is this?

This is a pip wrapper that keeps all dependencies in your project direcory, and manages virtual enviroments behind the scenes.

It's like npm(lite), but for python.


## Usage

1) have python/pip installed
2) copy plp.py into your project directory
3) inside your project directory run `python ./plp.py init`
4) install packages like you would with pip: `python ./plp.py install <packages, args, etc.>`
5) run your python scripts with `python ./plp.py run <script-name.py>`

e.g.: 

```powershell
python ./plp.py init
python ./plp.py install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
python ./plp.py run my_inference_script.py
```

 just works. (in windows). no need to activate virtual environments, no need to worry about global packages, no need to worry about system packages.

## Motivation

I wanted to install pytorch cuda (https://pytorch.org/get-started/locally/), but 
1) installing it with pip is a bad idea, according to everyone
2) I'm afraid of forgetting to activate/deactivate virtual environments
3) the poetry maintainers are jerks (https://github.com/python-poetry/poetry/issues/7685)
4) activating virtual environments on windows doesn't actually work unless you set the execution policy to unrestricted (https://stackoverflow.com/questions/18713086/virtualenv-wont-activate-on-windows). How about... no?

So that's how bob's your uncle.

## How it works

1) `init` creates a virtual environment called `.venv` (your "node_modules") and a `plp.json` (your "package.json") file in the current directory
2) `install` installs the package into the `.venv` virtual environment, and adds it to the `plp.json` file, and uses the standard `requirements.txt` as your lock file, meaning your pip friends or your docker build or whatever can just use that if they don't want to use plp.
3) `run` ensures that the script is run in the `.venv` virtual environment. 

## Notes on: requirements.txt

`install` will honor the requirements.txt file if it exists, even if the dependencies are not in plp.py. plp will still properly install everything in the appropriate virtual environment, so you can use plp with your existing projects.

## Notes on: plp.json

`plp.json` is where your core dependencies could live, if you wanted to reinstall the project. It's like a lightweight version of the `package.json` file. You can ignore it if you want, and use the requirements.txt to port your dependencies. It might be useful however if you want to clean your dependencies at some point.

## Notes on: Using this collabortively with git:

add `.venv` to your `.gitignore` file

your buddies can just work with the requirements.txt file if they don't want to use plp.

## Dependencies

- python

## Feature Requests

please open an issue, thx :)