""" """

import os
import sys
import time
from bisect import bisect  # RGB

import h5py
import numpy as np
import plotly.graph_objects as go
import pysptools.eea as eea
import pywt  # DIMENSIONALITY REDUCTION
import scipy.io as spio  # RGB
import spectral
import umap
from numpy.linalg import svd
from pybaselines import Baseline
from scipy import interpolate
from scipy.interpolate import PchipInterpolator  # RGB
from scipy.io import loadmat
from scipy.ndimage import gaussian_filter, median_filter
from scipy.optimize import nnls
from scipy.signal import find_peaks, peak_widths, savgol_filter
from scipy.sparse import csc_matrix, issparse
from sklearn.decomposition import NMF, PCA

# import ramanspy as rp
from sklearn.metrics.pairwise import distance_metrics


def open_file(filepath, hsi_cube_var=None, wl_var=None):
    """ """
    file_extension = filepath.split(".")[-1].lower()
    if file_extension not in ["mat", "h5"]:
        print(
            f"Error: file format not supported. Expected .mat o .h5, found .{file_extension}."
        )
        return None, None

    hypercube_names = [
        "data",
        "data_RIFLE",
        "Y",
        "Hyperspectrum_cube",
        "XRFdata",
        "spectra",
        "HyperMatrix",
        "H",
    ]
    wls_names = [
        "WL",
        "WL_RIFLE",
        "X",
        "fr_real",
        "spectra",
        "wavelength",
        "ENERGY",
        "t",
    ]

    data = None
    wl = None

    if hsi_cube_var is not None and wl_var is not None:
        hypercube_names.append(hsi_cube_var)
        wls_names.append(wl_var)

    # if .mat file
    if file_extension == "mat":
        f = loadmat(filepath)
        print("Dataset presents (MATLAB file):")
        for dataset_name in f:
            print(dataset_name)
            if dataset_name in hypercube_names:
                data = np.array(f[dataset_name])
                if dataset_name == "Hyperspectrum_cube":
                    data = data[:, :, ::-1]
                data = np.rot90(data, k=1, axes=(0, 1))
                # data = data[::-1, ::-1, :]
                if dataset_name == "H":
                    wl = np.linspace(0, 1, data.shape[2])
            if dataset_name in wls_names:
                wl = np.array(f[dataset_name]).flatten()
                if dataset_name == "fr_real":
                    wl = 3 * 10**5 / wl
                    wl = wl[::-1]
        if data is not None and wl is not None:
            data = np.rot90(data, k=3)
            print("Data shape:", data.shape, "\nWL shape:", wl.shape)
            return data, wl
        else:
            print("ERROR: the .mat file does not contain correct data names.")
            return 1, 1

    # If .h5 file
    elif file_extension == "h5":
        with h5py.File(filepath, "r") as f:
            print("Dataset presents (HDF5 file):")
            for dataset_name in f:
                print(dataset_name)
                if dataset_name in hypercube_names:
                    data = np.array(f[dataset_name])
                    if dataset_name == "Hyperspectrum_cube":
                        data = data[:, :, ::-1]
                if dataset_name in wls_names:
                    wl = np.array(f[dataset_name]).flatten()
                    if dataset_name == "fr_real":
                        wl = 3 * 10**5 / wl
                        wl = wl[::-1]
        if data is not None and wl is not None:
            data = np.rot90(data, k=3)
            print("Data shape:", data.shape, "\nWL shape:", wl.shape)
            return data, wl
        else:
            print("ERROR: the .h5 file does not contain correct data names.")
            return 1, 1


# %% CROP XY
def crop_xy(data, shape, rgb=None):
    min_y, max_y = int(np.min(shape[:, 2])), int(np.max(shape[:, 2]))
    min_x, max_x = int(np.min(shape[:, 1])), int(np.max(shape[:, 1]))

    print("Points selected for cropping: ", min_x, max_x, min_y, max_y)
    crop_array = [min_x, max_x, min_y, max_y]
    data = data[
        crop_array[0] : crop_array[1], crop_array[2] : crop_array[3], :
    ]
    print(f"Cropped shape: {data.shape}")

    if rgb is not None:
        rgb = rgb[
            crop_array[0] : crop_array[1], crop_array[2] : crop_array[3], :
        ]
        return data, rgb
    else:
        return data


# %% CREATE MASK
def create_mask(data, rgb, mask):
    data = data * mask[: data.shape[0], : data.shape[1], np.newaxis]
    rgb = rgb * mask[: data.shape[0], : data.shape[1], np.newaxis]
    return data, rgb


# WE ARE USING IT?
def plotSpectra(data, label, wl):
    """ """
    dataMasked = np.einsum("ijk,jk->ijk", data, label)
    dataSum = np.sum(
        dataMasked.reshape(
            dataMasked.shape[0], dataMasked.shape[1] * dataMasked.shape[2]
        ),
        1,
    )
    print(dataSum)
    return dataSum


# %% NORMALIZATION
def normalize(channel):
    """ """
    return (channel - np.min(channel)) / (np.max(channel) - np.min(channel))


