OBJECTIVE:

The overall purpose of this plugin is to facilitate the mapping of fields from one layer to another, potentially with transformations, in a QGIS context.


SUMMARY:

Here's a summary of how the plugin works:

Initialization:
When the LayerAttributesDialog is instantiated, it takes two layer names as arguments - source_layer_name and destination_layer_name, from the layers selected in the Layers panel of the current QgsProject instance.
It then creates three tables: a source table, a destination table, and a mapping table.

Table Population:
The populate_tables method fetches the fields of both the source and destination layers from the mapLayers . It fills the source and destination tables with these field names and their data types.
It then attempts to automatically create a mapping between fields with the same name in the source and destination tables, using the populate_mapping_table method.

Drag and Drop Functionality:
The source and destination tables have been enabled for drag operations. The mapping table, on the other hand, only accepts drop operations. This means that you can drag rows from the source or destination tables and drop them onto the mapping table.

Mapping Table:
The mapping table contains three columns - Source Field, Transformation, and Destination Field. When a mapping row is double-clicked, it opens the ExpressionDialog.

Expression Dialog:
This dialog allows the user to enter and validate an expression.
This expression can include the name of the source field and the name of the layer, which are provided through buttons in the dialog.
Once the user has entered an expression and clicked the Validate button, the dialog checks whether the expression is valid.
If it is, the OK button is enabled, allowing the user to confirm their entry.

Row Deletion:
The Remove Mapping button allows the user to delete selected rows from the mapping table.

Color Indicators:
The refresh_table_colors method assigns colors to rows in the tables to provide visual feedback to the user.
If a source or a destination field is used in the mapping, its row is highlighted in the source or destination tables.
If the source and destination fields in a mapping have the same data type, the row in the mapping table is highlighted in green; if they do not, the row is highlighted in red.
