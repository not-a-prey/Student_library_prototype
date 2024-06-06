from flask import Flask, request, jsonify
import sqlite3 as sql
import base64

app = Flask(__name__)


def get_db_connection():
    try:
        conn = sql.connect('student_textbooks.db')
        conn.row_factory = sql.Row
        return conn
    except sql.Error as e:
        print(f"Помилка при підключенні до бази даних {e}.")
        return None


@app.route('/add_textbook', methods=['POST'])
def add_textbook():
    try:
        data = request.json
        title = data['title']
        discipline = data['discipline']
        author = data['author']
        description = data['description']
        link = data['link']
        image_path = data['image_path']

        with open(image_path, 'rb') as f:
            image = base64.b64encode(f.read()).decode('utf-8')

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
    INSERT INTO textbooks (title, discipline, author, description, link, image)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (title, discipline, author, description, link, image))
        conn.commit()
        conn.close()
        return jsonify({'status': 'Підручник успішно додано!'})
    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)})


@app.route('/search_textbooks', methods=['GET'])
def search_textbooks():
    try:
        query = request.args.get('query', '').lower()
        query = f"%{query}%"

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
        SELECT id, title, discipline, author, description, link, image FROM textbooks''')
        results = cur.fetchall()
        conn.close()

        found_textbooks = [dict(row) for row in results]

        matching_textbooks = [
            book for book in found_textbooks
            if query[1:-1] in book["title"].lower()
            or query[1:-1] in book["discipline"].lower()
            or query[1:-1] in book["author"].lower()
        ]

        return jsonify(matching_textbooks)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'Error', 'message': str(e)})


@app.route('/get_textbook_by_id/<int:id>', methods=['GET'])
def get_textbook_by_id(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
        SELECT title, discipline, author, description, link, image FROM textbooks WHERE id = ?''', (id,))
        result = cur.fetchone()
        conn.close()
        if result:
            textbook = dict(result)
            textbook['image'] = base64.b64encode(textbook['image']).decode('utf-8')
            return jsonify(textbook)
        else:
            return jsonify({'error': 'Такого підручника не знайдено!'}), 404
    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)})


@app.route('/delete_textbook/<int:id>', methods=['DELETE'])
def delete_textbook(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
        DELETE FROM textbooks WHERE id = ?''', (id,))
        conn.commit()
        conn.close()
        return jsonify({'status': 'Підручник було успішно видалено!'})
    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)})


@app.route('/update_textbook/<int:id>', methods=['PUT'])
def update_textbook(id):
    try:
        data = request.json
        title = data.get('title')
        discipline = data.get('discipline')
        author = data.get('author')
        description = data.get('description')
        link = data.get('link')
        image_path = data.get('image_path')

        with open(image_path, 'rb') as f:
            image = f.read()

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            UPDATE textbooks SET title = ?, discipline = ?, author = ?, description = ?, link = ?, image = ?)
            WHERE id = ?
            ''', (title, discipline, author, description, link, image, id))
        conn.commit()
        conn.close()
        return jsonify({'status': 'Дані підручника успішно змінено!'})
    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)})


if __name__ == '__main__':
    app.run(debug=True)