# %% CREATE RGB
def HSI2RGB(wY, HSI_cube, ydim, xdim, d, threshold):
    """ """
    # wY: wavelengths in nm
    # Y : HSI as a (#pixels x #bands) matrix,
    # dims: x & y dimension of image
    # d: 50, 55, 65, 75, determines the illuminant used, if in doubt use d65
    # thresholdRGB : True if thesholding should be done to increase contrast
    #
    #
    # If you use this method, please cite the following paper:
    #  M. Magnusson, J. Sigurdsson, S. E. Armansson, M. O. Ulfarsson,
    #  H. Deborah and J. R. Sveinsson,
    #  "Creating RGB Images from Hyperspectral Images Using a Color Matching Function",
    #  IEEE International Geoscience and Remote Sensing Symposium, Virtual Symposium, 2020
    #
    #  @INPROCEEDINGS{hsi2rgb,
    #  author={M. {Magnusson} and J. {Sigurdsson} and S. E. {Armansson}
    #  and M. O. {Ulfarsson} and H. {Deborah} and J. R. {Sveinsson}},
    #  booktitle={IEEE International Geoscience and Remote Sensing Symposium},
    #  title={Creating {RGB} Images from Hyperspectral Images using a Color Matching Function},
    #  year={2020}, volume={}, number={}, pages={}}
    #
    # Paper is available at
    # https://www.researchgate.net/profile/Jakob_Sigurdsson

    HSI = np.reshape(HSI_cube, [-1, HSI_cube.shape[2]]) / HSI_cube.max()

    # Load reference illuminant
    file_path = os.path.join(os.path.dirname(__file__), "D_illuminants.mat")
    D = spio.loadmat(file_path)
    # D = spio.loadmat(
    #    r"C:\Users\User\OneDrive - Politecnico di Milano\PhD\Programmi\Pyhton\ANALISI\D_illuminants.mat"
    # )
    w = D["wxyz"][:, 0]
    x = D["wxyz"][:, 1]
    y = D["wxyz"][:, 2]
    z = D["wxyz"][:, 3]
    D = D["D"]

    i = {50: 2, 55: 3, 65: 1, 75: 4}
    wI = D[:, 0]
    I_matrix = D[:, i[d]]

    # Interpolate to image wavelengths
    I_matrix = PchipInterpolator(wI, I_matrix, extrapolate=True)(
        wY
    )  # interp1(wI,I,wY,'pchip','extrap')';
    x = PchipInterpolator(w, x, extrapolate=True)(
        wY
    )  # interp1(w,x,wY,'pchip','extrap')';
    y = PchipInterpolator(w, y, extrapolate=True)(
        wY
    )  # interp1(w,y,wY,'pchip','extrap')';
    z = PchipInterpolator(w, z, extrapolate=True)(
        wY
    )  # interp1(w,z,wY,'pchip','extrap')';

    # Truncate at 780nm
    i = bisect(wY, 780)
    HSI = HSI[:, 0:i] / HSI.max()
    wY = wY[:i]
    I_matrix = I_matrix[:i]
    x = x[:i]
    y = y[:i]
    z = z[:i]

    # Compute k
    k = 1 / np.trapz(y * I_matrix, wY)

    # Compute X,Y & Z for image
    X = k * np.trapz(HSI @ np.diag(I_matrix * x), wY, axis=1)
    Z = k * np.trapz(HSI @ np.diag(I_matrix * z), wY, axis=1)
    Y = k * np.trapz(HSI @ np.diag(I_matrix * y), wY, axis=1)

    XYZ = np.array([X, Y, Z])

    # Convert to RGB
    M = np.array(
        [
            [3.2404542, -1.5371385, -0.4985314],
            [-0.9692660, 1.8760108, 0.0415560],
            [0.0556434, -0.2040259, 1.0572252],
        ]
    )
    sRGB = M @ XYZ

    # Gamma correction
    gamma_map = sRGB > 0.0031308
    sRGB[gamma_map] = 1.055 * np.power(sRGB[gamma_map], (1.0 / 2.4)) - 0.055
    sRGB[np.invert(gamma_map)] = 12.92 * sRGB[np.invert(gamma_map)]
    # Note: RL, GL or BL values less than 0 or greater than 1 are clipped to 0 and 1.
    sRGB[sRGB > 1] = 1
    sRGB[sRGB < 0] = 0

    if threshold:
        for idx in range(3):
            y = sRGB[idx, :]
            a, b = np.histogram(y, 100)
            b = b[:-1] + np.diff(b) / 2
            a = np.cumsum(a) / np.sum(a)
            th = b[0]
            i = a < threshold
            if i.any():
                th = b[i][-1]
            y = y - th
            y[y < 0] = 0

            a, b = np.histogram(y, 100)
            b = b[:-1] + np.diff(b) / 2
            a = np.cumsum(a) / np.sum(a)
            i = a > 1 - threshold
            th = b[i][0]
            y[y > th] = th
            y = y / th
            sRGB[idx, :] = y

    R = np.reshape(sRGB[0, :], [ydim, xdim])
    G = np.reshape(sRGB[1, :], [ydim, xdim])
    B = np.reshape(sRGB[2, :], [ydim, xdim])
    return np.transpose(np.array([R, G, B]), [1, 2, 0])


# %% RGB TO HEX: create a matrix with hex strings of rgb in that pixel
def RGB_to_hex(RGB_image, brightness_factor=1.1):
    """ """
    RGB_image = np.clip(RGB_image * brightness_factor, 0, 1)
    image_scaled = (RGB_image * 255).astype(int)
    hex_matrix = np.apply_along_axis(
        lambda rgb: "#{:02x}{:02x}{:02x}".format(*rgb),
        axis=2,
        arr=image_scaled,
    )
    return hex_matrix


