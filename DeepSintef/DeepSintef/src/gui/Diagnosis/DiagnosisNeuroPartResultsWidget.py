from __main__ import qt, ctk, slicer, vtk
from glob import glob

from src.utils.resources import SharedResources


class DiagnosisNeuroPartResultsWidget(qt.QWidget):
    def __init__(self, parent=None):
        super(DiagnosisNeuroPartResultsWidget, self).__init__(parent)
        self.base_layout = qt.QGridLayout()

        self.volume_label = qt.QLabel('Volume:')
        self.volume_lineedit = qt.QLineEdit()
        self.volume_lineedit.setReadOnly(True)
        self.base_layout.addWidget(self.volume_label, 0, 0)
        self.base_layout.addWidget(self.volume_lineedit, 0, 1)

        self.laterality_label = qt.QLabel('Laterality:')
        self.laterality_lineedit = qt.QLineEdit()
        self.laterality_lineedit.setReadOnly(True)
        self.base_layout.addWidget(self.laterality_label, 1, 0)
        self.base_layout.addWidget(self.laterality_lineedit, 1, 1)

        self.resectability_index_label = qt.QLabel('Resectability:')
        self.resectability_index_lineedit = qt.QLineEdit()
        self.resectability_index_lineedit.setReadOnly(True)
        self.base_layout.addWidget(self.resectability_index_label, 2, 0)
        self.base_layout.addWidget(self.resectability_index_lineedit, 2, 1)

        self.lobes_label = qt.QLabel('Lobes:')
        self.lobes_tablewidget = qt.QTableWidget()
        self.lobes_tablewidget.setColumnCount(2)
        self.lobes_tablewidget.setHorizontalHeaderLabels(['Lobe', 'Dice overlap'])
        self.base_layout.addWidget(self.lobes_label, 3, 0)
        self.base_layout.addWidget(self.lobes_tablewidget, 3, 1)

        self.tracts_overlap_label = qt.QLabel('Tracts overlap:')
        self.tracts_overlap_tablewidget = qt.QTableWidget()
        self.tracts_overlap_tablewidget.setColumnCount(2)
        self.tracts_overlap_tablewidget.setHorizontalHeaderLabels(['Tract', 'Dice overlap'])
        self.base_layout.addWidget(self.tracts_overlap_label, 4, 0)
        self.base_layout.addWidget(self.tracts_overlap_tablewidget, 4, 1)

        self.tracts_distance_label = qt.QLabel('Tracts distance:')
        self.tracts_distance_tablewidget = qt.QTableWidget()
        self.tracts_distance_tablewidget.setColumnCount(2)
        self.tracts_distance_tablewidget.setHorizontalHeaderLabels(['Tract', 'Minimum distance'])
        self.base_layout.addWidget(self.tracts_distance_label, 5, 0)
        self.base_layout.addWidget(self.tracts_distance_tablewidget, 5, 1)

        self.setLayout(self.base_layout)

    def update_results(self, values):
        self.volume_lineedit.setText(str(values['Overall'].mni_space_tumor_volume) + 'ml')
        self.laterality_lineedit.setText(values['Overall'].laterality + ' with ' + str(values['Overall'].laterality_percentage) + '%')
        self.resectability_index_lineedit.setText(str(values['Overall'].mni_space_resectability_score) + '%')

        main_lobes = values['Overall'].mni_space_lobes_overlap
        self.lobes_tablewidget.setRowCount(len(main_lobes.keys()))
        for l, ln in enumerate(main_lobes.keys()):
            self.lobes_tablewidget.setItem(l, 0, qt.QTableWidgetItem(ln))
            self.lobes_tablewidget.setItem(l, 1, qt.QTableWidgetItem(str(main_lobes[ln]) + '%'))

        tracts_overlap = values['Overall'].mni_space_tracts_overlap
        self.tracts_overlap_tablewidget.setRowCount(len(tracts_overlap.keys()))
        for l, ln in enumerate(tracts_overlap.keys()):
            self.tracts_overlap_tablewidget.setItem(l, 0, qt.QTableWidgetItem(ln))
            self.tracts_overlap_tablewidget.setItem(l, 1, qt.QTableWidgetItem(str(tracts_overlap[ln]) + '%'))

        tracts_distance = values['Overall'].mni_space_tracts_distance
        self.tracts_distance_tablewidget.setRowCount(len(tracts_distance.keys()))
        for l, ln in enumerate(tracts_distance.keys()):
            self.tracts_distance_tablewidget.setItem(l, 0, qt.QTableWidgetItem(ln))
            self.tracts_distance_tablewidget.setItem(l, 1, qt.QTableWidgetItem(str(tracts_distance[ln]) + 'mm'))

        self.lobes_tablewidget.horizontalHeader().setStretchLastSection(True)
        self.lobes_tablewidget.verticalHeader().setStretchLastSection(True)
        self.lobes_tablewidget.horizontalHeader().setSectionResizeMode(qt.QHeaderView.Stretch)
        self.lobes_tablewidget.verticalHeader().setSectionResizeMode(qt.QHeaderView.Stretch)

        self.tracts_overlap_tablewidget.horizontalHeader().setStretchLastSection(True)
        self.tracts_overlap_tablewidget.verticalHeader().setStretchLastSection(True)
        self.tracts_overlap_tablewidget.horizontalHeader().setSectionResizeMode(qt.QHeaderView.Stretch)
        self.tracts_overlap_tablewidget.verticalHeader().setSectionResizeMode(qt.QHeaderView.Stretch)

        self.tracts_distance_tablewidget.horizontalHeader().setStretchLastSection(True)
        self.tracts_distance_tablewidget.verticalHeader().setStretchLastSection(True)
        self.tracts_distance_tablewidget.horizontalHeader().setSectionResizeMode(qt.QHeaderView.Stretch)
        self.tracts_distance_tablewidget.verticalHeader().setSectionResizeMode(qt.QHeaderView.Stretch)
