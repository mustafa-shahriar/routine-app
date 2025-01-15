import toga
import calendar
from datetime import time
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from .db import update_entry_in_db, delete_entry_from_db, is_valid_time_with_id

def init_main_ui(app):
    # Input Form
    app.subject_input = toga.TextInput(placeholder='Subject Name', style=Pack(flex=1))
    app.day_input = toga.Selection(items=[day for day in calendar.day_name], style=Pack(flex=1, padding=5))
    start_label = toga.Label("Start Time: ")
    end_label = toga.Label("End Time: ")
    day_input_label = toga.Label("Day: ")
    app.start_time_input = toga.TimeInput(style=Pack(flex=1, padding=5))
    app.end_time_input = toga.TimeInput(style=Pack(flex=1, padding=5))

    start_time_input_box = toga.Box(
        children = [
            start_label,
            app.start_time_input
        ],
        style = Pack(direction=ROW, flex=1,alignment=CENTER)
    )

    end_time_input_box = toga.Box(
        children = [
            end_label,
            app.end_time_input
        ],
        style = Pack(direction=ROW, flex=1, alignment=CENTER)
    )

    day_input_box = toga.Box(
        children = [
            day_input_label,
            app.day_input
        ],
        style = Pack(direction=ROW, flex=1, alignment=CENTER)
    )

    add_button = toga.Button("Add", on_press=app.add_entry_handler)
    input_box = toga.Box(
        children = [
            app.subject_input,
            day_input_box,
            start_time_input_box,
            end_time_input_box,
            add_button
        ],
        style = Pack(direction=COLUMN, padding=5)
    )

    # Routine view
    select_view_label = toga.Label("Routine: ")
    app.select_view_input = toga.Selection(
        items = [{"name": "All", "value": "All"}] +
            [{ "name": day, "value": day if day != app.today else day + " (today)"} for day in calendar.day_name],
        accessor = "value",
        on_change = app.select_view_input_handler,
        style=Pack(flex=1, padding=5)
    )
    select_view_box = toga.Box(
       children = [
            select_view_label,
            app.select_view_input
        ],
        style = Pack(direction=ROW, flex=1, alignment=CENTER)
    )

    app.routine_table = toga.Table(
        # headings = ["day", "Subject", "Start", "End"],
        headings = ["day", "Subject", "time"],
        on_activate = app.on_double_click_handler,
        style = Pack(flex=1)
    )
    routine_view_box = toga.Box(
        children = [
            select_view_box,
            app.routine_table
        ],
        style = Pack(direction=COLUMN, padding=5)
    )

    # Extra Buttons
    view_todays_routine_button = toga.Button("View Today's routine", style=Pack(padding=5), on_press=app.view_todays_routine_handler)
    clear_all_button = toga.Button("Clear All", style=Pack(padding=5), on_press=app.clear_all_handler)
    extra_buttons_box = toga.Box(
        children = [
            view_todays_routine_button,
            clear_all_button
        ],
        style = Pack(direction=COLUMN, padding=5,)
    )

    # Main Box
    app.main_ui = toga.Box(
        children = [
            input_box,
            routine_view_box,
            extra_buttons_box,
        ],
        style=Pack(direction=COLUMN, padding=10)
    )


def init_edit_ui(app):
    app.edit_subject_input = toga.TextInput(style=Pack(flex=1))
    app.edit_day_input = toga.Selection(items=[day for day in calendar.day_name], style=Pack(flex=1, padding=5))
    app.edit_start_time_input = toga.TimeInput(style=Pack(flex=1, padding=5))
    app.edit_end_time_input = toga.TimeInput(style=Pack(flex=1, padding=5))

    dialog_box = toga.Box(
        children=[
            toga.Label("Subject: "),
            app.edit_subject_input,
            toga.Label("Day: "),
            app.edit_day_input,
            toga.Label("Start Time: "),
            app.edit_start_time_input,
            toga.Label("End Time: "),
            app.edit_end_time_input,
        ],
        style=Pack(direction=COLUMN, padding=10)
    )

    def on_save_button_press(widget):
        updated_entry = {
            "id": app.edit_row.id,
            "subject": app.edit_subject_input.value,
            "day": app.edit_day_input.value,
            "start": app.edit_start_time_input.value.isoformat(),
            "end": app.edit_end_time_input.value.isoformat()
        }

        if updated_entry["start"] >= updated_entry["end"]:
                app.main_window.info_dialog("Error", "Start time must be earlier than end time.")
                return

        if not is_valid_time_with_id(app, updated_entry["day"], updated_entry["start"], updated_entry["end"], updated_entry["id"]):
            app.main_window.info_dialog("Error", "An entry already exists for that time range.")
            return

        if updated_entry["subject"] == "":
            app.main_window.info_dialog("Error!", "Subject can't be empty")
            return

        update_entry_in_db(app, updated_entry)

        updated_entry["start"] = str(updated_entry["start"][:5])
        updated_entry["end"] = str(updated_entry["end"][:5])
        updated_entry["time"] = updated_entry["start"] + "-" + updated_entry["end"]
        for i, entry in enumerate(app.routine_table.data):
            if entry.id == app.edit_row.id:
                app.routine_table.data[i] = updated_entry
        app.main_window.info_dialog("Success", "Routine updated successfully")
        app.set_main_ui()

    def on_delete_button_press(widget):
        delete_entry_from_db(app, app.edit_row.id)
        app.routine_table.data = [entry for entry in app.routine_table.data if entry.id != app.edit_row.id]
        app.main_window.info_dialog("Deleted", "Routine deleted successfully")
        app.set_main_ui()

    save_button = toga.Button("Save", on_press=on_save_button_press)
    delete_button = toga.Button("Delete", on_press=on_delete_button_press)
    cancel_button = toga.Button("Cancel", on_press=lambda widget: app.set_main_ui())

    button_box = toga.Box(
        children=[save_button, delete_button, cancel_button],
        style=Pack(direction=ROW, padding=10, alignment=CENTER)
    )

    app.edit_ui = toga.Box(
        children=[dialog_box, button_box],
        style=Pack(direction=COLUMN, padding=20)
    )
