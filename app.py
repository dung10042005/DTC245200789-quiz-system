import json
import os
import time

import pymysql
from flask import Flask, jsonify, render_template, request
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "quizdb_mysql")
MYSQL_USER = os.getenv("MYSQL_USER", "quizuser_mysql")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")

REQUEST_COUNT = Counter(
    "quiz_http_requests_total",
    "Total HTTP requests received by the Quiz application",
    ["method", "endpoint", "status"],
)

QUESTIONS = [
    {
        "id": 1,
        "question": "Python là loại ngôn ngữ lập trình nào?",
        "options": [
            {"value": "A", "text": "Ngôn ngữ lập trình bậc cao"},
            {"value": "B", "text": "Ngôn ngữ đánh dấu"},
            {"value": "C", "text": "Hệ điều hành"},
            {"value": "D", "text": "Hệ quản trị cơ sở dữ liệu"},
        ],
        "answer": "A",
    },
    {
        "id": 2,
        "question": "Kiểu dữ liệu nào trong Python dùng để lưu một dãy phần tử có thứ tự?",
        "options": [
            {"value": "A", "text": "bool"},
            {"value": "B", "text": "list"},
            {"value": "C", "text": "None"},
            {"value": "D", "text": "float"},
        ],
        "answer": "B",
    },
    {
        "id": 3,
        "question": "Lệnh nào thường dùng để hiển thị nội dung ra màn hình trong Python?",
        "options": [
            {"value": "A", "text": "echo()"},
            {"value": "B", "text": "show()"},
            {"value": "C", "text": "print()"},
            {"value": "D", "text": "writeScreen()"},
        ],
        "answer": "C",
    },
]


def get_connection():
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.Cursor,
        connect_timeout=5,
        read_timeout=5,
        write_timeout=5,
    )


def init_db():
    """Create the questions table and seed sample questions if empty."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS questions (
                    id INT PRIMARY KEY,
                    question TEXT NOT NULL,
                    options JSON NOT NULL,
                    answer CHAR(1) NOT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
            cur.execute("SELECT COUNT(*) FROM questions")
            count = cur.fetchone()[0]

            if count == 0:
                cur.executemany(
                    """
                    INSERT INTO questions (id, question, options, answer)
                    VALUES (%s, %s, %s, %s)
                    """,
                    [
                        (
                            q["id"],
                            q["question"],
                            json.dumps(q["options"], ensure_ascii=False),
                            q["answer"],
                        )
                        for q in QUESTIONS
                    ],
                )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def load_questions():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, question, options FROM questions ORDER BY id"
            )
            rows = cur.fetchall()
        return [
            {
                "id": row[0],
                "question": row[1],
                "options": (
                    json.loads(row[2]) if isinstance(row[2], str) else row[2]
                ),
            }
            for row in rows
        ]
    finally:
        conn.close()


@app.after_request
def record_request(response):
    REQUEST_COUNT.labels(
        request.method,
        request.endpoint or "unknown",
        str(response.status_code),
    ).inc()
    return response


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.get("/api/questions")
def api_questions():
    try:
        return jsonify(load_questions())
    except pymysql.MySQLError:
        app.logger.exception("Unable to read questions from MySQL")
        return jsonify({"error": "Không thể tải câu hỏi lúc này."}), 503


@app.post("/api/submit")
def submit_quiz():
    data = request.get_json(silent=True) or {}
    answers = data.get("answers", {})

    if not isinstance(answers, dict):
        return jsonify({"error": "Dữ liệu câu trả lời không hợp lệ."}), 400

    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT id, answer FROM questions")
            answer_key = {
                str(row[0]): row[1].strip()
                for row in cur.fetchall()
            }
    except pymysql.MySQLError:
        app.logger.exception("Unable to grade quiz using MySQL")
        return jsonify({"error": "Không thể chấm điểm lúc này."}), 503
    finally:
        if conn is not None:
            conn.close()

    answered = sum(1 for question_id in answers if question_id in answer_key)
    correct = sum(
        1
        for question_id, answer in answers.items()
        if question_id in answer_key
        and isinstance(answer, str)
        and answer == answer_key[question_id]
    )
    total = len(answer_key)

    return jsonify({
        "total": total,
        "answered": answered,
        "correct": correct,
        "score": round(correct / total * 10, 2) if total else 0,
    })


@app.get("/metrics")
def metrics():
    return generate_latest(), 200, {
        "Content-Type": CONTENT_TYPE_LATEST
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