# %% FALSE RGB:
def falseRGB(data, wl, R, G, B):
    """ """
    R = np.array(R)
    G = np.array(G)
    B = np.array(B)
    R_image = np.mean(
        data[
            :,
            :,
            (np.abs(wl - R[0])).argmin() : (np.abs(wl - R[1])).argmin() + 1,
        ],
        axis=2,
    )
    G_image = np.mean(
        data[
            :,
            :,
            (np.abs(wl - G[0])).argmin() : (np.abs(wl - G[1])).argmin() + 1,
        ],
        axis=2,
    )
    B_image = np.mean(
        data[
            :,
            :,
            (np.abs(wl - B[0])).argmin() : (np.abs(wl - B[1])).argmin() + 1,
        ],
        axis=2,
    )
    R_image = normalize(R_image)
    G_image = normalize(G_image)
    B_image = normalize(B_image)
    rgb_image = np.stack([R_image, G_image, B_image], axis=-1)
    rgb_uint8 = (rgb_image * 255).astype(np.uint8)
    return rgb_uint8


# %% SVD DENOISING
def SVD_denoise(dataset, components, matrices=None):
    if matrices is None:
        data_reshaped = dataset.reshape(-1, dataset.shape[2])
        U, S, VT = svd(data_reshaped, full_matrices=False)
    else:
        U, S, VT = matrices

    data_approx = np.dot(
        U[:, :components], np.dot(np.diag(S[:components]), VT[:components, :])
    )
    data_denoised = data_approx.reshape(dataset.shape)
    return data_denoised, [U, S, VT]


# %% PREPROCESSING
def preprocessing(
    data,
    medfilt_w,
    gaussian_s,
    savgol_w,
    savgol_pol,
    bkg_w,
    medfilt_checkbox=True,
    gaussian_checkbox=True,
    savgol_checkbox=True,
    bkg_checkbox=True,
):
    """ """
    data_processed = data
    print("Data is now data_processed")

    if savgol_checkbox:
        print(
            "Doing Savitzki-Golay filter: Window=",
            str(savgol_w),
            " Polynomial: ",
            str(savgol_pol),
        )
        data_processed = savgol_filter(
            data_processed, savgol_w, savgol_pol, axis=2
        )

    if bkg_checkbox:
        baseline_fitter = Baseline(x_data=np.arange(data_processed.shape[2]))
        data_reshaped = data_processed.reshape(-1, data_processed.shape[2])
        for i in range(data_processed.shape[0] * data_processed.shape[1]):
            # baseline = baseline_fitter.asls(data_reshaped[i,:], lam=1e8, p=0.2)[0]
            # baseline = baseline_fitter.beads(data_reshaped[i,:], lam_0=0.06, lam_1=0.8, lam_2=0.5, tol=1e-6,
            # freq_cutoff=0.04, asymmetry=3)[0]

            baseline = baseline_fitter.snip(
                data_reshaped[i, :],
                max_half_window=bkg_w,
                decreasing=True,
                smooth_half_window=2,
            )[0]

            data_reshaped[i, :] = np.clip(
                data_reshaped[i, :] - baseline, 0, max(data_reshaped[i, :])
            )
        data_processed = data_reshaped.reshape(data_processed.shape)

    if medfilt_checkbox:
        print("Doing medfilt with window: " + str(medfilt_w))
        for i in range(data_processed.shape[2]):
            data_processed[:, :, i] = abs(
                # medfilt2d(data_processed[:, :, i], medfilt_w)
                median_filter(data_processed[:, :, i], size=medfilt_w)
                # gaussian_filter(data_processed[:, :, i], sigma=medfilt_w)
            )

    if gaussian_checkbox:
        print("Doing gaussian filter with sigma: " + str(gaussian_s))
        for i in range(data_processed.shape[2]):
            data_processed[:, :, i] = gaussian_filter(
                data_processed[:, :, i], sigma=gaussian_s
            )

    return data_processed


# %% DESPIKE DATA


def spike_removal(
    y,
    width_threshold,
    prominence_threshold=None,
    moving_average_window=10,
    width_param_rel=0.8,
    interp_type="linear",
):
    """
    Detects and replaces spikes in the input spectrum with interpolated values. Algorithm first
    published by N. Coca-Lopez in Analytica Chimica Acta. https://doi.org/10.1016/j.aca.2024.342312

    Parameters:
    y (numpy.ndarray): Input spectrum intensity.
    width_threshold (float): Threshold for peak width.
    prominence_threshold (float): Threshold for peak prominence.
    moving_average_window (int): Number of points in moving average window.
    width_param_rel (float): Relative height parameter for peak width.
    tipo: type of interpolation (linear, quadratic, cubic)

    Returns:
    numpy.ndarray: Signal with spikes replaced by interpolated values.
    """

    # First, we find all peaks showing a prominence above prominence_threshold on the spectra
    peaks, _ = find_peaks(y, prominence=prominence_threshold)

    # Create a vector where spikes will be flag: no spike = 0, spike = 1.
    spikes = np.zeros(len(y))

    # Calculation of the widths of the found peaks
    widths = peak_widths(y, peaks)[0]

    # Calculation of the range where the spectral points are asumed to be corrupted
    widths_ext_a = peak_widths(y, peaks, rel_height=width_param_rel)[2]
    widths_ext_b = peak_widths(y, peaks, rel_height=width_param_rel)[3]

    # Flagging the area previously defined if the peak is considered a spike (width below width_threshold)
    for _a, width, ext_a, ext_b in zip(
        range(len(widths)), widths, widths_ext_a, widths_ext_b, strict=False
    ):
        if width < width_threshold:
            spikes[int(ext_a) - 1 : int(ext_b) + 2] = 1

    y_out = y.copy()

    # Interpolation of corrupted points
    for i, spike in enumerate(spikes):
        if spike != 0:  # If we have a spike in position i
            window = np.arange(
                i - moving_average_window, i + moving_average_window + 1
            )
            window = window[
                (window >= 0) & (window < len(y))
            ]  # evita out-of-bounds

            window_exclude_spikes = window[spikes[window] == 0]
            if len(window_exclude_spikes) >= 2 and np.min(
                window_exclude_spikes
            ) <= i <= np.max(window_exclude_spikes):
                interpolator = interpolate.interp1d(
                    window_exclude_spikes,
                    y[window_exclude_spikes],
                    kind=interp_type,
                    bounds_error=False,
                    fill_value="extrapolate",
                )
                y_out[i] = interpolator(i)
            elif len(window_exclude_spikes) > 0:
                y_out[i] = np.mean(y[window_exclude_spikes])

    return y_out


