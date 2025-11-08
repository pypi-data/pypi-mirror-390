import os
from .pypdl import pypdl_download

# magnet = "magnet:?xt=urn:btih:8B7E180839C73FA9E1534CAE6CC31079D0A0D059&dn=Wednesday.S01.COMPLETE.720p.NF.WEBRip.x264-GalaxyTV&tr=udp://tracker.coppersurfer.tk:6969/announce&tr=udp://9.rarbg.to:2920/announce&tr=udp://tracker.opentrackr.org:1337&tr=udp://tracker.internetwarriors.net:1337/announce&tr=udp://tracker.leechers-paradise.org:6969/announce&tr=udp://tracker.coppersurfer.tk:6969/announce&tr=udp://tracker.pirateparty.gr:6969/announce&tr=udp://tracker.cyberia.is:6969/announce"

# dir = "/content/torr"


code = """
from torrentp import TorrentDownloader
torrent_file = TorrentDownloader('{}', '{}')
torrent_file.start_download()
"""


def torrent(magnet_URL, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    exec(code.format(magnet_URL, save_dir))

# dest .torrent save 
# save_dir torrent_files save
def torrent_fileurl(file_url, dest, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    try:
        pypdl_download(file_url, dest)
        torrent(dest, save_dir)
    except Exception as e:
        print(e)

# torrent will work same
def torrent_file(file_path, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    try:
        torrent(file_path, save_dir)
    except Exception as e:
        print(e)