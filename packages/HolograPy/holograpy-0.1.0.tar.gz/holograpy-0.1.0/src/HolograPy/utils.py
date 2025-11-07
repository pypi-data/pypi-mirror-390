import numpy as np
import plotly.graph_objects as go
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
import os

def compute_grid_2d(origin, v1, v2, spacing_x, spacing_y, n_x, n_y):
    """
    Generates a 3D grid of points from an origin and three directional basis vectors.

    Args:
        origin   : (3,) array-like — starting point of the grid.
        v1, v2 : (3,) array-like — direction vectors defining the grid axes.
        spacing_x, spacing_y : float — spacing between adjacent points along v1 and v2.
        n_x, n_y : int — number of points along each direction.

    Returns:
        np.ndarray of shape (n_x * n_y, 3): Cartesian coordinates of all grid points.
    """
    
    origin = np.asarray(origin)
    v1 = np.asarray(v1)
    v2 = np.asarray(v2)
    
    # Normalize direction vectors
    v1_unit = v1 / np.linalg.norm(v1)
    v2_unit = v2 / np.linalg.norm(v2)
    
    points = []
    for i in range(n_x):
        for j in range(n_y):
            point = origin + j * spacing_x * v1_unit + i * spacing_y * v2_unit
            points.append(point)

    return np.array(points)


def compute_grid_3d(origin, v1, v2, v3, spacing_x, spacing_y, spacing_z, n_x, n_y, n_z):
    """
    Generates a 3D grid of points from an origin and three directional basis vectors.

    Args:
        origin   : (3,) array-like — starting point of the grid.
        v1, v2, v3 : (3,) array-like — direction vectors defining the grid axes.
        spacing_x, spacing_y, spacing_z : float — spacing between adjacent points along v1, v2, v3.
        n_x, n_y, n_z : int — number of points along each direction.

    Returns:
        np.ndarray of shape (n_x * n_y * n_z, 3): Cartesian coordinates of all grid points.
    """
    
    origin = np.asarray(origin, dtype=float)
    v1 = np.asarray(v1, dtype=float)
    v2 = np.asarray(v2, dtype=float)
    v3 = np.asarray(v3, dtype=float)

    # Normalize direction vectors
    v1_unit = v1 / np.linalg.norm(v1)
    v2_unit = v2 / np.linalg.norm(v2)
    v3_unit = v3 / np.linalg.norm(v3)

    # Create coordinate indices
    i, j, k = np.meshgrid(
        np.arange(n_x), np.arange(n_y), np.arange(n_z), indexing="ij"
    )

    # Compute points using broadcasting
    points = (
        origin
        + spacing_x * i[..., None] * v1_unit
        + spacing_y * j[..., None] * v2_unit
        + spacing_z * k[..., None] * v3_unit
    )

    return points.reshape(-1, 3)
    

def GF_forward_model(eval_points, modulator_points, modulator_normals, modulator_areas, k):
    """
    Vectorised Green's-function propagator for planar modulating elements (constant-pressure facets).

    args:
        eval_points       : (Neval, 3) numpy array of evaluation points (x, y, z)
        modulator_points  : (Nmod, 3) numpy array of element centre positions (x', y', z')
        modulator_normals : either (Nmod, 3) array of outward normals OR (3,) single normal vector
        modulator_areas   : either (Nmod,) array of element areas OR scalar (single area value)
        k                 : scalar wavenumber (rad/m)

    returns:
        H : complex pressure/propagator matrix of shape (Neval, Nmod)
            (rows correspond to eval points, columns to modulator elements)
    """
    
    # Ensure arrays
    eval_points = np.asarray(eval_points)
    modulator_points = np.asarray(modulator_points)
    modulator_normals = np.asarray(modulator_normals)
    modulator_areas = np.asarray(modulator_areas)
    
    Nmod = modulator_points.shape[0]

    # --- Handle modulator_normals input flexibility ---
    if modulator_normals.ndim == 1 and modulator_normals.size == 3:
        modulator_normals = np.tile(modulator_normals, (Nmod, 1))
    elif modulator_normals.shape != (Nmod, 3):
        raise ValueError(
            f"modulator_normals must be shape (Nmod, 3) or (3,), but got {modulator_normals.shape}"
        )

    # --- Handle modulator_areas input flexibility ---
    if modulator_areas.ndim == 0:
        modulator_areas = np.full(Nmod, modulator_areas)
    elif modulator_areas.ndim == 1 and modulator_areas.size == 1:
        modulator_areas = np.full(Nmod, modulator_areas.item())
    elif modulator_areas.ndim != 1 or modulator_areas.size != Nmod:
        raise ValueError(
            f"modulator_areas must be scalar or shape (Nmod,), but got {modulator_areas.shape}"
        )

    # --- Compute Green's function ---
    
    # Vector from each modulator (source) to each evaluation point: (Neval, Nmod, 3)
    r_vec = eval_points[:, np.newaxis, :] - modulator_points[np.newaxis, :, :]

    # Distance magnitudes r (Neval, Nmod)
    r = np.linalg.norm(r_vec, axis=2)

    # Avoid division by zero
    eps = np.finfo(float).eps
    r_safe = np.where(r == 0, eps, r)

    # Dot product (x - x') · n'  -> shape (Neval, Nmod)
    dot = np.sum(r_vec * modulator_normals[np.newaxis, :, :], axis=2)

    # Partial derivative of Green's function w.r.t. source normal:
    prefactor = -1.0 / (4.0 * np.pi)
    exp_term = np.exp(1j * k * r_safe)
    num = (1j * k * r_safe) - 1.0
    g = prefactor * exp_term * (num / (r_safe**3))

    # Handle potential overflow/underflow
    g = np.where(np.isfinite(g), g, 0.0 + 0.0j)

    # Multiply by projection (dot) and element areas
    H = g * dot * modulator_areas[np.newaxis, :]  # (Neval, Nmod)

    return H



