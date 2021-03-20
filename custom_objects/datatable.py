import tkinter as tk
from tkinter import ttk
import pandas as pd


class DataTable(ttk.Treeview):
    def __init__(self, parent, axis=None):
        super().__init__(parent)
        self.stored_dataframe = pd.DataFrame()

        if axis == "both":
            scroll_Y = tk.Scrollbar(self, orient="vertical", command=self.yview)
            scroll_X = tk.Scrollbar(self, orient="horizontal", command=self.xview)
            self.configure(yscrollcommand=scroll_Y.set, xscrollcommand=scroll_X.set)
            scroll_Y.pack(side="right", fill="y")
            scroll_X.pack(side="bottom", fill="x")
        elif axis == "x":
            scroll_X = tk.Scrollbar(self, orient="horizontal", command=self.xview)
            self.configure(xscrollcommand=scroll_X.set)
            scroll_X.pack(side="bottom", fill="x")
        elif axis == "y":
            scroll_Y = tk.Scrollbar(self, orient="vertical", command=self.yview)
            self.configure(yscrollcommand=scroll_Y.set)
            scroll_Y.pack(side="right", fill="y")
        else:
            pass

    def set_datatable_from_dataframe(self, dataframe):
        self.stored_dataframe = dataframe
        self._draw_table(dataframe)

    def set_datatable_from_object(self, objects):
        if not isinstance(objects, list):
            objects = [objects]
        df = pd.DataFrame([vars(header) for header in objects])
        self.stored_dataframe = df
        self._draw_table(df)

    def _draw_table(self, dataframe):
        self.delete(*self.get_children())
        columns = list(dataframe.columns)
        self.__setitem__("column", columns)
        self.__setitem__("show", "headings")

        for col in columns:
            self.heading(col, text=col)

        df_rows = dataframe.to_numpy().tolist()
        for row in df_rows:
            self.insert("", "end", values=row)
        return None

    def find_value(self, pairs):
        # pairs is a dictionary
        new_df = self.stored_dataframe
        for col, value in pairs.items():
            query_string = f"{col}.str.contains('{value}')"
            new_df = new_df.query(query_string, engine="python")
        self._draw_table(new_df)

    def reset_table(self):
        self._draw_table(self.stored_dataframe)
