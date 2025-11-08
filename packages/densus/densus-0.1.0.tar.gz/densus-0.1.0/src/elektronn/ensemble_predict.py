import warnings
import sys
import itertools
import pickle
from . import utils
from . import visualization_utils
import torch
import copy
import argparse
from torch_geometric.data import Data
import csv
from datetime import datetime
import pathlib
import os
import numpy as np
from pathlib import Path

# load basisfunction params (ok to run on import)
basisfunction_params = pickle.load(open(Path(__file__).with_name("basisfunction_params.pkl"), "rb"))

angstrom2bohr = 1.8897259886

# ----------------------- Functions only (no script code here) ----------------------- #

def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def read_xyz_file_corrected(file_path):
    import periodictable
    with open(file_path, "r") as file:
        lines = file.readlines()[2:]

    atom_types_list, positions_list = [], []

    for line in lines:
        parts = line.split()
        if len(parts) < 4:
            continue
        atom_type, x, y, z = parts[:4]
        element = getattr(periodictable, atom_type)
        atomic_number = int(element.number)
        atom_types_list.append(atomic_number)
        positions_list.append([float(x), float(y), float(z)])

    positions = torch.tensor(positions_list, dtype=torch.float64)
    exponents = torch.tensor([list(map(float, basisfunction_params[a]["exp"])) for a in atom_types_list], dtype=torch.float64)
    norms = torch.tensor([list(map(float, basisfunction_params[a]["norm"])) for a in atom_types_list], dtype=torch.float64)
    atom_types_tensor = torch.tensor(atom_types_list, dtype=torch.long)
    onehot = torch.eye(18)[atom_types_tensor]

    return atom_types_tensor, onehot, positions, exponents, norms, np.array(atom_types_list), file_path


def get_iso_permuted_molecule(x, pos_orig, atomic_numbers, exps, norms, filename):
    x = torch.tensor(x)
    pos_orig = torch.tensor(pos_orig)
    atomic_numbers = torch.tensor(atomic_numbers)
    exp = torch.tensor(exps)
    norm = torch.tensor(norms)

    p_pos = copy.deepcopy(pos_orig)
    p_pos[:, 0] = pos_orig[:, 1]
    p_pos[:, 1] = pos_orig[:, 2]
    p_pos[:, 2] = pos_orig[:, 0]

    return Data(
        pos=p_pos.float(),
        pos_orig=pos_orig.float(),
        x=x.float(),
        exp=exp.float(),
        norm=norm.float(),
        atomic_numbers=atomic_numbers,
        filename=filename,
    )


def read_molecule_from_xyz(file_path, version):
    if version == "2.0":
        data_in = read_xyz_file_corrected(file_path)
    else:
        raise ValueError("Only version 2.0 supported in pip package")
    return get_iso_permuted_molecule(*data_in[:6])


def ElektroNN_Ensemble(data, models_specified, map_location):
    print("predicting", data.filename)
    mask = (data.exp != 0).float().detach()
    data = data.to(map_location)
    preds = [m(data) * mask.to(map_location) for m in models_specified]
    return torch.stack(preds).mean(0)


