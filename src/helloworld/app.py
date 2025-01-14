"""
My first application
"""

import toga
import calendar
from datetime import datetime, time
from .ui import init_edit_ui, init_main_ui
from .db import init_db, insert_into_db, is_valid_time, get_all_entry

class HelloWorld(toga.App):
    def startup(self):
        init_db(self)
        self.today = calendar.day_name[datetime.now().weekday()] 
        self.main_window = toga.MainWindow(title=self.formal_name)
        init_main_ui(self) 
        init_edit_ui(self)
        self.set_main_ui()
        self.main_window.show()
        self.load_routine()

    def load_routine(self):
        self.routine_table.data = self.get_routine_data()

    def get_routine_data(self):
        data = [
            {**entry, "time": entry["start"] + "-" + entry["end"]} for entry in get_all_entry(self)
            if self.select_view_input.value.name == "All" or entry["day"] == self.select_view_input.value.name
        ]
        return data

    def get_input(self):
        return {
            "subject": self.subject_input.value.strip(),
            "day": self.day_input.value,
            "start": self.start_time_input.value,
            "end": self.end_time_input.value
        }

    def clear_input(self):
        self.subject_input.value = ""

    def set_main_ui(self):
        self.main_window.content = self.main_ui


    ###################################################################
    #                         Handlers                                #
    ###################################################################

    def select_view_input_handler(self, widget):
        self.load_routine()

    def clear_all_handler(self, widget):
        query = "DELETE FROM routines"
        self.cursor.execute(query)
        self.conn.commit()
        self.routine_table.data = self.get_routine_data()

    def view_todays_routine_handler(self, widget):
        index = 0
        for i, selection in enumerate(self.select_view_input.items):
            if selection.name == self.today:
                index = i
                break
        self.select_view_input.value = self.select_view_input.items[index]

    def add_entry_handler(self, widget):
        value = self.get_input()
        if value["start"] >= value["end"]:
            self.main_window.info_dialog("Error!","Invalid time range")
            return
        value["start"] = value["start"].isoformat()
        value["end"] = value["end"].isoformat()
        if not is_valid_time(self, value["day"], value["start"], value["end"]):
            self.main_window.info_dialog("Error!","An entry already exists for that time range.")
            return
        if value["subject"] == "": self.main_window.info_dialog("Error!", "Subject can't be empty")

        insert_into_db(self, value) 
        self.clear_input()
        value["id"] = self.cursor.lastrowid
        value["start"] = str(value["start"][:5])
        value["end"] = str(value["end"][:5])
        value["time"] = value["start"] + "-" + value["end"]
        if self.select_view_input.value.name == "All" or self.select_view_input.value.name == value["day"]:
            self.routine_table.data.append(value)

    def on_double_click_handler(self, widget, row):
        self.edit_subject_input.value = row.subject
        self.edit_day_input.value = row.day
        self.edit_start_time_input.value = time.fromisoformat(row.start)
        self.edit_end_time_input.value = time.fromisoformat(row.end)
        self.edit_row = row
        self.main_window.content = self.edit_ui

def main():
    return HelloWorld()
