""" """

import sys
from os.path import dirname

sys.path.append(dirname(dirname(__file__)))
import napari
import numpy as np
import pyqtgraph as pg
from magicgui.widgets import (
    CheckBox,
    ComboBox,
    Container,
    PushButton,
    SpinBox,
)
from qtpy.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from napari_musa.modules.functions import PCA_analysis, RGB_to_hex


class PCA(QWidget):
    def __init__(self, viewer: napari.Viewer, data, plot):
        super().__init__()
        self.viewer = viewer
        self.data = data
        self.plot = plot
        self.hex_reshaped = np.zeros(1)
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
        layout.addWidget(self.create_pca_controls())
        layout.addWidget(self.create_pca_scatterplot())
        layout.addStretch()

    def create_pca_controls(self):
        PCA_box = QGroupBox("PCA parameters")
        PCA_main_layout = QVBoxLayout()
        PCA_main_layout.addSpacing(10)
        # - - - pca data - - -
        self.reduced_dataset = CheckBox(text="Apply to reduced dataset")
        self.modes_combobox = ComboBox(
            choices=self.data.modes, label="Select the imaging mode"
        )  # DROPDOWN FOR CALIBRATION
        self.n_components = SpinBox(
            min=1, max=100, value=10, step=1, name="Number of components"
        )

        PCA_perform_btn = PushButton(text="Perform PCA")
        PCA_perform_btn.clicked.connect(self.PCA_perform_btn_f)
        PCA_main_layout.addWidget(
            Container(
                widgets=[
                    self.reduced_dataset,
                    self.modes_combobox,
                    self.n_components,
                    PCA_perform_btn,
                ]
            ).native
        )
        PCA_box.setLayout(PCA_main_layout)
        return PCA_box

    def create_pca_scatterplot(self):
        PCA_box = QGroupBox("PCA scatterplot")
        PCA_layout_plot_var = QVBoxLayout()
        PCA_layout_plot_var.addSpacing(10)
        # - - - pca variables - - -
        self.x_axis = SpinBox(min=1, max=100, value=1, step=1, name="X axis")
        self.y_axis = SpinBox(min=1, max=100, value=2, step=1, name="Y axis")
        PCA_layout_plot_var.addWidget(
            Container(widgets=[self.x_axis, self.y_axis]).native
        )
        PCA_layout_perform = QHBoxLayout()
        self.PCA_colorRGB = CheckBox(text="Scatterplot with True RGB")
        PCA_show_plot_btn = PushButton(text="Show PCA scatterplot")
        PCA_show_plot_btn.clicked.connect(self.PCA_show_plot_btn_f)
        PCA_layout_perform.addWidget(
            Container(
                widgets=[self.PCA_colorRGB, PCA_show_plot_btn],
                layout="horizontal",
            ).native
        )
        PCA_layout_plot_var.addLayout(PCA_layout_perform)

        self.pca_plot = pg.PlotWidget()
        self.plot.setup_scatterplot(self.pca_plot)

        # Add control buttons for scatter plot interaction
        btn_layout = QHBoxLayout()

        for icon, func in [
            ("fa5s.home", lambda: self.pca_plot.getViewBox().autoRange()),
            (
                "fa5s.draw-polygon",
                lambda: self.plot.polygon_selection(self.pca_plot),
            ),
            ("ri.add-box-fill", self.handle_selection),
            (
                "mdi6.image-edit",
                lambda: self.plot.save_image_button(self.pca_plot),
            ),
        ]:
            btn = self.plot.create_button(icon)
            btn.clicked.connect(func)
            btn_layout.addWidget(btn)

        self.point_size = SpinBox(
            min=1, max=100, value=1, step=1, name="Point size"
        )
        btn_layout.addSpacing(30)
        btn_layout.addWidget(Container(widgets=[self.point_size]).native)
        PCA_layout_plot_var.addLayout(btn_layout)
        PCA_layout_plot_var.addWidget(self.pca_plot)
        PCA_box.setLayout(PCA_layout_plot_var)
        return PCA_box

    def PCA_perform_btn_f(self):
        mode = self.modes_combobox.value
        if self.reduced_dataset.value:
            self.PCA_dataset = self.data.hypercubes_red[mode]
        else:
            self.PCA_dataset = self.data.hypercubes[mode]

        self.data.pca_maps[mode], W = PCA_analysis(
            self.PCA_dataset, self.n_components.value
        )

        print("PCA dataset shape: ", self.data.pca_maps[mode].shape)
        # Add the PCA maps to the viewer
        self.viewer.add_image(
            self.data.pca_maps[mode].transpose(2, 0, 1),
            name=str(mode) + " - PCA ",
            colormap="gray_r",
            # ={"type": "hyperspectral_cube"},
        )

    def PCA_show_plot_btn_f(self):
        """Plot UMAP scatter plot"""
        mode = self.modes_combobox.value
        pca_xaxis = self.x_axis.value - 1
        pca_yaxis = self.y_axis.value - 1
        H_PCA_reshaped = self.data.pca_maps[self.modes_combobox.value].reshape(
            -1, self.n_components.value
        )
        self.H_PCA_reshaped_selected = np.stack(
            (H_PCA_reshaped[:, pca_xaxis], H_PCA_reshaped[:, pca_yaxis])
        ).T

        if self.PCA_colorRGB.value:
            if self.reduced_dataset.value:
                colors = np.array(RGB_to_hex(self.data.rgb_red[mode])).reshape(
                    -1
                )
            else:
                colors = np.array(RGB_to_hex(self.data.rgb[mode])).reshape(-1)
        else:
            colors = pg.mkBrush("#262930")

        # print("Colors: \n", colors.reshape(-1))
        self.points = []
        self.plot.show_scatterplot(
            self.pca_plot,
            self.H_PCA_reshaped_selected,
            colors,
            self.points,
            self.point_size.value,
        )

    def handle_selection(self):
        """Handle polygon selection and create label layer"""
        mode = self.modes_combobox.value
        if self.reduced_dataset.value:
            dataset = self.data.hypercubes_red[mode]
            self.points = []

        else:
            dataset = self.data.hypercubes[mode]
        self.plot.show_selected_points(
            self.H_PCA_reshaped_selected,
            dataset,
            mode,
            self.points,
        )

    def update_number_H(self):
        """ """
        index = self.viewer.dims.current_step[0]
        index = min(index, self.n_components.value - 1)
        self.viewer.text_overlay.text = f"PCA number: {index}"
