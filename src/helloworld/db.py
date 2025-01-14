import toga
import sqlite3

def init_db(app):
    db_path = toga.App.app.paths.app / 'resources/routines.db'
    app.conn = sqlite3.connect(db_path)
    app.conn.row_factory = sqlite3.Row
    app.cursor = app.conn.cursor()
    app.cursor.execute('''
        CREATE TABLE IF NOT EXISTS routines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            day TEXT NOT NULL,
            start TIME NOT NULL,
            end TIME NOT NULL
        )
    ''')
    app.conn.commit()

def get_all_entry(app):
    query = "SELECT * FROM routines"
    app.cursor.execute(query)
    result = [
        {"id": row[0], "subject": row[1], "day": row[2], "start": str(row[3][:5]), "end": str(row[4][:5]) }
        for row in app.cursor.fetchall()
    ]
    return result

def insert_into_db(self, entry):
    query = '''
        INSERT INTO routines (subject, day, start, end)
        values (?, ?, ?, ?)
    '''
    values = (entry["subject"], entry["day"], entry["start"], entry["end"])
    self.cursor.execute(query,values)
    self.conn.commit()

def update_entry_in_db(app, entry):
    query = '''
        UPDATE routines
        SET subject = ?, day = ?, start = ?, end = ?
        WHERE id = ?
    '''
    app.cursor.execute(query, (entry["subject"], entry["day"], entry["start"], entry["end"], entry["id"]))
    app.conn.commit()

def delete_entry_from_db(app, entry_id):
    query = 'DELETE FROM routines WHERE id = ?'
    app.cursor.execute(query, (entry_id,))
    app.conn.commit()


def is_valid_time_with_id(app, day, start, end, id):
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
    app.cursor.execute(query, (day, id, start, start, end, end))
    return len([r for r in app.cursor.fetchall()]) == 0

def is_valid_time(app, day, start, end):
    query = """
        SELECT * FROM routines
        WHERE
            day = ? AND
            (
                (? >= start AND ? <= end) OR
                (? >= start AND ? <= end)
            )
        """
    app.cursor.execute(query, (day, start, start, end, end))
    return len([r for r in app.cursor.fetchall()]) == 0
