import shutil
import os
import PyInstaller.__main__
# Not tested on non-Windows but it should work... I think?

def clean_folders(folders):
    for path in folders:
        if os.path.exists(path):
            try: shutil.rmtree(path)
            except: pass

print("Preparing folders for packaging...")

temp_dir = "temp"
dist_dir = "dist"
build_dir = "build"
data_dir = "data"
out_filename = "poe-gem-arbitrage-1.4.0-alpha"


temp_full_path = os.path.abspath(temp_dir)
dist_full_path = os.path.abspath(dist_dir)
data_full_path = os.path.abspath(dist_dir)

clean_folders([temp_dir, dist_dir, build_dir])
os.mkdir(temp_dir)

print("Running pyinstaller...")
PyInstaller.__main__.run([
    '.\gem-arbitrage.py',
    '--onefile',
    '--icon=data/icon.ico',
    '--hide-console=hide-early'
])
print("Copying binary and license...")
for f in os.listdir(dist_dir):
    shutil.copy(os.path.join(dist_dir, f), temp_full_path)
shutil.copy("../LICENSE", temp_full_path)

print("Adding data folder...")
shutil.copytree(data_dir, os.path.join(temp_dir, data_dir))

print("Zipping data...")
shutil.make_archive(out_filename, 'zip', temp_dir)

print("(Attempting to) clean up...")
clean_folders([dist_dir, build_dir, temp_dir])
if os.path.exists("gem-arbitrage.spec"):
    os.remove("gem-arbitrage.spec")