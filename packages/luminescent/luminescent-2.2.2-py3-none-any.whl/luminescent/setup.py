import platform
import subprocess
from .constants import *
from .layers import *
from .utils import *
from .materials import *
import json
import gdsfactory as gf
from copy import deepcopy

# from time import time
import datetime
from math import cos, pi, sin
import os
import numpy as np

from sortedcontainers import SortedDict, SortedSet
from gdsfactory.generic_tech import LAYER_STACK, LAYER


def SpherePort(
    name,
    center,
    radius,
    frame=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
    angres=np.deg2rad(10),
    θmin=1e-3,
    θmax=np.pi,
    φmin=0,
    φmax=2 * np.pi,
):
    frame = np.array(frame).T
    return {
        "name": name,
        "type": "sphere",
        "center": center,
        "radius": radius,
        "frame": frame,
        "angres": angres,
        "θmin": θmin,
        "θmax": θmax,
        "φmin": φmin,
        "φmax": φmax,
    }


def PlanePort(
    name,
    center=None,
    x=None,
    y=None,
    z=None,
    frame=None,
    normal=None,
    tangent=None,
    length=None,
    width=None,
    direction="+",
):
    if frame is None:
        if z is not None:
            if direction.startswith("+"):
                frame = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
            else:
                frame = [[-1, 0, 0], [0, 1, 0], [0, 0, -1]]
        elif x is not None:
            if direction.startswith("+"):
                frame = [[0, 1, 0], [0, 0, 1], [1, 0, 0]]
            else:
                frame = [[0, -1, 0], [0, 0, 1], [-1, 0, 0]]
        elif y is not None:
            if direction.startswith("+"):
                frame = [[0, 0, 1], [1, 0, 0], [0, 1, 0]]
            else:
                frame = [[0, 0, -1], [1, 0, 0], [0, -1, 0]]
    frame = np.array(frame).T

    if normal is None:
        normal = frame[:, 2]
    if tangent is None:
        tangent = frame[:, 0]
    r = {
        "name": name,
        "type": "plane",
        "center": center,
        "length": length,
        "width": width,
        "x": x,
        "y": y,
        "z": z,
        "frame": frame,
        "normal": normal,
        "tangent": tangent,
        "direction": direction,
    }
    if length is not None:
        r["start"] = [-length / 2, -width / 2]
        r["stop"] = [length / 2, width / 2]
    # print(r)
    return r


def Mode(
    fields=None,
    enum=0,
    ports=None,
    frequency=None,
    wavelength=None,
    nmodes=None,
    dl=None,
    **kwargs,
):
    """
       Mode solution for a port geometry at given frequency or wavelength. Sources and monitors automatically use (or interpolate) mode solution with the closest frequency

       Args:

       - fields: If None, modes will be solved for automatically. Otherwise, dict or (if using higher order modes) list of dicts with precomputed mode fields eg [{'Ex': np_array, 'Ey': ..., 'Hx': ..., 'Hy': ...} ..., ]
       - frequency or wavelength: specify one (not both)
       - ports: ports that this mode applies to eg ["o1","o2"]. If None, applies to all ports.
       - nmodes: number of modes to solve for if fields is None. More modes mean more accurate  forward and reflected total power coefficients. None means automatic (1 for metal transmission lines, 2 for dielectric waveguide)
    - dl: either dx or [dx, dy] mesh resolution for mode solver. Otherwise will be set automatically. Do not set if `fields` is set.
    """
    # - dl: either dx or [dx, dy] mesh resolution. Required for supplied mode fields. Optional otherwise (will be set automatically for for mode solver)
    # if fields is not None:
    if type(fields) is dict:
        modes = [fields]
        assert dl is None
    elif type(fields) is list:
        modes = fields
        assert dl is None
    elif fields is None:
        modes = None
    else:
        raise ValueError(f"fields should be dict or list or None. Got {type(fields)}")

    return {
        **kwargs,
        "modes": modes,
        "enum": enum,
        "ports": ports,
        "frequency": frequency,
        "wavelength": wavelength,
        "nmodes": nmodes,
        "dl": dl,
    }


