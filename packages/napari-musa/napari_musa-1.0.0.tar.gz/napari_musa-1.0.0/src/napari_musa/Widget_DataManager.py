"""Widget to manage and process the data"""

import sys
from os.path import dirname, splitext

sys.path.append(dirname(dirname(__file__)))

import h5py
import napari
import numpy as np
from magicgui.widgets import (
    CheckBox,
    ComboBox,
    Container,
    FloatSpinBox,
    PushButton,
    SpinBox,
)
from napari.utils.notifications import show_info, show_warning
from PIL import Image
from qtpy.QtCore import QTimer, Signal
from qtpy.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from scipy.io import savemat

from napari_musa.modules.functions import (
    HSI2RGB,
    SVD_denoise,
    create_mask,
    crop_xy,
    derivative,
    despike,
    dimensionality_reduction,
    open_file,
    preprocessing,
    reduce_spatial_dimension_dwt,
)


class DataManager(QWidget):  # From QWidget
    """ """

    mode_added = Signal()

    def __init__(self, viewer: napari.Viewer, data):
        """ """
        super().__init__()  # Initialize the QWidget
        self.viewer = viewer
        self.data = data
        # Configure the scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()  # Container widget
        content_layout = QVBoxLayout(
            content_widget
        )  # Vertical layout: organize widgets from top to bottom
        # Configure UI
        self.createUI(
            content_layout
        )  # The function to create the UI that fills the content_layout
        # Configure principal layout
        scroll.setWidget(
            content_widget
        )  # content_widget is a content of scroll area
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def createUI(self, layout):
        """Create the components for the UI"""
        layout.addWidget(self.create_open_box())
        layout.addWidget(self.create_save_layer_box())
        layout.addWidget(self.create_processing_box())
        layout.addWidget(self.create_manipulation_box())
        layout.addWidget(self.create_dimred_box())

    # %% Creation of UI boxes
    # OPEN BOX
    def create_open_box(self):
        """Create box and elements for file opening"""
        open_box = QGroupBox("Open file")
        open_layout = QVBoxLayout()
        open_layout.addSpacing(10)
        # Elements
        self.modes_combobox = ComboBox(
            choices=self.data.modes, label="Select the imaging mode"
        )
        open_btn = PushButton(text="Open File")
        open_btn.clicked.connect(self.open_btn_f)

        # Add widgets to the layout
        open_layout.addWidget(
            Container(
                widgets=[self.modes_combobox], layout="horizontal"
            ).native
        )
        open_layout.addWidget(
            Container(
                widgets=[
                    open_btn,
                ],
                layout="horizontal",
            ).native
        )
        open_box.setLayout(open_layout)
        return open_box

    def create_save_layer_box(self):
        """Create box and elements to save a selected layer"""
        save_box = QGroupBox("Save")
        save_layout = QVBoxLayout()
        save_layout.addSpacing(10)
        savedata_btn = PushButton(text="Save selected layer")
        savedata_btn.clicked.connect(self.savedata_btn_f)

        save_layout.addWidget(
            Container(
                widgets=[
                    savedata_btn,
                ],
                layout="horizontal",
            ).native
        )
        save_box.setLayout(save_layout)
        return save_box

    # PREPROCESSING BOX
    def create_processing_box(self):
        """Preprocessing of the data"""
        processing_box = QGroupBox("Processing")
        processing_layout = QVBoxLayout()
        processing_layout.addSpacing(20)
        #
        # Crop
        crop_box = QGroupBox("Crop")
        crop_layout = self.create_crop_section()
        crop_box.setLayout(crop_layout)
        processing_layout.addSpacing(20)
        processing_layout.addWidget(crop_box)

        # Mask
        mask_box = QGroupBox("Mask")
        mask_layout = self.create_mask_section()
        mask_box.setLayout(mask_layout)
        processing_layout.addSpacing(20)
        processing_layout.addWidget(mask_box)

        #
        # Data cleaning
        cleaning_box = QGroupBox("Data cleaning")
        cleaning_layout = QVBoxLayout()  # one layout for each box box
        cleaning_layout.addSpacing(10)
        # Despike
        despike_layout = self.create_despike_section()
        cleaning_layout.addLayout(despike_layout)
        # SVD preprocessing
        SVD_denoise_layout = self.create_SVD_denoise_section()
        cleaning_layout.addLayout(SVD_denoise_layout)
        # Median filter
        medfilt_layout = self.create_medfilt_section()
        cleaning_layout.addLayout(medfilt_layout)
        # Gaussian filter
        gaussian_layout = self.create_gaussian_section()
        cleaning_layout.addLayout(gaussian_layout)
        # Savitzky-Golay
        savgol_layout = self.create_savgol_section()
        cleaning_layout.addLayout(savgol_layout)
        # Background
        bkg_layout = self.create_bkg_section()
        cleaning_layout.addLayout(bkg_layout)
        # Preprocessing button
        processing_btn_layout = QVBoxLayout()
        preprocessing_btn = PushButton(text="Process data")
        preprocessing_btn.clicked.connect(self.preprocessing_btn_f)
        processing_btn_layout.addWidget(
            Container(widgets=[preprocessing_btn]).native
        )
        cleaning_layout.addLayout(processing_btn_layout)
        cleaning_box.setLayout(cleaning_layout)
        # Add cleaning box to processing layout
        processing_layout.addWidget(cleaning_box)
        processing_box.setLayout(processing_layout)
        return processing_box

    # MANIPULATION BOX
    def create_manipulation_box(self):
        manipulation_box = QGroupBox("Data manipulation")
        manipulation_layout = QVBoxLayout()
        manipulation_layout.addSpacing(20)
        derivative_btn = PushButton(text="Create first derivative")
        derivative_btn.clicked.connect(self.derivative_btn_f)
        manipulation_layout.addWidget(
            Container(
                widgets=[
                    derivative_btn,
                ],
                layout="horizontal",
            ).native
        )

        manipulation_box.setLayout(manipulation_layout)
        return manipulation_box

    # DIMENSIONAL REDUCTION BOX
    def create_dimred_box(self):
        dimred_box = QGroupBox("Dimensionality reduction")
        dimred_layout = QVBoxLayout()
        dimred_layout.addSpacing(20)
        self.spectral_dimred_checkbox = CheckBox(text="Spectral Reduction")
        self.spatial_dimred_checkbox = CheckBox(text="Spatial Reduction")
        dimred_btn = PushButton(text="Reduce data")
        dimred_btn.clicked.connect(self.dimred_btn_f)
        dimred_layout.addWidget(
            Container(
                widgets=[
                    self.spectral_dimred_checkbox,
                    self.spatial_dimred_checkbox,
                    dimred_btn,
                ]
            ).native
        )
        dimred_box.setLayout(dimred_layout)
        return dimred_box

    # UI SUB-BOXES
    def create_crop_section(self):
        """Crop and create mask"""
        crop_xy_layout = QHBoxLayout()
        crop_xy_btn = PushButton(text="Crop \n (rectangle shape)")
        crop_xy_btn.clicked.connect(self.crop_xy_btn_f)
        crop_xy_layout.addWidget(Container(widgets=[crop_xy_btn]).native)

        crop_wl_layout = QHBoxLayout()
        self.min_wl_spinbox = SpinBox(
            min=0, max=10000, step=1, value=0, label="Min. WL channel"
        )
        self.max_wl_spinbox = SpinBox(
            min=0, max=10000, step=1, value=100, label="Max. WL channel"
        )
        crop_wl_btn = PushButton(text="Crop wavelengths")
        crop_wl_btn.clicked.connect(self.crop_wl_btn_f)
        crop_wl_layout.addWidget(
            Container(
                widgets=[
                    self.min_wl_spinbox,
                    self.max_wl_spinbox,
                    crop_wl_btn,
                ]
            ).native
        )
        crop_xy_layout.addLayout(crop_wl_layout)
        return crop_xy_layout

    def create_mask_section(self):
        mask_layout = QHBoxLayout()
        self.mask_reduced_checkbox = CheckBox(text="From reduced dataset")
        mask_btn = PushButton(text="Create Mask \n(from Label layer)")
        mask_btn.clicked.connect(self.mask_btn_f)
        mask_layout.addWidget(
            Container(
                widgets=[
                    self.mask_reduced_checkbox,
                    mask_btn,
                ],
                layout="horizontal",
            ).native
        )
        return mask_layout

    def create_despike_section(self):
        """UI of despike section"""
        despike_layout = QHBoxLayout()
        despike_btn = PushButton(text="Despike")
        despike_btn.clicked.connect(self.despike_btn_f)
        despike_layout.addWidget(Container(widgets=[despike_btn]).native)
        return despike_layout

    def create_SVD_denoise_section(self):
        """UI of SVD denoising section"""
        SVD_layout = QHBoxLayout()
        SVD_btn = PushButton(text="SVD Calculation")
        SVD_btn.clicked.connect(self.SVD_btn_f)
        self.SVD_spinbox = SpinBox(
            min=1, max=1000, value=5, step=1, name="N. of components"
        )
        SVD_denoise_btn = PushButton(text="SVD Denoise")
        SVD_denoise_btn.clicked.connect(self.SVD_denoise_btn_f)

        SVD_layout.addWidget(Container(widgets=[SVD_btn]).native)
        SVD_layout.addWidget(
            Container(widgets=[self.SVD_spinbox, SVD_denoise_btn]).native
        )
        return SVD_layout

    def create_medfilt_section(self):
        """Median filter"""
        medfilt_layout = QHBoxLayout()
        # self.medfilt_checkbox = CheckBox(text="2D Gaussian filter")
        # self.medfilt_spinbox = FloatSpinBox(
        #    min=0.3, max=5.0, value=1.0, step=0.1, name="Sigma"
        self.medfilt_checkbox = CheckBox(text="2D medfilt")
        self.medfilt_spinbox = SpinBox(
            min=1, max=101, value=5, step=2, name="Window"
        )
        medfilt_layout.addWidget(
            Container(widgets=[self.medfilt_checkbox]).native
        )
        medfilt_layout.addWidget(
            Container(widgets=[self.medfilt_spinbox]).native
        )
        return medfilt_layout

    def create_gaussian_section(self):
        """gaussian filter"""
        gaussian_layout = QHBoxLayout()
        self.gaussian_checkbox = CheckBox(text="2D Gaussian filter")
        self.gaussian_spinbox = FloatSpinBox(
            min=0.3, max=5.0, value=1.0, step=0.1, name="Sigma"
        )
        gaussian_layout.addWidget(
            Container(widgets=[self.gaussian_checkbox]).native
        )
        gaussian_layout.addWidget(
            Container(widgets=[self.gaussian_spinbox]).native
        )
        return gaussian_layout

    def create_savgol_section(self):
        """Savitzky-Golay"""
        savgol_layout = QHBoxLayout()
        savgol_variables_layout = QHBoxLayout()
        self.savgol_checkbox = CheckBox(text="Savitzky-Golay filter")
        self.savgolw_spinbox = SpinBox(
            min=1, max=100, value=11, step=2, name="Window"
        )
        self.savgolp_spinbox = SpinBox(
            min=1, max=100, value=3, step=2, name="Polynom"
        )
        savgol_layout.addWidget(
            Container(widgets=[self.savgol_checkbox]).native
        )
        savgol_variables_layout.addWidget(
            Container(
                widgets=[self.savgolw_spinbox, self.savgolp_spinbox]
            ).native
        )
        savgol_layout.addLayout(savgol_variables_layout)
        return savgol_layout

    def create_bkg_section(self):
        """Background correction"""
        bkg_layout = QHBoxLayout()
        bkg_variables_layout = QHBoxLayout()

        self.bkg_checkbox = CheckBox(text="Background correction (SNIP)")
        self.bkgw_spinbox = SpinBox(
            min=1, max=1000, value=30, step=2, name="Window"
        )
        bkg_layout.addWidget(Container(widgets=[self.bkg_checkbox]).native)
        bkg_variables_layout.addWidget(
            Container(widgets=[self.bkgw_spinbox]).native
        )
        bkg_layout.addLayout(bkg_variables_layout)
        return bkg_layout

    # %% Button functions
    def open_btn_f(self):
        """ """
        self.data.filepath, _ = QFileDialog.getOpenFileName()
        print(f"The data with path {self.data.filepath} will now be opened")
        data_mode = self.modes_combobox.value

        self.data.hypercubes[data_mode], self.data.wls[data_mode] = open_file(
            self.data.filepath
        )
        if isinstance(self.data.hypercubes[data_mode], int) and isinstance(
            self.data.wls[data_mode], int
        ):
            hsi_cube_name, ok1 = QInputDialog.getText(
                None,
                "Name of the spectral hypercube",
                "Insert the variable name of the spectral hypercube:",
            )
            wl_name, ok2 = QInputDialog.getText(
                None,
                "Name of the wavelengths vector",
                "Insert the variable name of the wavelengths vector:",
            )

            if ok1 and ok2:
                self.data.hypercubes[data_mode], self.data.wls[data_mode] = (
                    open_file(
                        self.data.filepath,
                        hsi_cube_var=hsi_cube_name,
                        wl_var=wl_name,
                    )
                )

        self.viewer.add_image(
            self.data.hypercubes[data_mode].transpose(
                2, 0, 1
            ),  # napari wants (channels, height, width)
            name=str(data_mode),
            metadata={"type": "hyperspectral_cube"},
        )
        # Array for spatial cropping
        # self.crop_array = [
        #    0,
        #    0,
        #    self.data.hypercubes[data_mode].shape[0],
        #    self.data.hypercubes[data_mode].shape[1],
        # ]

    def savedata_btn_f(self):
        data_mode = self.modes_combobox.value
        selected_layer = self.viewer.layers.selection.active
        cube_types = [
            "hyperspectral_cube",
            "reduced_hsi_cube",
            "masked_hsi_cube",
        ]
        rgb_types = ["rgb", "reduced_rgb", "masked_rgb", "false_rgb"]
        if (
            selected_layer
            and selected_layer.metadata.get("type") in cube_types
        ):
            save_dict = {
                "data": selected_layer.data.transpose(1, 2, 0),
                "WL": self.data.wls[data_mode],
            }
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save selected dataset",
                "",
                "MATLAB file (*.mat);;HDF5 file (*.h5)",
            )
            savemat(filename, save_dict)

            if not filename:
                return  # the user has canceled the save dialog

            ext = splitext(filename)[1].lower()
            if ext == "":
                if _.startswith("MATLAB"):
                    filename += ".mat"
                    ext = ".mat"
                elif _.startswith("HDF5"):
                    filename += ".h5"
                    ext = ".h5"

            if ext == ".mat":
                savemat(filename, save_dict)
            elif ext == ".h5":
                with h5py.File(filename, "w") as f:
                    f.create_dataset(
                        "data", data=self.data.hypercubes[data_mode]
                    )
                    f.create_dataset("WL", data=self.data.wls[data_mode])

        # RGB
        elif (
            selected_layer and selected_layer.metadata.get("type") in rgb_types
        ):
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save selected rgb",
                "",
                "PNG image (*.png);;JPEG image (*.jpg *.jpeg)",
            )
            if not filename:
                return
            if not (
                filename.lower().endswith(".png")
                or filename.lower().endswith(".jpg")
                or filename.lower().endswith(".jpeg")
            ):
                if _.startswith("PNG"):
                    filename += ".png"
                else:
                    filename += ".jpg"
            rgb_data = selected_layer.data
            if rgb_data.dtype != "uint8":
                rgb_data = (
                    255
                    * (rgb_data - rgb_data.min())
                    / (rgb_data.max() - rgb_data.min())
                ).astype("uint8")
            rgb_image = Image.fromarray(rgb_data[..., :3])
            rgb_image.save(filename)

        # LABEL LAYER
        elif isinstance(selected_layer, napari.layers.Labels):
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save selected label layer",
                "",
                "PNG image (*.png);;JPEG image (*.jpg *.jpeg)",
            )
            if not filename:
                return
            if not (
                filename.lower().endswith(".png")
                or filename.lower().endswith(".jpg")
                or filename.lower().endswith(".jpeg")
            ):
                if _.startswith("PNG"):
                    filename += ".png"
                else:
                    filename += ".jpg"
            labels = selected_layer.data.astype(np.uint8)
            colormap = selected_layer.colormap
            lut = (
                colormap.map(np.arange(labels.max() + 1))[:, :3] * 255
            ).astype(np.uint8)
            colored_labels = lut[labels]
            alpha = np.where(labels == 0, 0, 255).astype(
                np.uint8
            )  # 255 = opaque
            rgba = np.dstack((colored_labels, alpha))  # (H, W, 4)
            img = Image.fromarray(rgba, mode="RGBA")
            img.save(filename)

    def crop_xy_btn_f(self):
        """ """
        data_mode = self.modes_combobox.value
        selected_layers = list(self.viewer.layers.selection)
        print(selected_layers)
        shape_layer = [
            layer
            for layer in selected_layers
            if isinstance(layer, napari.layers.Shapes)
        ]
        # If there are not selected shape layers
        if not shape_layer or len(shape_layer[0].data) == 0:
            show_warning("No shape layer or rect found")
            print("No shape layer or rect found")
            return None

        shape = shape_layer[0].data[0]
        if self.data.rgb.get(data_mode) is not None:
            print(self.data.rgb[data_mode].shape)
            self.data.hypercubes[data_mode], self.data.rgb[data_mode] = (
                crop_xy(
                    self.data.hypercubes[data_mode],
                    shape,
                    rgb=self.data.rgb[data_mode],
                )
            )
            print(self.data.rgb[data_mode].shape)
            if any(
                layer.name == str(data_mode) + " RGB"
                for layer in self.viewer.layers
            ):
                self.viewer.layers.remove(str(data_mode) + " RGB")
            self.viewer.add_image(
                self.data.rgb[data_mode],
                name=str(data_mode) + " RGB",
                rgb=True,
                metadata={"type": "rgb"},
            )
        else:
            self.data.hypercubes[data_mode] = crop_xy(
                self.data.hypercubes[data_mode], shape
            )
        if any(layer.name == str(data_mode) for layer in self.viewer.layers):
            self.viewer.layers.remove(str(data_mode))
        self.viewer.add_image(
            self.data.hypercubes[data_mode].transpose(2, 0, 1),
            name=str(data_mode),
            metadata={"type": "hyperspectral_cube"},
        )
        return

    def crop_wl_btn_f(self):
        """ """
        data_mode = self.modes_combobox.value
        min_wl = self.min_wl_spinbox.value
        max_wl = self.max_wl_spinbox.value
        self.data.hypercubes[data_mode] = self.data.hypercubes[data_mode][
            :, :, min_wl:max_wl
        ]
        self.data.wls[data_mode] = self.data.wls[data_mode][min_wl:max_wl]
        print(f"Cropped shape: {self.data.hypercubes[data_mode].shape}")
        if any(layer.name == str(data_mode) for layer in self.viewer.layers):
            self.viewer.layers.remove(str(data_mode))
        self.viewer.add_image(
            self.data.hypercubes[data_mode].transpose(2, 0, 1),
            name=str(data_mode),
            metadata={"type": "hyperspectral_cube"},
        )
        return

    def mask_btn_f(self):
        """ """
        data_mode = self.modes_combobox.value
        # SELECT LABEL LAYER
        # takes all the layers but the seleciton is only in the image (WL) in which i've done it
        active_layer = self.viewer.layers.selection.active
        print(isinstance(active_layer, napari.layers.Labels))
        if isinstance(active_layer, napari.layers.Labels):
            labels_layer = active_layer.data
        else:
            show_warning("The selected layer is not a label layer")
            return

        # If coming from UMAP, we don't need to do np.sum
        print(labels_layer.shape)
        binary_mask = np.where(labels_layer == 0, np.nan, 1).astype(float)

        if self.mask_reduced_checkbox.value:
            data = self.data.hypercubes_red[data_mode]
            rgb = self.data.rgb_red[data_mode]
        else:
            data = self.data.hypercubes[data_mode]
            if self.data.rgb.get(data_mode) is None:
                show_warning("RGB image not found \nRGB created")
                self.data.rgb[data_mode] = HSI2RGB(
                    self.data.wls[data_mode],
                    self.data.hypercubes[data_mode],
                    self.data.hypercubes[data_mode].shape[0],
                    self.data.hypercubes[data_mode].shape[1],
                    65,
                    False,
                )
                print(self.data.rgb[data_mode].shape)
                self.viewer.add_image(
                    self.data.rgb[data_mode],
                    name=str(data_mode) + " RGB",
                    rgb=True,
                    metadata={"type": "rgb"},
                )
            rgb = self.data.rgb[data_mode]

        (
            self.data.hypercubes_masked[data_mode],
            self.data.rgb_masked[data_mode],
        ) = create_mask(data, rgb, binary_mask)

        self.viewer.add_image(
            self.data.hypercubes_masked[data_mode].transpose(2, 0, 1),
            name=str(data_mode) + " masked",
            metadata={"type": "masked_hsi_cube"},
        )

        self.viewer.add_image(
            self.data.rgb_masked[data_mode],
            name=str(data_mode) + " masked - RGB",
            metadata={"type": "masked_rgb"},
        )
        return

    def despike_btn_f(self):
        data_mode = self.modes_combobox.value
        self.data.hypercubes[data_mode] = despike(
            self.data.hypercubes[data_mode]
        )
        print(f"Despiked dataset of {data_mode} created")
        QTimer.singleShot(
            0, lambda: show_info("Despiked dataset of {data_mode} created")
        )
        if any(layer.name == str(data_mode) for layer in self.viewer.layers):
            self.viewer.layers.remove(str(data_mode))
        self.viewer.add_image(
            self.data.hypercubes[data_mode].transpose(2, 0, 1),
            name=str(data_mode),
            metadata={"type": "hyperspectral_cube"},
        )
        return

    def SVD_btn_f(self):
        data_mode = self.modes_combobox.value

        self.data.hypercubes[data_mode], self.data.svd_maps[data_mode] = (
            SVD_denoise(
                self.data.hypercubes[data_mode],
                self.data.hypercubes[data_mode].shape[2],  # all components
            )
        )
        U_3D = self.data.svd_maps[data_mode][0].reshape(
            self.data.hypercubes[data_mode].shape
        )
        if any(layer.name == str(data_mode) for layer in self.viewer.layers):
            self.viewer.layers.remove(str(data_mode))
        self.viewer.add_image(
            U_3D.transpose(2, 0, 1),
            name=str(data_mode) + " - SVD",
            metadata={"type": "SVD_hsi"},
        )
        return

    def SVD_denoise_btn_f(self):
        data_mode = self.modes_combobox.value
        components = self.SVD_spinbox.value
        self.data.hypercubes[data_mode], maps = SVD_denoise(
            self.data.hypercubes[data_mode],
            components,
            matrices=self.data.svd_maps[data_mode],
        )
        print(f"SVD denoise of {data_mode} created")
        QTimer.singleShot(
            0, lambda: show_info("SVD denoise of {data_mode} created")
        )
        self.viewer.add_image(
            self.data.hypercubes[data_mode].transpose(2, 0, 1),
            name=str(data_mode),
            metadata={"type": "hyperspectral_cube"},
        )
        return

    def preprocessing_btn_f(self):
        data_mode = self.modes_combobox.value
        medfilt_checkbox = self.medfilt_checkbox.value
        gaussian_checkbox = self.gaussian_checkbox.value
        savgol_checkbox = self.savgol_checkbox.value
        bkg_checkbox = self.bkg_checkbox.value
        medfilt_w = self.medfilt_spinbox.value
        gaussian_s = self.gaussian_spinbox.value
        savgol_w = self.savgolw_spinbox.value
        savgol_p = self.savgolp_spinbox.value
        bkg_w = self.bkgw_spinbox.value

        self.data.hypercubes[data_mode] = preprocessing(
            self.data.hypercubes[data_mode],
            medfilt_w,
            gaussian_s,
            savgol_w,
            savgol_p,
            bkg_w,
            medfilt_checkbox=medfilt_checkbox,
            gaussian_checkbox=gaussian_checkbox,
            savgol_checkbox=savgol_checkbox,
            bkg_checkbox=bkg_checkbox,
        )
        QTimer.singleShot(0, lambda: show_info("Preprocessing completed!"))
        if any(layer.name == str(data_mode) for layer in self.viewer.layers):
            self.viewer.layers.remove(str(data_mode))
        self.viewer.add_image(
            self.data.hypercubes[data_mode].transpose(2, 0, 1),
            name=str(data_mode),
            metadata={"type": "hyperspectral_cube"},
        )
        return

    def derivative_btn_f(self):
        data_mode = self.modes_combobox.value
        name = str(data_mode) + " - derivative"
        # Add the name of the derivative in the list of modes and in the combobox
        if name not in self.data.modes:
            self.data.modes.append(name)
            self.modes_combobox.choices = self.data.modes
            self.mode_added.emit()

        self.data.hypercubes[data_mode + " - derivative"] = derivative(
            self.data.hypercubes[data_mode],
            savgol_w=9,
            savgol_pol=3,
            deriv=1,
        )
        self.viewer.add_image(
            self.data.hypercubes[data_mode + " - derivative"].transpose(
                2, 0, 1
            ),
            name=str(data_mode + " - derivative"),
            metadata={"type": "hyperspectral_cube"},
        )
        self.data.wls[data_mode + " - derivative"] = self.data.wls[data_mode]

        return

    def dimred_btn_f(self):
        data_mode = self.modes_combobox.value
        dataset = self.data.hypercubes[data_mode]
        spectral_dimred_checkbox = self.spectral_dimred_checkbox.value
        spatial_dimred_checkbox = self.spatial_dimred_checkbox.value
        (
            self.data.hypercubes_red[data_mode],
            self.data.wls_red[data_mode],
            self.data.rgb_red[data_mode],
        ) = dimensionality_reduction(
            dataset,
            spectral_dimred_checkbox,
            spatial_dimred_checkbox,
            self.data.wls[data_mode],
        )
        print(
            f"Dimensionality of dataset (Mode: {data_mode}) has been reduced"
        )
        print(
            f"New channel array of dimension {self.data.wls_red[data_mode].shape}"
        )
        print(
            f"New rgb matrix of reduced dataset. Dimensions: {self.data.rgb_red[data_mode].shape}"
        )
        if spatial_dimred_checkbox:
            (
                self.data.hypercubes_spatial_red[data_mode],
                self.data.hypercubes_spatial_red_params[data_mode],
            ) = reduce_spatial_dimension_dwt(dataset)

        # print(self.data.hypercubes_red[data_mode].shape)
        self.viewer.add_image(
            self.data.hypercubes_red[data_mode].transpose(2, 0, 1),
            name=str(data_mode) + " - REDUCED",
            metadata={"type": "reduced_hsi_cube"},
        )
        self.viewer.add_image(
            self.data.rgb_red[data_mode],
            name=str(data_mode) + " - REDUCED RGB",
            metadata={"type": "reduced_rgb"},
        )

    # %% Other functions
    def update_wl(self):
        """ """
        data_mode = self.modes_combobox.value
        wl_index = self.viewer.dims.current_step[0]
        max_index = len(self.data.wls[data_mode]) - 1
        wl_index = min(wl_index, max_index)
        wl_value = wl_index
        wl = round(self.data.wls[data_mode][wl_index], 2)
        self.viewer.text_overlay.text = (
            f"Wavelength: {wl} nm \nChannel: {wl_value}"
        )

    def layer_auto_selection(self):
        """ """
        selected_layer = self.viewer.layers.selection.active
        if selected_layer is None:
            return
        elif selected_layer.metadata.get("type") == "hyperspectral_cube":
            print(selected_layer.name)
            self.modes_combobox.value = selected_layer.name

        """
        # cambiare nomi in modo che tolgo la grandezza della stringa del nome
        elif selected_layer.metadata.get("type") == "rgb":
            print(selected_layer.name[:-4])
            self.modes_combobox.value = selected_layer.name[:-4]
        elif selected_layer.metadata.get("type") == "reduced_hsi_cube":
            print(selected_layer.name[:-10])
            self.modes_combobox.value = selected_layer.name[:-10]
        elif selected_layer.metadata.get("type") == "reduced_rgb":
            print(selected_layer.name[:-14])
            self.modes_combobox.value = selected_layer.name[:-14]
        elif selected_layer.metadata.get("type") == "masked_hsi_cube":
            print(selected_layer.name[:-7])
            self.modes_combobox.value = selected_layer.name[:-7]
        elif selected_layer.metadata.get("type") == "masked_rgb":
            print(selected_layer.name[:-13])
            self.modes_combobox.value = selected_layer.name[:-13]
        elif selected_layer.metadata.get("type") == "denoised_hsi":
            print(selected_layer.name[:-11])
            self.modes_combobox.value = selected_layer.name[:-11]
        elif selected_layer.metadata.get("type") == "SVD_hsi":
            print(selected_layer.name[:-6])
            self.modes_combobox.value = selected_layer.name[:-6]
        """
