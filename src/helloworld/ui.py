import toga
import calendar
from datetime import time
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER

def init_main_ui(toga_app):
    # Input Form
    toga_app.subject_input = toga.TextInput(placeholder='Subject Name', style=Pack(flex=1))
    toga_app.day_input = toga.Selection(items=[day for day in calendar.day_name], style=Pack(flex=1, padding=5))
    start_label = toga.Label("Start Time: ")
    end_label = toga.Label("End Time: ")
    day_input_label = toga.Label("Day: ")
    toga_app.start_time_input = toga.TimeInput(style=Pack(flex=1, padding=5))
    toga_app.end_time_input = toga.TimeInput(style=Pack(flex=1, padding=5))

    start_time_input_box = toga.Box(
        children = [
            start_label,
            toga_app.start_time_input
        ],
        style = Pack(direction=ROW, flex=1,alignment=CENTER)
    )

    end_time_input_box = toga.Box(
        children = [
            end_label,
            toga_app.end_time_input
        ],
        style = Pack(direction=ROW, flex=1, alignment=CENTER)
    )

    day_input_box = toga.Box(
        children = [
            day_input_label,
            toga_app.day_input
        ],
        style = Pack(direction=ROW, flex=1, alignment=CENTER)
    )

    add_button = toga.Button("Add", on_press=toga_app.add_entry)
    input_box = toga.Box(
        children = [
            toga_app.subject_input,
            day_input_box,
            start_time_input_box,
            end_time_input_box,
            add_button
        ],
        style = Pack(direction=COLUMN, padding=5)
    )

    # Routine view
    select_view_label = toga.Label("Routine: ")
    toga_app.select_view_input = toga.Selection(
        items = [{"name": "All", "value": "All"}] +
            [{ "name": day, "value": day if day != toga_app.today else day + " (today)"} for day in calendar.day_name],
        accessor = "value",
        on_change = toga_app.select_view_input_handler,
        style=Pack(flex=1, padding=5)
    )
    select_view_box = toga.Box(
       children = [
            select_view_label,
            toga_app.select_view_input
        ],
        style = Pack(direction=ROW, flex=1, alignment=CENTER)
    )

    toga_app.routine_table = toga.Table(
        # headings = ["day", "Subject", "Start", "End"],
        headings = ["day", "Subject", "time"],
        on_activate = toga_app.on_double_click_handler,
        style = Pack(flex=1)
    )
    routine_view_box = toga.Box(
        children = [
            select_view_box,
            toga_app.routine_table
        ],
        style = Pack(direction=COLUMN, padding=5)
    )

    # Extra Buttons
    view_todays_routine_button = toga.Button("View Today's routine", style=Pack(padding=5), on_press=toga_app.view_todays_routine)
    clear_all_button = toga.Button("Clear All", style=Pack(padding=5), on_press=toga_app.clear_all)
    extra_buttons_box = toga.Box(
        children = [
            view_todays_routine_button,
            clear_all_button
        ],
        style = Pack(direction=COLUMN, padding=5,)
    )

    # Main Box
    toga_app.main_ui = toga.Box(
        children = [
            input_box,
            routine_view_box,
            extra_buttons_box,
        ],
        style=Pack(direction=COLUMN, padding=10)
    )


def init_edit_ui(toga_app):
    toga_app.edit_subject_input = toga.TextInput(style=Pack(flex=1))
    toga_app.edit_day_input = toga.Selection(items=[day for day in calendar.day_name], style=Pack(flex=1, padding=5))
    toga_app.edit_start_time_input = toga.TimeInput(style=Pack(flex=1, padding=5))
    toga_app.edit_end_time_input = toga.TimeInput(style=Pack(flex=1, padding=5))

    dialog_box = toga.Box(
        children=[
            toga.Label("Subject: "),
            toga_app.edit_subject_input,
            toga.Label("Day: "),
            toga_app.edit_day_input,
            toga.Label("Start Time: "),
            toga_app.edit_start_time_input,
            toga.Label("End Time: "),
            toga_app.edit_end_time_input,
        ],
        style=Pack(direction=COLUMN, padding=10)
    )

    def on_save_button_press(widget):
        updated_entry = {
            "id": toga_app.edit_row.id,
            "subject": toga_app.edit_subject_input.value,
            "day": toga_app.edit_day_input.value,
            "start": toga_app.edit_start_time_input.value.isoformat(),
            "end": toga_app.edit_end_time_input.value.isoformat()
        }

        if updated_entry["start"] >= updated_entry["end"]:
                toga_app.main_window.info_dialog("Error", "Start time must be earlier than end time.")
                return

        if not toga_app.is_valid_time_with_id(updated_entry["day"], updated_entry["start"], updated_entry["end"], updated_entry["id"]):
            toga_app.main_window.info_dialog("Error", "An entry already exists for that time range.")
            return

        if updated_entry["subject"] == "": toga_app.main_window.info_dialog("Error!", "Subject can't be empty")

        toga_app.update_entry_in_db(updated_entry)

        updated_entry["start"] = str(updated_entry["start"][:5])
        updated_entry["end"] = str(updated_entry["end"][:5])
        updated_entry["time"] = updated_entry["start"] + "-" + updated_entry["end"]
        for i, entry in enumerate(toga_app.routine_table.data):
            if entry.id == toga_app.edit_row.id:
                toga_app.routine_table.data[i] = updated_entry
        toga_app.main_window.info_dialog("Success", "Routine updated successfully")
        toga_app.set_main_ui()

    def on_delete_button_press(widget):
        toga_app.delete_entry_from_db(toga_app.edit_row.id)
        toga_app.routine_table.data = [entry for entry in toga_app.routine_table.data if entry.id != toga_app.edit_row.id]
        toga_app.main_window.info_dialog("Deleted", "Routine deleted successfully")
        toga_app.set_main_ui()

    save_button = toga.Button("Save", on_press=on_save_button_press)
    delete_button = toga.Button("Delete", on_press=on_delete_button_press)
    cancel_button = toga.Button("Cancel", on_press=lambda widget: toga_app.set_main_ui())

    button_box = toga.Box(
        children=[save_button, delete_button, cancel_button],
        style=Pack(direction=ROW, padding=10, alignment=CENTER)
    )

    toga_app.edit_ui = toga.Box(
        children=[dialog_box, button_box],
        style=Pack(direction=COLUMN, padding=20)
    )
