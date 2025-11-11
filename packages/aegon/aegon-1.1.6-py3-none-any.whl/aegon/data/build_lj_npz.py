import numpy as np
from pathlib import Path

def parse_xyz_concatenated(xyz_file):
    with open(xyz_file) as f:
        lines = [ln.strip() for ln in f if ln.strip()]

    clusters = {}
    i = 0
    while i < len(lines):
        n_atoms = int(lines[i]); i += 1
        header = lines[i].split(); i += 1
        energy = float(header[0])
        label = header[1] if len(header) > 1 else f"LJ{n_atoms:03d}"

        coords = []
        for _ in range(n_atoms):
            parts = lines[i].split(); i += 1
            coords.append([float(x) for x in parts[1:4]])

        clusters[n_atoms] = {
            "energy": energy,
            "label": label,
            "positions": np.array(coords, dtype=np.float64)
        }

    return clusters


def build_npz(xyz_file="Wales003to150.xyz", output="lj_clusters_data.npz"):
    clusters = parse_xyz_concatenated(xyz_file)
    np.savez_compressed(
        output,
        **{f"LJ{n:03d}": clusters[n] for n in sorted(clusters)}
    )
    print(f"✅ Archivo comprimido creado: {output} ({len(clusters)} estructuras).")


if __name__ == "__main__":
    build_npz()

