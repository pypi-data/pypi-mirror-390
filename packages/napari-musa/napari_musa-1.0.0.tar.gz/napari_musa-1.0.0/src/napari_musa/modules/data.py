""" """

import sys
from os.path import dirname

sys.path.append(dirname(dirname(__file__)))

# print("here: ", dirname(dirname(__file__)))    #print for the directory folder


class Data:
    """ """

    def __init__(self):
        """ """
        self.filepath = ""
        self.hypercubes = {}
        self.hypercubes_red = {}
        self.hypercubes_spatial_red = {}  # For the spectra
        self.hypercubes_spatial_red_params = {}
        self.hypercubes_masked = {}
        self.wls = {}
        self.rgb = {}  # Dictionary needed for the fusion process
        self.rgb_red = {}  # Dictionary needed for the fusion process
        self.rgb_masked = {}
        self.wls_red = {}
        self.pca_maps = {}
        self.nmf_maps = {}
        self.nmf_basis = {}
        self.svd_maps = {}
        self.umap_maps = {}  # valutare se da togliere.
        self.vertex_basis = {}
        self.nnls_maps = {}
        self.sam_maps = {}
        self.modes = [
            "Reflectance",
            "PL",
            "PL - 2",
            "Raman",
            "Fused",
            "-",
        ]  # fused: self.modes.append
        self.mode = None  # valutare se da togliere con nuovo widget
        self.wl_value = 0
        self.fusion_modes = []


# %% Other functions
