""" """

from contextlib import suppress

import napari
import numpy as np
import pyqtgraph as pg
import pyqtgraph.exporters
import qtawesome as qta  # Icons
from magicgui.widgets import PushButton
from matplotlib.path import Path
from napari.utils.notifications import show_info, show_warning
from qtpy import QtCore
from qtpy.QtWidgets import QFileDialog, QWidget


class Plot(QWidget):
    """Class for the plots"""

    def __init__(self, viewer: napari.Viewer, data):
        """ """
        super().__init__()
        self.viewer = viewer
        self.data = data
        self.poly_roi = None
        self.drawing = False
        self.vertical_line = None
        self.mouse_connected = False

    def setup_plot(self, plot, fused=False):
        self.ax = self.ax2 = self.ax3 = None  # Reset of the axis
        plot.figure.patch.set_facecolor("#262930")
        #
        if fused and len(self.data.fusion_modes) > 2:
            n_axes = 3
        elif fused:
            n_axes = 2
        else:
            n_axes = 1
        #
        axes = plot.figure.subplots(1, n_axes)
        if n_axes == 1:
            axes = [
                axes
            ]  # if n_axes = 1, subplots return a single axis, not a list of axes. we'll make it a list anyway
        self.ax, *rest = (
            axes  # unpacking (self.ax = ax1, the other(s) to rest)
        )
        self.ax2 = rest[0] if len(rest) > 0 else None
        self.ax3 = rest[1] if len(rest) > 1 else None

        for ax in axes:
            if ax is not None:
                ax.set_facecolor("#262930")
                ax.tick_params(axis="x", colors="#D3D4D5", labelsize=14)
                ax.tick_params(axis="y", colors="#D3D4D5", labelsize=14)
                ax.grid(
                    True,
                    linestyle="--",
                    linewidth=0.5,
                    color="#D3D4D5",
                    alpha=0.5,
                )
                for position, spine in ax.spines.items():
                    if position in ["left", "bottom"]:
                        spine.set_color("#D3D4D5")
                        spine.set_linewidth(1)
                        spine.set_visible(True)
                    else:
                        spine.set_visible(False)

    def show_plot(
        self,
        plot,
        mode,
        std_flag=False,
        norm_flag=False,
        reduced_dataset_flag=False,
        export_txt_flag=False,
        derivative_flag=False,
    ):
        """ """
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
        # Clean and reset the plot
        fig = plot.figure
        fig.clf()
        self.setup_plot(plot, fused=(mode == "Fused"))
        fused_flag = mode == "Fused"
        # Secondary axis for derivative
        ax_der = None
        if derivative_flag and not fused_flag:
            ax_der = self.ax.twinx()
            ax_der.tick_params(axis="y", colors="#FFA500", labelsize=14)
            ax_der.spines["right"].set_color("#FFA500")
            ax_der.set_ylabel("Derivative", color="#FFA500")
        #
        num_classes = int(labels_data.max())
        colormap = np.array(selected_layer.colormap.colors)
        print("Shape of mask; ", labels_data.shape)
        wavelengths = self.data.wls[mode]
        # Compute spectra and derivatives
        spectra, stds, spectra_der, stds_der = (
            self.compute_spectra(  # funxtion for compute spectra
                wavelengths,
                mask=labels_data,
                mode=mode,
                reduced_flag=reduced_dataset_flag,
                num_classes=num_classes,
                normalize_flag=norm_flag,
                derivative_flag=derivative_flag,
            )
        )

        # PLOT SPECTRA
        for index in range(num_classes):
            color = colormap[index + 1, :3]
            # Fused mode
            if fused_flag:
                self.plot_fused(
                    index, spectra, stds, color, std_flag
                )  # function for fused
                continue
            # principal spectrum
            self.plot_spectrum(
                self.ax,
                wavelengths,
                spectra[index],
                stds[index] if std_flag else None,
                color,
            )
            if derivative_flag and ax_der is not None:
                self.plot_spectrum(
                    ax_der,
                    wavelengths,
                    spectra_der[index],
                    stds_der[index] if std_flag else None,
                    color,
                    linestyle="--",
                )
        #
        if export_txt_flag:
            filename, selected_filter = QFileDialog.getSaveFileName(
                self, "Save spectra", "", "CSV file (*.csv);;Text file (*.txt)"
            )
            if filename:

                if not (
                    filename.lower().endswith(".txt")
                    or filename.lower().endswith(".csv")
                ):
                    if selected_filter.startswith("Text"):
                        filename += ".txt"
                    else:
                        filename += ".csv"
                if not std_flag:
                    stds = np.zeros_like(spectra)
                print(spectra.shape, stds.shape)

                if filename.endswith(".txt"):
                    self.export_spectra_txt(
                        filename, wavelengths, spectra.T, stds.T, mode="txt"
                    )

                elif filename.endswith(".csv"):
                    self.export_spectra_txt(
                        filename, wavelengths, spectra.T, stds.T, mode="csv"
                    )
        plot.draw()

    def compute_spectra(
        self,
        wavelengths,
        mask,
        mode,
        reduced_flag,
        num_classes,
        normalize_flag,
        derivative_flag,
    ):
        """Compute mean and std of spectra (and derivative if requested)."""
        wl_len = len(wavelengths)
        spectra = np.zeros((num_classes, wl_len))
        stds = np.zeros_like(spectra)
        spectra_der = np.zeros_like(spectra)
        stds_der = np.zeros_like(stds)

        #
        # Select the right data
        def select_cube(mode):
            """"""
            if reduced_flag:
                cube = self.data.hypercubes_spatial_red.get(mode)
                if cube is not None:
                    return self.data.hypercubes_spatial_red
                return self.data.hypercubes_red
            return self.data.hypercubes

        #
        for idx in range(num_classes):
            points = np.array(np.where(mask == idx + 1))
            if points.size == 0:
                continue  # Jump to the next cycle
            # Handle Fused
            if mode == "Fused":
                cube = select_cube("Fused")
                data_selected = np.concatenate(
                    [
                        cube[m][points[0], points[1], :]
                        for m in self.data.fusion_modes
                    ],
                    axis=1,
                )
            else:
                cube = select_cube(mode)
                data_selected = cube[mode][points[0], points[1], :]
            #
            mean_spec = np.mean(data_selected, axis=0)
            std_spec = np.std(data_selected, axis=0)
            #
            if normalize_flag:
                min_val, max_val = np.min(mean_spec), np.max(mean_spec)
                if max_val > min_val:  # evita divisioni per zero
                    mean_spec = (mean_spec - min_val) / (max_val - min_val)
                    std_spec /= max_val - min_val
            spectra[idx] = mean_spec
            stds[idx] = std_spec
            #
            if derivative_flag:
                cube_der = select_cube(mode + " - derivative")
                if cube_der.get(mode + " - derivative") is not None:
                    data_der = cube_der[mode + " - derivative"][
                        points[0], points[1], :
                    ]
                    spectra_der[idx] = np.mean(data_der, axis=0)
                    stds_der[idx] = np.std(data_der, axis=0)
        return spectra, stds, spectra_der, stds_der

    def plot_spectrum(self, ax, x, y, std=None, color="blue", linestyle="-"):
        """Plot with optional standard deviation shading."""
        ax.plot(x, y, color=color, linewidth=2, linestyle=linestyle)
        if std is not None:
            ax.fill_between(x, y - std, y + std, color=color, alpha=0.3)

    def plot_fused(self, index, spectra, stds, color, std_flag):
        """Handle the plotting of fused datasets."""
        fusion_modes = self.data.fusion_modes
        wls = [self.data.wls[m] for m in fusion_modes]
        wl_points = np.cumsum(
            [w.shape[0] for w in wls]
        )  # list with n of elements in wls + cumulative sum
        #
        start = 0
        axes = [self.ax, self.ax2, getattr(self, "ax3", None)]
        for i, (ax, wl) in enumerate(zip(axes, wls, strict=False)):
            end = wl_points[i]
            if ax is None:
                break
            y = spectra[index, start:end]
            s = stds[index, start:end]
            ax.plot(wl, y, color=color, linewidth=2)
            if std_flag:
                ax.fill_between(wl, y - s, y + s, color=color, alpha=0.3)
            start = end

    # %% Export spectra
    def export_spectra_txt(self, filename, wavelengths, spectra, stds, mode):
        """Export spectra and standard deviation to TXT."""
        print("Spectra and std shape: ", spectra.shape, stds.shape)
        print("Wavelengths shape: ", wavelengths.shape)
        M = spectra.shape[1]
        cols = [wavelengths]
        for j in range(M):
            cols.append(spectra[:, j])
            cols.append(stds[:, j])
        data_to_save = np.column_stack(cols)

        if mode == "txt":
            header_parts = ["Wavelength"]
            header_parts += [f"Spectrum{j+1}\tStd{j+1}" for j in range(M)]
            header_txt = "\t".join(header_parts)
            np.savetxt(
                filename,
                data_to_save,
                fmt="%.6f",
                delimiter="\t",
                header=header_txt,
                comments="",
            )
            show_info("The .txt has been saved")
        if mode == "csv":
            header_csv = "Wavelength," + ",".join(
                [f"Spectrum{j+1},Std{j+1}" for j in range(M)]
            )
            np.savetxt(
                filename,
                data_to_save,
                fmt="%.6f",
                delimiter=",",
                header=header_csv,
                comments="",
            )
            show_info("The .csv has been saved")

    # -----------------------------------------------------------------------------------------------
    # %% SCATTERPLOT
    # -----------------------------------------------------------------------------------------------
    def setup_scatterplot(self, plot):
        """Setup basic scatterplot appearance"""
        plot.setBackground("w")
        for axis in ("left", "bottom"):
            plot.getAxis(axis).setTicks([])
            plot.getAxis(axis).setStyle(tickLength=0)
            plot.getAxis(axis).setPen(None)
        plot.setMinimumSize(400, 400)

    ## ICONS
    def polygon_selection(self, plot):
        """Polygonal selection on scatterplot"""
        self.plot = plot
        self.temp_points = []
        # Remove old ROIs
        if self.poly_roi:
            # Disconnect if necessary
            if self.mouse_connected:
                with suppress(TypeError):
                    self.plot.scene().sigMouseClicked.disconnect(
                        self.add_point_to_polygon
                    )
                # try:
                #    self.plot.scene().sigMouseClicked.disconnect(
                #        self.add_point_to_polygon
                #    )
                # except TypeError:
                #    pass
            self.plot.removeItem(self.poly_roi)

        self.poly_roi = pg.PolyLineROI(
            [],
            closed=False,
            pen="r",
            handlePen=pg.mkPen("red"),
        )
        self.plot.addItem(self.poly_roi)
        self.drawing = True
        # connect
        if not self.mouse_connected:
            self.plot.scene().sigMouseClicked.connect(
                self.add_point_to_polygon
            )
            self.mouse_connected = True

    def add_point_to_polygon(self, event):
        """Add points to the ROI"""
        if not self.drawing:
            return
        if event.button() == QtCore.Qt.LeftButton:
            pos = self.plot.plotItem.vb.mapSceneToView(event.scenePos())
            point = (pos.x(), pos.y())
            self.temp_points.append(point)
            self.poly_roi.setPoints(self.temp_points)
            if event.double():
                self.drawing = False
                self.poly_roi.closed = True
                self.poly_roi.setPoints(
                    self.temp_points
                )  # richiude visivamente
                if self.mouse_connected:
                    with suppress(TypeError):
                        self.plot.scene().sigMouseClicked.disconnect(
                            self.add_point_to_polygon
                        )
                    # try:
                    #    self.plot.scene().sigMouseClicked.disconnect(
                    #        self.add_point_to_polygon
                    #    )
                    # except TypeError:
                    #    pass
                    # self.mouse_connected = False

    def show_selected_points(self, scatterdata, hsi_image, mode, points):
        """ """
        if not self.poly_roi:
            print("No active selection!")
            return
        polygon = self.poly_roi.getState()["points"]
        polygon = np.array(polygon)
        path = Path(polygon)
        points_mask = path.contains_points(scatterdata)
        selected_indices = [
            index for index, value in enumerate(points_mask) if value
        ]
        if len(points) > 0:
            selected_indices = points[selected_indices]
        # print("Punti selezionati:", selected_points)
        # print("Indici selezionati:", selected_indices)
        # CREATION OF LAYER LABELS
        labels = np.zeros(
            (hsi_image.shape[0], hsi_image.shape[1]), dtype=np.int32
        )
        existing_layers = [
            layer
            for layer in self.viewer.layers
            if layer.name == f"{mode} SCATTERPLOT LABELS"
        ]
        if existing_layers:
            labels_layer = existing_layers[0]
            labels = labels_layer.data
            new_label_value = labels.max() + 1
        else:
            labels_layer = None
            labels = np.zeros(
                (hsi_image.shape[0], hsi_image.shape[1]), dtype=np.int32
            )
            new_label_value = 1

        labels.flat[np.asarray(selected_indices, dtype=np.intp)] = (
            new_label_value
        )
        # LABELS IN THE SELCTED POINTS
        # for idx in selected_indices:
        #    row, col = divmod(idx, hsi_image.shape[1])  # Converted in 2D
        #    labels[row, col] = new_label_value
        if labels_layer:
            # labels_layer.data = labels
            labels_layer.refresh()
        else:
            labels_layer = self.viewer.add_labels(
                labels, name=f"{mode} SCATTERPLOT LABELS"
            )
        self.temp_points = []

    def save_image_button(self, plot):
        """ """
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save UMAP image", "", "png (*.png)"
        )
        if filename:
            exporter = pg.exporters.ImageExporter(plot.getPlotItem())
            exporter.parameters()["width"] = 2000
            exporter.parameters()["height"] = 2000
            exporter.export(filename)
            print("Image saved!")

    def show_scatterplot(self, plot, data, hex_colors, points, size):
        """Display sctterplot"""
        if hasattr(self, "scatter") and self.scatter:
            plot.removeItem(self.scatter)
            self.scatter = None
        if len(points) > 0:
            self.scatter = pg.ScatterPlotItem(
                pos=data,
                pen=None,
                symbol="o",
                size=size,
                brush=hex_colors[points],
            )
        else:
            self.scatter = pg.ScatterPlotItem(
                pos=data, pen=None, symbol="o", size=size, brush=hex_colors
            )
        plot.addItem(self.scatter)
        plot.getViewBox().autoRange()
        plot.update()

    # %% Customization
    def customize_toolbar(self, toolbar):
        """Customaize the toolbar of the plot"""
        # Cambia sfondo della toolbar
        toolbar.setStyleSheet("background-color: #262930; border: none;")

        # Mappa nome azione → nome file icona
        icon_map = {
            "Home": "fa5s.home",
            "Back": "fa5s.arrow-left",
            "Forward": "fa5s.arrow-right",
            "Pan": "fa5s.expand-arrows-alt",
            "Zoom": "ei.zoom-in",
            "Subplots": "msc.settings",
            "Customize": "mdi.chart-scatter-plot",
            "Save": "fa5.save",
        }

        for action in toolbar.actions():
            text = action.text()
            if text in icon_map:
                action.setIcon(qta.icon(f"{icon_map[text]}", color="#D3D4D5"))

    def create_button(self, icon_name):
        """Create styled icon button"""
        btn = PushButton(text="").native
        btn.setIcon(qta.icon(f"{icon_name}", color="#D3D4D5"))  # Icon
        btn.setStyleSheet(
            """
            QPushButton {
                background-color: #262930;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #3E3F40;
            }"""
        )
        btn.setFixedSize(30, 30)  # Dimensione fissa
        return btn

    # %% Show spectra for endmembers extraction
    def show_spectra(
        self,
        plot,
        spectra,
        mode,
        basis_numbers,
        export_txt_flag=False,
    ):
        # Clean and reset the plot
        fig = plot.figure
        fig.clf()
        self.setup_plot(plot, fused=(mode == "Fused"))

        wavelengths = self.data.wls[mode]

        colormap = np.array(napari.utils.colormaps.label_colormap().colors)
        for index, element in enumerate(basis_numbers):
            if mode == "Fused":
                self.plot_fused(
                    index,
                    spectra.transpose(),
                    np.zeros_like(spectra.transpose()),  # Std deviation
                    colormap[element + 3, :3],
                    False,
                )

            else:
                self.ax.plot(
                    wavelengths,
                    spectra[:, index],
                    color=colormap[element + 3, :3],
                    linewidth=2,
                )

        if export_txt_flag:
            filename, selected_filter = QFileDialog.getSaveFileName(
                self, "Save spectra", "", "CSV file (*.csv);;Text file (*.txt)"
            )
            if filename:

                if not (
                    filename.lower().endswith(".txt")
                    or filename.lower().endswith(".csv")
                ):
                    if selected_filter.startswith("Text"):
                        filename += ".txt"
                    else:
                        filename += ".csv"

                std = np.zeros_like(spectra)
                print(spectra.shape, std.shape)

                if filename.endswith(".txt"):
                    self.export_spectra_txt(
                        filename, wavelengths, spectra, std, mode="txt"
                    )

                elif filename.endswith(".csv"):
                    self.export_spectra_txt(
                        filename, wavelengths, spectra, std, mode="csv"
                    )

        plot.draw()
