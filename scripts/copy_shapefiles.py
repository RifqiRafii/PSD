import os
import shutil

base_dir = r"data\geojson"

# Mapping kelas ke folder sumber
src_map = {
    "sawah": os.path.join(base_dir, "sawah"),
    "bangunan": os.path.join(base_dir, "bangunan"),
    "mangrove": os.path.join(base_dir, "mangrove"),
    "lahan_hijau": os.path.join(base_dir, "lahan hijau"),
    "lahan hijau": os.path.join(base_dir, "lahan hijau"),
    "laut_lepas": os.path.join(base_dir, "laut"),
    "laut": os.path.join(base_dir, "laut"),
    "danau": os.path.join(base_dir, "Danau"),
    "Danau": os.path.join(base_dir, "Danau")
}

# Salin ke materi/sampel/{kelas} dan sampel/{kelas}
dest_bases = [
    r"materi\sampel",
    r"sampel",
    r"materi",
    r"."
]

# Juga nama alias untuk notebook Klasifikasi_Tutupan_Lahan_Multikelas_Jatim.ipynb
alias_map = {
    "Sampel Sawah": os.path.join(base_dir, "sawah"),
    "Sampel Non-sawah": os.path.join(base_dir, "bangunan"),
    "mangrove": os.path.join(base_dir, "mangrove"),
    "lahan hijau": os.path.join(base_dir, "lahan hijau"),
    "laut_lepas": os.path.join(base_dir, "laut"),
    "Danau": os.path.join(base_dir, "Danau")
}

for folder_name, src_path in alias_map.items():
    for parent in [r"materi", r"."]:
        target = os.path.join(parent, folder_name)
        os.makedirs(target, exist_ok=True)
        for f in os.listdir(src_path):
            shutil.copy2(os.path.join(src_path, f), os.path.join(target, f))

for folder_name, src_path in src_map.items():
    for parent in [r"materi\sampel", r"sampel"]:
        target = os.path.join(parent, folder_name)
        os.makedirs(target, exist_ok=True)
        for f in os.listdir(src_path):
            shutil.copy2(os.path.join(src_path, f), os.path.join(target, f))

print("Semua shapefile berhasil didistribusikan ke direktori target!")
