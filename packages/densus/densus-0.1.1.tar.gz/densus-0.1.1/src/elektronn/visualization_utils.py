from e3nn.nn.models.gate_points_2101 import Network
from e3nn import o3
import os
import warnings
import sys
import pickle
import copy
import torch
import numpy as np
import torch_geometric.data
import sys
import os
import pickle
import time
import numpy as np
import torch
from itertools import zip_longest
import periodictable as pt
from copy import deepcopy
import py3Dmol
import periodictable
import plotly.graph_objects as go
from plotly.subplots import make_subplots


model_kwargs = {
    "irreps_in": "18x 0e",
    "irreps_hidden": [
        (mul, (l, p)) for l, mul in enumerate([125, 40, 25, 15]) for p in [-1, 1]
    ],
    "irreps_out": "14x0e + 14x1o + 5x2e + 4x3o + 2x4e ",
    "irreps_node_attr": None,
    "irreps_edge_attr": o3.Irreps.spherical_harmonics(3),
    "layers": 3,
    "max_radius": 3.5,
    "number_of_basis": 10,
    "radial_layers": 1,
    "radial_neurons": 128,
    "num_neighbors": 12.2298,
    "num_nodes": 24,
    "reduce_output": False,
}


class LoadModels:

    def __init__(
        self,
        models,
        num_models,
        model_path,
        model_kwargs,
        map_location="cpu",
        all_models=True,
    ):
        self.models_to_load = models
        self.num_models = num_models
        self.model_path = model_path
        model_kwargs = model_kwargs
        self.map_location = map_location
        self.models = []
        self.all_models = all_models

    def load(self):
        if not self.all_models:
            for i in self.models_to_load:
                model = Network(**model_kwargs)
                model.to(self.map_location)
                model.load_state_dict(
                    torch.load(
                        self.model_path + f"model_fold_{i}.pth",
                        map_location=self.map_location,
                    )
                )
                print("loaded", f"model_fold_{i}.pth")
                self.models.append(model)
        else:
            for i in range(self.num_models):
                model = Network(**model_kwargs)
                model.to(self.map_location)
                model.load_state_dict(
                    torch.load(
                        self.model_path + f"model_fold_{i+1}.pth",
                        map_location=self.map_location,
                    )
                )
                print("loaded", f"model_fold_{i+1}.pth")
                self.models.append(model)


# Example usage
# num_models = 5
# map_location = "cpu"


# Suppress specific UserWarnings
# warnings.filterwarnings("ignore", category=UserWarning, module='torch.jit._check')

# loader_all = LoadModels([], num_models, model_path, map_location, all_models=True)
# loader_all.load()


