"""
My first application
"""

import toga
import sqlite3
import calendar
from datetime import datetime, time
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER

from .ui import init_edit_ui, init_main_ui

class HelloWorld(toga.App):
    def startup(self):
        self.init_db()
        self.today = calendar.day_name[datetime.now().weekday()] 
        self.main_window = toga.MainWindow(title=self.formal_name)
        init_main_ui(self) 
        init_edit_ui(self)
        self.set_main_ui()
        self.main_window.show()
        self.load_routine()

    def select_view_input_handler(self, widget):
        selection_value = self.select_view_input.value.name
        print(selection_value)
        self.routine_table.data = self.get_routine_data()

    def load_routine(self):
        self.routine_table.data = self.get_routine_data()

    def get_routine_data(self):
        data = [
            {**entry, "time": entry["start"] + "-" + entry["end"]} for entry in self.get_all_entry()
            if self.select_view_input.value.name == "All" or entry["day"] == self.select_view_input.value.name
        ]
        return data

    def get_all_entry(self):
        query = "SELECT * FROM routines"
        self.cursor.execute(query)
        result = [
            {"id": row[0], "subject": row[1], "day": row[2], "start": str(row[3][:5]), "end": str(row[4][:5]) }
            for row in self.cursor.fetchall()
        ]
        return result

    def clear_all(self, widget):
        query = "DELETE FROM routines"
        self.cursor.execute(query)
        self.conn.commit()
        self.routine_table.data = self.get_routine_data()

    def view_todays_routine(self, widget):
        index = 0
        for i, selection in enumerate(self.select_view_input.items):
            if selection.name == self.today:
                index = i
                break
        self.select_view_input.value = self.select_view_input.items[index]

    def add_entry(self, widget):
        value = self.get_input()
        if value["start"] >= value["end"]:
            self.main_window.info_dialog("Error!","Invalid time range")
            return
        value["start"] = value["start"].isoformat()
        value["end"] = value["end"].isoformat()
        if not self.is_valid_time(value["day"], value["start"], value["end"]):
            self.main_window.info_dialog("Error!","An entry already exists for that time range.")
            return
        if value["subject"] == "": self.main_window.info_dialog("Error!", "Subject can't be empty")

        self.insert_into_db(value) 
        self.clear_input()
        value["id"] = self.cursor.lastrowid
        value["start"] = str(value["start"][:5])
        value["end"] = str(value["end"][:5])
        value["time"] = value["start"] + "-" + value["end"]
        if self.select_view_input.value.name == "All" or self.select_view_input.value.name == value["day"]:
            self.routine_table.data.append(value)

    def init_db(self):
        db_path = toga.App.app.paths.app / 'resources/routines.db'
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS routines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                day TEXT NOT NULL,
                start TIME NOT NULL,
                end TIME NOT NULL
            )
        ''')
        self.conn.commit()

    def insert_into_db(self, entry):
        query = '''
            INSERT INTO routines (subject, day, start, end)
            values (?, ?, ?, ?)
        '''
        values = (entry["subject"], entry["day"], entry["start"], entry["end"])
        self.cursor.execute(query,values)
        self.conn.commit()

    def is_valid_time_with_id(self, day, start, end, id):
        query = """
            SELECT * FROM routines
            WHERE
                day = ? AND
                id != ? AND
                (
                    (? >= start AND ? <= end) OR
                    (? >= start AND ? <= end)
                )
            """
        self.cursor.execute(query, (day, id, start, start, end, end))
        return len([r for r in self.cursor.fetchall()]) == 0

    def is_valid_time(self, day, start, end):
        query = """
            SELECT * FROM routines
            WHERE
                day = ? AND
                (
                    (? >= start AND ? <= end) OR
                    (? >= start AND ? <= end)
                )
            """
        self.cursor.execute(query, (day, start, start, end, end))
        return len([r for r in self.cursor.fetchall()]) == 0

    def get_input(self):
        return {
            "subject": self.subject_input.value.strip(),
            "day": self.day_input.value,
            "start": self.start_time_input.value,
            "end": self.end_time_input.value
        }

    def clear_input(self):
        self.subject_input.value = ""

    def on_double_click_handler(self, widget, row):
        self.edit_subject_input.value = row.subject
        self.edit_day_input = row.day
        self.edit_start_time_input = time.fromisoformat(row.start)
        self.edit_end_time_input = time.fromisoformat(row.end)
        self.edit_row = row
        self.main_window.content = self.edit_ui

    def update_entry_in_db(self, entry):
        query = '''
            UPDATE routines
            SET subject = ?, day = ?, start = ?, end = ?
            WHERE id = ?
        '''
        self.cursor.execute(query, (entry["subject"], entry["day"], entry["start"], entry["end"], entry["id"]))
        self.conn.commit()

    def delete_entry_from_db(self, entry_id):
        query = 'DELETE FROM routines WHERE id = ?'
        self.cursor.execute(query, (entry_id,))
        self.conn.commit()

    def set_main_ui(self):
        self.main_window.content = self.main_ui


def main():
    return HelloWorld()
