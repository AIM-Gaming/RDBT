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

# USERS: POST
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