def despike(cube, window_size=3, threshold=0.5):
    """
    Per ogni banda, calcola l'autocorrelazione locale e sostituisce i pixel con valori bassi (< threshold)
    con la media dei vicini, *escludendo* i pixel marcati.
    """
    h, w, b = cube.shape
    corrected = cube.copy()
    corrected_reshaped = corrected.reshape(-1, b)

    for k in range(h * w):
        spectrum = corrected_reshaped[k, :]
        intensity_despiked = spike_removal(
            spectrum,
            width_threshold=3,
            prominence_threshold=20,
            moving_average_window=10,
            width_param_rel=0.8,
            interp_type="linear",
        )

        corrected_reshaped[k, :] = intensity_despiked
    corrected = corrected_reshaped.reshape(h, w, b)

    return corrected


# %% DIMENSIONALITY REDUCTION
# SPATIAL DIMENSION WITH DWT
def reduce_spatial_dimension_dwt(hsi_cube, wavelet="haar", level=1):
    """ """
    H, W, B = hsi_cube.shape
    reduced_cube = []
    LH_cube = []
    HL_cube = []
    HH_cube = []

    for b in range(B):  # Iterations on spectral bands
        # 2D DWT ats each band
        coeffs2 = pywt.wavedec2(
            hsi_cube[:, :, b], wavelet=wavelet, level=level
        )
        LL, (LH, HL, HH) = coeffs2
        reduced_cube.append(LL)
        LH_cube.append(LH)
        HL_cube.append(HL)
        HH_cube.append(HH)

    # The list converted in a cube
    reduced_cube = np.stack(reduced_cube, axis=-1)
    LH_cube = np.stack(LH_cube, axis=-1)
    HL_cube = np.stack(HL_cube, axis=-1)
    HH_cube = np.stack(HH_cube, axis=-1)

    scaling_factor = np.mean(hsi_cube) / np.mean(reduced_cube)
    reduced_cube = reduced_cube * scaling_factor

    return reduced_cube, (LH_cube, HL_cube, HH_cube, scaling_factor)


def reduce_spatial_dimension_dwt_inverse(
    hsi_cube, params, wavelet="haar", level=1
):
    """ """
    H, W, B = hsi_cube.shape
    reconstructed_cube = []
    LH, HL, HH, scaling_factor = params
    hsi_cube = hsi_cube / scaling_factor
    for b in range(B):  # Iterations on spectral bands
        # 2D DWT ats each band
        coeffs = (hsi_cube[:, :, b], (LH[:, :, b], HL[:, :, b], HH[:, :, b]))
        rec = pywt.waverec2(coeffs, wavelet=wavelet)
        reconstructed_cube.append(rec)

    # The list converted in a cube
    reconstructed_cube = np.stack(reconstructed_cube, axis=-1)

    return reconstructed_cube


# SPECTRAL DIMENSION WITH DWT
def reduce_bands_with_dwt(hsi_data, wavelet="db1", level=2):
    """ """
    h, w, b = hsi_data.shape
    approx_bands = []

    # Iteration on spatial pixels
    for i in range(h):
        for j in range(w):
            # DWT along spectral bands
            coeffs = pywt.wavedec(
                hsi_data[i, j, :], wavelet=wavelet, level=level
            )
            approx = coeffs[0]
            approx_bands.append(approx)

    # The list converted in a cube
    approx_bands = np.array(approx_bands)
    b_reduced = approx_bands.shape[1]
    reduced_hsi = approx_bands.reshape(h, w, b_reduced) / level

    scaling_factor = np.mean(hsi_data) / np.mean(reduced_hsi)
    reduced_hsi = reduced_hsi * scaling_factor

    return reduced_hsi


# TOTAL DIMENSIONALITY REDUCTION
def dimensionality_reduction(
    data, spectral_dimred_checkbox, spatial_dimred_checkbox, wl
):
    """ """
    reduced_data = data
    if spatial_dimred_checkbox:
        reduced_data, (LH, HL, HH, scaling) = reduce_spatial_dimension_dwt(
            reduced_data
        )
        reduced_data = reduced_data / 2
        # dataset_reshaped = (
        #    np.reshape(reduced_data, [-1, reduced_data.shape[2]])
        #    / reduced_data.max()
        # )

        reduced_rgb = HSI2RGB(
            wl,
            reduced_data,
            reduced_data.shape[0],
            reduced_data.shape[1],
            65,
            False,
        )
    if spectral_dimred_checkbox:
        reduced_data = reduce_bands_with_dwt(reduced_data)
        if (
            not spatial_dimred_checkbox
        ):  # if just spectral reduction, RGB is the RGB of the whole HS cube
            reduced_rgb = HSI2RGB(
                wl,
                data,
                data.shape[0],
                data.shape[1],
                65,
                False,
            )

    print("Original dimensions of the hypercube:", data.shape)
    print("Reduced dimensions of the reduced hypercube:", reduced_data.shape)
    reduced_wl = np.arange(reduced_data.shape[2])
    return reduced_data, reduced_wl, reduced_rgb