def PM_forward_model(eval_points, tran_points, tran_normals, k, A=0.17, V=20, d=9/1000):
    """ 
    Fully vectorised piston model for an array of transducer normals.
    
    args:
        eval_points : (Neval, 3) numpy array of evaluation points
        tran_points : (Ntran, 3) numpy array of transducer positions
        tran_normals: either (Ntran, 3) array of normal vectors OR (3,) single normal vector
        k           : wavenumber [rad/m]
        A           : transducer constant
        V           : voltage by which transducers are driven [V]
        d           : transducer diameter [m]
    
    returns:
        H : complex pressure array of shape (Neval, Ntran)
    """
    
    # Calculate reference pressure
    p0 = A * V
    
    # --- Handle tran_normals input flexibility ---
    tran_normals = np.asarray(tran_normals)
    
    # If it's a single vector (3,), tile it to match number of transducers
    if tran_normals.ndim == 1 and tran_normals.size == 3:
        tran_normals = np.tile(tran_normals, (tran_points.shape[0], 1))
    elif tran_normals.shape != tran_points.shape:
        raise ValueError("tran_normals must be either shape (Ntran, 3) or (3,)")

    # Compute vector from each transducer to each evaluation point
    # Shape after broadcasting: (Neval, Ntran, 3)
    tp = eval_points[:, np.newaxis, :] - tran_points[np.newaxis, :, :]
    
    # Norms of tp vectors and transducer normals
    r = np.linalg.norm(tp, axis=2)  # distance matrix (Neval, Ntran)
    tran_norms = np.linalg.norm(tran_normals, axis=1)  # (Ntran,)
    
    # Cross product and sin(theta)
    cross = np.cross(tp, tran_normals[np.newaxis, :, :])  # (Neval, Ntran, 3)
    sin_theta = np.linalg.norm(cross, axis=2) / (r * tran_norms)
    
    # Bessel argument
    J_arg = k * (d / 2) * sin_theta
    
    # Taylor expansion of J1(J_arg)/J_arg
    tay = (1/2) - (J_arg**2 / 16) + (J_arg**4 / 384) - (J_arg**6 / 18432) + (J_arg**8 / 1474560) - (J_arg**10 / 176947200)
    
    # Directivity function
    H = 2 * p0 * (tay / r) * np.exp(1j * k * r)  # (Neval, Ntran)
    
    return H


