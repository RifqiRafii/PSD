"""
Script: run_all_notebooks.py
Deskripsi: Menjalankan sel kode dari ketiga notebook secara terurut menggunakan .venv:
1. Klasifikasi_Tutupan_Lahan_Multikelas_Jatim.ipynb
2. klasifikasi_lulc_jatim.ipynb
3. klasifikasi_tutupan_lahan_6_kelas.ipynb

Menangkap output, mendeteksi error jika ada, dan menyimpan hasilnya.
"""

import os
import sys
import json
import traceback

NOTEBOOKS = [
    "materi/Klasifikasi_Tutupan_Lahan_Multikelas_Jatim.ipynb",
    "materi/klasifikasi_lulc_jatim.ipynb",
    "materi/klasifikasi_tutupan_lahan_6_kelas.ipynb"
]

def run_notebook(nb_path):
    print(f"\n{'='*70}\n[RUNNING NOTEBOOK]: {nb_path}\n{'='*70}")
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    # Lingkungan eksekusi lokal tersendiri per notebook
    # Ubah working directory ke direktori notebook untuk mencocokkan kernel Jupyter
    orig_cwd = os.getcwd()
    nb_dir = os.path.dirname(os.path.abspath(nb_path))
    os.chdir(nb_dir)
    print(f"Working directory: {os.getcwd()}")

    global_env = {
        "__name__": "__main__",
        "__file__": os.path.abspath(nb_path)
    }

    total_cells = len([c for c in nb["cells"] if c["cell_type"] == "code"])
    code_idx = 0

    for idx, cell in enumerate(nb["cells"]):
        if cell["cell_type"] != "code":
            continue
        code_idx += 1
        src = "".join(cell["source"])

        # Filter baris magic pip yang tidak perlu dieksekusi via exec
        clean_lines = []
        for line in src.splitlines():
            if line.strip().startswith("%pip") or line.strip().startswith("!pip"):
                clean_lines.append(f"# {line}")
            elif line.strip().startswith("%matplotlib") or line.strip().startswith("%time"):
                clean_lines.append(f"# {line}")
            else:
                clean_lines.append(line)
        code_to_exec = "\n".join(clean_lines)

        print(f"--> [Sel {code_idx}/{total_cells} (ID: {cell.get('id', idx)})]: ... ", end="", flush=True)

        try:
            exec(code_to_exec, global_env)
            print("BERHASIL")
        except Exception as e:
            print(f"\n[ERROR PADA SEL {code_idx}]:")
            print(f"Error type: {type(e).__name__}: {e}")
            traceback.print_exc(file=sys.stdout)
            os.chdir(orig_cwd)
            return False

    os.chdir(orig_cwd)
    print(f"[SUKSES PENUH]: Semua sel di {nb_path} berjalan mulus 100%!")
    return True

if __name__ == "__main__":
    results = {}
    for nb in NOTEBOOKS:
        results[nb] = run_notebook(nb)

    print("\n" + "="*70)
    print("RINGKASAN EKSEKUSI:")
    for nb, ok in results.items():
        status = "BERHASIL (100% SUCCESS)" if ok else "GAGAL (ERROR)"
        print(f" - {nb}: {status}")
    print("="*70)
