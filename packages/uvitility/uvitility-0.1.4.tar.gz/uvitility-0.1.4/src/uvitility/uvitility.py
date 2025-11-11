#!/usr/bin/env python3


import os
import numpy as np
import matplotlib.pyplot as plt

from astropy.io import fits


# To ignore warning
np.seterr(divide="ignore", invalid="ignore")

# A dictionary of window sizes and frame rates.
window_rate_dict = {
    "511": 28.7185,
    "349": 61.0,
    "299": 82.0,
    "249": 115.0,
    "199": 180.0,
    "149": 300.0,
    "99": 640.0,
}


# To detect sawtooth in data.
def find_breaks(data):
    if len(data) == 0:
        return None
    data1 = np.roll(data, 1)
    data1[0] = 0
    mask = data < data1
    indices = [i for i, m in enumerate(mask) if m is True]
    return np.array(indices)


# Function to create images.
def centroid_check(L1_FITS):
    hdulist = fits.open(L1_FITS)

    # To get the frame rate.
    try:
        window = str(hdulist[0].header["win_x_sz"])
        frame_rate = window_rate_dict[str(window)]
    except KeyError:
        window = str(hdulist[0].header["win_y_sz"])
        frame_rate = window_rate_dict[str(window)]

    # ~25 seconds of initial data could be BOD check.
    BOD_frame_length = frame_rate * 25
    frames = hdulist[2].data["SecHdrImageFrameCount"]
    breaks = find_breaks(frames)
    if breaks is None:
        return
    BOD_breaks = breaks[breaks < BOD_frame_length]
    BOD_mask = np.ones(len(frames), dtype=bool)
    BOD_mask[frames == 1] = False
    if len(BOD_breaks) != 0:
        BOD_mask[: BOD_breaks[-1]] = False

    if len(frames[BOD_mask]) == 0:
        return

    # The Centroid column read as 8-bit integers (2016 columns).
    droid_array = hdulist[2].data["Centroid"]
    droid_array = droid_array[BOD_mask]

    # Unpacks elements of an 8-bit int array into a binary-valued output array.
    # Now with 16128 columns.
    bit_data = np.unpackbits(droid_array, axis=1)

    # Reshaping the array with only 3 words (48 bits) in the row.
    len_row = len(bit_data) * 336
    bit_dat = bit_data.reshape(len_row, 48)

    # bit data gets converted to useful events data. Hold my beer!
    Rx = bit_dat[:, 0].astype(int) * 256
    Lx = np.packbits(bit_dat[:, 1:9])
    Ix = Rx + Lx

    Ry = bit_dat[:, 16].astype(int) * 256
    Ly = np.packbits(bit_dat[:, 17:25])
    Iy = Ry + Ly

    powers = np.array([32, 16, 8, 4, 2, 1], dtype=np.int8)

    Fx = bit_dat[:, 9:15]
    Fx = Fx.dot(powers)

    Fy = bit_dat[:, 25:31]
    Fy = Fy.dot(powers)

    # To convert the 6-bit integers to subpixels.
    substep = 0.03125

    Fx[Fx > 31] = Fx[Fx > 31] - 64
    Fx = Fx * substep

    Fy[Fy > 31] = Fy[Fy > 31] - 64
    Fy = Fy * substep

    # Adding the integer and float parts together.
    X_pos = Ix + Fx
    Y_pos = Iy + Fy

    hot_pixel_mask = ~np.logical_and(Ix == 131, Iy == 216)

    X_pos = X_pos[hot_pixel_mask]
    Y_pos = Y_pos[hot_pixel_mask]

    # Keeping some standards.
    X_p = X_pos[X_pos > 0.0]
    Y_p = Y_pos[X_pos > 0.0]

    fig, axs = plt.subplots(5, 2, figsize=(15, 9))

    marker_size = 0.2
    alpha = 0.2

    axs[0][0].scatter(X_p, Y_p, s=marker_size, alpha=alpha)
    axs[0][0].set_xlim(0, 102)
    axs[1][0].scatter(X_p, Y_p, s=marker_size, alpha=alpha)
    axs[1][0].set_xlim(102, 204)
    axs[2][0].scatter(X_p, Y_p, s=marker_size, alpha=alpha)
    axs[2][0].set_xlim(204, 306)
    axs[3][0].scatter(X_p, Y_p, s=marker_size, alpha=alpha)
    axs[3][0].set_xlim(306, 408)
    axs[4][0].scatter(X_p, Y_p, s=marker_size, alpha=alpha)
    axs[4][0].set_xlim(408, 512)
    axs[4][0].set_xlabel("X-centroids")

    axs[0][1].scatter(Y_p, X_p, s=marker_size, alpha=alpha)
    axs[0][1].set_xlim(0, 102)
    axs[1][1].scatter(Y_p, X_p, s=marker_size, alpha=alpha)
    axs[1][1].set_xlim(102, 204)
    axs[2][1].scatter(Y_p, X_p, s=marker_size, alpha=alpha)
    axs[2][1].set_xlim(204, 306)
    axs[3][1].scatter(Y_p, X_p, s=marker_size, alpha=alpha)
    axs[3][1].set_xlim(306, 408)
    axs[4][1].scatter(Y_p, X_p, s=marker_size, alpha=alpha)
    axs[4][1].set_xlim(408, 512)
    axs[4][1].set_xlabel("Y-centroids")

    path = os.path.normpath(L1_FITS)
    if len(path.split(os.sep)) > 1:
        parent = path.split(os.sep)[-2]
        filename = path.split(os.sep)[-1]
        figure_name = filename.replace(".fits", "_stretched_data.png")
        figure_name = parent + "_" + figure_name
    else:
        parent = os.getcwd() + os.sep
        figure_name = L1_FITS.replace(".fits", "_stretched_data.png")

    plt.savefig(
        figure_name,
        format="png",
        bbox_inches="tight",
        dpi=100,
        facecolor="w",
        transparent=False,
    )

    plt.clf()

    fig, axs = plt.subplots(5, 2, figsize=(15, 9))

    bins = np.arange(0, 512, 0.5)
    X_array, bin_edges = np.histogram(X_p, bins=bins)
    Y_array, bin_edges = np.histogram(Y_p, bins=bins)

    axs[0][0].plot(bin_edges[1:], X_array)
    axs[0][0].set_xlim(0, 102)
    axs[1][0].plot(bin_edges[1:], X_array)
    axs[1][0].set_xlim(102, 204)
    axs[2][0].plot(bin_edges[1:], X_array)
    axs[2][0].set_xlim(204, 306)
    axs[3][0].plot(bin_edges[1:], X_array)
    axs[3][0].set_xlim(306, 408)
    axs[4][0].plot(bin_edges[1:], X_array)
    axs[4][0].set_xlim(408, 512)
    axs[4][0].set_xlabel("X-centroids")

    axs[0][1].plot(bin_edges[1:], Y_array)
    axs[0][1].set_xlim(0, 102)
    axs[1][1].plot(bin_edges[1:], Y_array)
    axs[1][1].set_xlim(102, 204)
    axs[2][1].plot(bin_edges[1:], Y_array)
    axs[2][1].set_xlim(204, 306)
    axs[3][1].plot(bin_edges[1:], Y_array)
    axs[3][1].set_xlim(306, 408)
    axs[4][1].plot(bin_edges[1:], Y_array)
    axs[4][1].set_xlim(408, 512)
    axs[4][1].set_xlabel("Y-centroids")

    filename = path.split(os.sep)[-1]
    figure_name = filename.replace(".fits", "_stretched_data_histogram.png")
    figure_name = parent + "_" + figure_name

    plt.savefig(
        figure_name,
        format="png",
        bbox_inches="tight",
        dpi=100,
        facecolor="w",
        transparent=False,
    )

    plt.close("all")

    bins = np.arange(0, 512)
    X_array, bin_edges = np.histogram(X_p, bins=bins)
    Y_array, bin_edges = np.histogram(Y_p, bins=bins)

    X_array = X_array[12:501]
    if len(X_array[X_array == 0]) > 0:
        print("\nPossible sparse data, the gap detection could be UNRELIABLE for:")
        print(L1_FITS)

    X_left_ratio = X_array[1:] / X_array[:-1]
    X_right_ratio = X_array[:-1] / X_array[1:]
    X_ratio_product = X_left_ratio[1:] * X_right_ratio[:-1]

    Y_array = Y_array[12:501]
    Y_left_ratio = Y_array[1:] / Y_array[:-1]
    Y_right_ratio = Y_array[:-1] / Y_array[1:]
    Y_ratio_product = Y_left_ratio[1:] * Y_right_ratio[:-1]

    threshold = 9
    Xgap_locations = np.argwhere(X_ratio_product > threshold)
    Ygap_locations = np.argwhere(Y_ratio_product > threshold)

    if len(Xgap_locations) != 0:
        print("\nPossible gap along X-centroids, check images to confirm.")
        print(L1_FITS, Xgap_locations[0] + 13)

    if len(Ygap_locations) != 0:
        print("\nPossible gap along Y-centroids, check images to confirm.")
        print(L1_FITS, Ygap_locations[0] + 13)


def check_centroid_gaps(L1_dir):
    print("\nPlease wait, this may take time.")

    for dirpath, dirnames, files in os.walk(L1_dir):
        for s in files:
            fnam = os.path.join(dirpath, s)
            if fnam[-5:] == ".fits" and fnam[-21] in ["N", "F"]:
                centroid_check(fnam)

    print("\nDone! Please inspect the plots.\n")