def wgs(A, b, K=500, incoming_field=None, smooth_sigma=None, alpha=0.8):
    """
    Weighted Gerchberg–Saxton (WGS) solver optimized for letters or structured targets.

    Parameters
    ----------
    A : np.ndarray, shape (M, N), complex
        Forward model matrix mapping the hologram plane to the target plane.
    b : np.ndarray, shape (M, 1) or (M,), complex
        Target complex field (desired amplitude and phase in the target plane).
    K : int, optional
        Number of iterations (default 500).
    incoming_field : np.ndarray, shape (N, 1) or (N,), complex, optional
        Incoming complex field at the hologram plane. Defaults to uniform plane wave.
    smooth_sigma : float or None, optional
        Standard deviation for Gaussian smoothing of the target amplitude.
        If None or 0, no smoothing is applied. 1 = maximum smoothing (good for letters).
    alpha : float, optional
        Relaxation parameter for hologram update (0 < alpha <= 1).

    Returns
    -------
    x : np.ndarray, shape (N, 1), complex
        Final hologram field: same amplitude as incoming_field, optimized phase.
    y : np.ndarray, shape (M, 1), complex
        Forward propagated field in the target plane.
    """
    M, N = A.shape
    b = b.reshape((M, 1))

    # Incoming field
    if incoming_field is None:
        inc = np.ones((N, 1), dtype=np.complex128)
    else:
        inc = incoming_field.reshape((N, 1))

    AT = np.conj(A).T
    x = inc.copy()

    # Create mask for letter region (non-zero amplitude)
    mask = (np.abs(b) > 0).astype(np.float32)

    # Optionally smooth mask
    if smooth_sigma and smooth_sigma > 0:
        mask = gaussian_filter(mask, sigma=smooth_sigma)

    # Flattened target amplitude
    target_amplitude = mask / np.max(mask)

    for _ in range(K):
        # Forward propagation
        y = A @ x  # preserves amplitude of incoming field

        # Replace amplitude in target plane with flattened amplitude in letter region
        p = target_amplitude * (y / np.abs(y))

        # Backward propagation
        r = AT @ p

        # Update hologram with relaxation, preserve incoming amplitude
        x_phase = r / np.abs(r)
        x = inc * ((1 - alpha) * (x / np.abs(x)) + alpha * x_phase)
        x = x / np.max(np.abs(x)) * np.abs(inc)  # preserve amplitude scale of incoming field

    # Final forward propagation
    y = A @ x

    return x, y


def char_to_array(chars, fontsize, image_size, font_file="Arial.ttf"):
    """
    Convert a character or list of characters to a normalized numpy array representation.

    Args:
        chars (str or list of str): Character(s) to convert.
        fontsize (int): Font size to use.
        image_size (tuple): Size of the output image (width, height).
        font_file (str): Name of a .ttf font file in the same directory.

    Returns:
        np.ndarray: Array of shape (num_chars, height, width) with values between 0 and 1.
    """
    if isinstance(chars, str):
        chars = [chars]

    if not os.path.isfile(font_file):
        raise ValueError(f"Font file '{font_file}' not found in current directory.")

    font = ImageFont.truetype(font_file, fontsize)
    arrays = []

    for char in chars:
        img = Image.new("L", image_size, color=255)
        draw = ImageDraw.Draw(img)

        bbox = draw.textbbox((0, 0), char, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        position = ((image_size[0] - w) / 2 - bbox[0], (image_size[1] - h) / 2 - bbox[1])

        draw.text(position, char, font=font, fill=0)

        arr = 1.0 - np.array(img, dtype=np.float32) / 255.0
        arrays.append(arr)

    return np.array(arrays)


def plot_transducers_plotly(fig, transducer_points, radius, label=None):
    """
    Plot transducers as filled black circles in a 3D Plotly figure.
    
    Parameters
    ----------
    fig : plotly.graph_objects.Figure
        Figure to plot into.
    origin : list[float]
        [x, y, z] coordinate to offset all transducer points by.
    transducer_points : np.ndarray
        Array of shape (N, 3) giving the (x, y, z) coordinates of transducer centers.
    radius : float
        Radius of each transducer circle.
    label : str, optional
        Label to appear in the legend (shown only once).
    """
    theta = np.linspace(0, 2*np.pi, 50)
    label_shown = False  # show legend label only once

    for pt in np.asarray(transducer_points):
        x0, y0, z0 = pt[0], pt[1], pt[2]

        # Circle boundary
        x = x0 + radius * np.cos(theta)
        y = y0 + radius * np.sin(theta)
        z = np.full_like(theta, z0)

        # Mesh3d vertices
        x_mesh = [x0] + x.tolist()
        y_mesh = [y0] + y.tolist()
        z_mesh = [z0] + z.tolist()

        # Triangles (fan from center)
        i_tri, j_tri, k_tri = [], [], []
        for k_idx in range(1, len(theta)):
            i_tri.append(0)
            j_tri.append(k_idx)
            k_tri.append(k_idx + 1)
        # Close loop
        i_tri.append(0)
        j_tri.append(len(theta))
        k_tri.append(1)

        fig.add_trace(go.Mesh3d(
            x=x_mesh,
            y=y_mesh,
            z=z_mesh,
            color='black',
            opacity=1.0,
            i=i_tri,
            j=j_tri,
            k=k_tri,
            name=label if (label and not label_shown) else None,
            showlegend=bool(label and not label_shown)
        ))

        label_shown = True  # only label the first one

    return fig
    
    
def plot_plane_points_plotly(fig, grid, color='black', size=4, label=None):
    """
    Plot all points of a 3D plane grid in a Plotly 3D figure.

    Parameters
    ----------
    fig : plotly.graph_objects.Figure
        A Plotly 3D figure to add points to.
    grid : np.ndarray
        Either:
          - shape (Nx, Ny, 3): 2D grid of 3D points, or
          - shape (N, 3): flattened array of 3D points.
    color : str
        Color of the points.
    size : float
        Size of the marker points.
    """
    grid = np.asarray(grid)
    
    # Handle both grid shapes
    if grid.ndim == 3 and grid.shape[2] == 3:
        x = grid[:, :, 0].flatten()
        y = grid[:, :, 1].flatten()
        z = grid[:, :, 2].flatten()
    elif grid.ndim == 2 and grid.shape[1] == 3:
        x, y, z = grid[:, 0], grid[:, 1], grid[:, 2]
    else:
        raise ValueError("grid must have shape (Nx, Ny, 3) or (N, 3).")

    # Add points to figure
    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers',
        marker=dict(color=color, size=size),
        name=label if label is not None else ""
    ))

    return fig
    
    
