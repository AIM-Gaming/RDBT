from fastapi import FastAPI
import mysql.connector
from typing import List, Optional, Dict, Any

from db import get_db_connection
app = FastAPI()


# USERS: GET
@app.get("/users/{user_id}/settings", response_model=Dict[str, Any])
def get_user_settings(user_id: int):
    """Fetch user settings from the database"""
    conn, cursor = get_db_connection(dictionary=True)
    
    try:
        cursor.execute("USE users;")
        cursor.execute("SELECT * FROM user_settings WHERE user_id = %s", (user_id,))
        settings = cursor.fetchone()
        
        if settings:
            return settings
        else:
            return {}
    finally:
        cursor.close()
        conn.close()


@app.get("/users/{user_id}/progress", response_model=Dict[str, Any])
def load_trivia_questions(user_id: int) -> Dict[str, Any]:
    """Fetch user progress from the database"""
    conn, cursor = get_db_connection(dictionary=True)
    
    try:
        cursor.execute("USE bible_trivia;")
        cursor.execute("""
            SELECT current_bank_index, current_question, score, lives, time_remaining, last_question, num_questions_per_round, question_id_list
            FROM user_progress
            WHERE user_id = %s
        """, (user_id,))
        progress = cursor.fetchone()
        
        if progress:
            return progress
        else:
            return {}
    except mysql.connector.Error as e:
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()
        conn.close()

@app.get("/users/{user_id}/lim_progress", response_model=Dict[str, Any])
def load_limited_progress(user_id: int):
    """Fetch limited user progress from the database"""
    conn, cursor = get_db_connection(dictionary=True)

    try:
        cursor.execute("USE bible_trivia;")
        cursor.execute("SELECT current_bank_index, current_question, score, lives, time_remaining, last_question "
                        "FROM user_progress WHERE user_id = %s", (user_id,))
        progress = cursor.fetchone()

        if progress:
            return progress
        else:
            return {}
    except mysql.connector.Error as e:
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()
        conn.close()

@app.get("/users/{user_id}/progress/last_question", response_model=int)
def get_last_question(user_id: int):
    """Fetch the last question ID in the database."""
    conn, cursor = get_db_connection()
    
    try:
        cursor.execute("USE bible_trivia;")
        cursor.execute("SELECT last_question FROM user_progress WHERE user_id = %s", (user_id,))
        last_question = cursor.fetchone()[0]
        
        if last_question:
            return last_question
        else:
            return 0
    except mysql.connector.Error:
        return 0
    finally:
        cursor.close()
        conn.close()

@app.get("/users/{user_id}/high_score", response_model=int)
def get_user_high_score(user_id: int):
    """Fetch the user's high score from the database."""
    conn, cursor = get_db_connection()

    try:
        cursor.execute("USE users;")
        cursor.execute("SELECT high_score FROM user_score WHERE user_id = %s", (user_id,))
        high_score = cursor.fetchone()[0]

        if high_score:
            return high_score
        else:
            return 0
    except mysql.connector.Error:
        return 0
    finally:
        cursor.close()
        conn.close()

