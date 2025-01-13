"""
My first application
"""

import toga
import sqlite3
import calendar
from datetime import datetime
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

class HelloWorld(toga.App):
    def startup(self):
        self.init_db()
        self.today = calendar.day_name[datetime.now().weekday()] 
        self.main_window = toga.MainWindow(title=self.formal_name)

        # Input Form
        self.subject_input = toga.TextInput(placeholder='Subject Name', style=Pack(flex=1))
        self.day_input = toga.Selection(items=[day for day in calendar.day_name])
        self.start_time_input = toga.TimeInput(style=Pack(flex=1))
        self.end_time_input = toga.TimeInput(style=Pack(flex=1))
        add_button = toga.Button("Add", on_press=self.add_entry)
        input_box = toga.Box(
            children = [
                self.subject_input,
                self.day_input,
                self.start_time_input,
                self.end_time_input
            ],
            style = Pack(direction=COLUMN, padding=5)
        )

        # Routine view
        self.select_view_input = toga.Selection(
            items = [{"name": "All", "value": "All"}] +
                [{ "name": day, "value": day if day != self.today else day + " (today)"} for day in calendar.day_name],
            accessor = "name",
            on_change = self.select_view_input_handler
        )
        self.routine_table = toga.Table(
            headings = ["Day", "Subject", "Start", "End"],
            accessor = "id",
            style = Pack(flex=1)
        )
        routine_view_box = toga.Box(
            children = [
                self.select_view_input,
                self.routine_table
            ],
            style = Pack(direction=COLUMN, padding=5)
        )
        self.routine_table.data = self.get_routine_data()

        # Extra Buttons
        view_todays_routine_button = toga.Button("View Today's routine", style=Pack(padding=5), on_press=self.view_todays_routine)
        clear_all_button = toga.Button("Clear All", style=Pack(padding=5), on_press=self.clear_all)
        extra_buttons_box = toga.Box(
            children = [
                view_todays_routine_button,
                clear_all_button
            ],
            style = Pack(direction=COLUMN, padding=5,)
        )

        # Main Box
        main_box = toga.Box(
            children = [
                input_box,
                routine_view_box,
                extra_buttons_box
            ],
            style=Pack(direction=COLUMN, padding=10)
        )

        self.main_window.content = main_box
        self.main_window.show()
    
    def select_view_input_handler(self):
        self.routine_table.data = self.get_routine_data()

    def on_double_click_handler(self, widget):
        print(widget)

    def get_routine_data(self):
        data = [
            entry for entry in self.get_all_entry()
            if self.select_view_input.value.value == "All" or entry["day"] == self.select_view_input.value.value
        ]
        return data


    def clear_all(self):
        query = "DELETE FROM routines"
        self.cursor.execute(query)
        self.conn.commit()
        self.routine_table.data = self.get_routine_data()

    def view_todays_routine(self):
        self.select_view_input.value = [entry for entry in self.select_view_input.items if entry["day"] == self.today]

    def add_entry(self):
        value = self.get_input()
        self.clear_input()
        if not self.is_valid_time(value["day"], value["start"], value["end"]):
            self.main_window.info_dialog("An entry already exists for that time range.")
            return
        self.insert_into_db(value) 
        value["id"] = self.cursor.lastrowid
        if self.select_view_input.value.value == value["day"]:
            self.routine_table.data.append(value)

    def init_db(self):
        self.conn = sqlite3.connect('routines.db')
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

    def get_all_entry(self):
        query = "SELECT * FROM routines"
        self.cursor.execute(query)
        result = [
            {"id": row[0], "subject": row[1], "day": row[2], "start": row[3], "end": row[4] }
            for row in self.cursor.fetchall()
        ]
        return result

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

    # def serialize_input_for_db(self, entry):
    #     return {"subject": entry["subject"], "day": entry["day"], "start": entry["start"].isoformat, "end": entry["end"].isoformat}

    def get_input(self):
        return {
            "subject": self.subject_input.value,
            "day": self.day_input.value.isoformat(),
            "start": self.start_time_input.value.isoformat(),
            "end": self.end_time_input
        }

    def clear_input(self):
        self.subject_input.value = ""


def main():
    return HelloWorld()
