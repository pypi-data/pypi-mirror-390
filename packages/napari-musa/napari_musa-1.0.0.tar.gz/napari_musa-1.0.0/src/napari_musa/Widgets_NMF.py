""" """

import sys
from os.path import dirname

sys.path.append(dirname(dirname(__file__)))
import napari
import numpy as np
from magicgui.widgets import (
    CheckBox,
    ComboBox,
    Container,
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
from qtpy.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from scipy.io import savemat

from napari_musa.modules.functions import (
    NMF_analysis,
    inverse_metrics,
)


class NMF(QWidget):
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

        self.build_nmf_group(content_layout)
        content_layout.addStretch()

        scroll.setWidget(content_widget)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def build_nmf_group(self, layout):
        """ """

        layout.addWidget(self.create_nmf_controls())
        layout.addWidget(self.create_mean_spectrum_area())
        layout.addStretch()

    def create_nmf_controls(self):
        """ """
        nmf_box = QGroupBox("NMF parameters")
        layout = QVBoxLayout()
        layout.addSpacing(10)

        row1 = QHBoxLayout()
        self.reduced_dataset = CheckBox(text="Apply to reduced dataset")
        self.masked_dataset = CheckBox(text="Apply to masked dataset")
        self.modes_combobox = ComboBox(
            choices=self.data.modes, label="Select the imaging mode"
        )
        row1.addWidget(self.reduced_dataset.native)
        row1.addWidget(self.modes_combobox.native)
        layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(self.masked_dataset.native)
        layout.addLayout(row2)

        self.init_dropdown = ComboBox(
            choices=[
                "random",
                "nndsvd",
                "nndsvda",
                "nndsvdar",
            ],
            label="Select the initialization",
        )
        self.n_components = SpinBox(
            min=1, max=500, value=5, step=1, name="N Components"
        )

        layout.addWidget(
            Container(
                widgets=[
                    self.init_dropdown,
                    self.n_components,
                ]
            ).native
        )

        run_btn = PushButton(text="Run NMF")
        run_btn.clicked.connect(self.run_nmf)
        layout.addWidget(run_btn.native)

        row3 = QHBoxLayout()
        self.nmf_basis_multiselecton = Select(label="Select Bases", choices=[])
        self.nmf_basis_multiselecton.changed.connect(
            self.on_basis_selection_changed
        )
        row3.addWidget(self.nmf_basis_multiselecton.native)
        layout.addLayout(row3)
        nmf_box.setLayout(layout)
        return nmf_box

    def create_mean_spectrum_area(self):
        """ """
        nmf_box = QGroupBox("NMF spectra")
        layout = QVBoxLayout()
        layout.addSpacing(10)
        self.mean_plot = FigureCanvas(Figure(figsize=(5, 3)))
        self.mean_plot.setMinimumSize(300, 450)
        self.mean_plot_toolbar = NavigationToolbar(self.mean_plot, self)
        self.plot.customize_toolbar(self.mean_plot_toolbar)
        self.plot.setup_plot(self.mean_plot)

        layout.addWidget(self.mean_plot)
        layout.addWidget(self.mean_plot_toolbar)

        # Export button
        export_btn = PushButton(text="Export spectra")
        export_btn.clicked.connect(self.export_spectrum)
        export_nmf_btn = PushButton(text="Export NMF matrices as .mat")
        export_nmf_btn.clicked.connect(self.export_nmf)

        layout.addWidget(Container(widgets=[export_btn]).native)
        layout.addWidget(Container(widgets=[export_nmf_btn]).native)
        nmf_box.setLayout(layout)
        return nmf_box

    def run_nmf(self):
        """Perform NMF"""
        mode = self.modes_combobox.value

        n_basis = self.n_components.value
        options = [f"Basis {i}" for i in range(n_basis)]

        if self.masked_dataset.value:
            dataset = self.data.hypercubes_masked[mode]
            data_reshaped = dataset.reshape(
                dataset.shape[0] * dataset.shape[1], -1
            )
            self.points = np.array(
                np.where(~np.isnan(np.mean(data_reshaped, axis=1)))
            ).flatten()
            print(self.points)

        elif self.reduced_dataset.value:
            dataset = self.data.hypercubes_red[mode]
            self.points = []
        else:
            dataset = self.data.hypercubes[mode]
            self.points = []

        self.data.nmf_maps[mode], self.data.nmf_basis[mode] = NMF_analysis(
            dataset,
            points=self.points,
            n_components=n_basis,
            init=self.init_dropdown.value,
        )

        self.nmf_basis_multiselecton.choices = options

        self.viewer.add_image(
            self.data.nmf_maps[mode].transpose(2, 0, 1),
            name=str(mode) + " - NMF",
            # ={"type": "hyperspectral_cube"},
        )

        show_info("NMF analysis completed!")

    def on_basis_selection_changed(self, value):
        mode = self.modes_combobox.value

        print("Selected bases:", value)
        print("Shape of the array:", self.data.nmf_basis[mode].shape)

        self.basis_numbers = sorted([int(s.split()[1]) for s in value])
        self.selected_basis = self.data.nmf_basis[mode][:, self.basis_numbers]
        print(self.selected_basis.shape)
        self.selected_basis_to_show = self.selected_basis

        if mode == "Fused":
            fusion_point = self.data.wls[self.data.fusion_modes[0]].shape[0]
            print(self.data.fusion_norm)
            # xxx aggiustare corrections
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

        # show_info(f"NMF bases selected: {self.basis_numbers}")

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

    def export_nmf(self):
        """Export nmf"""
        mode = self.modes_combobox.value
        H = self.data.nmf_maps[mode]
        W = self.data.nmf_basis[mode]

        save_dict = {
            "H": H,
            "W": W,
        }

        filename, _ = QFileDialog.getSaveFileName(
            self, "Save nmf .mat", "", "mat (*.mat)"
        )
        if filename:
            savemat(filename, save_dict)

    def update_number_H(self):
        """ """
        index = self.viewer.dims.current_step[0]
        index = min(index, self.n_components.value - 1)
        self.viewer.text_overlay.text = f"Component number: {index}"