@app.get("/users/{user_id}/get_last_active")
def get_last_active_user(user_id: int):
    conn, cursor = get_db_connection()

    try:
        cursor.execute("USE users;")
        cursor.execute("SELECT last_active FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()

        if result:
            return result
        else:
            return False
    except mysql.connector.Error as e:
        return False
    finally:
        cursor.close()
        conn.close()


# USERS: POST
@app.post("/users/{user_id}/update_high_score")
def update_user_high_score(user_id: int, score: int):
    """Update user high score when score is greater than the previous high score."""
    conn, cursor = get_db_connection()
    
    try:
        cursor.execute("USE users;")
        cursor.execute("UPDATE user_score SET high_score = %s WHERE user_id = %s", (score, user_id))
        conn.commit()
        return {"status": "success", "user_id": user_id}
    except mysql.connector.Error as e:
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()
        conn.close()

@app.post("/users/{user_id}/save_progress")
def save_progress(user_id: int, progress: Dict[str, Any]):
    """Save user progress from QuizManager to the database
    
    Expected progress dict keys:
    - current_bank_index: int
    - current_question: int
    - score: int
    - lives: int
    - time_remaining: int
    - last_question: int or None
    - num_questions_per_round: int
    - question_id_list: JSON string of question IDs
    """
    conn, cursor = get_db_connection()
    
    try:
        cursor.execute("USE bible_trivia;")
        
        # Use REPLACE to insert or update
        cursor.execute("""
            REPLACE INTO user_progress (user_id, current_bank_index, current_question, score, lives, time_remaining, last_question, num_questions_per_round, question_id_list)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            progress.get("current_bank_index"),
            progress.get("current_question"),
            progress.get("score"),
            progress.get("lives"),
            progress.get("time_remaining"),
            progress.get("last_question"),
            progress.get("num_questions_per_round"),
            progress.get("question_id_list")
        ))
        conn.commit()
        return {"status": "success", "user_id": user_id}
    except mysql.connector.Error as e:
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()
        conn.close()

@app.post("/users/{user_id/reset_progress")
def reset_user_progress(user_id: int):
    conn, cursor = get_db_connection()

    try:
        cursor.execute("USE bible_trivia;")
        cursor.execute("""
            UPDATE user_progress
            SET current_bank_index = %s, 
                current_question = %s, 
                score = %s, 
                lives = %s, 
                time_remaining = %s,
                last_question = NULL, 
                num_questions_per_round = %s, 
                question_id_list = NULL
            WHERE user_id = %s
        """, (1, 0, 0, 4, 30, 6, user_id))
        conn.commit()
        return {"status": "success", "user_id": user_id}
    except mysql.connector.Error as e:
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()
        conn.close()

@app.post("/users/{user_id}/log_out")
def log_user_out(user_id: int):
    conn, cursor = get_db_connection()
    try:
        cursor.execute("USE users;")
        cursor.execute("UPDATE users SET logged_in = FALSE WHERE id = %s", (user_id,))
        conn.commit()
        return {"status": "success", "user_id": user_id}
    except mysql.connector.Error as e:
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()
        conn.close()

@app.post("/users/{user_id}/set_last_active")
def update_last_active_user(user_id: int):
    conn, cursor = get_db_connection()
    try:
        cursor.execute("USE users;")
        cursor.execute("UPDATE users SET last_active = NOW() WHERE id = %s", (user_id,))
        conn.commit()
        return {"status": "success", "user_id": user_id}
    except mysql.connector.Error as e:
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()
        conn.close()



# BIBLE TRIVIA: GET
@app.get("/bible_trivia/questions", response_model=List[Dict[str, Any]])
def get_all_questions(bank_id: int, selected_bible_version: str = 'NIV'):
    conn, cursor = get_db_connection(dictionary=True)
    
    # Fetch questions with corresponding answers
    try:
        cursor.execute("USE bible_trivia;")
        cursor.execute("""
            SELECT
                q.id as question_id,
                q.question_text,
                a.answer_id,
                a.answer_text,
                a.is_correct,
                IF(a.is_correct, NULL, (
                    SELECT GROUP_CONCAT(DISTINCT sr2.bible_ref SEPARATOR ', ')
                    FROM scripture_references sr2
                    JOIN answers a2 ON sr2.answer_id = a2.answer_id
                    WHERE a2.question_id = a.question_id AND a2.is_correct = 1
                )) AS bible_ref
            FROM questions q
            JOIN answers a ON q.id = a.question_id
            LEFT JOIN scripture_references sr ON a.answer_id = sr.answer_id
            WHERE q.question_bank_id = %s
            AND (a.bible_version = %s OR a.bible_version = 'ALL')
        """, (bank_id, selected_bible_version))
        raw_data = cursor.fetchall()
        
        return raw_data
    except mysql.connector.Error as e:
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()
        conn.close()

@app.get("/bible_trivia/questions_by_ids", response_model=List[Dict[str, Any]])
def get_questions_by_ids(question_ids: List[int], selected_bible_version: str = 'NIV') -> List[Dict[str, Any]]:
    conn, cursor = get_db_connection(dictionary=True)
    
    try:
        cursor.execute("USE bible_trivia;")
        format_strings = ','.join(['%s'] * len(question_ids))
        cursor.execute(f"""
            SELECT
                q.id as question_id,
                q.question_text,
                a.answer_id,
                a.answer_text,
                a.is_correct,
                IF(a.is_correct, NULL, (
                    SELECT GROUP_CONCAT(DISTINCT sr2.bible_ref SEPARATOR ', ')
                    FROM scripture_references sr2
                    JOIN answers a2 ON sr2.answer_id = a2.answer_id
                    WHERE a2.question_id = a.question_id AND a2.is_correct = 1
                )) AS bible_ref
            FROM questions q
            JOIN answers a ON q.id = a.question_id
            LEFT JOIN scripture_References sr ON a.answer_id = sr.answer_id
            WHERE q.id IN ({format_strings})
            AND (a.bible_version = %s OR a.bible_version = 'ALL')
        """, (*question_ids, selected_bible_version))
        raw_data = cursor.fetchall()

        return raw_data
    except mysql.connector.Error as e:
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()
        conn.close()

@app.get("/bible_trivia/last_round", response_model=int)
def get_last_round():
    """Fetch the last round in the database."""
    conn, cursor = get_db_connection()
    
    try:
        cursor.execute("USE bible_trivia;")
        cursor.execute("SELECT MAX(question_bank_id) FROM questions;")
        last_round = cursor.fetchone()[0]
        
        if last_round:
            return last_round
        else:
            return 0
    except mysql.connector.Error:
        return 0
    finally:
        cursor.close()
        conn.close()

# BIBLE TRIVIA: POST