def Source(
    name,
    source_port_margin,
    wavelength=None,
    frequency=None,
    bandwidth=None,
    duration=None,
    modenums=[0],
):
    """
    Modulated Gaussian pulse source with gradual spectral roll off  at bandwidth limits. Becomes continuous wave if `bandwidth=0`.

    Args:

    - name: should match a port name eg "o1"
    - source_port_margin: distance from port along outward normal to source
    - wavelength or frequency: Specify either (not both)
    - bandwidth: in same units as above
    - modenums: list of mode numbers to excite
    """
    # if not bandwidth:
    #     if frequency:
    #         bandwidth = frequency
    #     elif wavelength:
    #         bandwidth = wavelength

    return {
        "name": name,
        "wavelength": wavelength,
        "bandwidth": bandwidth,
        "duration": duration,
        "frequency": frequency,
        "modenums": modenums,
        "source_port_margin": source_port_margin,
    }


def setup(
    path,
    study,
    wavelength,
    wavelengths,
    layer_stack,
    materials_library,
    wl1f=None,
    bbox=None,
    boundaries=["PML", "PML", "PML"],
    nres=4,
    dx=None,
    dy=None,
    dz=None,
    component=None,
    z=None,
    # zmargin=None,
    zmin=None,
    zmax=None,
    height_port_margin=None,
    lateral_port_margin=None,
    inset=0,
    port_margin="auto",
    sources=[],
    monitors=[],
    core="core",
    exclude_layers=[],
    Courant=None,
    gpu="CUDA",
    dtype=np.float32,
    saveat=1000,
    ckptat=5,
    gradient_checkpoint=None,
    magic="",
    name=None,
    modes=None,
    ports=None,
    approx_2D_mode=False,
    show_grid=True,
    Tsim=None,
    field_decay_threshold=None,
    path_length_multiple=None,
    relative_pml_depths=1,
    relative_courant=0.9,
    hasPEC=None,
    keys=None,
    ordering="frequency",
    designs=[],
    targets=[],
    load_saved_designs=False,
    optimizer=None,
    verbose=False,
    pixel_size=0.01,
    views=[],
    fps=5,
    secret=None,
    info=None,
    subpixel_smoothing=True,
    subpixel_smoothing_sampling_distance=None,
):
    # if force:
    #     shutil.rmtree(path, ignore_errors=True)
    # elif os.path.exists(path):
    #     raise FileExistsError(
    #         f"Path {path} already exists. Use force=True to overwrite."
    #     )

    os.makedirs(path, exist_ok=True)
    if info is None:
        info = {}
    json.dump(info, open(os.path.join(path, "info.json"), "w"), indent=4)
    if approx_2D_mode:
        N = 2
    else:
        N = 3
        approx_2D_mode = None

    if inset is None:
        inset = [0] * N

    writejsonnp(
        os.path.join(path, "visualization.json"),
        {"views": views, "fps": fps},
    )
    prob = {
        "nres": nres,
        "wavelength": wavelength,
        "wavelengths": wavelengths,
        "name": name,
        "path": path,
        "keys": keys,
        "dx": dx,
        "dy": dy,
        "dz": dz,
        "z": z,
        "Tsim": Tsim,
        "field_decay_threshold": field_decay_threshold,
        "path_length_multiple": path_length_multiple,
        "saveat": saveat,
        "ckptat": ckptat,
        "gradient_checkpoint": gradient_checkpoint,
        "verbose": verbose,
        "views": views,
        "boundaries": boundaries[0:N],
        "show_grid": show_grid,
        "approx_2D_mode": approx_2D_mode,
        "relative_pml_depths": relative_pml_depths,
        "relative_courant": relative_courant,
        "hasPEC": hasPEC,
        "ordering": ordering,
        "pixel_size": pixel_size,
        "secret": secret,
        "study": study,
        "subpixel_smoothing": subpixel_smoothing,
        "subpixel_smoothing_sampling_distance": subpixel_smoothing_sampling_distance,
        "materials_library": materials_library,
        "designs": designs,
        "optimizer": optimizer,
        "N": N,
        "load_saved_designs": load_saved_designs,
        "targets": targets,
    }

    prob["class"] = "pic"
    prob["dtype"] = str(dtype)
    prob["timestamp"] = (
        datetime.datetime.now().isoformat(timespec="seconds").replace(":", "-")
    )
    prob["magic"] = magic

    gpu_backend = gpu
    # if gpu_backend:s
    prob["gpu_backend"] = gpu_backend

    if component is None:
        0
    else:
        c = component
        if ports is None:
            ports = []

        if c.get_ports_list():
            d = layer_stack.layers[core]
            hcore = d.thickness
            zcore = d.zmin

            if height_port_margin is None:
                height_port_margin = 3 * hcore
            if type(height_port_margin) in [int, float]:
                height_port_margin = [height_port_margin, height_port_margin]

            port_width = max([p.width / 1e0 for p in c.ports])
            if lateral_port_margin is None:
                lateral_port_margin = port_width
            if type(lateral_port_margin) in [int, float]:
                lateral_port_margin = [lateral_port_margin, lateral_port_margin]

            wmode = port_width + lateral_port_margin[0] + lateral_port_margin[1]
            hmode = hcore + height_port_margin[0] + height_port_margin[1]
            zmode = zcore - height_port_margin[0]
            zcenter = zmode + hmode / 2

            for p in c.get_ports_list(prefix="o"):
                center = (np.array(p.center) / 1e0).tolist()
                normal = [
                    cos(p.orientation / 180 * pi),
                    sin(p.orientation / 180 * pi),
                ]
                tangent = [
                    -sin(p.orientation / 180 * pi),
                    cos(p.orientation / 180 * pi),
                ]
                if N == 3:
                    center.append(zcenter)
                    normal.append(0)
                    tangent.append(0)

                v = PlanePort(
                    center=center,
                    name=p.name,
                    normal=normal,
                    tangent=tangent,
                    length=wmode,
                    width=hmode,
                )
                z, n = [0, 0, 1], [*normal, 0][:3]
                t = np.cross(z, n).tolist()
                v["frame"] = np.array([t, z, n]).T

                v["start"] = [-wmode / 2, zmode - zcenter]
                v["stop"] = [wmode / 2, zmode + hmode - zcenter]
                ports.append(v)

        bbox2 = c.bbox_np()
        if bbox is None:
            bbox = bbox2.tolist()
            bbox[0].append(zmin)
            bbox[1].append(zmax)

        layers = set(c.layers) - set(exclude_layers)

    for mode in modes:
        if mode["frequency"]:
            mode["wavelength"] = wl1f / mode["frequency"]
            # f = wavelength / mode["wavelength"]
            # mode["frequency"] = f
            # if mode["bandwidth"]:
            #     mode["bandwidth"] = wavelength / (
            #         mode["wavelength"] - mode["bandwidth"] / 2
            #     ) - wavelength / (mode["wavelength"] + mode["bandwidth"] / 2)
    for target in targets:
        if target["frequency"]:
            target["wavelength"] = wl1f / target["frequency"]

    MODES = os.path.join(path, "modes")
    os.makedirs(MODES, exist_ok=True)
    GEOMETRY = os.path.join(path, "geometry")
    os.makedirs(GEOMETRY, exist_ok=True)

    if c:
        layer_stack_info = material_voxelate(
            c, zmin, zmax, layers, layer_stack, materials_library, GEOMETRY
        )

        dir = os.path.dirname(os.path.realpath(__file__))

        prob["layer_stack"] = layer_stack_info

    for v in ports:
        if v["type"] == "sphere":
            0
        else:
            if v["center"] is None:
                if v["z"] is not None:
                    v["center"] = [
                        (bbox[0][0] + bbox[1][0]) / 2,
                        (bbox[0][1] + bbox[1][1]) / 2,
                    ] + [v["z"]]
                    v["length"] = bbox[1][0] - bbox[0][0]
                    v["width"] = bbox[1][1] - bbox[0][1]
                elif v["x"] is not None:
                    v["center"] = [
                        v["x"],
                        (bbox[0][1] + bbox[1][1]) / 2,
                        (bbox[0][2] + bbox[1][2]) / 2,
                    ]
                    v["length"] = bbox[1][1] - bbox[0][1]
                    v["width"] = bbox[1][2] - bbox[0][2]
                elif v["y"] is not None:
                    v["center"] = [
                        (bbox[0][0] + bbox[1][1]) / 2,
                        v["y"],
                        (bbox[0][2] + bbox[1][2]) / 2,
                    ]
                    v["width"] = bbox[1][2] - bbox[0][2]
                    v["length"] = bbox[1][0] - bbox[0][0]
                v["start"] = [-v["length"] / 2, -v["width"] / 2]
                v["stop"] = [+v["length"] / 2, +v["width"] / 2]
    for s in sources:
        p = next((p for p in ports if p["name"] == s["name"]), None)
        s.update(p)
        ct = np.array(p["center"])
        n = np.array(p["normal"])
        if s["wavelength"] is None:
            s["wavelength"] = wl1f / s["frequency"]
        s["center"] = (ct + n * s["source_port_margin"]).tolist()
    monitors = ports
    bg = materials_library["background"]["epsilon"]
    ime = []
    hasPEC = False
    for f in os.listdir(GEOMETRY):
        i, mat, layer_name, _ = f[:-4].split(SEP)
        if mat in materials_library:
            eps = materials_library[mat].get("epsilon", None)
            if eps is not None:
                hasPEC = isPEC(eps) or hasPEC
                ime.append(
                    (int(i), trimesh.load(os.path.join(GEOMETRY, f)), eps, layer_name)
                )
    mesheps = [x[1:] for x in sorted(ime, key=lambda x: x[0])]
    l = []
    for mode in modes:
        if not mode["wavelength"]:
            mode["wavelength"] = wavelength
        if not mode["ports"]:
            v = monitors[0]
        else:
            v = next(
                m
                for m in monitors
                if mode["ports"] is None or m["name"] in mode["ports"]
            )

        if v["type"] == "plane":
            start = v["start"]
            stop = v["stop"]

            L = stop[0] - start[0]
            W = stop[1] - start[1]

            if mode["modes"]:
                for m in mode["modes"]:
                    for v in m.values():
                        if type(v) is np.ndarray:
                            dx = L / v.shape[0]
                            dy = W / v.shape[1]
                            dl = [dx, dy]
                            mode["dl"] = dl

            dl = mode["dl"]
            if dl is None:
                if hasPEC:
                    dl = L / 40
                else:
                    dl = L / 40

            if type(dl) is float or type(dl) is int:
                dl = [dl, dl]

            dx, dy = dl
            dx = L / round(L / dx)
            dy = W / round(W / dy)

            mode["dl"] = [dx, dy]

            if mode["modes"]:
                l.append(mode)
            else:
                center = v["center"]
                if len(center) == 2:
                    center = [*center, zcenter]
                polyeps = section_mesh(
                    mesheps,
                    center,
                    v["frame"],
                    start,
                    stop,
                    bg,
                )
                # print(f"polyeps: {polyeps}")
                if "metallic_boundaries" in mode:
                    hasPEC = True
                    metallic_boundaries = mode["metallic_boundaries"]
                else:
                    metallic_boundaries = []
                if not mode["nmodes"]:
                    mode["nmodes"] = 1 if hasPEC else 2
                nmodes = mode["nmodes"]

                wavelength = mode["wavelength"]
                eps = epsilon_from_polyeps(polyeps, bg, start, stop, dx, dy).tolist()
                if hasPEC:
                    _modes = solvemodes_femwell(
                        polyeps,
                        start,
                        stop,
                        wavelength,
                        nmodes,
                        dx,
                        dy,
                        metallic_boundaries,
                    )
                else:
                    _modes = solvemodes(
                        polyeps, bg, start, stop, wavelength, nmodes, dx, dy
                    )
                l.append(
                    {
                        **mode,
                        "modes": _modes,
                        "dl": [dx, dy],
                        "epsilon": eps,
                    }
                )
        else:
            l.append(mode)

    prob["modes"] = l
    prob["bbox"] = bbox
    prob.update({"monitors": monitors, "sources": sources})
    if not os.path.exists(path):
        os.makedirs(path)
    return prob