# %% DERIVATIVE
def derivative(data, savgol_w=9, savgol_pol=3, deriv=1):
    """ """
    data_firstDev = np.zeros_like(data)
    print(
        "Doing Savitzki-Golay filter: Window=",
        str(savgol_w),
        " Polynomial: ",
        str(savgol_pol),
        " Derivarive: ",
        str(deriv),
    )
    data_firstDev = savgol_filter(
        data, savgol_w, savgol_pol, deriv=deriv, axis=2
    )

    return data_firstDev


# %% METRICS
def metrics(data, metric):
    params = {}
    if metric == "Frobenius norm":
        norm = np.linalg.norm(data)
        print(f"Frobenius norm for the dataset: {norm}")
        data_norm = data / norm
        params["norm"] = norm

    if metric == "Z score":
        data_reshaped = data.reshape(-1, data.shape[2])
        mu, sigma = np.mean(data_reshaped), np.std(data_reshaped)
        print(f"Mean of the dataset: {mu}")
        print(f"Std of the dataset: {sigma}")
        data_reshaped_norm = (data_reshaped - mu) / sigma
        data_reshaped_norm = data_reshaped_norm - data_reshaped_norm.min()
        data_norm = data_reshaped_norm.reshape(data.shape)
        params["mu"], params["sigma"] = mu, sigma

    if metric == "Z score - dataset":
        mu = data.mean(axis=(0, 1))
        sigma = data.var(axis=(0, 1))
        print(mu.shape, sigma.shape)
        sigma[sigma == 0] = 1
        sigma_tot = np.sum(np.sqrt(sigma))
        data_norm = (data - mu[None, None, ...]) / sigma_tot
        data_norm = data_norm - data_norm.min(axis=(0, 1))
        params["mu"], params["sigma"] = mu, sigma_tot

    if metric == "Z score - spectrum":
        mu = data.mean(axis=(0, 1))
        sigma = data.std(axis=(0, 1))
        print(mu.shape)
        sigma[sigma == 0] = 1
        data_norm = (data - mu[None, None, ...]) / sigma[None, None, ...]
        data_norm = data_norm - data_norm.min(axis=(0, 1))
        params["mu"], params["sigma"] = mu, sigma

    if metric == "SNV":
        mu = data.mean(axis=2)
        sigma = data.std(axis=2)
        sigma[sigma == 0] = 1
        data_norm = (data - mu[..., None]) / sigma[..., None]
        print(f"Mean of the dataset shape: {mu.shape}")
        params["mu"], params["sigma"] = mu, sigma

    if metric == "Sum to one":
        sum_data = data.sum(axis=2)
        print("Dimension of sum: ", sum_data.shape)
        sum_data[sum_data == 0] = 1
        data_norm = data / sum_data[..., None]
        params["sum"] = sum_data

    if metric == "Global min-max":
        min_data, max_data = data.min(axis=(0, 1)), data.max(axis=(0, 1))
        print(
            f"Dimension of min matrix of the dataset: {min_data.shape}, Dimension of max matrix of the dataset: {max_data.shape}"
        )
        data_norm = (data - min_data[None, None, ...]) / (max_data - min_data)[
            None, None, ...
        ]
        params["min"], params["max"] = min_data, max_data

    if metric == "Robust min-max":
        out = np.empty_like(data)
        for b in range(data.shape[2]):
            band = data[:, :, b]
            p_low, p_high = np.percentile(band, (2, 98))
            out[:, :, b] = (band - p_low) / (p_high - p_low)
        data_norm = np.clip(out, 0, 1)
        print("Robust min-max performed")
        params["p_low"], params["p_high"] = np.array(p_low), np.array(p_high)

    if metric == "Pixel min-max":
        min_data = data.min(axis=2)
        max_data = data.max(axis=2)
        print(
            f"Dimension of min matrix of the dataset: {min_data.shape}, Dimension of max matrix of the dataset: {max_data.shape}"
        )
        diff = max_data - min_data
        diff[diff == 0] = 1
        data_norm = (data - min_data[..., None]) / diff[..., None]
        params["min"], params["diff"] = min_data, diff

    print(f"Dimension of the normalized dataset: {data_norm.shape}")
    return data_norm, params


# %% INVERSE METRICS
def inverse_metrics(spectrum_norm, metric, params):
    if metric == "Frobenius norm":
        return spectrum_norm * params["norm"]

    if metric == "Z score":
        return spectrum_norm * params["sigma"] + params["mu"]

    if metric == "Z score - dataset":
        return spectrum_norm * params["sigma"] + params["mu"][..., None]

    if metric == "Z score - spectrum":
        return (
            spectrum_norm * params["sigma"][..., None]
            + params["mu"][..., None]
        )

    if metric == "SNV":
        mu_all = spectrum_norm.mean(axis=0)
        sigma_all = spectrum_norm.std(axis=0)
        sigma_all[sigma_all == 0] = 1  # evita divisione per zero
        # mu, sigma = params["mu_pixel"], params["sigma_pixel"]
        return spectrum_norm * sigma_all[None, ...] + mu_all[None, ...]

    if metric == "Sum to one":
        sum_all = spectrum_norm.sum(axis=0)
        return spectrum_norm * sum_all[..., None]

    if metric == "Global min-max":
        return (
            spectrum_norm * (params["max"] - params["min"])[..., None]
            + params["min"][..., None]
        )

    if metric == "Robust min-max":
        return (
            spectrum_norm * (params["p_high"] - params["p_low"])[..., None]
            + params["p_low"][..., None]
        )

    if metric == "Pixel min-max":
        min_all = spectrum_norm.min(axis=0)
        max_all = spectrum_norm.max(axis=0)
        diff_all = max_all - min_all
        return spectrum_norm * diff_all[None, ...] + min_all[None, :]


