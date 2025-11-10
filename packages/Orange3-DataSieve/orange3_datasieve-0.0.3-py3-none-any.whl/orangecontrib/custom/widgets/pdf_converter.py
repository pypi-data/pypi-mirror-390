import os
import json
import base64
from io import BytesIO
import requests
import camelot
import numpy as np
import pandas as pd
from pypdfium2 import PdfDocument
from datetime import datetime
from PyQt5.QtCore import QUrl, QObject, pyqtSlot
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QFileDialog, QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView
from Orange.widgets.gui import ProgressBar
from Orange.widgets.widget import OWWidget, Output, Msg
from Orange.widgets.settings import Setting
from Orange.data import Table, Domain, StringVariable, ContinuousVariable, TimeVariable


def _get_expiration_date():
    # Use the "Publish to web" CSV link from Google Sheets
    csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQxFzdr6gkoUjtP3fbQ2S0lLRgikHwx7a5NyCYBnAtg2yXubdgiF8Rpdhd1WzH29zga16s8M1YGblgJ/pub?output=csv"
    try:
        resp = requests.get(csv_url)
        resp.raise_for_status()
        # Assume first line contains date
        first_line = resp.text.strip().splitlines()[0].split(",")[0]
        # Try parsing ISO then fallback to DD/MM/YYYY
        for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                return datetime.strptime(first_line, fmt)
            except ValueError:
                continue
        print(f"Unknown date format: {first_line}")
        return None
    except Exception as e:
        print(f"Failed to fetch expiry date from sheet: {e}")
        return None


class Bridge(QObject):
    def __init__(self, view, parent_widget):
        super().__init__()
        self.view = view
        self.parent_widget = parent_widget
        self.pdf_images = []
        self.current_page = 0
        self.dpi = 100

    @pyqtSlot(str)
    def loadPdf(self, pdf_path):
        # Force the user to update to newer version
        expiration_date = _get_expiration_date()
        if datetime.now() > expiration_date:
            print("This PDF loader has expired and cannot be used.")
            return
        try:
            self.parent_widget.file_path = pdf_path

            pdf = PdfDocument(pdf_path)
            self.pdf_images = []
            scale_factor = self.dpi / 72.0
            for page in pdf:
                bitmap = page.render(scale=scale_factor)
                pil_image = bitmap.to_pil()
                buffer = BytesIO()
                pil_image.save(buffer, format="PNG")
                base64_img = base64.b64encode(buffer.getvalue()).decode("utf-8")
                self.pdf_images.append(f"data:image/png;base64,{base64_img}")
            self.current_page = 0
            self.parent_widget.steps = len(self.pdf_images)
            self.sendCurrentPage()
        except Exception as e:
            print(f"Failed to load PDF: {e}")

    @pyqtSlot()
    def nextPage(self):
        if self.current_page + 1 < len(self.pdf_images):
            self.current_page += 1
            self.sendCurrentPage()

    @pyqtSlot()
    def prevPage(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.sendCurrentPage()

    @pyqtSlot()
    def sendCurrentPage(self):
        if 0 <= self.current_page < len(self.pdf_images):
            img = self.pdf_images[self.current_page]
            self.view.page().runJavaScript(
                f"displayPdfImage('{img}', {self.current_page + 1}, {len(self.pdf_images)}, '{self.parent_widget.file_path}')"
            )

    def restoreHtmlDelimiters(self, delimiters):
        javascript_code = f"restoreHtmlDelimiters({delimiters})"
        print(javascript_code)
        self.view.page().runJavaScript(javascript_code)

    def restoreHtmlTableArea(self, table_area):
        javascript_code = f"restoreHtmlTableArea({table_area})"
        print(javascript_code)
        self.view.page().runJavaScript(javascript_code)

    def restoreBreakLines(self, value):
        javascript_code = f"restoreBreakLines({value})"
        self.view.page().runJavaScript(javascript_code)

    @pyqtSlot(str)
    def saveHtmlState(self, html_delimiters):
        self.parent_widget.html_delimiters = html_delimiters
        print("HTML delimiters saved")

    @pyqtSlot()
    def openFileDialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.view, "Open PDF File", "", "PDF Files (*.pdf)"
        )
        if file_path:
            self.loadPdf(file_path)

    @pyqtSlot(str)
    def getCoordinatesFromJs(self, data):
        data = json.loads(data)
        table_area = ", ".join(data["tableArea"])
        delimiters = ", ".join(data["delimiters"])
        html_delimiters = data["htmlDelimiters"]
        html_table_area = data["htmlTableArea"]
        break_lines = data["breakLines"]
        # print(
        #     f"Python received the following left and top values from JS when the user clicked OK: {html_table_area}"
        # )

        self.parent_widget.table_area = table_area
        self.parent_widget.delimiters = delimiters
        self.parent_widget.html_delimiters = html_delimiters
        self.parent_widget.html_table_area = html_table_area
        self.parent_widget.break_lines = break_lines

        self.closeWidget()
        self.parent_widget.process_pdf_with_coordinates(
            self.parent_widget.file_path,
            table_area,
            delimiters,
            break_lines=break_lines,
        )

    @pyqtSlot()
    def closeWidget(self):
        self.parent_widget.close()


