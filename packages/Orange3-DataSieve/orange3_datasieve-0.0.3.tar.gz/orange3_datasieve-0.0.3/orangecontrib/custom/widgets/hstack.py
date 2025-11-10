import numpy as np
import pandas as pd
import traceback

from Orange.data import Table, Domain, ContinuousVariable, StringVariable, TimeVariable
from Orange.data.pandas_compat import table_to_frame
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import Input, Output, OWWidget, Msg


class OWHStack(OWWidget):
    """Horizontally stack multiple input tables with matching or padded rows."""

    name = "HStack"
    description = (
        "Horizontally stack multiple tables (concatenate columns side-by-side)."
    )
    icon = "icons/hstack.svg"
    category = "Orange3-DataSieve"
    priority = 10

    class Inputs:
        data = Input("Multiple Tables", Table, multiple=True)

    class Outputs:
        data = Output("Horizontally Stacked Tables", Table)

    class Error(OWWidget.Error):
        row_mismatch = Msg(
            "Input tables have different number of rows (padding not enabled)."
        )

    allow_padding: bool = Setting(False)

    want_main_area = False
    resizing_enabled = True

    def __init__(self):
        super().__init__()
        self.input_tables_dict = {}
        self.input_tables = []

        self.resize(250, 150)
        self._setup_ui()

    def _setup_ui(self):
        box = gui.widgetBox(self.controlArea, "Parameters")
        top_box = gui.hBox(box)
        gui.checkBox(top_box, self, "allow_padding", label="Allow padding")
        gui.button(top_box, self, "Apply", callback=self._process)

        self.info_box = gui.widgetBox(self.controlArea, "Info")
        self.info_label = gui.widgetLabel(self.info_box, "No data loaded")

    @Inputs.data
    def set_data(self, data: Table, id=None):
        """Handle multiple input tables."""
        if data is not None:
            self.input_tables_dict[id] = data
        else:
            self.input_tables_dict.pop(id, None)

        self.input_tables = [
            t for t in self.input_tables_dict.values() if t is not None
        ]

        self.info_label.setText(
            f"Loaded {len(self.input_tables)} tables"
            if self.input_tables
            else "No data loaded"
        )
        self.clear_messages()

        if len(self.input_tables) >= 2:
            self._process()
        else:
            self.Outputs.data.send(None)

    def _process(self):
        """Process and horizontally stack the input tables."""
        if not self.input_tables:
            self.Outputs.data.send(None)
            return

        try:
            dfs = [table_to_frame(t, include_metas=True) for t in self.input_tables]
            row_counts = [len(df) for df in dfs]

            if len(set(row_counts)) != 1 and not self.allow_padding:
                self.Error.row_mismatch()
                self.Outputs.data.send(None)
                return

            combined_df = pd.concat(dfs, axis=1, ignore_index=False)
            self.Outputs.data.send(self._to_orange_table(combined_df))
            self.Error.row_mismatch.clear()

        except Exception:
            traceback.print_exc()
            self.Outputs.data.send(None)

    def _to_orange_table(self, df: pd.DataFrame) -> Table:
        df.columns = self._make_unique_column_names(df.columns)

        attrs, metas = [], []
        x_data, m_data = [], []

        for col in df.columns:
            data = df[col]
            if pd.api.types.is_numeric_dtype(data):
                attrs.append(ContinuousVariable(col))
                x_data.append(data.to_numpy(dtype=float))
            elif pd.api.types.is_datetime64_any_dtype(data):
                metas.append(TimeVariable(col))
                m_data.append(data.astype("int64") / 1e9)
            else:
                metas.append(StringVariable(col))
                m_data.append(data.astype(str).to_numpy())

        X = np.column_stack(x_data) if x_data else np.empty((len(df), 0))
        M = np.column_stack(m_data) if m_data else None
        domain = Domain(attrs, metas)
        return Table.from_numpy(domain, X, metas=M)

    def _make_unique_column_names(self, columns):
        seen, unique = {}, []
        for col in columns:
            base = str(col)
            count = seen.get(base, 0)
            new_col = base if count == 0 else f"{base}_{count}"
            while new_col in unique:
                count += 1
                new_col = f"{base}_{count}"
            seen[base] = count + 1
            unique.append(new_col)
        return unique

    def send_report(self):
        self.report_items(
            [
                ("Allow padding", "Yes" if self.allow_padding else "No"),
                ("# of tables", len(self.input_tables)),
            ]
        )
