from pypdl import Pypdl
# pypdl 1.4.2
def pypdl_download(url: str, save_dest: str, num_connections=10):
    dl = Pypdl()
    dl.start(url, save_dest, num_connections=num_connections, display=True, multithread=True)

def download(url, save_dest):
    pypdl_download(url, save_dest)

# Example usage:
# url = "https://streamtape.com/get_video?id=d71p7vqm6gSQ0W&expires=1694917360&ip=FHIsDRqOKxSHDN&token=1M3hCTNqKz7w"
# dest = "/content/GoogleColab/lfab.mp4"
# pypdl_download(url, dest)