class PrepareDatasets:
    def __init__(self, dataset_path, num_classes, testcriteria, traincriteria):
        self.dataset_path = dataset_path
        self.num_classes = num_classes
        self.testcriteria = testcriteria
        self.traincriteria = traincriteria
        self.encoded_train_datasets = None
        self.encoded_test_datasets = None
        self.train_identities = None
        self.test_identities = None
        self.prepare_datasets()

    def generate_one_hot_encoding(self, input_list):
        input_list = [int(x) for x in input_list]
        return torch.eye(self.num_classes)[input_list].float()

    def process_datasets(self, train_datasets, test_datasets):
        encoded_train_datasets = []
        encoded_test_datasets = []

        for dataset_path in train_datasets:
            dataset = self.get_iso_permuted_dataset(dataset_path)
            for data_point in dataset:
                atomic_numbers = data_point["atomic_numbers"]
                one_hot_encoding = self.generate_one_hot_encoding(atomic_numbers)
                data_point["x"] = one_hot_encoding
            encoded_train_datasets.append(dataset)

        for dataset_path in test_datasets:
            dataset = self.get_iso_permuted_dataset(dataset_path)
            for data_point in dataset:
                atomic_numbers = data_point["atomic_numbers"]
                one_hot_encoding = self.generate_one_hot_encoding(atomic_numbers)
                data_point["x"] = one_hot_encoding
            encoded_test_datasets.append(dataset)

        return encoded_train_datasets, encoded_test_datasets

    def get_iso_permuted_dataset(self, picklefile, **atm_iso):

        dataset = []

        for molecule in pickle.load(open(picklefile, "rb")):
            pos = molecule["pos"]
            z = molecule["type"].unsqueeze(1)
            x = molecule["onehot"]
            c = molecule["coefficients"]
            n = molecule["norms"]
            exp = molecule["exponents"]

            full_c = copy.deepcopy(c)
            iso_c = torch.zeros_like(c)

            # Extract atomic number information
            atomic_numbers = z.squeeze().tolist()

            pop = torch.where(n != 0, c * 2 * np.sqrt(2) / n, n)

            # Permute positions: YZX -> XYZ
            p_pos = copy.deepcopy(pos)
            p_pos[:, 0] = pos[:, 1]
            p_pos[:, 1] = pos[:, 2]
            p_pos[:, 2] = pos[:, 0]

            dataset += [
                torch_geometric.data.Data(
                    pos=p_pos.to(torch.float32),
                    pos_orig=pos.to(torch.float32),
                    z=z.to(torch.float32),
                    x=x.to(torch.float32),
                    y=pop.to(torch.float32),
                    c=c.to(torch.float32),
                    full_c=full_c.to(torch.float32),
                    iso_c=iso_c.to(torch.float32),
                    exp=exp.to(torch.float32),
                    norm=n.to(torch.float32),
                    atomic_numbers=atomic_numbers,
                )
            ]

        return dataset

    def prepare_datasets(self):
        all_pkl_files = os.listdir(self.dataset_path)

        train_datasets = [
            os.path.join(self.dataset_path, file)
            for file in all_pkl_files
            if any(criteria in file for criteria in self.traincriteria)
        ]
        self.train_identities = [
            file
            for file in all_pkl_files
            if any(criteria in file for criteria in self.traincriteria)
        ]

        test_datasets = [
            os.path.join(self.dataset_path, file)
            for file in all_pkl_files
            if any(criteria in file for criteria in self.testcriteria)
        ]
        self.test_identities = [
            file
            for file in all_pkl_files
            if any(criteria in file for criteria in self.testcriteria)
        ]

        self.encoded_train_datasets, self.encoded_test_datasets = self.process_datasets(
            train_datasets, test_datasets
        )


def visualize_molecule(positions, atomic_numbers):
    # Convert positions to numpy array if it's a tensor
    if isinstance(positions, torch.Tensor):
        positions = positions.numpy()
    if isinstance(atomic_numbers, torch.Tensor):
        atomic_numbers = atomic_numbers.numpy()

    # Convert float32 values to float
    positions = positions.astype(float)
    atomic_numbers = [int(i) for i in atomic_numbers]

    # Define colors for elements
    element_colors = {
        1: "white",  # Hydrogen
        6: "gray",  # Carbon
        7: "blue",  # nitrogen
        8: "red",  # Oxygen
        9: "pink",
        15: "black",
        16: "yellow",
        17: "green",
    }

    # Create a Py3Dmol view
    view = py3Dmol.view(width=800, height=600)

    # Add atoms to the viewer with custom colors based on element
    for pos, num in zip(positions, atomic_numbers):
        element = periodictable.elements[num].symbol
        color = element_colors.get(
            num, "gray"
        )  # Default to gray if element color is not defined
        view.addSphere(
            {
                "center": {"x": float(pos[0]), "y": float(pos[1]), "z": float(pos[2])},
                "radius": 0.2,
                "color": color,
                "elem": element,
            }
        )

    # Add bonds between atoms based on distance
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            distance = np.linalg.norm(positions[i] - positions[j])
            if distance < 1.5:  # Define a threshold for bond formation
                view.addCylinder(
                    {
                        "start": {
                            "x": float(positions[i][0]),
                            "y": float(positions[i][1]),
                            "z": float(positions[i][2]),
                        },
                        "end": {
                            "x": float(positions[j][0]),
                            "y": float(positions[j][1]),
                            "z": float(positions[j][2]),
                        },
                        "radius": 0.1,
                        "color": "black",  # Color for bonds
                    }
                )

    # Show the viewer
    view.zoomTo()
    return view.show()


colorscale = [
    [0.0, "rgb(255, 255, 255)"],  # White at 0.0
    [0.005, "rgb(135,206,250)"],
    [0.01, "rgb(132, 112, 255)"],
    [0.03, "rgb(30, 144, 255)"],  # cadetblue2
    [0.1, "rgb(62, 62, 226)"],  # Medium blue at 0.1
    [0.2, "rgb(0, 128, 255)"],  # Deep sky blue at 0.2
    [0.3, "rgb(0, 130, 128)"],  # Teal at 0.3
    [0.4, "rgb(85, 107, 47)"],  # Dark olive green at 0.4
    [0.5, "rgb(255, 215, 0)"],  # Gold at 0.5
    [0.6, "rgb(255, 140, 0)"],  # Dark orange at 0.6
    [0.7, "rgb(222, 79, 107)"],  # pink
    [1.0, "rgb(218, 62, 93)"],
]  # Dark pink
# [1.5, 'rgb(102, 0, 102)']       # Purple at 1.5