def save_to_pickle(obj, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as file:
        pickle.dump(obj, file)
        
def write_cube_file(filename, atomic_numbers, positions, x, y, z, density):
    # Calculate the origin and spacing
    angstrom2bohr = 1.8897259886

    origin = np.array([x.min(), y.min(), z.min()])
    angstrom_origin = origin * angstrom2bohr
    angstrom_positions = positions * angstrom2bohr
    angstrom_x = x * angstrom2bohr
    angstrom_y = y * angstrom2bohr
    angstrom_z = z * angstrom2bohr

    spacing = np.array(
        [x[1, 0, 0] - x[0, 0, 0], y[0, 1, 0] - y[0, 0, 0], z[0, 0, 1] - z[0, 0, 0]]
    )
    angstrom_spacing = spacing * angstrom2bohr
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(filename, "w") as file:
        file.write("Cube file after density fitting\n")
        
        file.write(f"Electron density (e-/bohr**3) Creation date: {current_date}\n")
        file.write(
            f"{len(atomic_numbers):5d}{angstrom_origin[0]:12.6f}{angstrom_origin[1]:12.6f}{angstrom_origin[2]:12.6f}\n"
        )
        file.write(f"{angstrom_x.shape[0]:5d}{angstrom_spacing[0]:12.6f}{0.0:12.6f}{0.0:12.6f}\n")
        file.write(f"{angstrom_y.shape[1]:5d}{0.0:12.6f}{angstrom_spacing[1]:12.6f}{0.0:12.6f}\n")
        file.write(f"{angstrom_z.shape[2]:5d}{0.0:12.6f}{0.0:12.6f}{angstrom_spacing[2]:12.6f}\n")

        for i in range(len(atomic_numbers)):
            file.write(
                f"{int(atomic_numbers[i]):5d}{0.0:12.6f}{angstrom_positions[i, 0]:12.6f}{angstrom_positions[i, 1]:12.6f}{angstrom_positions[i, 2]:12.6f}\n"
            )

        density_reshaped = density.reshape(angstrom_x.shape[0], angstrom_y.shape[1], angstrom_z.shape[2])
        
        for ix in range(angstrom_x.shape[0]):
            for iy in range(angstrom_y.shape[1]):
                for iz in range(angstrom_z.shape[2]):
                    file.write(f"{density_reshaped[ix, iy, iz]:14.20e}")
                    if (iz + 1) % 6 == 0 or iz == len(z) - 1:
                        file.write("\n")
                    else:
                        file.write(" ")

def save_to_pickle(obj, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as file:
        pickle.dump(obj, file)


# ----------------------- MAIN SCRIPT ENTRYPOINT ----------------------- #

def main():
    parser = argparse.ArgumentParser(description="ElektroNN ensemble predictor")
    parser.add_argument("--modeldir")
    parser.add_argument("--maploc")
    parser.add_argument("--moleculepath")
    parser.add_argument("--dir", action="store_true")
    parser.add_argument("--vis", action="store_true")
    parser.add_argument("--cube", action="store_true")
    parser.add_argument("--outputpath")
    parser.add_argument("--version")
    parser.add_argument("--spacing", type=float)

    args = parser.parse_args()

    print(f"Current number of threads: {torch.get_num_threads()}")
    torch.set_num_threads(torch.get_num_threads())
    torch.set_num_interop_threads(torch.get_num_threads())

    print(f"New number of threads: {torch.get_num_threads()}")
    print(f"New number of inter-op threads: {torch.get_num_interop_threads()}")

    from .visualization_utils import LoadModels, model_kwargs, generate_grid, \
        coeff_unperm_gau2grid_density_kdtree_ml_only_v2, write_cube_file

    loader = LoadModels([2], 5, args.modeldir, model_kwargs, args.maploc, all_models=True)
    loader.load()
    models_specified = loader.models

    if args.dir:
        file_paths = [os.path.join(args.moleculepath, f) for f in os.listdir(args.moleculepath)
                      if os.path.isfile(os.path.join(args.moleculepath, f))]
        molecules = [read_molecule_from_xyz(fp, args.version) for fp in file_paths]
    else:
        molecules = [read_molecule_from_xyz(args.moleculepath, args.version)]

    predictions = [ElektroNN_Ensemble(m, models_specified, args.maploc) for m in molecules]

    for mol, pred in zip(molecules, predictions):
        mol.full_c = pred
        base = os.path.splitext(os.path.basename(mol.filename))[0]
        outdir = os.path.join(args.outputpath, base)
        os.makedirs(outdir, exist_ok=True)
        save_to_pickle(mol, os.path.join(outdir, "prediction.pkl"))
        print(f"Saved {base}")

    print(f"Done. Output written to {args.outputpath}")


if __name__ == "__main__":
    main()

