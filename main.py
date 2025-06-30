import os
import sys
from dotenv import load_dotenv
import subprocess
import shutil
from datetime import datetime

# Load konfigurasi dari file .env
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")  # format: mongodb+srv://user:pass@cluster/db
DATABASE = os.getenv("MONGO_DATABASE")
RCLONE_DIR = os.getenv("RCLONE_DIR", "rclone-gdrive")

date_str = datetime.now().strftime("%Y%m%d")
BACKUP_DIR = f"{date_str}_{DATABASE}_backup"
ARCHIVE_FILE = f"{BACKUP_DIR}.gz"

def backup_mongodb(uri, database, backup_dir):
    try:
        # Dump database MongoDB
        command = [
            "mongodump",
            f"--uri={uri}",
            f"--db={database}",
            f"--out={backup_dir}"
        ]
        subprocess.run(command, check=True)
        print(f"Backup MongoDB berhasil disimpan ke direktori '{backup_dir}'.")

        # Kompres hasil backup ke tar.gz
        subprocess.run(["tar", "-czvf", ARCHIVE_FILE, backup_dir], check=True)
        print(f"Backup dikompres menjadi file '{ARCHIVE_FILE}'.")

        # Pindahkan file ke direktori rclone
        shutil.move(ARCHIVE_FILE, RCLONE_DIR)
        print(f"File '{ARCHIVE_FILE}' berhasil dipindahkan ke direktori rclone '{RCLONE_DIR}'.")

        # Hapus folder hasil dump setelah dikompres
        shutil.rmtree(backup_dir)

    except Exception as e:
        print(f"Terjadi kesalahan saat backup MongoDB: {str(e)}")

def restore_mongodb(uri, database, archive_file):
    try:
        # Ekstrak file tar.gz
        subprocess.run(["tar", "-xzvf", archive_file], check=True)
        extracted_folder = archive_file.replace(".tar.gz", "")
        print(f"File '{archive_file}' berhasil diekstrak ke folder '{extracted_folder}'.")

        # Restore database MongoDB
        command = [
            "mongorestore",
            f"--uri={uri}",
            f"--db={database}",
            f"{extracted_folder}/{database}"
        ]
        subprocess.run(command, check=True)
        print(f"Database MongoDB '{database}' berhasil direstore dari '{archive_file}'.")

        # Hapus folder setelah restore
        shutil.rmtree(extracted_folder)

    except Exception as e:
        print(f"Terjadi kesalahan saat restore MongoDB: {str(e)}")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        print("Pilih operasi:")
        print("1. Backup MongoDB")
        print("2. Restore MongoDB")
        choice = input("Masukkan pilihan Anda (1/2): ")

    if choice == '1':
        backup_mongodb(MONGO_URI, DATABASE, BACKUP_DIR)
    elif choice == '2':
        archive_input = input("Masukkan nama file .tar.gz untuk restore: ").strip()
        restore_mongodb(MONGO_URI, DATABASE, archive_input)
    else:
        print("Pilihan tidak valid.")

