from flask import Flask, render_template, request, jsonify
import json
import sqlite3
import subprocess
import os
from datetime import datetime, timedelta

app = Flask(__name__)


# ========== БАЗА ДАННЫХ ==========
def init_db():
    """Создаёт базу данных и таблицу для заявок"""
    conn = sqlite3.connect('appointments.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            diagnosis TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ База данных инициализирована")


init_db()

# ========== ЗАГРУЗКА ОТВЕТОВ ==========
try:
    with open("answers.json", "r", encoding="utf-8") as f:
        answers = json.load(f)
    print("✅ Ответы загружены из answers.json")
except FileNotFoundError:
    print("❌ Файл answers.json не найден!")
    answers = {}


# ========== ГЛАВНАЯ СТРАНИЦА ==========
@app.route("/")
def index():
    """Главная страница с тестом"""
    return render_template("index.html")


# ========== ЗАПУСК ТЕСТА ==========
@app.route("/run_test")
def run_test():
    """Запускает Pygame тест в отдельном процессе"""
    try:
        # Очищаем старый результат перед запуском нового теста
        with open("result.txt", "w", encoding="utf-8") as f:
            f.write("")

        # Запускаем test_game.py в отдельном процессе
        subprocess.Popen(["python", "test_game.py"])

        print("🚀 Тест запущен!")
        return jsonify({"status": "success", "message": "Тест запущен!"})
    except Exception as e:
        print(f"❌ Ошибка запуска теста: {e}")
        return jsonify({"status": "error", "message": str(e)})


# ========== ПОЛУЧИТЬ РЕЗУЛЬТАТ ТЕСТА ==========
@app.route("/get_result")
def get_result():
    """Читает результат теста из файла result.txt"""
    try:
        if os.path.exists("result.txt"):
            with open("result.txt", "r", encoding="utf-8") as f:
                result = f.read().strip()

            if result:
                print(f"📋 Результат теста: {result[:50]}...")
                return jsonify({"status": "success", "result": result})
            else:
                return jsonify({"status": "waiting", "result": ""})
        else:
            return jsonify({"status": "waiting", "result": ""})
    except Exception as e:
        print(f"❌ Ошибка чтения результата: {e}")
        return jsonify({"status": "error", "result": ""})


# ========== ПРОВЕРКА ОТВЕТОВ ==========
@app.route("/check", methods=["POST"])
def check_answers():
    """Проверяет ответы пользователя"""
    user_answers = request.json.get("answers", [])

    correct_count = 0
    for i, answer in enumerate(user_answers):
        if str(i + 1) in answers:
            if answer.lower() == answers[str(i + 1)].lower():
                correct_count += 1

    if correct_count < 7:
        diagnosis = "ВНИМАНИЕ: Возможны проблемы с цветовосприятием! Рекомендуем обратиться к офтальмологу."
    else:
        diagnosis = "Отклонений не выявлено."

    return jsonify({
        "correct": correct_count,
        "total": 10,
        "diagnosis": diagnosis
    })


# ========== СОХРАНЕНИЕ ЗАЯВКИ ==========
@app.route("/appointment", methods=["POST"])
def appointment():
    """Сохраняет заявку на приём в базу данных"""
    try:
        data = request.json
        name = data.get("name", "").strip()
        phone = data.get("phone", "").strip()
        diagnosis = data.get("diagnosis", "").strip()

        if not name or not phone:
            return jsonify({"status": "error", "message": "Заполните имя и телефон!"})

        # Сохраняем в базу данных
        conn = sqlite3.connect('appointments.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO appointments (name, phone, diagnosis)
            VALUES (?, ?, ?)
        ''', (name, phone, diagnosis))
        conn.commit()
        conn.close()

        print(f"📞 Новая заявка: {name}, {phone}, Диагноз: {diagnosis[:50] if diagnosis else 'Нет'}")

        return jsonify({"status": "success", "message": "Спасибо! Мы свяжемся с вами в ближайшее время."})

    except Exception as e:
        print(f"❌ Ошибка сохранения заявки: {e}")
        return jsonify({"status": "error", "message": "Ошибка сервера. Попробуйте позже."})


# ========== АДМИНКА (ПРОСМОТР ЗАЯВОК) ==========
@app.route("/admin")
def admin():
    """Страница для просмотра всех заявок с правильным временем (+7 часов)"""
    try:
        conn = sqlite3.connect('appointments.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, phone, diagnosis, created_at FROM appointments ORDER BY id DESC')
        rows = cursor.fetchall()
        conn.close()

        # Функция для преобразования времени (+7 часов)
        def format_datetime(dt_str):
            if not dt_str:
                return "—"
            try:
                dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
                dt = dt + timedelta(hours=7)  # +7 часов (Новосибирск, Красноярск)
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                return dt_str

        total = len(rows)

        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Админка - Заявки на приём</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; padding: 30px; background: #f5f5f5; }}
                h1 {{ color: #2c3e50; }}
                .total {{ background: #3498db; color: white; padding: 10px 20px; border-radius: 10px; display: inline-block; margin-bottom: 20px; }}
                table {{ border-collapse: collapse; width: 100%; background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background: #3498db; color: white; }}
                tr:nth-child(even) {{ background: #f9f9f9; }}
                tr:hover {{ background: #f1f1f1; }}
                .back-link {{ display: inline-block; margin-top: 20px; color: #3498db; text-decoration: none; }}
                .back-link:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <h1>📋 Список заявок на приём</h1>
            <div class="total">Всего заявок: {total}</div>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Имя</th>
                    <th>Телефон</th>
                    <th>Диагноз</th>
                    <th>Дата и время</th>
                </tr>
        '''

        for row in rows:
            html += f'''
                <tr>
                    <td>{row[0]}</td>
                    <td>{row[1]}</td>
                    <td>{row[2]}</td>
                    <td style="max-width: 300px;">{row[3] if row[3] else '—'}</td>
                    <td>{format_datetime(row[4])}</td>
                </tr>
            '''

        html += '''
            </table>
            <a href="/" class="back-link">← Вернуться на главную</a>
        </body>
        </html>
        '''
        return html

    except Exception as e:
        return f"<h1>Ошибка</h1><p>{e}</p>"


# ========== ЗАПУСК СЕРВЕРА ==========
if __name__ == "__main__":
    print("=" * 50)
    print("👁️  Тест на дальтонизм - Сервер запущен!")
    print("📱 Открой в браузере: http://127.0.0.1:5000")
    print("📊 Админка: http://127.0.0.1:5000/admin")
    print("=" * 50)
    app.run(debug=True)