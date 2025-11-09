import subprocess, sys, importlib.metadata

def install_if_needed(package: str):
    try:
        current_version = importlib.metadata.version(package)
        result = subprocess.run(
            [sys.executable, "-m", "pip", "index", "versions", package],
            capture_output=True, text=True
        )
        if "LATEST" in result.stdout and current_version in result.stdout:
            return
        else:...
    except importlib.metadata.PackageNotFoundError:...

    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", package])
    except Exception as e:
        print(e)
packages = ["httpx", "h2", "h11", "certifi"]

for pkg in packages:
    install_if_needed(pkg)


from .Client import Client
