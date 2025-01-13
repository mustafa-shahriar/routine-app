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
        self.day_input = toga.Selection(items=[day for day in calendar.day_name], style=Pack(flex=1, padding=5))
        self.start_time_input = toga.TimeInput(style=Pack(flex=1, padding=5))
        self.end_time_input = toga.TimeInput(style=Pack(flex=1, padding=5))
        add_button = toga.Button("Add")
        input_box = toga.Box(
            children = [
                self.subject_input,
                self.day_input,
                self.start_time_input,
                self.end_time_input,
                add_button
            ],
            style = Pack(direction=COLUMN, padding=5)
        )

        # Routine view
        self.select_view_input = toga.Selection(
            items = [{"name": "All", "value": "All"}] +
                [{ "name": day, "value": day if day != self.today else day + " (today)"} for day in calendar.day_name],
            accessor = "value",
            on_change = self.select_view_input_handler
        )
        self.routine_table = toga.Table(
            headings = ["Day", "Subject", "Start", "End"],
            style = Pack(flex=1)
        )
        routine_view_box = toga.Box(
            children = [
                self.select_view_input,
                self.routine_table
            ],
            style = Pack(direction=COLUMN, padding=5)
        )
        # self.routine_table.data = []

        # Extra Buttons
        view_todays_routine_button = toga.Button("View Today's routine", style=Pack(padding=5))
        clear_all_button = toga.Button("Clear All", style=Pack(padding=5))
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


    def select_view_input_handler(self, widget):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()
        for table in tables:
            self.main_window.info_dialog("An entry already exists for that time range." + table[0])

    def init_db(self):
        self.conn = sqlite3.connect(toga.App.app.paths.app / './resources/db/routines.db')
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


def main():
    return HelloWorld()
