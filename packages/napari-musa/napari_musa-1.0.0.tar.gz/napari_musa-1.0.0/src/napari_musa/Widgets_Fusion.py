""" """

import sys
from os.path import dirname

sys.path.append(dirname(dirname(__file__)))
import napari
from magicgui.widgets import (
    CheckBox,
    ComboBox,
    Container,
    PushButton,
    SpinBox,
)
from napari.utils.notifications import show_info
from qtpy.QtCore import QTimer
from qtpy.QtWidgets import (
    QGroupBox,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from napari_musa.modules.functions import (
    HSI2RGB,
    datasets_fusion,
)


class Fusion(QWidget):
    """ """

    def __init__(self, viewer: napari.Viewer, data):
        """ """
        super().__init__()
        self.viewer = viewer
        self.data = data
        self.init_ui()

    def init_ui(self):
        """ """
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # fusion_group = self.build_fusion_group()
        # content_layout.addWidget(fusion_group)
        content_layout.addWidget(self.create_fusion_controls_box())
        content_layout.addWidget(self.create_midlevel_fusion_controls())
        content_layout.addStretch()

        scroll.setWidget(content_widget)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def create_fusion_controls_box(self):
        """ """
        fusion_box = QGroupBox("Low-Level Fusion")
        layout = QVBoxLayout()

        self.reduced_dataset_checkbox = CheckBox(
            text="Fuse the reduced datasets (Only if you have both reduced datasets)"
        )

        self.modes_fusion = ComboBox(
            choices=[
                "Frobenius norm",
                "Z score",
                "Z score - dataset",
                "Z score - spectrum",
                "SNV",
                "Sum to one",
                "Global min-max",
                "Robust min-max",
                "Pixel min-max",
            ],
            label="Select fusion modality",
        )

        self.modes_combobox_1 = ComboBox(
            choices=self.data.modes, label="Select the first dataset"
        )
        self.modes_combobox_2 = ComboBox(
            choices=self.data.modes,
            label="Select the second dataset",
            value="PL",
        )
        self.modes_combobox_3 = ComboBox(
            choices=self.data.modes,
            label="Select the third dataset",
            value="-",
        )

        fusion_perform_btn = PushButton(text="Fuse the chosen datasets")
        fusion_perform_btn.clicked.connect(self.fusion_perform_btn_f)

        layout.addWidget(
            Container(
                widgets=[
                    self.reduced_dataset_checkbox,
                    self.modes_fusion,
                    self.modes_combobox_1,
                    self.modes_combobox_2,
                    self.modes_combobox_3,
                    fusion_perform_btn,
                ]
            ).native
        )
        fusion_box.setLayout(layout)
        return fusion_box

    def create_midlevel_fusion_controls(self):
        """ """
        fusion_box = QGroupBox("Mid-Level Fusion - PCA")
        layout = QVBoxLayout()

        self.PCA_components = SpinBox(
            min=1, max=100, value=1, step=1, name="PCA components"
        )

        self.modes_combobox_1_MLF = ComboBox(
            choices=self.data.modes, label="Select the first dataset"
        )
        self.modes_combobox_2_MLF = ComboBox(
            choices=self.data.modes,
            label="Select the second dataset",
            value="PL",
        )
        self.modes_combobox_3_MLF = ComboBox(
            choices=self.data.modes,
            label="Select the third dataset",
            value="-",
        )

        MLfusion_perform_btn = PushButton(text="Fuse the chosen datasets")
        MLfusion_perform_btn.clicked.connect(self.MLfusion_perform_btn_f)

        layout.addWidget(
            Container(
                widgets=[
                    self.PCA_components,
                    self.modes_combobox_1_MLF,
                    self.modes_combobox_2_MLF,
                    self.modes_combobox_3_MLF,
                    MLfusion_perform_btn,
                ]
            ).native
        )
        fusion_box.setLayout(layout)
        return fusion_box

    def fusion_perform_btn_f(self):
        """ """
        # Parameters
        self.data.fusion_norm = self.modes_fusion.value  # Norm used for fusion
        self.data.fusion_modes = (
            []
        )  # Tells which datasets are fused (Refle-PL, PL1-PL2, etc.)
        self.data.fusion_modes.append(self.modes_combobox_1.value)
        self.data.fusion_modes.append(self.modes_combobox_2.value)
        wl1 = self.data.wls[self.modes_combobox_1.value]
        wl2 = self.data.wls[self.modes_combobox_2.value]
        #
        # If a third dataset is selected
        if self.modes_combobox_3.value != "-":
            self.data.fusion_modes.append(self.modes_combobox_3.value)
            wl3 = self.data.wls[self.modes_combobox_1.value]
        #
        # If we want to fuse the reduced datasets
        if self.reduced_dataset_checkbox.value:
            # If 1 and 2 have the spatial reduction (should be when I have both spatial and spectral reduction)
            # First are fused the spatial reduced datasets
            if (
                self.data.hypercubes_spatial_red.get(
                    self.modes_combobox_1.value
                )
                is not None
                and self.data.hypercubes_spatial_red.get(
                    self.modes_combobox_2.value
                )
                is not None
            ):
                dataset1 = self.data.hypercubes_spatial_red[
                    self.modes_combobox_1.value
                ]
                dataset2 = self.data.hypercubes_spatial_red[
                    self.modes_combobox_2.value
                ]
                (
                    self.data.hypercubes_spatial_red[
                        "Fused"
                    ],  # Fusion of spatial reduced datasets
                    self.data.wls["Fused"],
                    self.data.fusion_params,
                ) = datasets_fusion(
                    dataset1, dataset2, wl1, wl2, norm=self.modes_fusion.value
                )
            # dataset1 and dataset2 for the fusion
            dataset1 = self.data.hypercubes_red[self.modes_combobox_1.value]
            dataset2 = self.data.hypercubes_red[self.modes_combobox_2.value]

            self.data.rgb_red["Fused"] = self.data.rgb_red[
                self.modes_combobox_1.value
            ]  # The rgb of the fused is the rgb of dataset 1
            (
                self.data.hypercubes_red["Fused"],
                self.data.wls["Fused"],
                self.data.fusion_params,
            ) = datasets_fusion(
                dataset1, dataset2, wl1, wl2, norm=self.modes_fusion.value
            )
            # If we have a third dataset
            if self.modes_combobox_3.value != "-":
                if (
                    self.data.hypercubes_spatial_red.get(
                        self.modes_combobox_3.value
                    )
                    is not None
                ):  # If we apply both spatial and spectral reduction, append 3rd spatial reduced dataset to the fused
                    # spatial reduced datasets
                    dataset3 = self.data.hypercubes_spatial_red[
                        self.modes_combobox_3.value
                    ]
                    (
                        self.data.hypercubes_spatial_red["Fused"],
                        self.data.wls["Fused"],
                        self.data.fusion_params,
                    ) = datasets_fusion(
                        self.data.hypercubes_spatial_red["Fused"],
                        dataset3,
                        self.data.wls["Fused"],
                        wl3,
                        norm=self.modes_fusion.value,
                    )
                dataset3 = self.data.hypercubes_red[
                    self.modes_combobox_3.value
                ]
                (
                    self.data.hypercubes_red["Fused"],
                    self.data.wls["Fused"],
                    self.data.fusion_params,
                ) = datasets_fusion(
                    self.data.hypercubes_red["Fused"],
                    dataset3,
                    self.data.wls["Fused"],
                    wl3,
                    norm=self.modes_fusion.value,
                )
            self.viewer.add_image(
                self.data.hypercubes_red["Fused"].transpose(2, 0, 1),
                name="Fused",
                metadata={"type": "hyperspectral_cube"},
            )
        #
        # If the dataset are not reduced
        else:
            dataset1 = self.data.hypercubes[self.modes_combobox_1.value]
            dataset2 = self.data.hypercubes[self.modes_combobox_2.value]
            if self.data.rgb.get(self.modes_combobox_1.value) is not None:
                self.data.rgb["Fused"] = self.data.rgb[
                    self.modes_combobox_1.value
                ]
            else:  # If we did not create the rgb of dataset 1, we compute it here
                self.data.rgb[self.modes_combobox_1.value] = HSI2RGB(
                    self.data.wls[self.modes_combobox_1.value],
                    dataset1,
                    dataset1.shape[0],
                    dataset1.shape[1],
                    65,
                    False,
                )

                self.viewer.add_image(
                    self.data.rgb[self.modes_combobox_1.value],
                    name=str(self.modes_combobox_1.value) + " RGB",
                    metadata={"type": "rgb"},
                )
            # Compute the fusion
            (
                self.data.hypercubes["Fused"],
                self.data.wls["Fused"],
                self.data.fusion_params,
            ) = datasets_fusion(
                dataset1, dataset2, wl1, wl2, norm=self.modes_fusion.value
            )
            # If we have a third dataset
            if self.modes_combobox_3.value != "-":
                dataset3 = self.data.hypercubes[self.modes_combobox_3.value]
                (
                    self.data.hypercubes["Fused"],
                    self.data.wls["Fused"],
                    self.data.fusion_params,
                ) = datasets_fusion(
                    self.data.hypercubes["Fused"],
                    dataset3,
                    self.data.wls["Fused"],
                    wl3,
                    norm=self.modes_fusion.value,
                )
            self.viewer.add_image(
                self.data.hypercubes["Fused"].transpose(2, 0, 1),
                name="Fused",
                metadata={"type": "hyperspectral_cube"},
            )
        QTimer.singleShot(0, lambda: show_info("Fusion completed!"))

    # xxx sistemarte
    def MLfusion_perform_btn_f(self):
        """ """
        # Parameters
        self.data.fusion_norm = self.modes_fusion.value  # Norm used for fusion
        self.data.fusion_modes = (
            []
        )  # Tells which datasets are fused (Refle-PL, PL1-PL2, etc.)
        self.data.fusion_modes.append(self.modes_combobox_1.value)
        self.data.fusion_modes.append(self.modes_combobox_2.value)
        wl1 = self.data.wls[self.modes_combobox_1.value]
        wl2 = self.data.wls[self.modes_combobox_2.value]
        #
        # If a third dataset is selected
        if self.modes_combobox_3.value != "-":
            self.data.fusion_modes.append(self.modes_combobox_3.value)
            wl3 = self.data.wls[self.modes_combobox_1.value]
        #
        # If we want to fuse the reduced datasets
        if self.reduced_dataset_checkbox.value:
            # If 1 and 2 have the spatial reduction (should be when I have both spatial and spectral reduction)
            # First are fused the spatial reduced datasets
            if (
                self.data.hypercubes_spatial_red.get(
                    self.modes_combobox_1.value
                )
                is not None
                and self.data.hypercubes_spatial_red.get(
                    self.modes_combobox_2.value
                )
                is not None
            ):
                dataset1 = self.data.hypercubes_spatial_red[
                    self.modes_combobox_1.value
                ]
                dataset2 = self.data.hypercubes_spatial_red[
                    self.modes_combobox_2.value
                ]
                (
                    self.data.hypercubes_spatial_red[
                        "Fused"
                    ],  # Fusion of spatial reduced datasets
                    self.data.wls["Fused"],
                    self.data.fusion_params,
                ) = datasets_fusion(
                    dataset1, dataset2, wl1, wl2, norm=self.modes_fusion.value
                )
            # dataset1 and dataset2 for the fusion
            dataset1 = self.data.hypercubes_red[self.modes_combobox_1.value]
            dataset2 = self.data.hypercubes_red[self.modes_combobox_2.value]

            self.data.rgb_red["Fused"] = self.data.rgb_red[
                self.modes_combobox_1.value
            ]  # The rgb of the fused is the rgb of dataset 1
            (
                self.data.hypercubes_red["Fused"],
                self.data.wls["Fused"],
                self.data.fusion_params,
            ) = datasets_fusion(
                dataset1, dataset2, wl1, wl2, norm=self.modes_fusion.value
            )
            # If we have a third dataset
            if self.modes_combobox_3.value != "-":
                if (
                    self.data.hypercubes_spatial_red.get(
                        self.modes_combobox_3.value
                    )
                    is not None
                ):  # If we apply both spatial and spectral reduction, append 3rd spatial reduced dataset to the fused
                    # spatial reduced datasets
                    dataset3 = self.data.hypercubes_spatial_red[
                        self.modes_combobox_3.value
                    ]
                    (
                        self.data.hypercubes_spatial_red["Fused"],
                        self.data.wls["Fused"],
                        self.data.fusion_params,
                    ) = datasets_fusion(
                        self.data.hypercubes_spatial_red["Fused"],
                        dataset3,
                        self.data.wls["Fused"],
                        wl3,
                        norm=self.modes_fusion.value,
                    )
                dataset3 = self.data.hypercubes_red[
                    self.modes_combobox_3.value
                ]
                (
                    self.data.hypercubes_red["Fused"],
                    self.data.wls["Fused"],
                    self.data.fusion_params,
                ) = datasets_fusion(
                    self.data.hypercubes_red["Fused"],
                    dataset3,
                    self.data.wls["Fused"],
                    wl3,
                    norm=self.modes_fusion.value,
                )
        #
        # If the dataset are not reduced
        else:
            dataset1 = self.data.hypercubes[self.modes_combobox_1.value]
            dataset2 = self.data.hypercubes[self.modes_combobox_2.value]
            if self.data.rgb.get(self.modes_combobox_1.value) is not None:
                self.data.rgb["Fused"] = self.data.rgb[
                    self.modes_combobox_1.value
                ]
            else:  # If we did not create the rgb of dataset 1, we compute it here
                self.data.rgb[self.modes_combobox_1.value] = HSI2RGB(
                    self.data.wls[self.modes_combobox_1.value],
                    dataset1,
                    dataset1.shape[0],
                    dataset1.shape[1],
                    65,
                    False,
                )

                self.viewer.add_image(
                    self.data.rgb[self.modes_combobox_1.value],
                    name=str(self.modes_combobox_1.value) + " RGB",
                    metadata={"type": "rgb"},
                )
            # Compute the fusion
            (
                self.data.hypercubes["Fused"],
                self.data.wls["Fused"],
                self.data.fusion_params,
            ) = datasets_fusion(
                dataset1, dataset2, wl1, wl2, norm=self.modes_fusion.value
            )
            # If we have a third dataset
            if self.modes_combobox_3.value != "-":
                dataset3 = self.data.hypercubes[self.modes_combobox_3.value]
                (
                    self.data.hypercubes["Fused"],
                    self.data.wls["Fused"],
                    self.data.fusion_params,
                ) = datasets_fusion(
                    self.data.hypercubes["Fused"],
                    dataset3,
                    self.data.wls["Fused"],
                    wl3,
                    norm=self.modes_fusion.value,
                )
        self.viewer.add_image(
            self.data.hypercubes["Fused"].transpose(2, 0, 1),
            name="Fused",
            metadata={"type": "hyperspectral_cube"},
        )
        QTimer.singleShot(0, lambda: show_info("Fusion completed!"))