def plot_plane_edges_plotly(fig, grid, n_cols=None, color='black', line_width=4, label=None):
    """
    Draw the 4 extreme edges of a grid of 3D points as separate lines in a Plotly 3D figure.

    Parameters
    ----------
    fig : plotly.graph_objects.Figure
        A Plotly figure (3D scene) to add traces to.
    grid : np.ndarray
        Either:
          - shape (Nx, Ny, 3) : a 2D grid of 3D points (preferred), OR
          - shape (N, 3)      : flattened points (row-major). If flattened, provide n_cols.
    n_cols : int, optional
        Number of columns when grid is flattened (shape (N,3)). If None, the function will
        try to infer a square layout (n_cols = int(sqrt(N))) and will raise if that fails.
    color : str
        Color for edge lines.
    line_width : int
        Width for edge lines.
    """
    grid = np.asarray(grid)
    if grid.ndim == 3:
        # Already shape (Nx, Ny, 3)
        Nx, Ny, D = grid.shape
        if D != 3:
            # raise ValueError("Expected last dimension to be 3 (x,y,z).")
            grid2 = grid  # shape (Nx, Ny, 3)
    elif grid.ndim == 2 and grid.shape[1] == 3:
        # Flattened points (N,3) -> need n_cols to reshape to (Nx, Ny, 3)
        N = grid.shape[0]
        if n_cols is None:
            # Try to infer square layout
            s = int(round(np.sqrt(N)))
            if s * s == N:
                n_cols = s
            else:
                raise ValueError(
                    "grid has shape (N,3) with N not a perfect square. "
                    "Please provide n_cols (number of columns) to reshape into (Nx, Ny, 3)."
                )
        if N % n_cols != 0:
            raise ValueError("N is not divisible by n_cols. Provide correct n_cols.")
        n_rows = N // n_cols
        grid2 = grid.reshape((n_rows, n_cols, 3))
        Nx, Ny = n_rows, n_cols
    else:
        raise ValueError("Unsupported grid shape. Expected (Nx,Ny,3) or (N,3).")

    # 1) Bottom edge: row 0, all columns (left->right)
    fig.add_trace(go.Scatter3d(
        x=grid2[0, :, 0],
        y=grid2[0, :, 1],
        z=grid2[0, :, 2],
        mode='lines',
        line=dict(color=color, width=line_width),
        showlegend=False
    ))

    # 2) Top edge: last row, all columns (left->right)
    fig.add_trace(go.Scatter3d(
        x=grid2[-1, :, 0],
        y=grid2[-1, :, 1],
        z=grid2[-1, :, 2],
        mode='lines',
        line=dict(color=color, width=line_width),
        showlegend=False
    ))

    # 3) Left edge: all rows, column 0 (bottom->top)
    fig.add_trace(go.Scatter3d(
        x=grid2[:, 0, 0],
        y=grid2[:, 0, 1],
        z=grid2[:, 0, 2],
        mode='lines',
        line=dict(color=color, width=line_width),
        showlegend=False
    ))

    # 4) Right edge: all rows, last column (bottom->top)
    fig.add_trace(go.Scatter3d(
        x=grid2[:, -1, 0],
        y=grid2[:, -1, 1],
        z=grid2[:, -1, 2],
        mode='lines',
        line=dict(color=color, width=line_width),
        name=label if label is not None else ""
    ))

    return fig