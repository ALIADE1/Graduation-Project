import os
import zipfile
import urllib.request
import sys

# Direct download URL
url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
zip_filename = "ffmpeg_temp.zip"

def progress_bar(block_num, block_size, total_size):
    downloaded = block_num * block_size
    if total_size > 0:
        percent = downloaded * 100 / total_size
        sys.stdout.write(f"\r⏳ Downloading: {percent:.1f}% ({downloaded / (1024*1024):.1f} MB)")
        sys.stdout.flush()

print("🚀 Starting FFmpeg download (approx 130MB)...")

try:
    # 1. Download with progress bar
    urllib.request.urlretrieve(url, zip_filename, progress_bar)
    print("\n\n📦 Download complete! Extracting files...")

    # 2. Extract specific files
    with zipfile.ZipFile(zip_filename, 'r') as z:
        count = 0
        for filename in z.namelist():
            if filename.endswith("bin/ffmpeg.exe") or filename.endswith("bin/ffprobe.exe"):
                target_name = os.path.basename(filename)
                print(f"   Extracting -> {target_name}")
                with open(target_name, "wb") as f:
                    f.write(z.read(filename))
                count += 1
    
    # 3. Cleanup
    if os.path.exists(zip_filename):
        os.remove(zip_filename)

    if count == 2:
        print("\n✅ Success! FFmpeg installed successfully.")
        print("You can now run: python run.py server")
    else:
        print("\n⚠️ Warning: Could not find ffmpeg files in the zip.")

except Exception as e:
    print(f"\n❌ Error occurred: {e}")

input("\nPress Enter to exit...")