# %% FUSION
def datasets_fusion(data1, data2, wl1, wl2, norm="Z score"):
    """ """
    print(
        f"Dimensions of dataset 1 and 2: \nData1: {data1.shape} \nData2: {data2.shape} \n\n"
    )

    data1_norm, params_1 = metrics(data1, metric=norm)
    data2_norm, params_2 = metrics(data2, metric=norm)

    wl_fused = np.concatenate((wl1, wl2))
    data_fused = np.concatenate((data1_norm, data2_norm), axis=2)
    fusion_point = data1_norm.shape[2]
    print(
        f"The new dataset has the shape: {data_fused.shape} \nThe fusion point is: {fusion_point}"
    )

    return data_fused, wl_fused, [params_1, params_2]


# %% ----- ----- ----- ----- ANALYSIS ----- ----- ----- -----


# %% PCA
def PCA_analysis(data, n_components, points=None, variance=False):
    """ """
    if points is None:
        points = []

    data_reshaped = data.reshape(data.shape[0] * data.shape[1], -1)
    pca = PCA(n_components)

    if len(points) > 0:
        pca.fit(data_reshaped[points, :])
        H = np.zeros((data.shape[0] * data.shape[1], n_components))
        H_reduced = pca.transform(data_reshaped[points, :])
        for i in range(n_components):
            H[points, i] = H_reduced[:, i]
        H = H.reshape(data.shape[0], data.shape[1], n_components)
    else:
        pca.fit(data_reshaped)
        H = pca.transform(data_reshaped).reshape(
            data.shape[0], data.shape[1], n_components
        )
    W = pca.components_  # EIGENVECTORS
    print("W shape: ", W.shape, "H shape: ", H.shape)
    print("Variance: ", pca.explained_variance_)

    if variance:
        cum_explained_var = []
        for i in range(len(pca.explained_variance_ratio_)):
            if i == 0:
                cum_explained_var.append(pca.explained_variance_ratio_[i])
            else:
                cum_explained_var.append(
                    pca.explained_variance_ratio_[i] + cum_explained_var[i - 1]
                )
        print(cum_explained_var)

        wl = np.arange(n_components)
        line = np.zeros_like(wl)
        line = np.full(n_components, 0.95)

        plot = go.Figure()
        plot.add_trace(
            go.Scatter(
                x=wl,
                y=cum_explained_var,
                marker={"size": 5},
                mode="markers",
                showlegend=False,
            )
        )
        plot.add_trace(
            go.Scatter(
                x=wl,
                y=line,
                line={"width": 1, "color": "red"},
                marker={"size": 5},
                mode="lines",
                name="95%",
            )
        )
        plot.update_layout(
            {
                "plot_bgcolor": "rgba(0, 0, 0, 0)",
                "paper_bgcolor": "rgba(0, 0, 0, 0)",
            },
            width=1000,
            height=600,
            xaxis_title="Number of components",
            yaxis_title="Contribution to toal variance",
            yaxis_range=[0.8, 1.01],
        )

        plot.show()
        return H, W, cum_explained_var
    else:
        return H, W


# %% UMAP
def UMAP_analysis(
    data,
    downsampling=1,
    points=None,
    metric="euclidean",
    n_neighbors=20,
    min_dist=0.0,
    spread=1.0,
    init="spectral",
    densmap=False,
    random_state=42,
):
    """ """
    if points is None:
        points = []
    start_time = time.time()  # Start of the timer

    if downsampling != 1:
        data = data[0::downsampling, 0::downsampling, :]
        print("Data downsampled dimesnion: ", data.shape)

    data_reshaped = data.reshape(data.shape[0] * data.shape[1], -1)
    print("Data reshaped dimension: ", data_reshaped.shape)

    fit = umap.UMAP(
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        n_components=2,
        metric=metric,
        n_jobs=-1,
        spread=spread,
        init=init,
        densmap=densmap,
    )
    # output_metric='hyperboloid',)
    if len(points) > 0:
        umap_result = fit.fit_transform(data_reshaped[points, :])
    else:
        umap_result = fit.fit_transform(data_reshaped)
    print("UMAP result dimension: ", umap_result.shape)
    elapsed_time = time.time() - start_time
    print(f"Time: {elapsed_time:.2f} seconds")

    return umap_result


# %% NMF
# %% UMAP
def NMF_analysis(
    data,
    points,
    n_components,
    init,
):
    """ """
    if points is None:
        points = []
    start_time = time.time()  # Start of the timer

    data_reshaped = data.reshape(data.shape[0] * data.shape[1], -1)
    print("Data reshaped dimension: ", data_reshaped.shape)

    fit = NMF(n_components=n_components, init=init, tol=5e-8, max_iter=10000)

    if len(points) > 0:
        H = fit.fit_transform(data_reshaped[points, :])
        W = fit.components_.T
        H_temp = np.zeros((data.shape[0] * data.shape[1], n_components))
        H_temp[points, :] = H
        H = H_temp.reshape(data.shape[0], data.shape[1], n_components)
    else:
        H = fit.fit_transform(data_reshaped)
        W = fit.components_.T
        H = H.reshape(data.shape[0], data.shape[1], W.shape[1])

    print(f"NMF result dimension: W shape {W.shape}, H shape {H.shape}")
    elapsed_time = time.time() - start_time
    print(f"Time: {elapsed_time:.2f} seconds")

    return H, W


