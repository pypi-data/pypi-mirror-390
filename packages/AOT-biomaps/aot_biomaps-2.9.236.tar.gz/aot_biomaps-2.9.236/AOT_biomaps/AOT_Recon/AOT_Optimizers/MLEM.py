from AOT_biomaps.AOT_Recon.ReconTools import _forward_projection, _backward_projection, check_gpu_memory, calculate_memory_requirement
from AOT_biomaps.Config import config
import numba
import torch
import numpy as np
import os
from tqdm import trange
import cupy as cp
import cupyx.scipy.sparse as cpsparse
import gc


def MLEM(
    SMatrix,
    y,
    numIterations=100,
    isSavingEachIteration=True,
    withTumor=True,
    device=None,
    use_numba=False,
    denominator_threshold=1e-6,
    max_saves=5000,
    show_logs=True,
    useSparseSMatrix=True,
    Z=350,
):
    """
    Unified MLEM algorithm for Acousto-Optic Tomography.
    Works on CPU (basic, multithread, optimized) and GPU (single or multi-GPU).
    Args:
        SMatrix: System matrix (shape: T, Z, X, N)
        y: Measurement data (shape: T, N)
        numIterations: Number of iterations
        isSavingEachIteration: If True, saves intermediate results
        withTumor: Boolean for description only
        device: Torch device (auto-selected if None)
        use_multi_gpu: If True and GPU available, uses all GPUs
        use_numba: If True and on CPU, uses multithreaded Numba
        max_saves: Maximum number of intermediate saves (default: 5000)
    Returns:
        Reconstructed image(s) and iteration indices (if isSavingEachIteration)
    """
    try:
        tumor_str = "WITH" if withTumor else "WITHOUT"
        # Auto-select device and method
        if device is None:
            if torch.cuda.is_available() and check_gpu_memory(config.select_best_gpu(), calculate_memory_requirement(SMatrix, y), show_logs=show_logs):
                device = torch.device(f"cuda:{config.select_best_gpu()}")
                use_gpu = True
            else:
                device = torch.device("cpu")
                use_gpu = False
        else:
            use_gpu = device.type == "cuda"
        # Dispatch to the appropriate implementation
        if use_gpu:
                if useSparseSMatrix:
                    return _MLEM_sparseCSR(SMatrix, y, numIterations, isSavingEachIteration, tumor_str, device.index, max_saves, denominator_threshold, Z, show_logs)
                else:
                    return _MLEM_single_GPU(SMatrix, y, numIterations, isSavingEachIteration, tumor_str, device, max_saves, denominator_threshold,show_logs)
        else:
            if use_numba:
                return _MLEM_CPU_numba(SMatrix, y, numIterations, isSavingEachIteration, tumor_str, max_saves, denominator_threshold, show_logs)
            else:
                return _MLEM_CPU_opti(SMatrix, y, numIterations, isSavingEachIteration, tumor_str, max_saves, denominator_threshold, show_logs)
    except Exception as e:
        print(f"Error in MLEM: {type(e).__name__}: {e}")
        return None, None

def _MLEM_single_GPU(SMatrix, y, numIterations, isSavingEachIteration, tumor_str, device, max_saves, denominator_threshold, show_logs=True):
    try:
        eps = torch.finfo(torch.float32).eps
        T, Z, X, N = SMatrix.shape
        ZX = Z * X
        TN = T * N
        A_flat = (
            torch.from_numpy(SMatrix)
            .to(device=device, dtype=torch.float32)
            .permute(0, 3, 1, 2)
            .contiguous()
            .reshape(TN, ZX)
        )
        y_flat = torch.from_numpy(y).to(device=device, dtype=torch.float32).reshape(-1)
        theta_flat = torch.ones(ZX, dtype=torch.float32, device=device)
        norm_factor_flat = (
            torch.from_numpy(SMatrix)
            .to(device=device, dtype=torch.float32)
            .sum(dim=(0, 3))
            .reshape(-1)
        )
        description = f"AOT-BioMaps -- ML-EM ---- {tumor_str} TUMOR ---- GPU {torch.cuda.current_device()}"
        # Calculate save indices
        if numIterations <= max_saves:
            save_indices = list(range(numIterations))
        else:
            step = numIterations // max_saves
            save_indices = list(range(0, numIterations, step))
            if save_indices[-1] != numIterations - 1:
                save_indices.append(numIterations - 1)
        saved_theta = []
        saved_indices = []
        with torch.no_grad():
            # Utilise range si show_logs=False, sinon trange
            iterator = trange(numIterations, desc=description) if show_logs else range(numIterations)
            for it in iterator:
                q_flat = A_flat @ theta_flat
                # Appliquer le seuil : si q_flat < denominator_threshold, on met e_flat à 1 (comme dans le code C++)
                mask = q_flat >= denominator_threshold
                e_flat = torch.where(mask, y_flat / (q_flat + eps), torch.ones_like(q_flat))
                c_flat = A_flat.T @ e_flat
                theta_flat = (theta_flat / (norm_factor_flat + eps)) * c_flat
                if isSavingEachIteration and it in save_indices:
                    saved_theta.append(theta_flat.reshape(Z, X).clone())
                    saved_indices.append(it)
        # Free memory
        del A_flat, y_flat, norm_factor_flat
        torch.cuda.empty_cache()
        if isSavingEachIteration:
            return [t.cpu().numpy() for t in saved_theta], saved_indices
        else:
            return theta_flat.reshape(Z, X).cpu().numpy(), None
    except Exception as e:
        print(f"Error in single-GPU MLEM: {type(e).__name__}: {e}")
        torch.cuda.empty_cache()
        return None, None

