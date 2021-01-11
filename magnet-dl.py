#!/usr/bin/env python3

import libtorrent as lt
import time
import sys
import os
import subprocess
import datetime


#TODO: https://github.com/danfolkes/Magnet2Torrent/blob/master/Magnet_To_Torrent2.py
#TODO: torrent fille support, auto save torrent file if magnet or hash is given


if len(sys.argv) <= 1:
    print("please provide a magnet link in quotes or a 40 characher hex hash as the only arguement")
    sys.exit(1)
elif len(sys.argv[1]) == 40:
    for i in sys.argv[1]:
        if not (i in "0123456789abcdefABCDEF"):
            print("invalid hash")
            sys.exit(1)
    hash = sys.argv[1]
    magnet_string = 'magnet:?xt=urn:btih:' + hash + '&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969&tr=udp%3A%2F%2Fzer0day.ch%3A1337&tr=udp%3A%2F%2Fopen.demonii.com%3A1337&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'
elif sys.argv[1][0:20] == 'magnet:?xt=urn:btih:':
    magnet_string = sys.argv[1]
else:
    print("invalid magnet link, it must formatted like  'magnet:?xt=urn:btih:' + HASH + '&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969%2Fannounce' ")
    sys.exit(1)


ses = lt.session({'listen_interfaces': '0.0.0.0:6881'})
params = {
    'save_path': '.',
    'storage_mode': lt.storage_mode_t(2),
#    'paused': False,
#    'auto_managed': True,
#    'duplicate_is_error': True
}

print(magnet_string)
handle = lt.add_magnet_uri(ses, magnet_string, params)
while (not handle.has_metadata()):
    time.sleep(.1)
info = handle.get_torrent_info()
h = ses.add_torrent({'ti': info, 'save_path': '.'})
h.set_sequential_download(True)
#h.set_upload_limit(1) # set upload to 2kB/s
s = h.status()
print('starting', s.name)
initializing = True
file_list = []

#print(dir(info))
#print(info.total_size())
#exit()

for x in range(info.files().num_files()):
        file_list.append(info.files().file_path(x))
        print(info.files().file_path(x))
print("Files:")
for i in file_list:
    print(i)
    if i.split('.')[-1] in ('avi', 'mp4', 'mkv'):
        vid_file = i
        break
while (not s.is_seeding):
    s = h.status()
    remaining_bytes = info.total_size() - s.total_done
    if s.download_rate > 0:
        remaining_seconds = remaining_bytes / s.download_rate 
        remaining_time = str(datetime.timedelta(seconds = remaining_seconds)).split(".")[0]
    else:
        remaining_time = "STALLED"
    print('\r%.2f%% complete (down: %.1f kB/s up: %.1f kB/s peers: %d remaining: %s) %s         ' % (
        s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000,
        s.num_peers, remaining_time, s.state), end=' ')


    if initializing and s.progress > 0.05:
        initializing = False
    alerts = ses.pop_alerts()
    for a in alerts:
        if a.category() & lt.alert.category_t.error_notification:
            print(a)
    sys.stdout.flush()
    time.sleep(1)
print(h.name(), 'complete')