# %% SiVM
def SiVM(
    data,
    n_bases=10,
    init="origin",
    metric="euclidean",
    silent=True,
    points=None,
):
    W = []
    # H_labels = []
    W_indices = []
    select = []
    # UPDATE W
    EPS = 10**-8

    # Reshape of the data
    data_reshaped = data.reshape(np.prod(data.shape[:2]), data.shape[2]).T
    data_shape = data.shape

    if len(points) > 0:
        data_reshaped = data_reshaped[points, :]

    # DIST FUNC
    def distfunc(data, vec):
        dist = distance_metrics()[metric](data.T, vec.T)[:, 0]
        return dist

    # DISTANCE
    def distance(data_reshaped, idx):
        """compute distances of a specific data point to all other samples"""
        print(
            "Compute the distances of a specific data point to all other samples"
        )
        if issparse(data_reshaped):
            print("The matrix is sparse")
            step = data_reshaped.shape[1]
        else:
            step = 50000
            print("The matrix is not sparse. 50000 steps are used.")

        d = np.zeros(
            data_reshaped.shape[1]
        )  # Creation of d, has the dimension of number of points

        if idx == -1:
            # If idx =-1, set vec to origin
            print("First cycle. Calulate the distances from the origin.")
            vec = np.zeros(
                (data_reshaped.shape[0], 1)
            )  # Creation of vec, has the dimension of a spectrum
            if issparse(data_reshaped):
                vec = csc_matrix(vec)
        else:
            print("Compute distance to node: ", str(idx))
            vec = data_reshaped[
                :, idx : idx + 1
            ]  # cur_p = 0 --> take the first element

        # slice data into smaller chunks
        for idx_start in range(
            0, data_reshaped.shape[1], step
        ):  # From 0 to all the pixels, qith 50 000 step
            if idx_start + step > data_reshaped.shape[1]:
                idx_end = data_reshaped.shape[1]
            else:
                idx_end = idx_start + step
            d[idx_start:idx_end] = distfunc(
                data_reshaped[:, idx_start:idx_end], vec
            )  # Calculate distance of each point of the chunk from the vector vec
            # print('Completed:' + str(idx_end/(data_reshaped.shape[1]/100.0)) + "%")
        return d

    # INIT_SIV
    if init == "fastmap":
        cur_p = 0  # set the starting index for fastmap initialization

        # after 3 iterations the first "real" index is found
        for _ in range(3):
            d = distance(data_reshaped, cur_p)
            cur_p = np.argmax(d)
            print(d)
        maxd = np.max(d)
        select.append(cur_p)
    elif init == "origin":
        cur_p = -1
        d = distance(data_reshaped, cur_p)
        maxd = np.max(d)
        select.append(cur_p)
    # ---

    d_square = np.zeros(data_reshaped.shape[1])
    d_sum = np.zeros(data_reshaped.shape[1])
    d_i_times_d_j = np.zeros(data_reshaped.shape[1])
    distiter = np.zeros(data_reshaped.shape[1])
    a = np.log(maxd)
    # a_inc = a.copy()

    for l_index in range(1, n_bases):
        d = distance(data_reshaped, select[l_index - 1])

        # take the log of d (sually more stable that d)
        d = np.log(d + EPS)

        d_i_times_d_j += d * d_sum
        d_sum += d
        d_square += d**2
        distiter = d_i_times_d_j + a * d_sum - (l_index / 2.0) * d_square

        # detect the next best data point
        select.append(np.argmax(distiter))

        if not silent:
            print("cur_nodes: " + str(select))
    # sort indices, otherwise h5py won't work
    W_calc = data_reshaped[:, np.sort(select)]

    # "unsort" it again to keep the correct order
    W_calc = W_calc[:, np.argsort(np.argsort(select))]
    # ----

    data = data_reshaped.T.reshape(data_shape)
    W.append(W_calc)
    W_indices.append(select)
    # H_labels.append(['Archetype '+str(i) for i in range(n_bases['value'])])

    W = np.array(W)
    W = W.reshape(W.shape[1], W.shape[2])
    print(W.shape)

    return W


# %% N-FINDR
def NFINDR(data, n_bases=10):
    W_calc = eea.NFINDR().extract(data, n_bases)
    W = np.array(W_calc).transpose
    print(W.shape)
    return W


# %% PPI
def PPI(data, n_bases=10):
    W_calc = eea.PPI().extract(data, n_bases)
    W = np.array(W_calc).transpose
    print(W.shape)
    return W


# %% NNLS
def nnls_analysis(data, W):
    data_reshaped = data.reshape(data.shape[0] * data.shape[1], -1)

    result = np.zeros((data_reshaped.shape[0], W.shape[1]))
    print(
        "Data shape: ",
        data_reshaped.shape,
        "\nEndmember matrix shape: ",
        W.shape,
    )

    for i in range(data_reshaped.shape[0]):
        result[i, :] = nnls(W, data_reshaped.T[:, i])[0]

    result = result.reshape(data.shape[0], data.shape[1], W.shape[1])
    return result


def sam_analysis(data, W, angle):
    print("Data shape: ", data.shape)
    print("Reference spectrum shape: ", W.shape)
    angles = np.zeros((data.shape[0], data.shape[1], W.shape[1]))
    print("Angles shape: ", angles.shape)
    for d in range(W.shape[1]):
        angles[:, :, d] = spectral.spectral_angles(
            data, W[:, d].reshape(1, W.shape[0])
        ).reshape(data.shape[0], data.shape[1])
        print("Angles shape: ", angles.shape)

        for i in range(angles.shape[0]):
            for j in range(angles.shape[1]):
                if angles[i, j, d] >= angle or np.isnan(angles[i, j, d]):
                    angles[i, j, d] = angle + 0.1
    print("Angles shape: ", angles.shape)
    return angles


