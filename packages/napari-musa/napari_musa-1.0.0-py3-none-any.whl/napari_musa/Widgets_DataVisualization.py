"""Widget to visualize the data"""

import sys
from os.path import dirname

sys.path.append(dirname(dirname(__file__)))

import napari
from magicgui.widgets import (
    CheckBox,
    Container,
    Label,
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
from qtpy.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from napari_musa.modules.functions import (
    HSI2RGB,
    falseRGB,
)


class DataVisualization(QWidget):  # From QWidget
    """ """

    def __init__(self, viewer: napari.Viewer, data, plot, datamanager):
        """ """
        super().__init__()  # Initialize the QWidget
        self.viewer = viewer
        self.data = data
        self.plot = plot
        self.datamanager = datamanager
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
        layout.addWidget(self.create_rgb_box())
        layout.addWidget(self.plot_box())

    # %% Creation of UI boxes
    # RGB BOX
    def create_rgb_box(self):
        """Create box and elements for file opening"""
        rgb_box = QGroupBox("Create RGB")
        # rgb_box.setFixedHeight(200)
        true_rgb_layout = QVBoxLayout()
        true_rgb_layout.addSpacing(10)
        # Elements
        true_rgb_btn = PushButton(text="Create True RGB")
        true_rgb_btn.clicked.connect(self.true_rgb_btn_f)

        # Add widgets to the layout
        true_rgb_layout.addWidget(
            Container(widgets=[true_rgb_btn], layout="horizontal").native
        )
        true_rgb_layout.addSpacing(30)
        #
        # FALSE RGB
        false_rgb_layout = QVBoxLayout()
        false_rgb_layout.addSpacing(5)
        R_layout, self.R_min_spinbox, self.R_max_spinbox = (
            self.create_channel_falsergb_section([650, 700], "R")
        )
        false_rgb_layout.addLayout(R_layout)
        false_rgb_layout.addSpacing(5)
        #
        G_layout, self.G_min_spinbox, self.G_max_spinbox = (
            self.create_channel_falsergb_section([550, 600], "G")
        )
        false_rgb_layout.addLayout(G_layout)
        false_rgb_layout.addSpacing(5)
        #
        B_layout, self.B_min_spinbox, self.B_max_spinbox = (
            self.create_channel_falsergb_section([450, 500], "B")
        )
        false_rgb_layout.addLayout(B_layout)
        false_rgb_layout.addSpacing(5)
        # False RGB button
        false_rgb_btn_layout = QHBoxLayout()
        false_rgb_btn = PushButton(text="Create False RGB")
        false_rgb_btn.clicked.connect(self.false_rgb_btn_f)
        false_rgb_btn_layout.addWidget(
            Container(widgets=[false_rgb_btn]).native
        )
        #
        false_rgb_layout.addLayout(false_rgb_btn_layout)
        true_rgb_layout.addLayout(false_rgb_layout)
        rgb_box.setLayout(true_rgb_layout)
        return rgb_box

    def create_channel_falsergb_section(self, value, label_name):
        """ """
        channel_layout = QHBoxLayout()
        label = Label(value=label_name)
        # label.native.setFixedWidth(20)
        # channel_layout.addSpacing(50)
        channel_layout.addWidget(label.native)
        min_spinbox = SpinBox(
            min=0, max=2500, step=1, value=value[0], label=label_name
        )
        max_spinbox = SpinBox(min=0, max=2500, step=1, value=value[1])
        channel_layout.addSpacing(50)
        channel_layout.addWidget(min_spinbox.native)
        channel_layout.addSpacing(50)
        channel_layout.addWidget(max_spinbox.native)

        return channel_layout, min_spinbox, max_spinbox

    def plot_box(self):
        """Plot of the mean spectrum"""
        plot_box = QGroupBox("Plot of mean spectrum")
        plot_layout = QVBoxLayout()
        plot_layout.addSpacing(10)
        # Plot
        plot_layout_graph = self.create_plot_graph_section()
        plot_layout.addLayout(plot_layout_graph)
        # Export
        plot_layout_export_txt = self.create_plot_export_section()
        plot_layout.addLayout(plot_layout_export_txt)
        plot_box.setLayout(plot_layout)
        return plot_box

    def create_plot_graph_section(self):
        """Mean spectrum"""
        plot_layout = QVBoxLayout()

        self.meanspec_plot = FigureCanvas(Figure(figsize=(5, 3)))
        self.meanspec_plot.setMinimumSize(300, 450)
        self.meanspec_plot_toolbar = NavigationToolbar(
            self.meanspec_plot, self
        )
        self.plot.customize_toolbar(self.meanspec_plot_toolbar)
        self.plot.setup_plot(self.meanspec_plot)
        #
        # Buttons and checkboxes
        controls_layout = QVBoxLayout()
        self.std_plot_checkbox = CheckBox(text="Plot standard deviation")
        self.norm_plot_checkbox = CheckBox(text="Normalize plot")
        self.derivative_checkbox = CheckBox(text="Plot with derivative")
        self.dimred_checkbox = CheckBox(text="Reduced dataset")
        for c in [
            self.std_plot_checkbox,
            self.norm_plot_checkbox,
            self.derivative_checkbox,
            self.dimred_checkbox,
        ]:
            controls_layout.addWidget(c.native)
        #
        plot_btn = PushButton(text="Mean spectrum")
        plot_btn.clicked.connect(
            lambda: self.plot.show_plot(
                self.meanspec_plot,
                mode=self.datamanager.modes_combobox.value,
                std_flag=self.std_plot_checkbox.value,
                norm_flag=self.norm_plot_checkbox.value,
                reduced_dataset_flag=self.dimred_checkbox.value,
                derivative_flag=self.derivative_checkbox.value,
            )
        )
        controls_layout.addWidget(plot_btn.native)
        plot_layout.addLayout(controls_layout)
        plot_layout.addWidget(self.meanspec_plot)
        plot_layout.addWidget(self.meanspec_plot_toolbar)

        return plot_layout

    def create_plot_export_section(self):
        """Export mean spectrum"""
        export_txt_layout = QVBoxLayout()

        export_txt_btn = PushButton(text="Export spectra")
        export_txt_btn.clicked.connect(
            lambda: self.plot.show_plot(
                self.meanspec_plot,
                mode=self.datamanager.modes_combobox.value,
                std_flag=self.std_plot_checkbox.value,
                norm_flag=self.norm_plot_checkbox.value,
                reduced_dataset_flag=self.dimred_checkbox.value,
                export_txt_flag=True,
            )
        )

        export_txt_layout.addWidget(Container(widgets=[export_txt_btn]).native)
        return export_txt_layout

    # %% Buttons functions
    def true_rgb_btn_f(self):
        """ """
        data_mode = self.datamanager.modes_combobox.value
        self.data.rgb[data_mode] = HSI2RGB(
            self.data.wls[data_mode],
            self.data.hypercubes[data_mode],
            self.data.hypercubes[data_mode].shape[0],
            self.data.hypercubes[data_mode].shape[1],
            65,
            False,
        )
        self.viewer.add_image(
            self.data.rgb[data_mode],
            name=str(data_mode) + " RGB",
            rgb=True,
            metadata={"type": "rgb"},
        )
        return

    def false_rgb_btn_f(self):
        """ """
        data_mode = self.datamanager.modes_combobox.value
        R_values = [self.R_min_spinbox.value, self.R_max_spinbox.value]
        G_values = [self.G_min_spinbox.value, self.G_max_spinbox.value]
        B_values = [self.B_min_spinbox.value, self.B_max_spinbox.value]
        falseRGB_image = falseRGB(
            self.data.hypercubes[data_mode],
            self.data.wls[data_mode],
            R_values,
            G_values,
            B_values,
        )
        self.viewer.add_image(
            falseRGB_image,
            name=str(data_mode) + " - FALSE RGB",
            rgb=True,
            metadata={"type": "false_rgb"},
        )

    # %% Other functions