def _MLEM_CPU_numba(SMatrix, y, numIterations, isSavingEachIteration, tumor_str, max_saves, denominator_threshold, show_logs=True):
    try:
        numba.set_num_threads(os.cpu_count())
        q_p = np.zeros((SMatrix.shape[0], SMatrix.shape[3]), dtype=np.float32)
        c_p = np.zeros((SMatrix.shape[1], SMatrix.shape[2]), dtype=np.float32)
        theta_p_0 = np.ones((SMatrix.shape[1], SMatrix.shape[2]), dtype=np.float32)
        matrix_theta = [theta_p_0]
        saved_indices = [0]
        normalization_factor = np.sum(SMatrix, axis=(0, 3)).astype(np.float32)

        # Calculate save indices
        if numIterations <= max_saves:
            save_indices = list(range(numIterations))
        else:
            step = numIterations // max_saves
            save_indices = list(range(0, numIterations, step))
            if save_indices[-1] != numIterations - 1:
                save_indices.append(numIterations - 1)

        description = f"AOT-BioMaps -- ML-EM ---- {tumor_str} TUMOR ---- processing on multithread CPU ({numba.config.NUMBA_DEFAULT_NUM_THREADS} threads) ----"
        iterator = trange(numIterations, desc=description) if show_logs else range(numIterations)

        for it in iterator:
            theta_p = matrix_theta[-1]
            _forward_projection(SMatrix, theta_p, q_p)

            # Appliquer le seuil : si q_p < denominator_threshold, on met e_p à 1
            mask = q_p >= denominator_threshold
            e_p = np.where(mask, y / (q_p + 1e-8), 1.0)

            _backward_projection(SMatrix, e_p, c_p)
            theta_p_plus_1 = theta_p / (normalization_factor + 1e-8) * c_p

            if isSavingEachIteration and (it + 1) in save_indices:
                matrix_theta.append(theta_p_plus_1)
                saved_indices.append(it + 1)
            else:
                matrix_theta[-1] = theta_p_plus_1

        if not isSavingEachIteration:
            return matrix_theta[-1], None
        else:
            return matrix_theta, saved_indices
    except Exception as e:
        print(f"Error in Numba CPU MLEM: {type(e).__name__}: {e}")
        return None, None

def _MLEM_CPU_opti(SMatrix, y, numIterations, isSavingEachIteration, tumor_str, max_saves, denominator_threshold, show_logs=True):
    try:
        T, Z, X, N = SMatrix.shape
        A_flat = SMatrix.astype(np.float32).transpose(0, 3, 1, 2).reshape(T * N, Z * X)
        y_flat = y.astype(np.float32).reshape(-1)
        theta_0 = np.ones((Z, X), dtype=np.float32)
        matrix_theta = [theta_0]
        saved_indices = [0]
        normalization_factor = np.sum(SMatrix, axis=(0, 3)).astype(np.float32)
        normalization_factor_flat = normalization_factor.reshape(-1)

        # Calculate save indices
        if numIterations <= max_saves:
            save_indices = list(range(numIterations))
        else:
            step = numIterations // max_saves
            save_indices = list(range(0, numIterations, step))
            if save_indices[-1] != numIterations - 1:
                save_indices.append(numIterations - 1)

        description = f"AOT-BioMaps -- ML-EM ---- {tumor_str} TUMOR ---- processing on single CPU (optimized) ----"
        iterator = trange(numIterations, desc=description) if show_logs else range(numIterations)

        for it in iterator:
            theta_p = matrix_theta[-1]
            theta_p_flat = theta_p.reshape(-1)
            q_flat = A_flat @ theta_p_flat

            # Appliquer le seuil : si q_flat < denominator_threshold, on met e_flat à 1
            mask = q_flat >= denominator_threshold
            e_flat = np.where(mask, y_flat / (q_flat + np.finfo(np.float32).tiny), 1.0)

            c_flat = A_flat.T @ e_flat
            theta_p_plus_1_flat = theta_p_flat / (normalization_factor_flat + np.finfo(np.float32).tiny) * c_flat
            theta_p_plus_1 = theta_p_plus_1_flat.reshape(Z, X)

            if isSavingEachIteration and (it + 1) in save_indices:
                matrix_theta.append(theta_p_plus_1)
                saved_indices.append(it + 1)
            else:
                matrix_theta[-1] = theta_p_plus_1

        if not isSavingEachIteration:
            return matrix_theta[-1], None
        else:
            return matrix_theta, saved_indices
    except Exception as e:
        print(f"Error in optimized CPU MLEM: {type(e).__name__}: {e}")
        return None, None