# %% VCA


def estimate_snr(Y, r_m, x):

    [L, N] = Y.shape  # L number of bands (channels), N number of pixels
    [p, N] = x.shape  # p number of endmembers (reduced dimension)

    P_y = np.sum(Y**2) / float(N)
    P_x = np.sum(x**2) / float(N) + np.sum(r_m**2)
    snr_est = 10 * np.log10((P_x - p / L * P_y) / (P_y - P_x))

    return snr_est


def vca(Y, R, verbose=True, snr_input=0):
    # Vertex Component Analysis
    #
    # Ae, indice, Yp = vca(Y,R,verbose = True,snr_input = 0)
    #
    # ------- Input variables -------------
    #  Y - matrix with dimensions L(channels) x N(pixels)
    #      each pixel is a linear mixture of R endmembers
    #      signatures Y = M x s, where s = gamma x alfa
    #      gamma is a illumination perturbation factor and
    #      alfa are the abundance fractions of each endmember.
    #  R - positive integer number of endmembers in the scene
    #
    # ------- Output variables -----------
    # Ae     - estimated mixing matrix (endmembers signatures)
    # indice - pixels that were chosen to be the most pure
    # Yp     - Data matrix Y projected.
    #
    # ------- Optional parameters---------
    # snr_input - (float) signal to noise ratio (dB)
    # v         - [True | False]
    # ------------------------------------
    #
    # Author: Adrien Lagrange (adrien.lagrange@enseeiht.fr)
    # This code is a translation of a matlab code provided by
    # Jose Nascimento (zen@isel.pt) and Jose Bioucas Dias (bioucas@lx.it.pt)
    # available at http://www.lx.it.pt/~bioucas/code.htm under a non-specified Copyright (c)
    # Translation of last version at 22-February-2018 (Matlab version 2.1 (7-May-2004))
    #
    # more details on:
    # Jose M. P. Nascimento and Jose M. B. Dias
    # "Vertex Component Analysis: A Fast Algorithm to Unmix Hyperspectral Data"
    # submited to IEEE Trans. Geosci. Remote Sensing, vol. .., no. .., pp. .-., 2004
    #
    #

    #############################################
    # Initializations
    #############################################
    if len(Y.shape) != 2:
        sys.exit(
            "Input data must be of size L (number of bands i.e. channels) by N (number of pixels)"
        )

    [L, N] = Y.shape  # L number of bands (channels), N number of pixels

    R = int(R)
    if R < 0 or R > L:
        sys.exit("ENDMEMBER parameter must be integer between 1 and L")

    #############################################
    # SNR Estimates
    #############################################

    if snr_input == 0:
        y_m = np.mean(Y, axis=1, keepdims=True)
        Y_o = Y - y_m  # data with zero-mean
        Ud = np.linalg.svd(np.dot(Y_o, Y_o.T) / float(N))[0][
            :, :R
        ]  # computes the R-projection matrix
        x_p = np.dot(Ud.T, Y_o)  # project the zero-mean data onto p-subspace

        SNR = estimate_snr(Y, y_m, x_p)

        if verbose:
            print(f"SNR estimated = {SNR}[dB]")
    else:
        SNR = snr_input
        if verbose:
            print(f"input SNR = {SNR}[dB]\n")

    SNR_th = 15 + 10 * np.log10(R)

    #############################################
    # Choosing Projective Projection or
    #          projection to p-1 subspace
    #############################################

    if SNR_th > SNR:
        if verbose:
            print("... Select proj. to R-1")

            d = R - 1
            if (
                snr_input == 0
            ):  # it means that the projection is already computed
                Ud = Ud[:, :d]
            else:
                y_m = np.mean(Y, axis=1, keepdims=True)
                Y_o = Y - y_m  # data with zero-mean

                Ud = np.linalg.svd(np.dot(Y_o, Y_o.T) / float(N))[0][
                    :, :d
                ]  # computes the p-projection matrix
                x_p = np.dot(
                    Ud.T, Y_o
                )  # project thezeros mean data onto p-subspace

            Yp = np.dot(Ud, x_p[:d, :]) + y_m  # again in dimension L

            x = x_p[:d, :]  #  x_p =  Ud.T * Y_o is on a R-dim subspace
            c = np.amax(np.sum(x**2, axis=0)) ** 0.5
            y = np.vstack((x, c * np.ones((1, N))))
    else:
        if verbose:
            print("... Select the projective proj.")

        d = R
        Ud = np.linalg.svd(np.dot(Y, Y.T) / float(N))[0][
            :, :d
        ]  # computes the p-projection matrix

        x_p = np.dot(Ud.T, Y)
        Yp = np.dot(
            Ud, x_p[:d, :]
        )  # again in dimension L (note that x_p has no null mean)

        x = np.dot(Ud.T, Y)
        u = np.mean(x, axis=1, keepdims=True)  # equivalent to  u = Ud.T * r_m
        y = x / (np.dot(u.T, x) + 1e-7)

    #############################################
    # VCA algorithm
    #############################################

    indice = np.zeros((R), dtype=int)
    A = np.zeros((R, R))
    A[-1, 0] = 1

    for i in range(R):
        w = np.random.rand(R, 1)
        f = w - np.dot(A, np.dot(np.linalg.pinv(A), w))
        f = f / np.linalg.norm(f)

        v = np.dot(f.T, y)

        indice[i] = np.argmax(np.absolute(v))
        A[:, i] = y[:, indice[i]]  # same as x(:,indice(i))

    Ae = Yp[:, indice]

    return Ae, indice, Yp
