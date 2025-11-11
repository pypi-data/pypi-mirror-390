""" """

import sys
from os.path import dirname

sys.path.append(dirname(dirname(__file__)))
import napari
import numpy as np
import pandas as pd
from magicgui.widgets import (
    CheckBox,
    ComboBox,
    Container,
    FloatSpinBox,
    PushButton,
    Select,
    SpinBox,
)
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
)
from matplotlib.backends.backend_qt5agg import (
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.figure import Figure
from napari.utils.notifications import show_info
from qtpy.QtCore import QTimer
from qtpy.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from napari_musa.modules.functions import (
    NFINDR,
    PPI,
    SiVM,
    inverse_metrics,
    nnls_analysis,
    sam_analysis,
    vca,
)


class EndmembersExtraction(QWidget):
    """ """

    def __init__(self, viewer: napari.Viewer, data, plot):
        """ """
        super().__init__()
        self.viewer = viewer
        self.data = data
        self.plot = plot
        self.init_ui()

    def init_ui(self):
        """ """
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        self.build_sivm_group(content_layout)
        content_layout.addStretch()

        scroll.setWidget(content_widget)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def build_sivm_group(self, layout):
        """ """
        layout.addWidget(self.create_endmextr_controls())
        layout.addWidget(self.create_upload_endmembers())
        layout.addWidget(self.create_nnls())
        layout.addWidget(self.create_sam())
        layout.addStretch()

    def create_endmextr_controls(self):
        """ """
        endm_box = QGroupBox("Endmembers")
        endm_layout = QVBoxLayout()
        endm_layout.addSpacing(10)
        row1 = QHBoxLayout()
        self.masked_dataset = CheckBox(text="Apply to masked dataset")
        self.modes_combobox = ComboBox(
            choices=self.data.modes, label="Select the imaging mode"
        )
        row1.addWidget(self.masked_dataset.native)
        row1.addWidget(self.modes_combobox.native)
        endm_layout.addLayout(row1)

        # row2 = QHBoxLayout()
        # row2.addWidget(self.masked_dataset.native)
        # layout.addLayout(row2)

        self.n_endmembers_spinbox = SpinBox(
            min=1, max=500, value=10, step=1, name="Endmembers"
        )
        endm_layout.addWidget(
            Container(widgets=[self.n_endmembers_spinbox]).native
        )

        row2 = QHBoxLayout()
        self.modes_vertex_analysis = ComboBox(
            choices=["SiVM", "VCA", "N-FINDR", "PPI"],
            label="Select the endmembers extraction mode",
        )
        run_btn = PushButton(text="Run endmember analysis")
        run_btn.clicked.connect(self.run_btn_f)
        row2.addWidget(
            Container(widgets=[self.modes_vertex_analysis, run_btn]).native
        )
        endm_layout.addLayout(row2)

        row3 = QHBoxLayout()
        self.sivm_basis_multiselecton = Select(
            label="Select Bases", choices=[]
        )
        self.sivm_basis_multiselecton.changed.connect(
            self.on_basis_selection_changed
        )
        row3.addWidget(self.sivm_basis_multiselecton.native)
        endm_layout.addLayout(row3)

        row4 = QVBoxLayout()
        self.mean_plot = FigureCanvas(Figure(figsize=(5, 3)))
        self.mean_plot.setMinimumSize(300, 450)
        self.mean_plot_toolbar = NavigationToolbar(self.mean_plot, self)
        self.plot.customize_toolbar(self.mean_plot_toolbar)
        self.plot.setup_plot(self.mean_plot)
        row4.addWidget(self.mean_plot)
        row4.addWidget(self.mean_plot_toolbar)
        # Export button
        export_btn = PushButton(text="Export selected spectra")
        export_btn.clicked.connect(self.export_spectrum)
        row4.addWidget(Container(widgets=[export_btn]).native)
        endm_layout.addLayout(row4)

        endm_box.setLayout(endm_layout)
        return endm_box

    def create_upload_endmembers(self):
        """ """
        upload_endm_box = QGroupBox("Upload Endmembers")
        upload_endm_layout = QVBoxLayout()
        upload_endm_layout.addSpacing(10)
        row1 = QHBoxLayout()
        self.upload_endmembers_checkbox = CheckBox(
            text="Use endmembers from file"
        )
        upload_endmember_btn = PushButton(text="Upload Endmembers")
        upload_endmember_btn.clicked.connect(self.upload_endmembers_btn_f)
        row1.addWidget(self.upload_endmembers_checkbox.native)
        row1.addWidget(upload_endmember_btn.native)
        upload_endm_layout.addLayout(row1)
        upload_endm_box.setLayout(upload_endm_layout)
        return upload_endm_box

    def create_nnls(self):
        """ """
        nnls_box = QGroupBox("NNLS Analysis")
        nnls_layout = QVBoxLayout()

        run_btn = PushButton(text="Run NNLS")
        run_btn.clicked.connect(self.run_nnls)
        nnls_layout.addSpacing(10)
        nnls_layout.addWidget(run_btn.native)
        nnls_box.setLayout(nnls_layout)
        return nnls_box

    def create_sam(self):
        sam_box = QGroupBox("SAM Analysis")
        sam_layout = QVBoxLayout()
        self.angle_spinbox = FloatSpinBox(
            min=0.0, max=1.0, value=0.1, step=0.1, label="Cosine value"
        )
        run_sam_btn = PushButton(text="Run SAM")
        run_sam_btn.clicked.connect(self.run_sam)
        sam_layout.addSpacing(10)
        sam_layout.addWidget(Container(widgets=[self.angle_spinbox]).native)
        sam_layout.addWidget(run_sam_btn.native)
        sam_box.setLayout(sam_layout)
        return sam_box

    def run_btn_f(self):
        """Perform SiVM"""
        self.sivm_basis_multiselecton.value = []
        mode = self.modes_combobox.value
        analysis_mode = self.modes_vertex_analysis.value
        n_basis = self.n_endmembers_spinbox.value
        options = [f"Basis {i}" for i in range(n_basis)]

        if self.masked_dataset.value:
            dataset = self.data.hypercubes_masked[mode]
            data_reshaped = dataset.reshape(
                dataset.shape[0] * dataset.shape[1], -1
            )
            dataset = np.nan_to_num(dataset, nan=0)

            self.points = np.array(
                np.where(~np.isnan(np.mean(data_reshaped, axis=1)))
            ).flatten()

        else:
            dataset = self.data.hypercubes[mode]
            self.points = []

        if analysis_mode == "SiVM":
            self.data.vertex_basis[mode] = SiVM(
                dataset, n_bases=n_basis, points=self.points
            )
        elif analysis_mode == "VCA":
            dataset_reshaped = dataset.reshape(
                dataset.shape[0] * dataset.shape[1], -1
            )
            if len(self.points) > 0:
                dataset_reshaped = dataset_reshaped[self.points, :]
            self.data.vertex_basis[mode] = vca(
                dataset_reshaped.transpose(), R=n_basis
            )[0]
        # CONTROLLARE SE VANNO E AGGIUNGERE I POINTS
        elif analysis_mode == "N-FINDR":
            self.data.vertex_basis[mode] = NFINDR(dataset, n_bases=n_basis)
            print(self.vertex_basis[mode].shape)

        elif analysis_mode == "PPI":
            self.data.vertex_basis[mode] = PPI(dataset, n_bases=n_basis)
            print(self.vertex_basis[mode].shape)

        self.sivm_basis_multiselecton.choices = options
        QTimer.singleShot(
            0, lambda: show_info("Endmember analysis completed!")
        )

    def on_basis_selection_changed(self, value):
        mode = self.modes_combobox.value

        print("Selected bases:", value)
        print("Shape of the array:", self.data.vertex_basis[mode].shape)

        self.basis_numbers = sorted([int(s.split()[1]) for s in value])
        self.selected_basis = self.data.vertex_basis[mode][
            :, self.basis_numbers
        ]
        print(self.selected_basis.shape)
        self.selected_basis_to_show = self.selected_basis

        if mode == "Fused":
            fusion_point = self.data.wls[self.data.fusion_modes[0]].shape[0]
            print(self.data.fusion_norm)
            # xxx aggiustare corrections
            print(self.data.fusion_params[0])
            self.selected_basis_to_show[:fusion_point, :] = inverse_metrics(
                self.selected_basis_to_show[:fusion_point, :],
                self.data.fusion_norm,
                self.data.fusion_params[0],
            )
            self.selected_basis_to_show[fusion_point:, :] = inverse_metrics(
                self.selected_basis_to_show[fusion_point:, :],
                self.data.fusion_norm,
                self.data.fusion_params[1],
            )

        self.plot.show_spectra(
            self.mean_plot,
            self.selected_basis_to_show,
            mode,
            basis_numbers=self.basis_numbers,
            export_txt_flag=False,
        )
        self.viewer.status = f"Selected basis: {self.basis_numbers}"
        # QTimer.singleShot(0, lambda: show_info(f"Selected basis: {self.basis_numbers}"))
        print("Selected basis: ", self.basis_numbers)

    def export_spectrum(self):
        """Export the mean spectrum"""
        mode = self.modes_combobox.value

        self.plot.show_spectra(
            self.mean_plot,
            self.selected_basis_to_show,
            mode,
            basis_numbers=self.basis_numbers,
            export_txt_flag=True,
        )

    def upload_endmembers_btn_f(self):
        """Upload endmembers from file"""

        filepath, _ = QFileDialog.getOpenFileName()
        print(f"The file with path {filepath} will now be opened")
        df_file = pd.read_csv(filepath, sep="\t")

        # wl = df_file[[col for col in df_file.columns if "Wavelength" in col]]
        spectra = df_file[
            [col for col in df_file.columns if "Spectrum" in col]
        ]
        # std = df_file[[col for col in df_file.columns if "Std" in col]]

        self.uploaded_endmembers = spectra.to_numpy()

    def run_nnls(self):
        """Perform NNLS"""
        mode = self.modes_combobox.value

        if self.masked_dataset.value:
            dataset = self.data.hypercubes_masked[mode]
            data_reshaped = dataset.reshape(
                dataset.shape[0] * dataset.shape[1], -1
            )
            self.points = np.array(
                np.where(~np.isnan(np.mean(data_reshaped, axis=1)))
            ).flatten()

            dataset = np.nan_to_num(dataset, nan=0)
        else:
            dataset = self.data.hypercubes[mode]
            self.points = []

        if self.upload_endmembers_checkbox.value:
            self.selected_basis = self.uploaded_endmembers

        print(self.selected_basis.shape)

        self.data.nnls_maps[mode] = nnls_analysis(
            dataset, W=self.selected_basis
        )
        self.viewer.add_image(
            self.data.nnls_maps[mode].transpose(2, 0, 1),
            name=str(mode) + " - NNLS",
            # ={"type": "hyperspectral_cube"},
        )

    def run_sam(self):
        """Perform SAM"""
        mode = self.modes_combobox.value

        if self.masked_dataset.value:
            dataset = self.data.hypercubes_masked[mode]
            data_reshaped = dataset.reshape(
                dataset.shape[0] * dataset.shape[1], -1
            )
            self.points = np.array(
                np.where(~np.isnan(np.mean(data_reshaped, axis=1)))
            ).flatten()

            dataset = np.nan_to_num(dataset, nan=0)
        else:
            dataset = self.data.hypercubes[mode]
            self.points = []

        if self.upload_endmembers_checkbox.value:
            self.selected_basis = self.uploaded_endmembers

        self.data.sam_maps[mode] = sam_analysis(
            dataset,
            W=self.selected_basis,
            angle=self.angle_spinbox.value,
        )

        self.viewer.add_image(
            self.data.sam_maps[mode].transpose(2, 0, 1),
            name=str(mode)
            + " - SAM with angle "
            + str(self.angle_spinbox.value),
            colormap="gray_r",
            # ={"type": "hyperspectral_cube"},
        )

    # %%
    def update_number_H(self):
        """ """
        basis_index = self.viewer.dims.current_step[0]
        basis_index = min(basis_index, len(self.basis_numbers) - 1)
        print(f"basis_index={basis_index}, basis_numbers={self.basis_numbers}")
        self.viewer.text_overlay.text = (
            f"Basis number: {self.basis_numbers[basis_index]}"
        )
