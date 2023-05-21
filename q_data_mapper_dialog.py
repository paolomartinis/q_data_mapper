# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QDataMapperDialog
                                 A QGIS plugin
 Map and refactor data from one layer to another
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2023-05-20
        git sha              : $Format:%H$
        copyright            : (C) 2023 by Idrostudi Srl
        email                : martinis@idrostudi.it
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""


from qgis.PyQt import QtWidgets, QtGui, QtCore
from qgis.core import QgsProject
from qgis.gui import QgsExpressionBuilderWidget
from qgis.core import QgsExpression, QgsExpressionContext, QgsExpressionContextUtils


class QDataMapperDialog(QtWidgets.QDialog):
    def __init__(self, iface, parent=None):
        super(QDataMapperDialog, self).__init__(parent)

        self.iface = iface
        self.selected_layers = []

        # Create layout
        layout = QtWidgets.QVBoxLayout(self)

        # Create source layer combo box
        self.cbSourceLayer = QtWidgets.QComboBox(self)
        layout.addWidget(self.cbSourceLayer)

        # Create destination layer combo box
        self.cbDestinationLayer = QtWidgets.QComboBox(self)
        layout.addWidget(self.cbDestinationLayer)

        # Create the buttons layout
        btn_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(btn_layout)

        # Create the swap button
        self.btnSwap = QtWidgets.QPushButton('Swap', self)
        self.btnSwap.clicked.connect(self.swap_layers)
        btn_layout.addWidget(self.btnSwap)

        # Create the mapping button
        self.btnMapData = QtWidgets.QPushButton('Start Mapping', self)
        self.btnMapData.clicked.connect(self.start_mapping)
        btn_layout.addWidget(self.btnMapData)

        # Populate combo boxes and set the current selection
        self.populate_combo_boxes()

    def get_selected_layers(self):
        layers = self.iface.layerTreeView().selectedLayers()
        return [layer.name() for layer in layers]

    def populate_combo_boxes(self):
        self.selected_layers = self.get_selected_layers()

        self.cbSourceLayer.clear()
        self.cbDestinationLayer.clear()

        self.cbSourceLayer.addItems(self.selected_layers)
        self.cbDestinationLayer.addItems(self.selected_layers)

        self.cbSourceLayer.setCurrentIndex(0)
        self.cbDestinationLayer.setCurrentIndex(1)

    def swap_layers(self):
        current_source = self.cbSourceLayer.currentText()
        current_destination = self.cbDestinationLayer.currentText()
        self.cbSourceLayer.setCurrentText(current_destination)
        self.cbDestinationLayer.setCurrentText(current_source)

    def start_mapping(self):
        source_layer_name = self.cbSourceLayer.currentText()
        destination_layer_name = self.cbDestinationLayer.currentText()
        
        self.layer_attrs_dialog = LayerAttributesDialog(source_layer_name, destination_layer_name)
        self.layer_attrs_dialog.show()

        # Close the QDataMapperDialog after showing the LayerAttributesDialog
        self.close()


class MappingTableWidget(QtWidgets.QTableWidget):
    def __init__(self, source_table, destination_table, parent=None):
        super(MappingTableWidget, self).__init__(parent)
        self.source_table = source_table
        self.destination_table = destination_table

    def count_destination_field(self, field_name):
        count = 0
        for i in range(self.rowCount()):
            if self.item(i, 2) and self.item(i, 2).text() == field_name:
                count += 1
        return count

    def dropEvent(self, event):
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            dropping_table = self
            source_table = event.source()
            dropped_row = source_table.currentRow()
            field_item = source_table.item(dropped_row, 0)
            field_name = field_item.text()

            # Check if this field is already mapped when dropping from destination_table
            if source_table == self.destination_table:
                if self.count_destination_field(field_name) > 0:
                    return

            dropped_point = event.pos()
            dropped_index = dropping_table.indexAt(dropped_point)
            dropped_on_row = dropped_index.row()

            if dropped_on_row == -1:
                dropped_on_row = dropping_table.rowCount()
                dropping_table.insertRow(dropped_on_row)
                dropping_table.setItem(dropped_on_row, 0 if source_table == self.source_table else 1, QtWidgets.QTableWidgetItem(""))

            field_item = QtWidgets.QTableWidgetItem(field_name)

            if source_table == self.source_table:
                dropping_table.setItem(dropped_on_row, 0, field_item)
            elif source_table == self.destination_table:
                dropping_table.setItem(dropped_on_row, 2, field_item)

        self.parent().refresh_table_colors()
        event.accept()

    def setRowColor(self, row, color):
        for col in range(self.columnCount()):
            item = self.item(row, col)
            if item is not None:
                item.setBackground(color)


