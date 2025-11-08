# make to mount the drive only in google colab
import os
import getpass

code = '''
# make to mount the drive only in google colab
try:
    from google.colab import drive
except ImportError:
    pass
drive.mount('/content/drive')
'''

secret_file_path = '/content/drive/MyDrive/Colab Notebooks/secrets/secrets.txt'

def Google_Secret(secret_file_path=secret_file_path):
    with open(secret_file_path, 'r') as file:
        lines = file.readlines()

    # Loop through the lines and process each one
    for line in lines:
        parts = line.strip().split('=')
        if len(parts) == 2:
            env_name, env_value = parts[0], parts[1]
            OsEnv(env_name, env_value)

# set env variable 
def OsEnv(name, value):
    os.environ[name] = value
    print(f"{name} env is done.")

# [Optional]------
def SetEnv(name):
    secret = getpass.getpass(f"Enter value of {name}: ")
    os.environ[name] = secret

def getpSecret():
    SetEnv("api_id")
    SetEnv("api_hash")
    SetEnv("bot_token")
# ------
def SetPass(inp, secr_file=secret_file_path):
    if inp == "A":
        try:
            exec(code)
        except:
            pass
        Google_Secret(secr_file)
    elif inp == "B":
        getpSecret()

# SetPass("A")