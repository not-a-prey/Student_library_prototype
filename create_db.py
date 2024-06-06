import sqlite3


def create_database():
    conn = sqlite3.connect('student_textbooks.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS textbooks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            discipline TEXT NOT NULL,
            author TEXT NOT NULL,
            description TEXT,
            link TEXT NOT NULL,
            image BLOB NOT NULL
    )''')
    conn.commit()
    conn.close()


if __name__ == '__main__':
    create_database()