class LayerAttributesDialog(QtWidgets.QDialog):
    """
    This class represents the main dialog of the plugin
    """

    def __init__(self, source_layer_name, destination_layer_name, parent=None):
        super(LayerAttributesDialog, self).__init__(parent)

        # Storing layer names
        self.source_layer_name = source_layer_name
        self.destination_layer_name = destination_layer_name

        # Creating labels for the three tables
        source_label = QtWidgets.QLabel("Source Table", self)
        mapping_label = QtWidgets.QLabel("Mapping Table", self)
        destination_label = QtWidgets.QLabel("Destination Table", self)

        # Initializing tables
        self.source_table = QtWidgets.QTableWidget(self)
        self.destination_table = QtWidgets.QTableWidget(self)
        # MappingTableWidget seems to be a custom widget not defined in the provided code
        self.mapping_table = MappingTableWidget(self.source_table, self.destination_table, self)

        # Populating the tables with fields from the respective layers
        self.populate_tables(source_layer_name, destination_layer_name)

        # Setting up table properties for drag and drop operations
        # Source table
        self.source_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.source_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.source_table.setDragEnabled(True)
        # Destination table
        self.destination_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.destination_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.destination_table.setDragEnabled(True)
        # Mapping table
        self.mapping_table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.mapping_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.mapping_table.setDragEnabled(False)
        self.mapping_table.setAcceptDrops(True)
        self.mapping_table.viewport().setAcceptDrops(True)
        self.mapping_table.setDragDropMode(QtWidgets.QAbstractItemView.DropOnly)
        self.mapping_table.setDropIndicatorShown(True)
        self.mapping_table.setDragDropOverwriteMode(False)
        self.mapping_table.cellDoubleClicked.connect(self.open_expression_dialog)

        # Setting up layout for the dialog
        # The three tables and their labels are placed side by side horizontally
        layout = QtWidgets.QHBoxLayout(self)
        source_layout = QtWidgets.QVBoxLayout()
        source_layout.addWidget(source_label)
        source_layout.addWidget(self.source_table)
        mapping_layout = QtWidgets.QVBoxLayout()
        mapping_layout.addWidget(mapping_label)
        mapping_layout.addWidget(self.mapping_table)
        destination_layout = QtWidgets.QVBoxLayout()
        destination_layout.addWidget(destination_label)
        destination_layout.addWidget(self.destination_table)
        layout.addLayout(source_layout)
        layout.addLayout(mapping_layout)
        layout.addLayout(destination_layout)

        # Adding a button to remove mappings
        self.btnRemoveMappingRow = QtWidgets.QPushButton('Remove Mapping', self)
        self.btnRemoveMappingRow.clicked.connect(self.remove_mapping_row)
        mapping_layout.addWidget(self.btnRemoveMappingRow)

        # Final setup for the dialog
        self.setLayout(layout)
        self.setWindowTitle('Layer Attributes')
        self.resize(1200, 800)

    def populate_tables(self, source_layer_name, destination_layer_name):
        source_layer = next((layer for layer in QgsProject.instance().mapLayers().values()
                             if layer.name() == source_layer_name), None)
        destination_layer = next((layer for layer in QgsProject.instance().mapLayers().values()
                                  if layer.name() == destination_layer_name), None)

        if source_layer is None or destination_layer is None:
            return

        source_fields = source_layer.fields()
        destination_fields = destination_layer.fields()

        self.source_table.setColumnCount(2)
        self.source_table.setHorizontalHeaderLabels(['Field Name', 'Data Type'])
        self.source_table.setRowCount(len(source_fields))

        for idx, field in enumerate(source_fields):
            field_name_item = QtWidgets.QTableWidgetItem(field.name())
            data_type_item = QtWidgets.QTableWidgetItem(field.typeName())

            self.source_table.setItem(idx, 0, field_name_item)
            self.source_table.setItem(idx, 1, data_type_item)

        self.destination_table.setColumnCount(2)
        self.destination_table.setHorizontalHeaderLabels(['Field Name', 'Data Type'])
        self.destination_table.setRowCount(len(destination_fields))

        for idx, field in enumerate(destination_fields):
            field_name_item = QtWidgets.QTableWidgetItem(field.name())
            data_type_item = QtWidgets.QTableWidgetItem(field.typeName())

            self.destination_table.setItem(idx, 0, field_name_item)
            self.destination_table.setItem(idx, 1, data_type_item)

        self.mapping_table.setColumnCount(3)
        self.mapping_table.setHorizontalHeaderLabels(['Source Field', 'Transformation', 'Destination Field'])
        self.mapping_table.setRowCount(0)
        self.populate_mapping_table()
        self.refresh_table_colors()

    def populate_mapping_table(self):
        for i in range(self.source_table.rowCount()):
            source_field = self.source_table.item(i, 0).text()
            for j in range(self.destination_table.rowCount()):
                destination_field = self.destination_table.item(j, 0).text()
                if source_field == destination_field:
                    self.mapping_table.insertRow(self.mapping_table.rowCount())
                    self.mapping_table.setItem(self.mapping_table.rowCount() - 1, 0, QtWidgets.QTableWidgetItem(source_field))
                    self.mapping_table.setItem(self.mapping_table.rowCount() - 1, 1, QtWidgets.QTableWidgetItem(""))  # empty transformation
                    self.mapping_table.setItem(self.mapping_table.rowCount() - 1, 2, QtWidgets.QTableWidgetItem(destination_field))

    def refresh_table_colors(self):
        for i in range(self.mapping_table.rowCount()):
            source_field_item = self.mapping_table.item(i, 0)
            destination_field_item = self.mapping_table.item(i, 2)

            # Check if item exists in mapping_table
            if source_field_item is not None:
                source_field_count = sum(1 for k in range(self.mapping_table.rowCount())
                                         if self.mapping_table.item(k, 0) is not None and 
                                         self.mapping_table.item(k, 0).text() == source_field_item.text())
                for j in range(self.source_table.rowCount()):
                    if self.source_table.item(j, 0).text() == source_field_item.text():
                        for col in range(self.source_table.columnCount()):
                            self.source_table.item(j, col).setBackground(QtGui.QColor(0, 255, 0, 50))  # Green
                        if source_field_count > 1:
                            bold_font = QtGui.QFont()
                            bold_font.setBold(True)
                            self.source_table.item(j, 0).setFont(bold_font)

            if destination_field_item is not None:
                for j in range(self.destination_table.rowCount()):
                    if self.destination_table.item(j, 0).text() == destination_field_item.text():
                        for col in range(self.destination_table.columnCount()):
                            self.destination_table.item(j, col).setBackground(QtGui.QColor(0, 255, 0, 50))  # Green

            if source_field_item is not None and destination_field_item is not None:
                source_data_type = self.get_field_data_type(source_field_item.text(), self.source_table)
                destination_data_type = self.get_field_data_type(destination_field_item.text(), self.destination_table)
                if source_data_type == destination_data_type:
                    self.mapping_table.setRowColor(i, QtGui.QColor(0, 255, 0, 50))  # Green
                else:
                    self.mapping_table.setRowColor(i, QtGui.QColor(255, 0, 0, 50))  # Red

    
    def get_field_data_type(self, field_name, table):
        for row in range(table.rowCount()):
            if table.item(row, 0).text() == field_name:
                return table.item(row, 1).text()
        return None

    def remove_mapping_row(self):
        currentRow = self.mapping_table.currentRow()
        if currentRow != -1:
            self.mapping_table.removeRow(currentRow)
            self.refresh_table_colors()

    def open_expression_dialog(self, row, column):
        if column == 1:  # Only handle clicks on the Transformation column
            item = self.mapping_table.item(row, column)
            source_field_name = self.mapping_table.item(row, column-1)
            source_layer = next((layer for layer in QgsProject.instance().mapLayers().values()
                                if layer.name() == self.source_layer_name), None)
        # Get the current expression
        current_expression = None
        if item:
            current_expression = item.text()

        dialog = ExpressionDialog(source_field_name, source_layer, current_expression, self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            item.setText(dialog.getExpression())


class ExpressionDialog(QtWidgets.QDialog):
    """
    This class represents the expression dialog that is opened when a row in the mapping table is double-clicked
    """

    def __init__(self, field_name, layer, current_expression, parent=None):
        super(ExpressionDialog, self).__init__(parent)

        self.field_name_item = field_name
        self.layer = layer

        # Create layout
        layout = QtWidgets.QVBoxLayout(self)

        # Create the expression input field with QgsExpressionBuilderWidget
        self.expressionBuilder = QgsExpressionBuilderWidget(self)
        self.expressionBuilder.setLayer(self.layer)

        # Set the current expression
        if current_expression:
            self.expressionBuilder.setExpressionText(current_expression)

        layout.addWidget(self.expressionBuilder)

        # Create horizontal layout for the buttons
        button_layout = QtWidgets.QHBoxLayout()

        # Create the source field name button
        self.btnFieldName = QtWidgets.QPushButton('Insert Field Name', self)
        self.btnFieldName.clicked.connect(self.insert_field_name)
        button_layout.addWidget(self.btnFieldName)

        # Create the layer name button
        self.btnLayerName = QtWidgets.QPushButton('Insert Layer Name', self)
        self.btnLayerName.clicked.connect(self.insert_layer_name)
        button_layout.addWidget(self.btnLayerName)

        # Add the horizontal layout to the main vertical layout
        layout.addLayout(button_layout)

        # Create the validate button
        self.btnValidate = QtWidgets.QPushButton('Validate', self)
        self.btnValidate.clicked.connect(self.validate_expression)
        layout.addWidget(self.btnValidate)

        # Create the OK button
        self.btnOK = QtWidgets.QPushButton('OK', self)
        self.btnOK.clicked.connect(self.accept)
        self.btnOK.setEnabled(False)  # Initially disabled
        layout.addWidget(self.btnOK)

        # Create the validation result label
        self.lblValidationResult = QtWidgets.QLabel(self)
        layout.addWidget(self.lblValidationResult)

        # Final setup for the dialog
        self.setLayout(layout)
        self.setWindowTitle('Enter Expression')

    def insert_field_name(self):
        # Get current text from the expression builder
        current_text = self.expressionBuilder.expressionText()

        field_name_item = self.field_name_item
        if field_name_item is not None:  # Check if item is not None to prevent AttributeError
            field_name = field_name_item.text()

            # Append the field name to the current text
            new_text = current_text + field_name

            # Set the new text in the expression builder
            self.expressionBuilder.setExpressionText(new_text)

    def insert_layer_name(self):
        # Get current text from the expression builder
        current_text = self.expressionBuilder.expressionText()

        # Append the layer name to the current text
        new_text = current_text + self.layer.name()

        # Set the new text in the expression builder
        self.expressionBuilder.setExpressionText(new_text)

    def validate_expression(self):
        expression = self.expressionBuilder.expressionText()

        exp = QgsExpression(expression)

        context = QgsExpressionContext()
        context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(self.layer))

        if exp.hasParserError():
            self.lblValidationResult.setText('Invalid expression: ' + exp.parserErrorString())
            self.btnOK.setEnabled(False)
        elif not exp.prepare(context):
            self.lblValidationResult.setText('Invalid expression: ' + exp.evalErrorString())
            self.btnOK.setEnabled(False)
        else:
            self.lblValidationResult.setText('Valid expression')
            self.btnOK.setEnabled(True)  # Enable OK button if expression is valid

    def getExpression(self):
        # Return the current expression
        return self.expressionBuilder.expressionText()
