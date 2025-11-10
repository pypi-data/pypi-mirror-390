import os
import re
import json
import pandas as pd
import numpy as np
from PyQt5.QtCore import QObject, pyqtSlot, QUrl, Qt
from PyQt5.QtWidgets import QLineEdit, QLabel, QComboBox, QRadioButton, QButtonGroup
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from Orange.widgets.widget import Input, Output
from Orange.widgets import widget, gui
from Orange.widgets.settings import Setting
from Orange.data import Table, Domain, ContinuousVariable, StringVariable


class Bridge(QObject):
    def __init__(self, view, parent_widget):
        super().__init__()
        self.view = view
        self.parent_widget = parent_widget

    def sendDataToJs(self, column_name, column_data, match):
        print("column_data")
        print(column_data)
        print("match")
        print("match")
        js_code = f"initialize_regex_table({json.dumps(column_name)}, {json.dumps(column_data)}, {json.dumps(match)})"
        self.view.page().runJavaScript(js_code)

    @pyqtSlot()
    def closeWidget(self):
        print("Closing widget from JS")
        self.parent_widget.close()


class OWRegexExtractor(widget.OWWidget):
    name = "Regex_Extractor"
    description = "Extract regex matches from sample text."
    category = "Orange3-DataSieve"
    icon = "icons/regex.svg"
    priority = 10

    class Inputs:
        data = Input("Input Table", Table)

    class Outputs:
        processed_data = Output("Regex Tables", Table)

    regex_pattern = Setting("")
    new_column_name = Setting("Extracted")
    selected_column = Setting("")
    match_option = Setting(0)  # 0 = first occurrence, 1 = find all

    def __init__(self):
        super().__init__()

        self.matches = []
        self.input_data = None
        self.current_dataframe = None

        # --- Control Area ---
        param_box = gui.widgetBox(
            self.controlArea, "Regex Extraction Parameters", orientation="vertical"
        )
        self.controlArea.layout().setAlignment(Qt.AlignTop)

        # Regex input
        regex_label = QLabel("Regex Expression:")
        self.regex_lineedit = QLineEdit()
        self.regex_lineedit.setPlaceholderText(r"\d{2}/\d{2}/\d{4} e.g. 02/20/2024")
        self.regex_lineedit.setText(self.regex_pattern)
        self.regex_lineedit.textChanged.connect(self.on_regex_expression_change)
        param_box.layout().addWidget(regex_label)
        param_box.layout().addWidget(self.regex_lineedit)

        # Column dropdown
        col_box = gui.hBox(param_box)
        col_box.setMinimumWidth(200)
        gui.label(col_box, self, "Select Column:")
        self.column_dropdown = QComboBox()
        self.column_dropdown.addItems(["No data connected"])
        self.column_dropdown.activated.connect(self.on_selected_column_user_change)
        col_box.layout().addWidget(self.column_dropdown)

        # Match option radio buttons
        match_box = gui.widgetBox(param_box, "Match Options", orientation="vertical")
        self.match_button_group = QButtonGroup()
        self.first_occurrence_radio = QRadioButton("First occurrence")
        self.find_all_radio = QRadioButton("Find all")
        if self.match_option == 0:
            self.first_occurrence_radio.setChecked(True)
        else:
            self.find_all_radio.setChecked(True)
        self.match_button_group.addButton(self.first_occurrence_radio, 0)
        self.match_button_group.addButton(self.find_all_radio, 1)
        self.match_button_group.buttonClicked.connect(self.on_match_option_change)
        match_box.layout().addWidget(self.first_occurrence_radio)
        match_box.layout().addWidget(self.find_all_radio)

        # New column name input
        new_col_label = QLabel("New Column Name:")
        self.new_col_input = QLineEdit()
        self.new_col_input.setPlaceholderText("e.g. Extracted Date")
        self.new_col_input.setText(self.new_column_name)
        self.new_col_input.textChanged.connect(self.on_new_column_name_change)
        param_box.layout().addWidget(new_col_label)
        param_box.layout().addWidget(self.new_col_input)

        # --- Main Area (Web preview) ---
        self.web_view = QWebEngineView()
        self.mainArea.layout().addWidget(self.web_view)

        self.channel = QWebChannel()
        self.bridge = Bridge(self.web_view, self)
        self.channel.registerObject("bridge", self.bridge)
        self.web_view.page().setWebChannel(self.channel)

        html_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "web_UI",
            "regex_ui",
            "index.html",
        )
        self.web_view.setUrl(QUrl.fromLocalFile(html_path))
        self.web_view.setZoomFactor(1.5)
        self.web_view.loadFinished.connect(self.on_page_loaded)

    def update_column_dropdown(self, dataframe: pd.DataFrame):
        column_names = dataframe.columns.tolist()
        self.column_dropdown.blockSignals(True)
        self.column_dropdown.clear()
        if not column_names:
            self.column_dropdown.addItem("No data connected")
            self.selected_column = ""
            self.column_dropdown.blockSignals(False)
            return
        self.column_dropdown.addItems(column_names)
        self.column_dropdown.blockSignals(False)
        # Restore previous selection
        if self.selected_column in column_names:
            idx = column_names.index(self.selected_column)
            self.column_dropdown.setCurrentIndex(idx)
        else:
            self.column_dropdown.setCurrentIndex(0)
            self.selected_column = column_names[0]

    @Inputs.data
    def set_data(self, data, id=None):
        if data is None:
            self.input_data = None
            self.current_dataframe = None
            self.column_dropdown.blockSignals(True)
            self.column_dropdown.clear()
            self.column_dropdown.addItems(["No data connected"])
            self.column_dropdown.blockSignals(False)
            try:
                self.Outputs.processed_data.send(None)
            except Exception:
                pass
            return

        self.input_data = data
        self.current_dataframe = self.orange_table_to_dataframe(data)
        self.update_column_dropdown(self.current_dataframe)
        self.update_table_display()

    def on_page_loaded(self):
        print("Web page loaded.")

    def on_selected_column_user_change(self, index: int):
        new_value = self.column_dropdown.itemText(index)
        if new_value:
            self.selected_column = new_value
        if self.current_dataframe is not None:
            self.on_regex_expression_change(self.regex_pattern)

    def on_match_option_change(self, button):
        self.match_option = self.match_button_group.id(button)
        if self.current_dataframe is not None:
            self.on_regex_expression_change(self.regex_pattern)

    def on_new_column_name_change(self, text):
        self.new_column_name = text.strip() or "Extracted"
        if self.current_dataframe is not None:
            self.on_regex_expression_change(self.regex_pattern)

    def on_regex_expression_change(self, pattern):
        self.regex_pattern = pattern
        if (
            self.current_dataframe is not None
            and self.selected_column in self.current_dataframe.columns
        ):
            df = self.current_dataframe.copy()
            column_name = self.selected_column
        else:
            df = pd.DataFrame(
                {"Sample Data": ["abc123", "xyz456", "test789", "no match"]}
            )
            column_name = "Sample Data"

        rows_matches = []
        if pattern:
            for text in df[column_name].astype(str):
                try:
                    matches = [m.group(0) for m in re.finditer(pattern, text)]
                except re.error as e:
                    print("Regex error:", e)
                    matches = []
                rows_matches.append(matches)
        else:
            rows_matches = [[] for _ in range(len(df))]

        base_colname = self.new_column_name or "Extracted"

        if self.match_option == 0:
            df[base_colname] = [r[0] if r else "" for r in rows_matches]
            js_matches = [r[0] if r else "" for r in rows_matches]
        else:
            max_len = max((len(r) for r in rows_matches), default=0)
            for i in range(max_len):
                colname = f"{base_colname}({i+1})"
                df[colname] = [r[i] if i < len(r) else "" for r in rows_matches]
            js_matches = rows_matches

        # Send to JS
        try:
            self.bridge.sendDataToJs(
                column_name=column_name,
                column_data=df[column_name].astype(str).tolist(),
                match=js_matches,
            )
        except Exception as e:
            print("Error sending to JS:", e)

        # Convert to Orange table and send output
        try:
            orange_table = self.dataframe_to_orange_table(df)
            self.Outputs.processed_data.send(orange_table)
        except Exception as e:
            print("Error converting to Orange table:", e)
            try:
                self.Outputs.processed_data.send(None)
            except Exception:
                pass

    def update_table_display(self):
        if (
            self.current_dataframe is not None
            and self.selected_column in self.current_dataframe.columns
        ):
            self.on_regex_expression_change(self.regex_pattern)

    def dataframe_to_orange_table(self, df: pd.DataFrame) -> Table:
        df = df.copy()
        df.columns = self.make_unique_column_names(df.columns)
        attributes = []
        metas = []
        X_data = []
        metas_data = []
        for col in df.columns:
            col_data = df[col]
            if pd.api.types.is_numeric_dtype(col_data):
                attributes.append(ContinuousVariable(col))
                X_data.append(col_data.to_numpy(dtype=float))
            else:
                metas.append(StringVariable(col))
                metas_data.append(col_data.astype(str).to_numpy())
        X_matrix = np.column_stack(X_data) if X_data else np.empty((len(df), 0))
        metas_matrix = np.column_stack(metas_data) if metas_data else None
        domain = Domain(attributes=attributes, metas=metas)
        return Table.from_numpy(domain, X=X_matrix, metas=metas_matrix)

    def make_unique_column_names(self, columns):
        seen = {}
        unique_columns = []
        for col in columns:
            original_col = str(col)
            if original_col not in seen:
                seen[original_col] = 0
                unique_columns.append(original_col)
            else:
                seen[original_col] += 1
                unique_columns.append(f"{original_col}_{seen[original_col]}")
        return unique_columns

    def orange_table_to_dataframe(self, data: Table) -> pd.DataFrame:
        domain = data.domain
        attr_names = [var.name for var in domain.attributes]
        class_names = [var.name for var in domain.class_vars]
        meta_names = [var.name for var in domain.metas]
        X = data.X if data.X.size else np.empty((len(data), 0))
        Y = (
            data.Y.reshape(-1, len(class_names))
            if domain.class_vars
            else np.empty((len(data), 0))
        )
        M = data.metas if data.metas.size else np.empty((len(data), 0))
        full_array = (
            np.hstack([X, Y, M])
            if (X.size or Y.size or M.size)
            else np.empty((len(data), 0))
        )
        all_columns = attr_names + class_names + meta_names
        df = pd.DataFrame(full_array, columns=all_columns)
        return df
