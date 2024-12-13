import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QPushButton,
    QTextEdit,
    QMessageBox,
    QFrame,
    QSizePolicy,
    QScrollArea,
    QSpacerItem
)
from PyQt5.QtCore import Qt
import json
from collections import OrderedDict


class SchemaBuilderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Schema Builder")
        self.properties = []
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignTop)

        # Scroll area to contain property entries
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.property_container = QFrame()
        self.property_container_layout = QVBoxLayout(self.property_container)
        self.property_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        scroll_area.setWidget(self.property_container)
        main_layout.addWidget(scroll_area)

        # Button container
        button_layout = QHBoxLayout()
        self.add_property_button = QPushButton("Add Property")
        self.add_property_button.clicked.connect(self.add_property_ui)
        button_layout.addWidget(self.add_property_button)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_ui)
        button_layout.addWidget(self.reset_button)

        self.generate_button = QPushButton("Save")
        self.generate_button.clicked.connect(self.generate_json_schema)
        button_layout.addWidget(self.generate_button)
        main_layout.addLayout(button_layout)

        # JSON Output
        self.json_output_text = QTextEdit()
        main_layout.addWidget(self.json_output_text)


    def add_property_ui(self, parent_frame=None, parent_prop=None, level=0):
      property_frame = QFrame()
      property_frame.setFrameStyle(QFrame.Panel | QFrame.Sunken)
      property_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
      property_layout = QHBoxLayout(property_frame)
      property_layout.setContentsMargins(20 * level, 5, 5, 5)
      
      # Add spacer for indentation
      spacer = QSpacerItem(20 * level, 1, QSizePolicy.Fixed, QSizePolicy.Minimum)
      property_layout.addItem(spacer)

      property_name_label = QLabel("Property")
      property_layout.addWidget(property_name_label)
      property_name_entry = QLineEdit()
      property_layout.addWidget(property_name_entry)

      type_label = QLabel("Type")
      property_layout.addWidget(type_label)
      type_combobox = QComboBox()
      type_combobox.addItems(["string", "object", "number", "enum"])
      property_layout.addWidget(type_combobox)
      type_combobox.setCurrentText("string")

      array_checkbox = QCheckBox("[]")
      property_layout.addWidget(array_checkbox)

      add_nested_button = QPushButton("Add Nested")
      add_nested_button.clicked.connect(lambda: self.add_nested_property_ui(property_frame, property_name_entry.text(), type_combobox.currentText(), level + 1))
      add_nested_button.setVisible(False)  # Initially hidden
      property_layout.addWidget(add_nested_button)

      delete_button = QPushButton("🗑")
      delete_button.clicked.connect(lambda: self.delete_property_ui(property_frame, parent_frame))
      property_layout.addWidget(delete_button)

      # Correct way to add to layout
      if parent_frame:
           parent_frame.layout().addWidget(property_frame) # add nested to the parent
      else:
          self.property_container_layout.addWidget(property_frame) # add parent to the main layout
          
      # Keep the object in properties, if not nested properties
      if not parent_prop:
          self.properties.append({
              "frame": property_frame,
              "name_entry": property_name_entry,
              "type_combobox": type_combobox,
              "array_checkbox": array_checkbox,
              "add_nested_button": add_nested_button,
              "nested_props": [],
              "parent_prop": parent_prop,
              "level": level
          })
      else:
          parent_prop["nested_props"].append({
              "frame": property_frame,
              "name_entry": property_name_entry,
              "type_combobox": type_combobox,
              "array_checkbox": array_checkbox,
              "add_nested_button": add_nested_button,
              "nested_props": [],
              "parent_prop": parent_prop,
              "level": level
          })
      
      type_combobox.currentTextChanged.connect(lambda text, btn=add_nested_button: btn.setVisible(text == "object"))


    def add_nested_property_ui(self, parent_frame, parent_name, parent_type, level):
        if parent_type != "object":
            QMessageBox.critical(self, "Error", "Nested properties can only be added to 'object' types.")
            return
        # find the correct parent on properties
        parent_prop = None
        if self.properties:
            for prop in self.properties:
                if prop["frame"] == parent_frame:
                    parent_prop = prop
        else:
             for prop_nested in parent_frame["nested_props"]:
                 if prop_nested["frame"] == parent_frame:
                    parent_prop = prop_nested
        if not parent_prop:
             QMessageBox.critical(self, "Error", "Parent property not found.")
             return
        self.add_property_ui(parent_frame,parent_prop,level)

    def delete_property_ui(self, property_frame, parent_frame):
       if not parent_frame:
            for prop in self.properties:
                if prop["frame"] == property_frame:
                    self.property_container_layout.removeWidget(property_frame)
                    property_frame.deleteLater()
                    self.properties.remove(prop)
                    break
       else:
           for prop_nested in parent_frame["nested_props"]:
                if prop_nested["frame"] == property_frame:
                    parent_frame.layout().removeWidget(property_frame)
                    property_frame.deleteLater()
                    parent_frame["nested_props"].remove(prop_nested)
                    break
                   
    def reset_ui(self):
        self.clear_properties(self.properties)
        self.properties = []
        self.json_output_text.clear()

    def clear_properties(self, prop_list):
        for prop in prop_list:
          if prop["nested_props"]:
              self.clear_properties(prop["nested_props"])
          prop["frame"].deleteLater()
        prop_list.clear()


    def generate_json_schema(self):
        try:
            schema = self._build_schema(self.properties)
            json_schema = json.dumps(schema, indent=4)
            self.json_output_text.clear()
            self.json_output_text.insertPlainText(json_schema)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def _build_schema(self, prop_list):
        schema = OrderedDict()
        schema["type"] = "object"
        schema["properties"] = OrderedDict()

        for prop in prop_list:
            prop_name = prop["name_entry"].text().strip()
            prop_type = prop["type_combobox"].currentText()
            is_array = prop["array_checkbox"].isChecked()

            if not prop_name:
                QMessageBox.critical(self, "Error", "Property name cannot be empty.")
                return

            if prop_name in schema["properties"]:
                QMessageBox.critical(
                    self, "Error", f"Property name '{prop_name}' already exists."
                )
                return

            if prop_type == "object" and prop["nested_props"]:
                schema["properties"][prop_name] = self._build_schema(prop["nested_props"])
            elif is_array:
              schema["properties"][prop_name] = {
                   "type": "array",
                    "items": {"type": prop_type}
                }
            else:
                schema["properties"][prop_name] = {"type": prop_type}

        return schema


if __name__ == "__main__":
    app = QApplication(sys.argv)
    schema_builder = SchemaBuilderApp()
    schema_builder.show()
    sys.exit(app.exec_())