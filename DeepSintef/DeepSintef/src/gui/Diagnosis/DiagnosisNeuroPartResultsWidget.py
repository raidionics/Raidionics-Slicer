from __main__ import qt, ctk, slicer, vtk
from glob import glob
import numpy as np

from src.utils.resources import SharedResources
from src.logic.neuro_diagnosis_result_parameters import NeuroDiagnosisParameters


class DiagnosisNeuroPartResultsWidget(qt.QWidget):
    def __init__(self, parent=None):
        super(DiagnosisNeuroPartResultsWidget, self).__init__(parent)
        self.base_layout = qt.QVBoxLayout()

        self.volume_groupbox = ctk.ctkCollapsibleGroupBox()
        self.volume_groupbox.setTitle("Volume")
        self.volume_groupbox_layout = qt.QGridLayout()
        self.volume_label = qt.QLabel('Patient space:')
        self.volume_lineedit = qt.QLineEdit()
        self.volume_lineedit.setReadOnly(True)
        self.volume_groupbox_layout.addWidget(self.volume_label, 0, 0)
        self.volume_groupbox_layout.addWidget(self.volume_lineedit, 0, 1)

        self.volume_mni_label = qt.QLabel('MNI space:')
        self.volume_mni_lineedit = qt.QLineEdit()
        self.volume_mni_lineedit.setReadOnly(True)
        self.volume_groupbox_layout.addWidget(self.volume_mni_label, 0, 2)
        self.volume_groupbox_layout.addWidget(self.volume_mni_lineedit, 0, 3)
        self.volume_groupbox.setLayout(self.volume_groupbox_layout)
        self.base_layout.addWidget(self.volume_groupbox)

        self.laterality_groupbox = ctk.ctkCollapsibleGroupBox()
        self.laterality_groupbox.setTitle("Laterality")
        self.laterality_groupbox_layout = qt.QGridLayout()
        self.laterality_right_label = qt.QLabel('Right hemisphere:')
        self.laterality_right_lineedit = qt.QLineEdit()
        self.laterality_right_lineedit.setReadOnly(True)
        self.laterality_groupbox_layout.addWidget(self.laterality_right_label, 0, 0)
        self.laterality_groupbox_layout.addWidget(self.laterality_right_lineedit, 0, 1)
        self.laterality_left_label = qt.QLabel('Left hemisphere:')
        self.laterality_left_lineedit = qt.QLineEdit()
        self.laterality_left_lineedit.setReadOnly(True)
        self.laterality_groupbox_layout.addWidget(self.laterality_left_label, 1, 0)
        self.laterality_groupbox_layout.addWidget(self.laterality_left_lineedit, 1, 1)
        self.laterality_midline_label = qt.QLabel('Midline crossing:')
        self.laterality_midline_lineedit = qt.QLineEdit()
        self.laterality_midline_lineedit.setReadOnly(True)
        self.laterality_groupbox_layout.addWidget(self.laterality_midline_label, 2, 0)
        self.laterality_groupbox_layout.addWidget(self.laterality_midline_lineedit, 2, 1)
        self.laterality_groupbox.setLayout(self.laterality_groupbox_layout)
        self.base_layout.addWidget(self.laterality_groupbox)

        self.resectability_groupbox = ctk.ctkCollapsibleGroupBox()
        self.resectability_groupbox.setTitle("Resectability")
        self.resectability_groupbox_layout = qt.QGridLayout()
        self.expected_residual_volume_label = qt.QLabel('Expected residual volume (ml):')
        self.expected_residual_volume_lineedit = qt.QLineEdit()
        self.expected_residual_volume_lineedit.setReadOnly(True)
        self.resectability_groupbox_layout.addWidget(self.expected_residual_volume_label, 0, 0)
        self.resectability_groupbox_layout.addWidget(self.expected_residual_volume_lineedit, 0, 1)
        self.resectability_index_label = qt.QLabel('Resection index:')
        self.resectability_index_lineedit = qt.QLineEdit()
        self.resectability_index_lineedit.setReadOnly(True)
        self.resectability_groupbox_layout.addWidget(self.resectability_index_label, 1, 0)
        self.resectability_groupbox_layout.addWidget(self.resectability_index_lineedit, 1, 1)
        self.resectability_groupbox.setLayout(self.resectability_groupbox_layout)
        self.base_layout.addWidget(self.resectability_groupbox)


        self.cortical_structures_groupbox = ctk.ctkCollapsibleGroupBox()
        self.cortical_structures_groupbox.setTitle("Cortical structures")
        self.cortical_structures_groupbox_layout = qt.QVBoxLayout()
        self.cortical_structures_groupbox.setLayout(self.cortical_structures_groupbox_layout)
        self.base_layout.addWidget(self.cortical_structures_groupbox)

        self.subcortical_structures_groupbox = ctk.ctkCollapsibleGroupBox()
        self.subcortical_structures_groupbox.setTitle("Subcortical structures")
        self.subcortical_structures_groupbox_layout = qt.QVBoxLayout()
        self.subcortical_structures_groupbox.setLayout(self.subcortical_structures_groupbox_layout)
        self.base_layout.addWidget(self.subcortical_structures_groupbox)
        self.base_layout.addStretch(1)

        self.setLayout(self.base_layout)

    def update_results(self, values):
        self.volume_lineedit.setText(str(np.round(values['Overall'].original_space_tumor_volume, 2)) + ' ml')
        self.volume_mni_lineedit.setText(str(np.round(values['Overall'].mni_space_tumor_volume, 2)) + ' ml')
        self.laterality_right_lineedit.setText(str(np.round(values['Overall'].right_laterality_percentage, 2)) + ' %')
        self.laterality_left_lineedit.setText(str(np.round(values['Overall'].left_laterality_percentage, 2)) + ' %')
        self.laterality_midline_lineedit.setText(values['Overall'].laterality_midline_crossing)

        if NeuroDiagnosisParameters.getInstance().tumor_type == 'HGGlioma':
            self.expected_residual_volume_lineedit.setText(str(np.round(values['Overall'].mni_space_expected_residual_tumor_volume, 3)) + ' ml')
            self.resectability_index_lineedit.setText(str(values['Overall'].mni_space_resectability_score))
            self.resectability_groupbox.setVisible(True)
        else:
            self.resectability_groupbox.setVisible(False)

        for i in reversed(range(self.cortical_structures_groupbox_layout.count())):
            self.cortical_structures_groupbox_layout.itemAt(i).widget().setParent(None)

        for a in values['Overall'].mni_space_cortical_structures_overlap.keys():
            dummy_widget = qt.QWidget()
            layout = qt.QHBoxLayout()
            struct_label = qt.QLabel(a + ':')
            struct_label.setFixedWidth(100)
            struct_tablewidget = qt.QTableWidget()
            struct_tablewidget.setColumnCount(2)
            struct_tablewidget.setRowCount(len(values['Overall'].mni_space_cortical_structures_overlap[a].keys()))
            struct_tablewidget.setHorizontalHeaderLabels(['Overlap (%)', 'Structure'])
            for s, sn in enumerate(values['Overall'].mni_space_cortical_structures_overlap[a].keys()):
                readable_name = sn.replace(a + '_', '').split('_')[0].replace('-', ' ')
                struct_tablewidget.setItem(s, 0, qt.QTableWidgetItem(str(np.round(values['Overall'].mni_space_cortical_structures_overlap[a][sn], 2))))
                struct_tablewidget.setItem(s, 1, qt.QTableWidgetItem(readable_name))
            struct_tablewidget.horizontalHeader().setStretchLastSection(True)
            struct_tablewidget.verticalHeader().setStretchLastSection(True)
            struct_tablewidget.horizontalHeader().setSectionResizeMode(qt.QHeaderView.ResizeToContents)
            struct_tablewidget.verticalHeader().setSectionResizeMode(qt.QHeaderView.ResizeToContents)
            struct_tablewidget.setEditTriggers(qt.QTableWidget.NoEditTriggers)
            struct_tablewidget.setMinimumHeight(100)
            struct_tablewidget.setMinimumWidth(350)
            layout.addWidget(struct_label)
            layout.addWidget(struct_tablewidget)
            layout.addStretch(1)
            dummy_widget.setLayout(layout)
            self.cortical_structures_groupbox_layout.addWidget(dummy_widget)

        for i in reversed(range(self.subcortical_structures_groupbox_layout.count())):
            self.subcortical_structures_groupbox_layout.itemAt(i).widget().setParent(None)

        for a in values['Overall'].mni_space_subcortical_structures_overlap.keys():
            dummy_widget = qt.QWidget()
            layout = qt.QHBoxLayout()
            struct_label = qt.QLabel(a + ' overlap:')
            struct_label.setFixedWidth(100)
            struct_tablewidget = qt.QTableWidget()
            struct_tablewidget.setColumnCount(2)
            # struct_tablewidget.setRowCount(len(values['Overall'].mni_space_subcortical_structures_overlap[a].keys()))
            struct_tablewidget.setRowCount(len(list(filter((0.0).__ne__, [np.round(x, 2) for x in values['Overall'].mni_space_subcortical_structures_overlap[a].values()]))))
            struct_tablewidget.setHorizontalHeaderLabels(['Overlap (%)', 'Structure'])
            count = 0
            for s, sn in enumerate(values['Overall'].mni_space_subcortical_structures_overlap[a].keys()):
                if np.round(values['Overall'].mni_space_subcortical_structures_overlap[a][sn], 2) != 0:
                    readable_name = sn.replace('_mni', '').replace('_', ' ')
                    struct_tablewidget.setItem(count, 0, qt.QTableWidgetItem(str(np.round(values['Overall'].mni_space_subcortical_structures_overlap[a][sn], 2))))
                    struct_tablewidget.setItem(count, 1, qt.QTableWidgetItem(readable_name))
                    count = count + 1
            struct_tablewidget.horizontalHeader().setStretchLastSection(True)
            struct_tablewidget.verticalHeader().setStretchLastSection(True)
            struct_tablewidget.horizontalHeader().setSectionResizeMode(qt.QHeaderView.ResizeToContents)
            struct_tablewidget.verticalHeader().setSectionResizeMode(qt.QHeaderView.ResizeToContents)
            struct_tablewidget.setEditTriggers(qt.QTableWidget.NoEditTriggers)
            struct_tablewidget.setMinimumHeight(100)
            struct_tablewidget.setMinimumWidth(350)
            layout.addWidget(struct_label)
            layout.addWidget(struct_tablewidget)
            layout.addStretch(1)
            dummy_widget.setLayout(layout)
            self.subcortical_structures_groupbox_layout.addWidget(dummy_widget)

        for a in values['Overall'].mni_space_subcortical_structures_distance.keys():
            dummy_widget = qt.QWidget()
            layout = qt.QHBoxLayout()
            struct_label = qt.QLabel(a + ' distance:')
            struct_label.setFixedWidth(100)
            struct_tablewidget = qt.QTableWidget()
            struct_tablewidget.setColumnCount(2)
            # struct_tablewidget.setRowCount(len(values['Overall'].mni_space_subcortical_structures_distance[a].keys()))
            struct_tablewidget.setRowCount(len(list(filter((-1.0).__ne__, [np.round(x, 2) for x in values['Overall'].mni_space_subcortical_structures_distance[a].values()]))))
            struct_tablewidget.setHorizontalHeaderLabels(['Distance (mm)', 'Structure'])
            count = 0
            for s, sn in enumerate(values['Overall'].mni_space_subcortical_structures_distance[a].keys()):
                if np.round(values['Overall'].mni_space_subcortical_structures_distance[a][sn], 2) != -1:
                    readable_name = sn.replace('_mni', '').replace('_', ' ')
                    struct_tablewidget.setItem(count, 0, qt.QTableWidgetItem(str(np.round(values['Overall'].mni_space_subcortical_structures_distance[a][sn], 2))))
                    struct_tablewidget.setItem(count, 1, qt.QTableWidgetItem(readable_name))
                    count = count + 1
            struct_tablewidget.horizontalHeader().setStretchLastSection(True)
            struct_tablewidget.verticalHeader().setStretchLastSection(True)
            struct_tablewidget.horizontalHeader().setSectionResizeMode(qt.QHeaderView.ResizeToContents)
            struct_tablewidget.verticalHeader().setSectionResizeMode(qt.QHeaderView.ResizeToContents)
            struct_tablewidget.setEditTriggers(qt.QTableWidget.NoEditTriggers)
            struct_tablewidget.setMinimumHeight(100)
            struct_tablewidget.setMinimumWidth(350)
            layout.addWidget(struct_label)
            layout.addWidget(struct_tablewidget)
            layout.addStretch(1)
            dummy_widget.setLayout(layout)
            self.subcortical_structures_groupbox_layout.addWidget(dummy_widget)