def _MLEM_sparseCSR(
    SMatrix,
    y,
    numIterations,
    isSavingEachIteration,
    tumor_str,
    device_index,
    max_saves,
    denominator_threshold,
    Z,
    show_logs=True,
):
    """
    MLEM implementation using CuPy with sparse CSR matrix on a single GPU.
    Caution : SMatrix must be a cupyx.scipy.sparse.csr_matrix please sparse it before using.
    """
    try:
        cp.cuda.Device(device_index).use()
        dtype = cp.float32
        eps = cp.finfo(dtype).eps

        # --- Préparation de la matrice et des données ---
        if not isinstance(SMatrix, cpsparse.csr_matrix):
            SMatrix = cpsparse.csr_matrix(SMatrix, dtype=dtype)
        else:
            SMatrix = SMatrix.astype(dtype)

        if not isinstance(y, cp.ndarray):
            y_cupy = cp.asarray(y, dtype=dtype)
        else:
            y_cupy = y.astype(dtype)

        TN, ZX = SMatrix.shape
        X = ZX // Z

        # Initialisation du volume reconstruit
        theta_flat = cp.full(ZX, 0.1, dtype=dtype)

        # Facteur de normalisation
        norm_factor = cp.maximum(SMatrix.sum(axis=0).ravel(), 1e-6)
        norm_factor_inv = 1.0 / norm_factor

        # Gestion des indices de sauvegarde
        if numIterations <= max_saves:
            save_indices = list(range(numIterations))
        else:
            step = max(1, numIterations // max_saves)
            save_indices = list(range(0, numIterations, step))
            if save_indices[-1] != numIterations - 1:
                save_indices.append(numIterations - 1)

        saved_theta = []
        saved_indices = []

        description = f"AOT-BioMaps -- ML-EM (sparse CSR) ---- {tumor_str} TUMOR ---- GPU {device_index}"

        iterator = trange(numIterations, desc=description, ncols=100) if show_logs else range(numIterations)

        # --- Boucle principale MLEM ---
        for it in iterator:
            # Étape 1 : Projection
            q_flat = SMatrix.dot(theta_flat)
            q_flat = cp.maximum(q_flat, denominator_threshold)

            # Étape 2 : Rapport y / (A*L)
            e_flat = y_cupy / q_flat

            # Étape 3 : Rétroprojection (A.T * e)
            c_flat = SMatrix.T.dot(e_flat)

            # Étape 4 : Mise à jour
            theta_flat = theta_flat * (norm_factor_inv * c_flat)
            theta_flat = cp.maximum(theta_flat, 0)

            # Sauvegarde éventuelle
            if isSavingEachIteration and it in save_indices:
                saved_theta.append(theta_flat.reshape(Z, X).get())  # transfert CPU
                saved_indices.append(it)

            # Libération mémoire GPU
            del q_flat, e_flat, c_flat
            cp.get_default_memory_pool().free_all_blocks()
            gc.collect()

            # Vérif convergence toutes les 10 itérations
            if it % 10 == 0 and show_logs:
                rel_change = cp.abs(theta_flat - theta_flat).max() / (theta_flat.max() + eps)
                if rel_change < 1e-4:
                    print(f"Convergence atteinte à l’itération {it}")
                    break

        # --- Fin : récupération du résultat ---
        result = theta_flat.reshape(Z, X).get()  # Retour sur CPU
        del theta_flat, norm_factor, norm_factor_inv
        cp.get_default_memory_pool().free_all_blocks()
        gc.collect()

        if isSavingEachIteration:
            return saved_theta, saved_indices
        else:
            return result, None

    except Exception as e:
        print(f"Erreur dans _MLEM_single_GPU_CuPy: {type(e).__name__}: {e}")
        cp.get_default_memory_pool().free_all_blocks()
        gc.collect()
        return None, None

