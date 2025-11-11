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
    FloatSpinBox,
    PushButton,
    SpinBox,
)
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
)
from matplotlib.backends.backend_qt5agg import (
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.figure import Figure
from napari.utils.notifications import show_info, show_warning
from qtpy.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from napari_musa.modules.functions import (
    RGB_to_hex,
    UMAP_analysis,
    reduce_spatial_dimension_dwt_inverse,
)


class UMAP(QWidget):
    """ """

    def __init__(self, viewer: napari.Viewer, data, plot):
        """ """
        super().__init__()
        self.viewer = viewer
        self.data = data
        self.plot = plot
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
        layout.addWidget(self.create_umap_controls_box())
        layout.addWidget(self.creare_scatterplot_box())
        layout.addWidget(self.creare_plot_box())
        layout.addWidget(self.create_inverse_reduction_box())

        # %% Creation of UI boxes

    def create_umap_controls_box(self):
        """ """
        controls_box = QGroupBox("UMAP Parameters")
        # rgb_box.setFixedHeight(200)
        controls_layout = QVBoxLayout()
        controls_layout.addSpacing(10)
        # Elements
        row1 = QHBoxLayout()
        self.reduced_dataset = CheckBox(text="Reduced dataset")
        self.masked_dataset = CheckBox(text="Masked dataset")
        self.modes_combobox = ComboBox(
            choices=self.data.modes, label="Select the imaging mode"
        )
        row1.addWidget(self.reduced_dataset.native)
        row1.addWidget(self.modes_combobox.native)
        controls_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(self.masked_dataset.native)
        controls_layout.addLayout(row2)

        self.downsampling_spinbox = SpinBox(
            min=1, max=6, value=1, step=1, name="Downsampling"
        )
        self.metric_dropdown = ComboBox(
            choices=[
                "cosine",
                "euclidean",
                "correlation",
                "mahalanobis",
                "seuclidean ",
                "braycurtis",
            ],
            label="Select the metric",
        )
        self.n_neighbors_spinbox = SpinBox(
            min=5, max=500, value=20, step=5, name="N Neighbours"
        )
        self.min_dist_spinbox = FloatSpinBox(
            min=0.0, max=1.0, value=0.0, step=0.1, name="Min dist"
        )
        self.spread_spinbox = FloatSpinBox(
            min=1.0, max=3.0, value=1.0, step=0.1, name="Spread"
        )
        self.init_dropdown = ComboBox(
            choices=["spectral", "pca", "tswspectral"], label="Init"
        )
        self.densmap = CheckBox(text="Densmap")
        controls_layout.addWidget(
            Container(
                widgets=[
                    self.downsampling_spinbox,
                    self.metric_dropdown,
                    self.n_neighbors_spinbox,
                    self.min_dist_spinbox,
                    self.spread_spinbox,
                    self.init_dropdown,
                    self.densmap,
                ]
            ).native
        )

        run_btn = PushButton(text="Run UMAP")
        run_btn.clicked.connect(self.run_umap)
        controls_layout.addWidget(run_btn.native)

        UMAP_loyout_perform = QHBoxLayout()
        self.UMAP_colorRGB = CheckBox(text="Scatterplot with True RGB")
        show_btn = PushButton(text="Show UMAP scatterplot")
        show_btn.clicked.connect(self.show_umap_scatter)
        UMAP_loyout_perform.addWidget(
            Container(
                widgets=[self.UMAP_colorRGB, show_btn], layout="horizontal"
            ).native
        )
        controls_layout.addLayout(UMAP_loyout_perform)
        controls_box.setLayout(controls_layout)
        return controls_box

    def creare_scatterplot_box(self):
        """ """
        scatterplot_box = QGroupBox("UMAP Scatterplot")
        layout = QVBoxLayout()
        layout.addSpacing(10)
        self.umap_plot = pg.PlotWidget()
        self.plot.setup_scatterplot(self.umap_plot)
        # Add control buttons for scatter plot interaction
        btn_layout = QHBoxLayout()
        for icon, func in [
            ("fa5s.home", lambda: self.umap_plot.getViewBox().autoRange()),
            (
                "fa5s.draw-polygon",
                lambda: self.plot.polygon_selection(self.umap_plot),
            ),
            ("ri.add-box-fill", self.handle_selection),
            (
                "mdi6.image-edit",
                lambda: self.plot.save_image_button(self.umap_plot),
            ),
        ]:
            btn = self.plot.create_button(icon)
            btn.clicked.connect(func)
            btn_layout.addWidget(btn)
        self.point_size = SpinBox(
            min=1, max=100, value=1, step=1, name="Point size"
        )
        show_areas_on_scatterplot_btn = PushButton(
            text="Show areas of Label Layer on scatteplot"
        )
        show_areas_on_scatterplot_btn.clicked.connect(
            self.show_areas_on_scatterplot_btn_f
        )
        btn_layout.addSpacing(30)
        btn_layout.addWidget(Container(widgets=[self.point_size]).native)
        layout.addLayout(btn_layout)
        layout.addWidget(self.umap_plot)
        layout.addWidget(show_areas_on_scatterplot_btn.native)
        scatterplot_box.setLayout(layout)
        return scatterplot_box

    def creare_plot_box(self):
        """ """
        meanplot_box = QGroupBox("Mean plot")
        layout = QVBoxLayout()
        layout.addSpacing(20)
        layout = QVBoxLayout()
        self.mean_plot = FigureCanvas(Figure(figsize=(5, 3)))
        self.mean_plot.setMinimumSize(300, 450)
        self.mean_plot_toolbar = NavigationToolbar(self.mean_plot, self)
        self.plot.customize_toolbar(self.mean_plot_toolbar)
        self.plot.setup_plot(self.mean_plot)

        mean_spec_btn = PushButton(text="Mean Spectrum")
        self.std_checkbox = CheckBox(text="Plot Std Dev")
        self.norm_checkbox = CheckBox(text="Normalize")
        self.derivative_checkbox = CheckBox(text="Derivative")

        mean_spec_btn.clicked.connect(
            lambda: self.plot.show_plot(
                self.mean_plot,
                mode=self.modes_combobox.value,
                std_flag=self.std_checkbox.value,
                norm_flag=self.norm_checkbox.value,
                reduced_dataset_flag=self.reduced_dataset.value,
                derivative_flag=self.derivative_checkbox.value,
            )
        )

        controls = [
            self.std_checkbox,
            self.norm_checkbox,
            self.derivative_checkbox,
            mean_spec_btn,
        ]
        layout.addWidget(Container(widgets=controls).native)
        layout.addWidget(self.mean_plot)
        layout.addWidget(self.mean_plot_toolbar)

        # Export button
        export_btn = PushButton(text="Export spectra")
        export_btn.clicked.connect(
            lambda: (
                self.plot.show_plot(
                    self.mean_plot,
                    mode=self.modes_combobox.value,
                    std_flag=self.std_checkbox.value,
                    norm_flag=self.norm_checkbox.value,
                    reduced_dataset_flag=self.reduced_dataset.value,
                    export_txt_flag=True,
                )
            )
        )
        layout.addWidget(Container(widgets=[export_btn]).native)
        meanplot_box.setLayout(layout)
        return meanplot_box

    def create_inverse_reduction_box(self):
        """ """
        inverse_reduction_box = QGroupBox("Inverse Dimensionality Reduction")
        # rgb_box.setFixedHeight(200)
        inverse_reduction_layout = QVBoxLayout()
        inverse_reduction_layout.addSpacing(10)
        # Elements
        inverse_reduction_btn = PushButton(text="Perform inverse reduction")
        inverse_reduction_btn.clicked.connect(self.inverse_reduction_btn_f)
        inverse_reduction_layout.addWidget(inverse_reduction_btn.native)

        inverse_reduction_box.setLayout(inverse_reduction_layout)
        return inverse_reduction_box

    def run_umap(self):
        """Perform UMAP"""
        mode = self.modes_combobox.value
        if self.masked_dataset.value:
            dataset = self.data.hypercubes_masked[mode]
            data_reshaped = dataset.reshape(
                dataset.shape[0] * dataset.shape[1], -1
            )
            self.points = np.array(
                np.where(~np.isnan(np.mean(data_reshaped, axis=1)))
            ).flatten()
        elif self.reduced_dataset.value:
            dataset = self.data.hypercubes_red[mode]
            self.points = []
        else:
            dataset = self.data.hypercubes[mode]
            self.points = []

        self.data.umap_maps[mode] = UMAP_analysis(
            dataset,
            downsampling=self.downsampling_spinbox.value,
            points=self.points,
            metric=self.metric_dropdown.value,
            n_neighbors=self.n_neighbors_spinbox.value,
            min_dist=self.min_dist_spinbox.value,
            spread=self.spread_spinbox.value,
            init=self.init_dropdown.value,
            densmap=self.densmap.value,
            random_state=42,
        )
        show_info("UMAP analysis completed!")

    def show_umap_scatter(self):
        """Plot UMAP scatter plot"""
        mode = self.modes_combobox.value
        self.umap_data = self.data.umap_maps[mode]
        if self.UMAP_colorRGB.value:
            if self.reduced_dataset.value:
                colors = np.array(RGB_to_hex(self.data.rgb_red[mode])).reshape(
                    -1
                )
            elif self.masked_dataset.value:
                colors = np.array(
                    RGB_to_hex(self.data.rgb_masked[mode])
                ).reshape(-1)
            else:
                colors = np.array(RGB_to_hex(self.data.rgb[mode])).reshape(-1)
        else:
            colors = pg.mkBrush("#262930")

        print("Colors: \n", colors)
        self.plot.show_scatterplot(
            self.umap_plot,
            self.umap_data,
            colors,
            self.points,
            self.point_size.value,
        )

    def handle_selection(self):
        """Handle polygon selection and create label layer"""
        mode = self.modes_combobox.value
        if self.reduced_dataset.value and not self.masked_dataset.value:
            dataset = self.data.hypercubes_red[mode]
            self.points = []
        elif self.masked_dataset.value or (
            self.reduced_dataset.value and self.masked_dataset.value
        ):
            dataset = self.data.hypercubes_masked[mode]
            data_reshaped = dataset.reshape(
                dataset.shape[0] * dataset.shape[1], -1
            )
            self.points = np.array(
                np.where(~np.isnan(np.mean(data_reshaped, axis=1)))
            ).flatten()
        else:
            dataset = self.data.hypercubes[mode]
            self.points = []
        self.plot.show_selected_points(
            self.umap_data,
            dataset,
            mode,
            self.points,
        )

    def show_areas_on_scatterplot_btn_f(self):
        mode = self.modes_combobox.value
        selected_layer = self.viewer.layers.selection.active
        # Check if the selected layer is a label layer
        if not isinstance(selected_layer, napari.layers.Labels):
            show_warning(
                "⚠️ The selected layer is not a label layer. Please, select a label layer."
            )
            return
        labels_data = selected_layer.data
        if labels_data is None or np.all(
            labels_data == 0
        ):  # check if all elements are 0
            show_warning("⚠️ The selected label layer is empty")
            return
        # num_classes = int(labels_data.max())
        colormap = np.array(selected_layer.colormap.colors)
        print(colormap)
        print(colormap.shape)
        # colormap[0] = [0, 0, 0, 0.5]
        rgb_image = colormap[labels_data]  # fancy indexing
        if self.reduced_dataset.value:
            dataset = self.data.hypercubes_red[mode]
            rgb_image = rgb_image[: dataset.shape[0], : dataset.shape[1], :]
        print(rgb_image)
        print(rgb_image.shape)
        colors = RGB_to_hex(rgb_image)

        self.plot.show_scatterplot(
            self.umap_plot,
            self.umap_data,
            colors.reshape(-1),
            self.points,
            self.point_size.value,
        )

    def inverse_reduction_btn_f(self):
        mode = self.modes_combobox.value
        selected_layer = self.viewer.layers.selection.active

        if isinstance(selected_layer, napari.layers.Labels):
            label_data = selected_layer.data
            reduced_data = self.data.hypercubes_spatial_red[mode]
            print(label_data.shape)
            label_data = label_data[
                : reduced_data.shape[0], : reduced_data.shape[1]
            ]
            num_classes = int(label_data.max())
            # colormap = np.array(selected_layer.colormap.colors)
            reduced_data_masked = np.zeros(
                (label_data.shape[0], label_data.shape[1], num_classes)
            )
            print(self.data.hypercubes_spatial_red_params[mode])
            print(self.data.hypercubes_spatial_red_params[mode][0])
            LH = reduced_data_masked
            HL = reduced_data_masked
            HH = reduced_data_masked
            for idx in range(num_classes):
                points = np.where(label_data == idx + 1, 1, 0).astype(float)
                print("Points shape:", points.shape)
                reduced_data_masked[:, :, idx] = (
                    np.mean(reduced_data, axis=2) * points
                )
                LH[:, :, idx] = (
                    np.mean(
                        self.data.hypercubes_spatial_red_params[mode][0],
                        axis=2,
                    )
                    * points
                )
                HL[:, :, idx] = (
                    np.mean(
                        self.data.hypercubes_spatial_red_params[mode][1],
                        axis=2,
                    )
                    * points
                )
                HH[:, :, idx] = (
                    np.mean(
                        self.data.hypercubes_spatial_red_params[mode][2],
                        axis=2,
                    )
                    * points
                )
            reconstructed_data_masked = reduce_spatial_dimension_dwt_inverse(
                reduced_data_masked,
                (LH, HL, HH, self.data.hypercubes_spatial_red_params[mode][3]),
            )
            masks = reconstructed_data_masked != 0  # boolean
            H, W, K = masks.shape
            labels_reconstructed = np.zeros((H, W), dtype=np.int32)
            for k in range(
                K
            ):  # first mask wins on the others, but with UMAP i should not have overlapping areas
                sel = masks[:, :, k] & (labels_reconstructed == 0)
                labels_reconstructed[sel] = k + 1
            lenx, leny, lenwl = self.data.hypercubes[mode].shape
            labels_reconstructed = labels_reconstructed[:lenx, :leny]
            # K = colormap.shape[0] - 1
            # color_dict = {i: colormap[i, :3] for i in range(1, K+1)}
            self.viewer.add_labels(
                labels_reconstructed,
                name=str(mode) + " - Inverse Reduced Selection",
            )

        else:
            show_warning(
                "⚠️ The selected layer is not a label layer. Please, select an image layer."
            )
            return
        return
