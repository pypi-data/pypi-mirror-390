""" """

import sys
from os.path import dirname

import napari

sys.path.append(dirname(dirname(__file__)))
# print("here: ", dirname(dirname(__file__)))

# from napari_hsi_analysis.modules.plot_widget import PlotWidget
import numpy as np
from qtpy.QtCore import QTimer

from napari_musa.modules.data import Data
from napari_musa.modules.plot import Plot
from napari_musa.Widget_DataManager import DataManager
from napari_musa.Widgets_DataVisualization import DataVisualization
from napari_musa.Widgets_EndmembersExtraction import EndmembersExtraction
from napari_musa.Widgets_Fusion import Fusion
from napari_musa.Widgets_NMF import NMF
from napari_musa.Widgets_PCA import PCA

# from napari_musa._widget_Label import LabelWidget
from napari_musa.Widgets_UMAP import UMAP


class NapariApp:
    """ """

    def __init__(self):
        """ """
        self.viewer = napari.Viewer()
        self.data = Data()
        self.plot_datavisualization = Plot(viewer=self.viewer, data=self.data)
        self.plot_umap = Plot(viewer=self.viewer, data=self.data)
        self.datamanager_widget = DataManager(self.viewer, self.data)
        self.datavisualization_widget = DataVisualization(
            self.viewer,
            self.data,
            self.plot_datavisualization,
            self.datamanager_widget,
        )
        self.fusion_widget = Fusion(self.viewer, self.data)
        self.umap_widget = UMAP(self.viewer, self.data, self.plot_umap)
        # self.label_widget = LabelWidget(
        #    self.viewer, self.data, self.datamanager_widget
        # )
        self.nmf_widget = NMF(self.viewer, self.data, self.plot_umap)
        self.endmextr_widget = EndmembersExtraction(
            self.viewer, self.data, self.plot_umap
        )
        self.plot_pca = Plot(viewer=self.viewer, data=self.data)
        self.pca_widget = PCA(self.viewer, self.data, self.plot_pca)

        self.setup_dock_widgets()
        self.setup_connections()
        self.viewer.layers.events.inserted.connect(self.on_new_layer)
        self.datamanager_widget.mode_added.connect(
            self.update_modes_comboboxes
        )

    # def create_dock_widget(self, widget, name, area="right", min_size=(400, 400)): 0
    #    """Add a dock widget to the viewer."""
    #    dock = self.viewer.window.add_dock_widget(widget, name=name, area=area)
    #    if min_size:
    #        dock.setMinimumSize(*min_size)
    #    return dock

    def setup_dock_widgets(
        self,
    ):
        """ """
        datamanager_dock = self.viewer.window.add_dock_widget(
            self.datamanager_widget, name="Data Manager", area="right"
        )
        #
        datavisualization_dock = self.viewer.window.add_dock_widget(
            self.datavisualization_widget,
            name="Data Visualization",
            area="right",
        )
        #
        umap_dock = self.viewer.window.add_dock_widget(
            self.umap_widget, name="UMAP", area="right"
        )
        #
        fusion_dock = self.viewer.window.add_dock_widget(
            self.fusion_widget, name="Fusion", area="right"
        )
        #
        # label_dock = self.viewer.window.add_dock_widget(
        #    self.label_widget, name="Labeling", area="right"
        # )
        endmextr_dock = self.viewer.window.add_dock_widget(
            self.endmextr_widget, name="Endmembers", area="right"
        )
        #
        nmf_dock = self.viewer.window.add_dock_widget(
            self.nmf_widget, name="NMF", area="right"
        )
        #
        pca_dock = self.viewer.window.add_dock_widget(
            self.pca_widget, name="PCA", area="right"
        )
        #
        self.viewer.window._qt_window.tabifyDockWidget(
            datamanager_dock, datavisualization_dock
        )
        self.viewer.window._qt_window.tabifyDockWidget(
            datavisualization_dock, fusion_dock
        )
        self.viewer.window._qt_window.tabifyDockWidget(fusion_dock, pca_dock)
        self.viewer.window._qt_window.tabifyDockWidget(pca_dock, endmextr_dock)
        self.viewer.window._qt_window.tabifyDockWidget(
            endmextr_dock, umap_dock
        )
        self.viewer.window._qt_window.tabifyDockWidget(umap_dock, nmf_dock)

    """
    def setup_connections(self):

        self.viewer.text_overlay.visible = True
        self.viewer.dims.events.current_step.connect(
            self.datamanager_widget.update_wl
        )
        self.viewer.layers.selection.events.active.connect(
            #self.datamanager_widget.on_layer_selected #OLD
            self.datamanager_widget.layer_auto_selection
        )
    """

    def setup_connections(self):
        """ """
        self.viewer.text_overlay.visible = True

        def on_step_change(event=None):
            layer = self.viewer.layers.selection.active
            if layer and isinstance(layer, napari.layers.Image):
                name = layer.name
                if "NNLS" in name or "SAM" in name:
                    self.endmextr_widget.update_number_H()
                elif "NMF" in name:
                    self.nmf_widget.update_number_H()
                elif "PCA" in name:
                    self.pca_widget.update_number_H()
                else:
                    self.datamanager_widget.update_wl()

        # collega la funzione wrapper
        self.viewer.dims.events.current_step.connect(on_step_change)

        # resto invariato
        self.viewer.layers.selection.events.active.connect(
            self.datamanager_widget.layer_auto_selection
        )

    def on_new_layer(self, event):
        layer = event.value
        if (
            isinstance(layer, napari.layers.Labels) and layer.data.ndim == 3
        ):  # (C, Y, X)

            def replace():
                if layer in self.viewer.layers:  # solo se esiste ancora
                    new_labels = np.zeros(layer.data.shape[1:], dtype=np.int32)
                    name = layer.name
                    self.viewer.layers.remove(layer)
                    self.viewer.add_labels(new_labels, name=name)

            QTimer.singleShot(0, replace)

    def update_modes_comboboxes(self):
        for widget in [
            self.datamanager_widget,
            self.umap_widget,
            self.fusion_widget,
            self.endmextr_widget,
            self.pca_widget,
            self.nmf_widget,
        ]:
            for attr_name in dir(widget):
                if attr_name.startswith("modes_combobox"):
                    if widget == self.fusion_widget:
                        widget.modes_combobox_1.choices = self.data.modes
                        widget.modes_combobox_2.choices = self.data.modes
                        widget.modes_combobox_3.choices = self.data.modes
                    else:
                        current_value = widget.modes_combobox.value
                        widget.modes_combobox.choices = self.data.modes
                    if current_value not in self.data.modes:
                        widget.modes_combobox.value = current_value

    def run(self):
        """ """
        napari.run()


if __name__ == "__main__":
    """ """
    app = NapariApp()
    app.run()
