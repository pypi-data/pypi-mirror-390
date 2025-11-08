import subprocess
import os
import shutil

def install_package(package_name):
    '''
    # Examp - install package
    ```py
    install_package("pyrogram")
    ```
    '''
    command = f"pip install {package_name}"
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    if process.returncode == 0:
        return "{package_name} Installed successfully !"
    else:
        return f"Installation failed with error: {error.decode('utf-8')}"

def uninstall_package(package_name):
    '''
    # Examp - uninstall package
    ```py
    uninstall_package("pyrogram")
    ```
    '''
    command = f"pip uninstall {package_name} -y"
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    
    if process.returncode == 0:
        return f"{package_name} uninstalled successfully !"
    else:
        return f"Uninstallation failed with error: {output.decode('utf-8')}"


def run_it(command, input_data=None):
    '''
    # Run  the shell commands

    ```py
    command = "pip uninstall pyrogarm"
    input_data = "Y"
    run_it(command)
    ```
    '''
    process = subprocess.Popen(
        command.split(),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    try:
        if input_data is not None:
            process.stdin.write(input_data)
        process.stdin.flush()
        output, error = process.communicate()
        if output:
            Output= "Output: ```\n" + output +"```"
            return Output
        elif error:
            # print("Error:", error)
            Error = "Error: ```\n"+ error + "\n```err"
            return Error
    except Exception as e:
        print(e)


def clone_repo(repo_url, destination:str=None):
    """
    a = clone_repo("https://github.com/heartlog/pasteconnect.git")
    print(a)
    """
    if destination is None:
        subprocess.run(['git', 'clone', repo_url])
    elif destination is not None:
        subprocess.run(['git', 'clone', repo_url, destination])

def delete_repo(repo_path):
    shutil.rmtree(repo_path)

# a = clone_repo("https://github.com/heartlog/pasteconnect.git", ".")
# print(a)

#b = delete_repo("repo")
#print(b)


# def run_simp(cmd):
#     out = subprocess.run(cmd)
#     print(out)

# def run_ssmiip(command):
#     try:
#         subprocess.check_output(command, shell=True)
#         print("Download completed")
#     except subprocess.CalledProcessError as e:
#         print(f"Download failed error code as {e.returncode}")


# print(run_it("pip uninstall pySmartDL", "Y"))