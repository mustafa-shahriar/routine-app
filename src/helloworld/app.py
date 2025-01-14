"""
My first application
"""

import toga
import sqlite3
import calendar
from datetime import datetime, time
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER

class HelloWorld(toga.App):
    def startup(self):
        self.init_db()
        self.today = calendar.day_name[datetime.now().weekday()] 
        self.main_window = toga.MainWindow(title=self.formal_name)

        # Input Form
        self.subject_input = toga.TextInput(placeholder='Subject Name', style=Pack(flex=1))
        self.day_input = toga.Selection(items=[day for day in calendar.day_name], style=Pack(flex=1, padding=5))
        start_label = toga.Label("Start Time: ")
        end_label = toga.Label("End Time: ")
        day_input_label = toga.Label("Day: ")
        self.start_time_input = toga.TimeInput(style=Pack(flex=1, padding=5))
        self.end_time_input = toga.TimeInput(style=Pack(flex=1, padding=5))

        start_time_input_box = toga.Box(
            children = [
                start_label,
                self.start_time_input
            ],
            style = Pack(direction=ROW, flex=1,alignment=CENTER)
        )

        end_time_input_box = toga.Box(
            children = [
                end_label,
                self.end_time_input
            ],
            style = Pack(direction=ROW, flex=1, alignment=CENTER)
        )

        day_input_box = toga.Box(
            children = [
                day_input_label,
                self.day_input
            ],
            style = Pack(direction=ROW, flex=1, alignment=CENTER)
        )

        add_button = toga.Button("Add", on_press=self.add_entry)
        input_box = toga.Box(
            children = [
                self.subject_input,
                day_input_box,
                start_time_input_box,
                end_time_input_box,
                add_button
            ],
            style = Pack(direction=COLUMN, padding=5)
        )

        # Routine view
        select_view_label = toga.Label("Routine: ")
        self.select_view_input = toga.Selection(
            items = [{"name": "All", "value": "All"}] +
                [{ "name": day, "value": day if day != self.today else day + " (today)"} for day in calendar.day_name],
            accessor = "value",
            on_change = self.select_view_input_handler,
            style=Pack(flex=1, padding=5)
        )
        select_view_box = toga.Box(
           children = [
                select_view_label,
                self.select_view_input
            ],
            style = Pack(direction=ROW, flex=1, alignment=CENTER)
        )

        self.routine_table = toga.Table(
            headings = ["day", "Subject", "Start", "End"],
            on_activate = self.on_double_click_handler,
            style = Pack(flex=1)
        )
        routine_view_box = toga.Box(
            children = [
                select_view_box,
                self.routine_table
            ],
            style = Pack(direction=COLUMN, padding=5)
        )

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
        self.main_box = toga.Box(
            children = [
                input_box,
                routine_view_box,
                extra_buttons_box
            ],
            style=Pack(direction=COLUMN, padding=10)
        )

        self.main_window.content = self.main_box
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
            entry for entry in self.get_all_entry()
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
        if value["subject"] == "": self.main_window.info_dianlog("Error!", "Subject can't be empty")

        self.insert_into_db(value) 
        self.clear_input()
        value["id"] = self.cursor.lastrowid
        value["start"] = str(value["start"][:5])
        value["end"] = str(value["end"][:5])
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
        subject_input = toga.TextInput(value=row.subject, style=Pack(flex=1))
        day_input = toga.Selection(items=[day for day in calendar.day_name], 
                                    value=row.day, style=Pack(flex=1, padding=5))
        start_time_input = toga.TimeInput(value=time.fromisoformat(row.start) , style=Pack(flex=1, padding=5))
        end_time_input = toga.TimeInput(value=time.fromisoformat(row.end), style=Pack(flex=1, padding=5))

        dialog_box = toga.Box(
            children=[
                toga.Label("Subject: "),
                subject_input,
                toga.Label("Day: "),
                day_input,
                toga.Label("Start Time: "),
                start_time_input,
                toga.Label("End Time: "),
                end_time_input,
            ],
            style=Pack(direction=COLUMN, padding=10)
        )

        def on_save_button_press(widget):
            updated_entry = {
                "id": row.id,
                "subject": subject_input.value,
                "day": day_input.value,
                "start": start_time_input.value.isoformat(),
                "end": end_time_input.value.isoformat()
            }

            if updated_entry["start"] >= updated_entry["end"]:
                    self.main_window.info_dialog("Error", "Start time must be earlier than end time.")
                    return

            if not self.is_valid_time_with_id(updated_entry["day"], updated_entry["start"], updated_entry["end"], updated_entry["id"]):
                self.main_window.info_dialog("Error", "An entry already exists for that time range.")
                return

            if updated_entry["subject"] == "": self.main_window.info_dianlog("Error!", "Subject can't be empty")

            self.update_entry_in_db(updated_entry)

            updated_entry["start"] = str(updated_entry["start"][:5])
            updated_entry["end"] = str(updated_entry["end"][:5])
            for i, entry in enumerate(self.routine_table.data):
                if entry.id == row.id:
                    self.routine_table.data[i] = updated_entry
            self.main_window.info_dialog("Success", "Routine updated successfully")
            self.set_main_box()

        def on_delete_button_press(widget):
            self.delete_entry_from_db(row.id)
            self.routine_table.data = [entry for entry in self.routine_table.data if entry.id != row.id]
            self.main_window.info_dialog("Deleted", "Routine deleted successfully")
            self.set_main_box()

        save_button = toga.Button("Save", on_press=on_save_button_press)
        delete_button = toga.Button("Delete", on_press=on_delete_button_press)
        cancel_button = toga.Button("Cancel", on_press=lambda widget: self.set_main_box())

        button_box = toga.Box(
            children=[save_button, delete_button, cancel_button],
            style=Pack(direction=ROW, padding=10, alignment=CENTER)
        )

        dialog = toga.Box(
            children=[dialog_box, button_box],
            style=Pack(direction=COLUMN, padding=20)
        )

        self.main_window.content = dialog

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

    def set_main_box(self):
        self.main_window.content = self.main_box


def main():
    return HelloWorld()