class PdfConverter(OWWidget):
    name = "PDF_Converter"
    description = (
        "This is a PDF Table Extractor widget that lets you interactively extract tables "
        "from PDF documents. You can load PDFs, visually select table areas by drawing boundaries, "
        "set column delimiters."
    )
    category = "Orange3-DataSieve"
    icon = "icons/pdf_converter.svg"
    want_main_area = True
    want_control_area = False
    priority = 1

    class Outputs:
        data = Output("Data", Table)

    file_path: str = Setting("", schema_only=True)
    table_area: str = Setting("", schema_only=True)
    delimiters: str = Setting("", schema_only=True)
    break_lines: int = Setting(1, schema_only=True)
    html_delimiters: list = Setting([], schema_only=True)
    html_table_area: dict = Setting({}, schema_only=True)

    class Error(OWWidget.Error):
        invalid_path = Msg("File path is invalid, File was not found.")
        processing_failed = Msg("Processing failed: {}")
        path_is_not_file = Msg("File path is not a PDF file.")

    class Warning(OWWidget.Warning):
        empty_input = Msg("No input data")
        partial_data = Msg("Some data is missing")

    class Information(OWWidget.Information):
        data_loaded = Msg("Data successfully loaded")
        processing_complete = Msg("Processing complete")

    def __init__(self):
        super().__init__()
        self.extracted_tables = []
        self.init_ui()
        self.steps = 0
        self.pb = None
        self.counter = 0

        if (
            self.file_path != ""
            and os.path.exists(self.file_path)
            and os.path.isfile(self.file_path)
            and self.table_area != []
        ):
            self.process_pdf_with_coordinates(
                self.file_path, self.table_area, self.delimiters
            )
        elif self.file_path != "" and not os.path.exists(self.file_path):
            self.Error.invalid_path()
        elif self.file_path != "" and not os.path.isfile(self.file_path):
            self.Error.path_is_not_file()

    def init_ui(self):
        layout = QVBoxLayout()
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        self.setup_webengine()
        self.mainArea.layout().addWidget(self.view)

    def setup_webengine(self):
        self.view = QWebEngineView()
        self.view.setZoomFactor(0.8)

        self.channel = QWebChannel()
        self.bridge = Bridge(self.view, self)

        self.channel.registerObject("bridge", self.bridge)
        self.view.page().setWebChannel(self.channel)

        html_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "web_UI",
            "pdf_converter_gui",
            "index.html",
        )
        self.view.setUrl(QUrl.fromLocalFile(html_path))

        self.view.loadFinished.connect(self.on_page_loaded)

    def on_page_loaded(self):
        print("Page loaded, checking for saved HTML delimiters and table area ...")

        if self.html_delimiters:
            print(f"Restoring saved HTML delimiters: {self.html_delimiters}")
            self.bridge.restoreHtmlDelimiters(self.html_delimiters)
        else:
            print("No saved HTML state found")

        if self.html_table_area:
            print(f"Restoring saved HTML table area: {self.html_table_area}")
            self.bridge.restoreHtmlTableArea(self.html_table_area)
        else:
            print("No saved HTML table area found")

        self.bridge.restoreBreakLines(self.break_lines)

        if self.file_path and os.path.exists(self.file_path):
            print(f"Loading saved PDF: {self.file_path}")
            self.bridge.loadPdf(self.file_path)

    def process_pdf_with_coordinates(
        self,
        file_path,
        table_area,
        delimiters,
        pages="all",
        flavor="stream",
        break_lines=True,
    ):
        self.setBlocking(True)
        if file_path is None:
            self.Error.invalid_path()
            self.Information.processing_complete.clear()
            self.setBlocking(False)
            return

        try:
            page_numbers = list(range(1, self.steps + 1))
            self.pb = ProgressBar(self, iterations=self.steps)
            self.counter = 0
            all_dataframes = []

            print(
                f"Reading PDF: {file_path} (Pages: {pages}, Flavor: {flavor}), Table area: {table_area}, Delimiters: {delimiters}"
            )
            text_split = break_lines == 1

            for i, page_num in enumerate(page_numbers):
                print(f"Processing page {page_num}...")

                tables = camelot.read_pdf(
                    file_path,
                    pages=str(page_num),
                    flavor=flavor,
                    table_areas=[table_area],
                    columns=[delimiters],
                    split_text=text_split,
                )

                if self.counter < self.steps:
                    self.pb.advance()
                    self.counter += 1

                QApplication.processEvents()  # allow progress bar to update

                for table in tables:
                    df_temp = table.df
                    df_temp["page"] = int(page_num)
                    all_dataframes.append(df_temp)

            self.pb.finish()
            self.setBlocking(False)
            concat_all_dataframes = pd.concat(all_dataframes, ignore_index=True)
            concat_all_dataframes = concat_all_dataframes.astype(str)

            table = self.dataframe_to_orange_table(concat_all_dataframes)
            self.Outputs.data.send(table)
            self.Error.clear()

            print(f"Total tables extracted: {len(tables)}")
            if len(tables) == 0:
                print("No tables found.")
                return

            self.status_label.setText(f"Processed: {os.path.basename(file_path)}")

        except Exception as e:
            print(f"Error: {e}")
            self.Information.processing_complete.clear()
            self.Error.processing_failed(str(e))
            self.setBlocking(False)

    def dataframe_to_orange_table(self, df: pd.DataFrame) -> Table:
        # Handle duplicate column names
        df.columns = self.make_unique_column_names(df.columns)

        attributes = []
        metas = []
        X_data = []
        metas_data = []

        for col in df.columns:
            col_data = df[col]
            dtype = col_data.dtype

            if col == "page":
                # Store page column as number -< attributes
                attributes.append(ContinuousVariable(col))
                X_data.append(col_data.to_numpy(dtype=int))

            elif pd.api.types.is_numeric_dtype(dtype):
                # Numeric columns -> attributes
                attributes.append(ContinuousVariable(col))
                X_data.append(col_data.to_numpy(dtype=float))

            elif pd.api.types.is_datetime64_any_dtype(dtype):
                # Datetime columns -> time variables (as metas)
                metas.append(TimeVariable(col))
                # Convert datetime64 to float timestamps (Orange expects float seconds since epoch)
                metas_data.append(col_data.astype("int64") / 1e9)

            else:
                # Strings and others -> metas
                metas.append(StringVariable(col))
                metas_data.append(col_data.astype(str).to_numpy())

        # Build matrices
        X_matrix = np.column_stack(X_data) if X_data else np.empty((len(df), 0))
        metas_matrix = np.column_stack(metas_data) if metas_data else None

        # Build domain
        domain = Domain(attributes=attributes, metas=metas)

        return Table.from_numpy(domain, X=X_matrix, metas=metas_matrix)

    def make_unique_column_names(self, columns):
        """Make column names unique by appending suffixes to duplicates"""
        seen = {}
        unique_columns = []

        for col in columns:
            original_col = str(col)
            if original_col not in seen:
                seen[original_col] = 0
                unique_columns.append(original_col)
            else:
                seen[original_col] += 1
                unique_name = f"{original_col}_{seen[original_col]}"
                unique_columns.append(unique_name)

        return unique_columns

    def onDeleteWidget(self):
        if hasattr(self, "bridge") and self.bridge:
            self.bridge.pdf_images = []
        super().onDeleteWidget()
