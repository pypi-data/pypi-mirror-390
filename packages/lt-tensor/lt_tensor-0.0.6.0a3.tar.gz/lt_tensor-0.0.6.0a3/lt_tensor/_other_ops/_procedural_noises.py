__all__ = [
    "domain_warped_fbm_3d",
    "fbm_3d",
    "domain_warped_fbm_2d",
    "fbm_2d",
    "simplex_noise_3d",
    "make_perm",
    "simplex_noise",
    "perlin_noise_3d",
    "perlin_noise",
    "worley_noise_2d",
    "worley_noise_3d",
    "curl_noise_2d",
    "curl_noise_3d",
]
from lt_utils.common import *
import torch
import math
from torch.nn import functional as F
import numpy as np


def perlin_noise(size: Tuple[int, int], grid_size: Tuple[int, int]):
    """
    Generate Perlin noise using PyTorch.

    Args:
        size (tuple): The resolution of the noise (height, width).
        grid_size (tuple): The resolution of the gradient grid (grid_height, grid_width).

    Returns:
        torch.Tensor: A tensor containing Perlin noise in range [-1, 1].
    """
    H, W = size
    gh, gw = grid_size

    # Random gradient directions (normalized)
    gradients = torch.randn(gh + 1, gw + 1, 2)
    gradients = F.normalize(gradients, dim=-1)

    # Coordinate grids in gradient space
    y, x = torch.meshgrid(
        torch.linspace(0, gh, H, device=gradients.device),
        torch.linspace(0, gw, W, device=gradients.device),
        indexing="ij",
    )

    # Integer part (grid cell indices)
    x0 = x.floor().long()
    y0 = y.floor().long()
    x1 = x0 + 1
    y1 = y0 + 1

    # Local coordinates within each grid cell
    xf = x - x0.float()
    yf = y - y0.float()
    local_coords = torch.stack((xf, yf), dim=-1)

    # Fade function for smoother interpolation
    def fade(t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    # Linear interpolation
    def lerp(a, b, t):
        return a + t * (b - a)

    # Dot product of distance and gradient
    def dot_grid_gradient(ix, iy, x, y):
        g = gradients[iy % gh, ix % gw]  # wrap gradients
        d = torch.stack((x - ix.float(), y - iy.float()), dim=-1)
        return (g * d).sum(dim=-1)

    # Compute noise contributions from 4 corners
    n00 = dot_grid_gradient(x0, y0, x, y)
    n10 = dot_grid_gradient(x1, y0, x, y)
    n01 = dot_grid_gradient(x0, y1, x, y)
    n11 = dot_grid_gradient(x1, y1, x, y)

    # Interpolate between results
    u = fade(xf)
    v = fade(yf)

    nx0 = lerp(n00, n10, u)
    nx1 = lerp(n01, n11, u)
    nxy = lerp(nx0, nx1, v)

    return nxy


def perlin_noise_3d(size: Tuple[int, int, int], grid_size: Tuple[int, int, int]):
    """
    Generate 3D Perlin noise using PyTorch.

    Args:
        size (tuple): Output resolution (depth, height, width).
        grid_size (tuple): Grid resolution (g_depth, g_height, g_width).

    Returns:
        torch.Tensor: 3D Perlin noise tensor of shape (D, H, W).
    """
    D, H, W = size
    gd, gh, gw = grid_size

    # Random gradient directions (normalized 3D vectors)
    gradients = torch.randn(gd + 1, gh + 1, gw + 1, 3)
    gradients = F.normalize(gradients, dim=-1)

    # Coordinate grid (in gradient space)
    z, y, x = torch.meshgrid(
        torch.linspace(0, gd, D, device=gradients.device),
        torch.linspace(0, gh, H, device=gradients.device),
        torch.linspace(0, gw, W, device=gradients.device),
        indexing="ij",
    )

    # Grid cell indices
    x0 = x.floor().long()
    y0 = y.floor().long()
    z0 = z.floor().long()
    x1 = x0 + 1
    y1 = y0 + 1
    z1 = z0 + 1

    # Local coordinates
    xf = x - x0.float()
    yf = y - y0.float()
    zf = z - z0.float()

    # Fade curve
    def fade(t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    def lerp(a, b, t):
        return a + t * (b - a)

    # Dot product helper
    def dot_grid_gradient(ix, iy, iz, x, y, z):
        g = gradients[iz % gd, iy % gh, ix % gw]
        d = torch.stack((x - ix.float(), y - iy.float(), z - iz.float()), dim=-1)
        return (g * d).sum(dim=-1)

    # Noise from 8 cube corners
    n000 = dot_grid_gradient(x0, y0, z0, x, y, z)
    n100 = dot_grid_gradient(x1, y0, z0, x, y, z)
    n010 = dot_grid_gradient(x0, y1, z0, x, y, z)
    n110 = dot_grid_gradient(x1, y1, z0, x, y, z)
    n001 = dot_grid_gradient(x0, y0, z1, x, y, z)
    n101 = dot_grid_gradient(x1, y0, z1, x, y, z)
    n011 = dot_grid_gradient(x0, y1, z1, x, y, z)
    n111 = dot_grid_gradient(x1, y1, z1, x, y, z)

    # Interpolation (trilinear)
    u = fade(xf)
    v = fade(yf)
    w = fade(zf)

    nx00 = lerp(n000, n100, u)
    nx10 = lerp(n010, n110, u)
    nx01 = lerp(n001, n101, u)
    nx11 = lerp(n011, n111, u)

    nxy0 = lerp(nx00, nx10, v)
    nxy1 = lerp(nx01, nx11, v)

    nxyz = lerp(nxy0, nxy1, w)

    return nxyz


def simplex_noise(x: int, y: int):
    """Usage example:
    ```
        import numpy as np
        import matplotlib.pyplot as plt

        size = 128
        scale = 0.05
        img = np.zeros((size, size))

        for y in range(size):
            for x in range(size):
                img[y, x] = simplex_noise(x * scale, y * scale)

        plt.imshow(img, cmap='terrain')
        plt.colorbar()
        plt.title("2D Simplex Noise")
        plt.show()
    ```
    """
    # Skewing/Unskewing factors
    F2 = 0.5 * (math.sqrt(3.0) - 1.0)
    G2 = (3.0 - math.sqrt(3.0)) / 6.0

    # Skew the input space
    s = (x + y) * F2
    i = math.floor(x + s)
    j = math.floor(y + s)

    # Unskew back to simplex space
    t = (i + j) * G2
    X0 = i - t
    Y0 = j - t
    x0 = x - X0
    y0 = y - Y0

    # Determine which triangle we are in
    if x0 > y0:
        i1, j1 = 1, 0
    else:
        i1, j1 = 0, 1

    # Offsets for remaining corners
    x1 = x0 - i1 + G2
    y1 = y0 - j1 + G2
    x2 = x0 - 1.0 + 2.0 * G2
    y2 = y0 - 1.0 + 2.0 * G2

    # Simple pseudo-random gradient hashing
    def hash(i, j):
        return ((i * 1836311903) ^ (j * 2971215073)) & 0xFFFFFFFF

    gradients = [(1, 1), (-1, 1), (1, -1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]

    def grad(i, j):
        h = hash(i, j) % len(gradients)
        return gradients[h]

    # Corner contributions
    def corner(g, x, y):
        t = 0.5 - x * x - y * y
        if t < 0:
            return 0.0
        t4 = t * t * t * t
        return t4 * (g[0] * x + g[1] * y)

    g0 = grad(i, j)
    g1 = grad(i + i1, j + j1)
    g2 = grad(i + 1, j + 1)

    n0 = corner(g0, x0, y0)
    n1 = corner(g1, x1, y1)
    n2 = corner(g2, x2, y2)

    # Scale to roughly [-1, 1]
    return 70.0 * (n0 + n1 + n2)


# 12 standard gradient directions (Ken Perlin's set)


# Permutation table: fixed base permutation, repeatable via seed
def make_perm(seed=0):
    rng = np.random.RandomState(seed)
    p = np.arange(256, dtype=int)
    rng.shuffle(p)
    return np.concatenate([p, p])  # repeat for overflow


def simplex_noise_3d(
    x: int,
    y: int,
    z: int,
    perm: Optional[np.ndarray] = None,
    f3=1.0 / 3.0,
    g3=1.0 / 6.0,
    grad3=np.array(
        [
            [1, 1, 0],
            [-1, 1, 0],
            [1, -1, 0],
            [-1, -1, 0],
            [1, 0, 1],
            [-1, 0, 1],
            [1, 0, -1],
            [-1, 0, -1],
            [0, 1, 1],
            [0, -1, 1],
            [0, 1, -1],
            [0, -1, -1],
        ],
        dtype=float,
    ),
):
    """Pure 3D Simplex noise, range ≈ [-1, 1].
    size = 128
    z = 16
    img = np.zeros((size, size))

    perm = _make_perm(seed=4544)

    for y in range(size):
        for x in range(size):
            img[y, x] = simplex_noise_3d(x * 0.05, y * 0.05, z * 0.05, perm)

    import matplotlib.pyplot as plt

    plt.imshow(img, cmap="viridis", origin="lower")
    plt.title("Simplex Noise 3D Slice")
    plt.show()

    """

    if perm is None:
        perm = make_perm(0)  # default seed

    # Skew the input space to determine which simplex cell we're in
    s = (x + y + z) * f3
    i = math.floor(x + s)
    j = math.floor(y + s)
    k = math.floor(z + s)

    # Unskew the cell origin back to (x,y,z) space
    t = (i + j + k) * g3
    X0 = i - t
    Y0 = j - t
    Z0 = k - t
    x0 = x - X0
    y0 = y - Y0
    z0 = z - Z0

    # Determine which simplex we’re in (rank order of x0, y0, z0)
    if x0 >= y0:
        if y0 >= z0:
            i1, j1, k1 = 1, 0, 0
            i2, j2, k2 = 1, 1, 0
        elif x0 >= z0:
            i1, j1, k1 = 1, 0, 0
            i2, j2, k2 = 1, 0, 1
        else:
            i1, j1, k1 = 0, 0, 1
            i2, j2, k2 = 1, 0, 1
    else:
        if y0 < z0:
            i1, j1, k1 = 0, 0, 1
            i2, j2, k2 = 0, 1, 1
        elif x0 < z0:
            i1, j1, k1 = 0, 1, 0
            i2, j2, k2 = 0, 1, 1
        else:
            i1, j1, k1 = 0, 1, 0
            i2, j2, k2 = 1, 1, 0

    # Offsets for other corners
    x1 = x0 - i1 + g3
    y1 = y0 - j1 + g3
    z1 = z0 - k1 + g3
    x2 = x0 - i2 + 2.0 * g3
    y2 = y0 - j2 + 2.0 * g3
    z2 = z0 - k2 + 2.0 * g3
    x3 = x0 - 1.0 + 3.0 * g3
    y3 = y0 - 1.0 + 3.0 * g3
    z3 = z0 - 1.0 + 3.0 * g3

    # Hashed gradient indices
    ii, jj, kk = i & 255, j & 255, k & 255
    g0 = grad3[perm[ii + perm[jj + perm[kk]]] % 12]
    g1 = grad3[perm[ii + i1 + perm[jj + j1 + perm[kk + k1]]] % 12]
    g2 = grad3[perm[ii + i2 + perm[jj + j2 + perm[kk + k2]]] % 12]
    g3 = grad3[perm[ii + 1 + perm[jj + 1 + perm[kk + 1]]] % 12]

    # Contribution from each corner
    def contrib(g, x, y, z):
        t = 0.6 - x * x - y * y - z * z
        if t < 0:
            return 0.0
        t *= t
        return t * t * np.dot(g, [x, y, z])

    n0 = contrib(g0, x0, y0, z0)
    n1 = contrib(g1, x1, y1, z1)
    n2 = contrib(g2, x2, y2, z2)
    n3 = contrib(g3, x3, y3, z3)

    # Final noise value scaled to roughly [-1, 1]
    return 32.0 * (n0 + n1 + n2 + n3)


def fbm_2d(
    x: int,
    y: int,
    octaves: int = 6,
    lacunarity: float = 2.0,
    persistence: float = 0.5,
    scale: float = 0.02,
):
    """
    Fractal Brownian Motion using 2D Simplex noise.

    Args:
        x, y : float
        octaves : number of noise layers
        lacunarity : frequency multiplier per octave
        persistence : amplitude decay per octave
        scale : base scale (controls zoom level)

    Returns:
        float : fBm noise value in [-1, 1] range

    Example usage:
    ```
    import numpy as np
    import matplotlib.pyplot as plt

    size = 256
    terrain = np.zeros((size, size))

    for y in range(size):
        for x in range(size):
            terrain[y, x] = fbm_2d(x, y,
                                octaves=6,
                                lacunarity=2.1,
                                persistence=0.48,
                                scale=0.015)

    plt.figure(figsize=(8,8))
    plt.imshow(terrain, cmap='terrain', origin='lower')
    plt.title("Fractal Brownian Motion Terrain (Simplex-based)")
    plt.colorbar(label='Height')
    plt.show()
    ```
    """
    value = 0.0
    amplitude = 1.0
    frequency = 1.0
    max_amplitude = 0.0

    for _ in range(octaves):
        nx = x * scale * frequency
        ny = y * scale * frequency
        value += amplitude * simplex_noise(nx, ny)
        max_amplitude += amplitude
        amplitude *= persistence
        frequency *= lacunarity

    # Normalize to roughly [-1, 1]
    return value / max_amplitude


def domain_warped_fbm_2d(
    x,
    y,
    base_octaves=5,
    base_scale=0.02,
    warp_octaves=3,
    warp_scale=0.04,
    warp_amplitude=20.0,
    lacunarity=2.0,
    persistence=0.5,
):
    """
    Domain-warped Fractal Brownian Motion (2D).

    Args:
        x, y : coordinates
        base_octaves : octaves for the main fBm
        base_scale : base frequency of main fBm
        warp_octaves : octaves for warp field
        warp_scale : scale (frequency) of warp field
        warp_amplitude : how much to warp coordinates
        lacunarity, persistence : control frequency/amplitude scaling

    Returns:
        float : warped fBm value in [-1, 1]

    Examples:
    ```
    import numpy as np
    import matplotlib.pyplot as plt

    size = 256
    terrain = np.zeros((size, size))

    for y in range(size):
        for x in range(size):
            terrain[y, x] = domain_warped_fbm_2d(x, y,
                                                base_octaves=6,
                                                base_scale=0.015,
                                                warp_octaves=3,
                                                warp_scale=0.03,
                                                warp_amplitude=15.0,
                                                lacunarity=2.1,
                                                persistence=0.5)

    plt.figure(figsize=(8, 8))
    plt.imshow(terrain, cmap='terrain', origin='lower')
    plt.title("Domain-Warped fBm Terrain (Simplex-based)")
    plt.colorbar(label='Height')
    plt.show()
    """

    # --- Warp field (displacement for coordinates) ---
    wx = fbm_2d(
        x + 100.0,
        y + 100.0,
        octaves=warp_octaves,
        lacunarity=lacunarity,
        persistence=persistence,
        scale=warp_scale,
    )

    wy = fbm_2d(
        x - 100.0,
        y - 100.0,
        octaves=warp_octaves,
        lacunarity=lacunarity,
        persistence=persistence,
        scale=warp_scale,
    )

    # Displace coordinates
    nx = x + warp_amplitude * wx
    ny = y + warp_amplitude * wy

    # --- Main terrain field ---
    h = fbm_2d(
        nx,
        ny,
        octaves=base_octaves,
        lacunarity=lacunarity,
        persistence=persistence,
        scale=base_scale,
    )

    return h


def fbm_3d(x, y, z, octaves=5, lacunarity=2.0, persistence=0.5, scale=0.02):
    value = 0.0
    amplitude = 1.0
    frequency = 1.0
    max_amplitude = 0.0

    for _ in range(octaves):
        nx = x * scale * frequency
        ny = y * scale * frequency
        nz = z * scale * frequency
        value += amplitude * simplex_noise_3d(nx, ny, nz)
        max_amplitude += amplitude
        amplitude *= persistence
        frequency *= lacunarity

    return value / max_amplitude


def domain_warped_fbm_3d(
    x,
    y,
    z,
    base_octaves=5,
    base_scale=0.02,
    warp_octaves=3,
    warp_scale=0.04,
    warp_amplitude=20.0,
    lacunarity=2.0,
    persistence=0.5,
):
    """
    3D domain-warped Fractal Brownian Motion.
    """
    # --- Warp fields (displace coordinates) ---
    wx = fbm_3d(
        x + 31.4,
        y + 47.2,
        z + 59.1,
        octaves=warp_octaves,
        lacunarity=lacunarity,
        persistence=persistence,
        scale=warp_scale,
    )
    wy = fbm_3d(
        x - 71.1,
        y + 13.3,
        z + 89.4,
        octaves=warp_octaves,
        lacunarity=lacunarity,
        persistence=persistence,
        scale=warp_scale,
    )
    wz = fbm_3d(
        x + 23.5,
        y - 37.9,
        z + 45.8,
        octaves=warp_octaves,
        lacunarity=lacunarity,
        persistence=persistence,
        scale=warp_scale,
    )

    # Warp the space
    nx = x + warp_amplitude * wx
    ny = y + warp_amplitude * wy
    nz = z + warp_amplitude * wz

    # --- Main field ---
    h = fbm_3d(
        nx,
        ny,
        nz,
        octaves=base_octaves,
        lacunarity=lacunarity,
        persistence=persistence,
        scale=base_scale,
    )
    return h


def worley_noise_2d(
    width, height, cell_size=32, distance_metric="euclidean", mode="f1"
):
    """
    Generate 2D Worley (Cellular) Noise.

    Args:
        width, height : output dimensions
        cell_size : size of each cell containing one feature point
        distance_metric : 'euclidean' or 'manhattan'
        mode : 'f1' (nearest) or 'f2-f1' (crack patterns)

    Returns:
        np.ndarray : noise map in [0, 1]

    example:
    ```
        noise_f1 = worley_noise_2d(256, 256, cell_size=32, mode='f1')
        noise_crack = worley_noise_2d(256, 256, cell_size=32, mode='f2-f1')

        plt.figure(figsize=(10, 4))
        plt.subplot(1, 2, 1)
        plt.imshow(noise_f1, cmap='viridis')
        plt.title("Worley F1 (Cellular Pattern)")
        plt.subplot(1, 2, 2)
        plt.imshow(noise_crack, cmap='inferno')
        plt.title("Worley (F2 - F1) Crack Pattern")
        plt.show()
    ```

    """
    nx, ny = width, height
    gx, gy = int(np.ceil(nx / cell_size)), int(np.ceil(ny / cell_size))

    # Generate random feature points within each grid cell
    fx = np.random.rand(gx, gy)
    fy = np.random.rand(gx, gy)

    # Coordinate grid
    xs, ys = np.meshgrid(np.arange(nx), np.arange(ny), indexing="xy")

    result = np.zeros((ny, nx))

    for j in range(gy):
        for i in range(gx):
            # Feature point position in world coords
            px = (i + fx[i, j]) * cell_size
            py = (j + fy[i, j]) * cell_size

            # Distance to this feature point
            dx = xs - px
            dy = ys - py

            if distance_metric == "euclidean":
                d = np.sqrt(dx * dx + dy * dy)
            else:
                d = np.abs(dx) + np.abs(dy)

            # Track nearest and 2nd nearest distances
            if (i, j) == (0, 0):
                d1 = d
                d2 = np.full_like(d, np.inf)
            else:
                d2 = np.minimum(np.maximum(d, d1), d2)
                d1 = np.minimum(d, d1)

    if mode == "f2-f1":
        result = d2 - d1
    else:
        result = d1

    # Normalize
    result = (result - result.min()) / (result.max() - result.min())
    return result


def curl_noise_2d(x, y, eps=1.0, scale=0.02):
    """
    Compute 2D curl noise vector at position (x, y).

    Args:
        eps : finite difference step
        scale : frequency of noise field

    Returns:
        (vx, vy): divergence-free vector field components

    Example:
    ```
    import matplotlib.pyplot as plt

    size = 64
    xv, yv = np.meshgrid(np.arange(size), np.arange(size), indexing='xy')
    u = np.zeros_like(xv, dtype=float)
    v = np.zeros_like(yv, dtype=float)

    for j in range(size):
        for i in range(size):
            vx, vy = curl_noise_2d(i, j, scale=0.05)
            u[j, i] = vx
            v[j, i] = vy

    plt.figure(figsize=(7,7))
    plt.quiver(xv, yv, u, v, scale=20)
    plt.title("2D Curl Noise Vector Field")
    plt.show()

    """

    # Base noise field (use fBm for richness)
    def n(px, py):
        return fbm_2d(px * scale, py * scale, octaves=4)

    # Partial derivatives (central differences)
    dx = (n(x + eps, y) - n(x - eps, y)) / (2 * eps)
    dy = (n(x, y + eps) - n(x, y - eps)) / (2 * eps)

    # 2D curl (rotate gradient 90 degrees)
    vx = dy
    vy = -dx
    return vx, vy


def curl_noise_3d(x, y, z, eps=1.0, scale=0.02):
    """
    Compute 3D curl noise vector at position (x, y, z).

    Args:
        eps : finite difference step
        scale : base scale for fBm field

    Returns:
        (vx, vy, vz) : divergence-free 3D vector

    Example:
        ```
        import matplotlib.pyplot as plt

        size = 64
        u = np.zeros((size, size))
        v = np.zeros((size, size))

        z = 0.0
        for j in range(size):
            for i in range(size):
                vx, vy, vz = curl_noise_3d(i, j, z, scale=0.05)
                u[j, i] = vx
                v[j, i] = vy

        plt.figure(figsize=(7,7))
        plt.quiver(u, v, scale=30)
        plt.title("2D Slice of 3D Curl Noise (Z=0)")
        plt.show()
        ```

        Normalize the Vector Field

        To make it usable as a direction field:
        ```
        length = np.sqrt(vx*vx + vy*vy + vz*vz) + 1e-8
        vx /= length
        vy /= length
        vz /= length
        ```

        blend two curl fields of different frequencies for multi-scale turbulence:
        ```
        vx1, vy1, vz1 = curl_noise_3d(x, y, z, scale=0.03)
        vx2, vy2, vz2 = curl_noise_3d(x, y, z, scale=0.1)
        vx = 0.7 * vx1 + 0.3 * vx2
        vy = 0.7 * vy1 + 0.3 * vy2
        vz = 0.7 * vz1 + 0.3 * vz2
        ```
    """

    # Vector field F = (fx, fy, fz)
    def F(px, py, pz):
        fx = fbm_3d(px, py, pz, scale=scale)
        fy = fbm_3d(py + 19.1, pz + 7.7, px + 3.1, scale=scale)
        fz = fbm_3d(pz + 13.5, px + 17.2, py + 9.5, scale=scale)
        return fx, fy, fz

    # Finite differences
    fx1, fy1, fz1 = F(x, y + eps, z)
    fx2, fy2, fz2 = F(x, y - eps, z)
    fx3, fy3, fz3 = F(x, y, z + eps)
    fx4, fy4, fz4 = F(x, y, z - eps)
    fx5, fy5, fz5 = F(x + eps, y, z)
    fx6, fy6, fz6 = F(x - eps, y, z)

    # Partial derivatives
    dFy_dz = (fy3 - fy4) / (2 * eps)
    dFz_dy = (fz1 - fz2) / (2 * eps)
    dFz_dx = (fz5 - fz6) / (2 * eps)
    dFx_dz = (fx3 - fx4) / (2 * eps)
    dFx_dy = (fx1 - fx2) / (2 * eps)
    dFy_dx = (fy5 - fy6) / (2 * eps)

    # Curl
    vx = dFz_dy - dFy_dz
    vy = dFx_dz - dFz_dx
    vz = dFy_dx - dFx_dy

    return vx, vy, vz


def worley_noise_3d(x, y, z, cell_size=1.0, seed=42, return_f2=False):
    """
    3D Worley (cellular) noise.

    Args:
        x, y, z : coordinates (floats or arrays)
        cell_size : spacing of feature cells
        seed : random seed for reproducibility
        return_f2 : if True, return both F1 and F2

    Returns:
        F1 (and optionally F2): nearest (and second-nearest) feature distance

    Example:
    ```
        import matplotlib.pyplot as plt

        size = 128
        xs = np.linspace(0, 10, size)
        ys = np.linspace(0, 10, size)
        x, y = np.meshgrid(xs, ys)
        z = np.zeros_like(x)

        f1, f2 = worley_noise_3d(x, y, z, cell_size=1.0, return_f2=True)
        value = f2 - f1  # Difference between first and second nearest

        plt.imshow(value, cmap='inferno', origin='lower')
        plt.title("Worley Noise (F2 - F1)")
        plt.colorbar()
        plt.show()
    ```
    """
    rng = np.random.default_rng(seed)

    # Determine integer cell coordinates
    xi = np.floor(x / cell_size).astype(int)
    yi = np.floor(y / cell_size).astype(int)
    zi = np.floor(z / cell_size).astype(int)

    # Initialize F1 and F2 as large values
    F1 = np.full_like(x, np.inf, dtype=float)
    F2 = np.full_like(x, np.inf, dtype=float)

    # Search nearby cells
    for dz in range(-1, 2):
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                # Neighbor cell coordinates
                cx = xi + dx
                cy = yi + dy
                cz = zi + dz

                # Random feature point inside that cell
                # Hash-based pseudorandom generation
                h = (cx * 374761393 + cy * 668265263 + cz * 2147483647) ^ seed
                h = (h * 0x27D4EB2D) & 0xFFFFFFFF
                rng_state = np.sin(h) * 43758.5453
                rx = rng_state % 1.0
                ry = (rng_state * 1.3) % 1.0
                rz = (rng_state * 1.7) % 1.0

                fx = (cx + rx) * cell_size
                fy = (cy + ry) * cell_size
                fz = (cz + rz) * cell_size

                # Distance to the feature point
                dist = np.sqrt((x - fx) ** 2 + (y - fy) ** 2 + (z - fz) ** 2)

                # Sort distances
                mask = dist < F1
                F2 = np.where(mask, F1, np.minimum(F2, dist))
                F1 = np.where(mask, dist, F1)

    return (F1, F2) if return_f2 else F1