def density_comparision_vis(
    x, y, z, target_density, points, colorscale, title, filename, difference=False
):

    rows = 1
    cols = 2
    specs = [[{"is_3d": True} for i in range(cols)] for j in range(rows)]

    fig = make_subplots(rows=rows, cols=cols, specs=specs, subplot_titles=(title,))

    fig.update_layout(
        height=500,  # box size
        width=1000,
    )

    traces = []

    traces.append(
        go.Volume(
            x=x.flatten(),
            y=y.flatten(),
            z=z.flatten(),
            value=target_density.flatten(),
            isomin=0.1 if difference == False else 0,  # all 0.1, percentage dif 0
            isomax=1.0,
            colorscale=colorscale,  # blues
            opacity=0.1,  # needs to be small to see through all surfaces
            surface_count=10,  # needs to be a large number for good volume rendering
            name="Target Density",
        )
    )

    fig.add_trace(traces[0], row=1, col=1)
    fig.update_layout(
        scene=dict(  # this removes the box
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False),
            zaxis=dict(showgrid=False),
        )
    )

    xs = points.cpu().numpy()[:, 0]
    ys = points.cpu().numpy()[:, 1]
    zs = points.cpu().numpy()[:, 2]
    geom = go.Scatter3d(
        x=xs,
        y=ys,
        z=zs,
        mode="markers",
        marker=dict(size=3, color="Black", opacity=1.0),
    )
    fig.add_trace(geom, row=1, col=1)

    fig.update_layout(showlegend=True)
    fig.write_html(filename)


def density_comparision_vis_transparent(
    x, y, z, target_density, points, colorscale, title, filename, difference=False
):
    rows = 1
    cols = 2
    specs = [[{"is_3d": True} for i in range(cols)] for j in range(rows)]

    fig = make_subplots(rows=rows, cols=cols, specs=specs, subplot_titles=(title,))

    traces = []

    traces.append(
        go.Volume(
            x=x.flatten(),
            y=y.flatten(),
            z=z.flatten(),
            value=np.log1p(target_density.flatten()),
            isomin=0.15 if not difference else 0,  # all 0.1, percentage dif 0
            isomax=1.5,
            colorscale="tealgrn",  # blues
            opacity=0.2,  # needs to be small to see through all surfaces
            surface_count=15,  # needs to be a large number for good volume rendering
            name="Target Density",
        )
    )

    fig.add_trace(traces[0], row=1, col=1)

    # Customize the scene to remove the box, set transparent background, and remove axis labels
    fig.update_layout(
        scene=dict(
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showline=False,
                ticks="",
                showticklabels=False,
                title="",  # Remove x-axis label
                backgroundcolor="rgba(0,0,0,0)",  # Set axis background color to transparent
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showline=False,
                ticks="",
                showticklabels=False,
                title="",  # Remove y-axis label
                backgroundcolor="rgba(0,0,0,0)",  # Set axis background color to transparent
            ),
            zaxis=dict(
                showgrid=False,
                zeroline=False,
                showline=False,
                ticks="",
                showticklabels=False,
                title="",  # Remove z-axis label
                backgroundcolor="rgba(0,0,0,0)",  # Set axis background color to transparent
            ),
            bgcolor="rgba(0,0,0,0)",  # Set scene background color to transparent
        )
    )

    xs = points.cpu().numpy()[:, 0]
    ys = points.cpu().numpy()[:, 1]
    zs = points.cpu().numpy()[:, 2]
    geom = go.Scatter3d(
        x=xs,
        y=ys,
        z=zs,
        mode="markers",
        marker=dict(size=3, color="Black", opacity=0.2),
    )
    fig.add_trace(geom, row=1, col=1)

    # Set the overall layout background to be transparent
    fig.update_layout(
        showlegend=True,
        paper_bgcolor="rgba(0,0,0,0)",  # Set paper background color to transparent
        plot_bgcolor="rgba(0,0,0,0)",  # Set plot background color to transparent
    )
    fig.update_layout(
        height=1200,  # change
        width=1600,
    )
    # Save a high resolution png transparent image
    fig.write_image(filename.replace(".html", ".svg"))
    fig.write_html(filename)

