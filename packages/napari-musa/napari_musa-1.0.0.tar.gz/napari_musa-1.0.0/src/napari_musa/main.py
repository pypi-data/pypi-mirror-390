""" """

import napari
import napari as np
from qtpy.QtCore import QTimer

from napari_musa.modules.data import Data
from napari_musa.modules.plot import Plot
from napari_musa.Widget_DataManager import DataManager
from napari_musa.Widgets_DataVisualization import DataVisualization
from napari_musa.Widgets_EndmembersExtraction import EndmembersExtraction
from napari_musa.Widgets_Fusion import Fusion
from napari_musa.Widgets_NMF import NMF
from napari_musa.Widgets_PCA import PCA
from napari_musa.Widgets_UMAP import UMAP


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


def run_napari_app():
    """Add widgets to the viewer"""
    try:
        viewer = napari.current_viewer()
    except AttributeError:
        viewer = napari.Viewer()

    # WIDGETS
    data = Data()
    plot_datavisualization = Plot(viewer=viewer, data=data)
    datamanager_widget = DataManager(viewer, data)
    datavisualization_widget = DataVisualization(
        viewer, data, plot_datavisualization, datamanager_widget
    )
    fusion_widget = Fusion(viewer, data)

    plot_umap = Plot(viewer=viewer, data=data)
    umap_widget = UMAP(viewer, data, plot_umap)
    nmf_widget = NMF(viewer, data, plot_umap)
    endmextr_widget = EndmembersExtraction(viewer, data, plot_umap)
    plot_pca = Plot(viewer=viewer, data=data)
    pca_widget = PCA(viewer, data, plot_pca)

    datamanager_widget.mode_added.connect(update_modes_comboboxes)

    # Add widget as dock
    datamanager_dock = viewer.window.add_dock_widget(
        datamanager_widget, name="Data Manager", area="right"
    )
    datavisualization_dock = viewer.window.add_dock_widget(
        datavisualization_widget, name="Data Visualization", area="right"
    )
    fusion_dock = viewer.window.add_dock_widget(
        fusion_widget, name="Fusion", area="right"
    )
    umap_dock = viewer.window.add_dock_widget(
        umap_widget, name="UMAP", area="right"
    )
    endmextr_dock = viewer.window.add_dock_widget(
        endmextr_widget, name="Endmembers", area="right"
    )
    pca_dock = viewer.window.add_dock_widget(
        pca_widget, name="PCA", area="right"
    )
    nmf_dock = viewer.window.add_dock_widget(
        nmf_widget, name="NMF", area="right"
    )

    # Tabify the widgets
    viewer.window._qt_window.tabifyDockWidget(
        datamanager_dock, datavisualization_dock
    )
    viewer.window._qt_window.tabifyDockWidget(
        datavisualization_dock, fusion_dock
    )
    viewer.window._qt_window.tabifyDockWidget(fusion_dock, umap_dock)
    viewer.window._qt_window.tabifyDockWidget(umap_dock, pca_dock)
    viewer.window._qt_window.tabifyDockWidget(pca_dock, endmextr_dock)
    viewer.window._qt_window.tabifyDockWidget(endmextr_dock, nmf_dock)
    # Text overlay in the viewer
    viewer.text_overlay.visible = True

    setup_connections()
    viewer.layers.events.inserted.connect(on_new_layer)
    viewer.layers.selection.events.active.connect(
        datamanager_widget.on_layer_selected
    )

    return None  # Non serve restituire nulla
