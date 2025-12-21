from kivy.app import App

import json
import random
import mysql.connector
from typing import List, Dict, Any, Tuple, Optional

from utils import debug_print
from db import get_db_connection


class QuizManager:
    def __init__(self, bible_version: str = 'NIV'):
        self.bible_version = bible_version
        
        self.questions: List[Dict] = []
        self.current_question_index = 0
        self.score = 0
        self.lives = 4
        self.time_remaining = 30
        self.current_bank_index = 1
        self.num_questions_per_round = 6
        self.game_over = True
        self.last_question_id = None
        self.used_question_ids = set()
        
        # Multiplayer specific
        self.players: Dict[str, Dict] = {}
    
    @property
    def user_id(self):
        """Dynamically fetch the user_id from the running app"""
        return App.get_running_app().user_id
    
    def load_questions(self, shuffle: bool = True, limit: Optional[int] = None):
        """Loads questions from the database"""
        conn, cursor = get_db_connection(dictionary=True)
        if not conn or not cursor:
            debug_print("Database connection failed in load_questions")
            self.questions = []
            return
        try:
            cursor.execute("USE bible_trivia;")
            cursor.execute("""
                SELECT current_bank_index, current_question, score, lives, time_remaining, last_question, num_questions_per_round, question_id_list
                FROM user_progress
                WHERE user_id = %s
            """, (self.user_id,))
            progress = cursor.fetchone()

            if progress:
                self.current_bank_index = progress["current_bank_index"]
                self.current_question_index = progress["current_question"]
                self.score = progress["score"]
                self.lives = progress["lives"]
                self.time_remaining = progress["time_remaining"]
                self.last_question_id = progress["last_question"]
                self.num_questions_per_round = progress["num_questions_per_round"]
                raw_qid_list = progress.get("question_id_list", "[]")
                if not raw_qid_list:
                    question_id_list = []
                else:
                    question_id_list = json.loads(raw_qid_list)

                if isinstance(question_id_list, int):
                    question_id_list = [question_id_list]
                elif isinstance(question_id_list, str):
                    question_id_list = [int(question_id_list)]

                if question_id_list:
                    self.questions = fetch_questions_by_ids(question_id_list, selected_bible_version=self.bible_version)
                else:
                    self.questions = fetch_all_questions(
                        bank_id=self.current_bank_index,
                        shuffle=shuffle,
                        limit=limit,
                        selected_bible_version=self.bible_version
                    ) or []

        except mysql.connector.Error as e:
            debug_print(f"Database error in load_questions: {e}")
        finally:
            cursor.close()
            conn.close()
        self.used_question_ids = set()
    
    def get_current_question(self) -> Optional[Dict]:
        """Return the current question data"""
        if 0 <= self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None
    
    def check_answer(self, selected_answer: str) -> dict[str, list[Any] | bool] | dict[str, list[Any] | bool]:
        """Check's the user's selected answer and updates score/lives"""
        current_question = self.get_current_question()
        if not current_question:
            debug_print("No current question found.")
            return {"is_correct": False, "scripture_references": []}
        
        # self.last_question_id = current_question["question_id"]
        answers = current_question["answers"]
        
        correct_answers = [ans["answer_text"] for ans in answers if ans["is_correct"]]
        scripture_refs = [ans["bible_ref"] for ans in answers if ans["answer_text"] == selected_answer]
        
        is_correct = selected_answer in correct_answers
        debug_print(f"Selected answer: {selected_answer}; Correct answer(s): {correct_answers}")
        
        if is_correct:
            debug_print(f"Correct answer selected: {selected_answer}")
            self.score += 10
        else:
            debug_print(f"Incorrect answer selected: {selected_answer}")
            self.lives -= 1
        
        if self.lives <= 0:
            self.game_over = True
        else:
            self.current_question_index += 1
        
        # self.last_question_id = current_question["question_id"]
        
        return {
            "is_correct": is_correct,
            "scripture_references": scripture_refs if scripture_refs else None
        }
    
    def next_question(self):
        """Advance to the next question, or mark game over if finished"""
        self.current_question_index += 1
        debug_print(f"Current bank index increased from {self.current_question_index - 1} to {self.current_question_index}")
        if self.current_question_index >= len(self.questions):
            return
        qid = self.questions[self.current_question_index]["question_id"]
        if qid in self.used_question_ids:
            return
            
    def at_end_of_round(self):
        """Decides what to do at the end of the round"""
        if self.current_question_index >= len(self.questions):
            if self.current_bank_index == 4:
                if self.score < 230:
                    self.game_over = True
        # Unfinished
    
    def is_game_over(self) -> bool:
        """Returns the game over status"""
        return self.game_over
    
    def save_progress(self):
        """Saves the current user's progress to the database"""
        conn, cursor = get_db_connection()
        
        try:
            cursor.execute("USE bible_trivia;")
            debug_print(f"Saving progress for user_id {self.user_id}")
            question_id_list = json.dumps([q["question_id"] for q in self.questions])
            
            if self.last_question_id is not None:
                cursor.execute("""
                            REPLACE INTO user_progress (user_id, current_bank_index, current_question, score, lives, time_remaining, last_question, num_questions_per_round, question_id_list)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (self.user_id, self.current_bank_index, self.current_question_index, self.score,
                              self.lives, self.time_remaining, self.last_question_id, self.num_questions_per_round, question_id_list))
            else:
                debug_print("No last question ID")
                cursor.execute("""
                            REPLACE INTO user_progress (user_id, current_bank_index, current_question, score, lives, time_remaining, num_questions_per_round, question_id_list)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (self.user_id, self.current_bank_index, self.current_question_index, self.score,
                              self.lives, self.time_remaining, self.num_questions_per_round, question_id_list))
            
            conn.commit()
        
        except mysql.connector.Error as e:
            debug_print(f"Database error in save_progress: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def load_progress(self):
        """Loads progress from the database"""
        conn, cursor = get_db_connection(dictionary=True)
        try:
            cursor.execute("USE bible_trivia;")
            cursor.execute("""
                SELECT current_bank_index, current_question, score, lives, time_remaining, last_question, num_questions_per_round, question_id_list
                FROM user_progress
                WHERE user_id = %s
            """, (self.user_id,))
            progress = cursor.fetchone()
            if progress:
                self.current_bank_index = progress["current_bank_index"]
                self.current_question_index = progress["current_question"]
                self.score = progress["score"]
                self.lives = progress["lives"]
                self.time_remaining = progress["time_remaining"]
                self.last_question_id = progress["last_question"]
                self.num_questions_per_round = progress.get("num_questions_per_round", 6)
                raw_qid_list = progress.get("question_id_list", "[]")
                if not raw_qid_list:
                    question_id_list = []
                else:
                    question_id_list = json.loads(raw_qid_list)

                if isinstance(question_id_list, int):
                    question_id_list = [question_id_list]
                elif isinstance(question_id_list, str):
                    question_id_list = [int(question_id_list)]

                if question_id_list:
                    self.questions = fetch_questions_by_ids(question_id_list, selected_bible_version=self.bible_version)
                    if self.last_question_id is not None:
                        for idx, q in enumerate(self.questions):
                            debug_print(f"Question ID: {q['question_id']}, Last Question ID: {self.last_question_id}")
                            if q["question_id"] == self.last_question_id:
                                debug_print(f"Match! Current question index set to {idx}")
                                self.current_question_index = idx
                                break
                else:
                    debug_print("No question ID list found")
                    return
        except mysql.connector.Error as e:
            debug_print(f"Database error in QuizManager.load_progress: {e}")
        finally:
            cursor.close()
            conn.close()


def fetch_all_questions(bank_id, shuffle=True, limit=None, selected_bible_version='NIV'):
    """Retrieve all questions (with answers) for a given question bank"""
    debug_print(f"fetch_all_questions() called with bank_id {bank_id}")
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
        
        # Organize answers under questions in a dictionary
        questions = {}
        for row in raw_data:
            q_id = row["question_id"]
            if q_id not in questions:
                questions[q_id] = {
                    "question_id": q_id,
                    "question_text": row["question_text"],
                    "answers": []
                }
            questions[q_id]["answers"].append({
                "answer_id": row["answer_id"],
                "answer_text": row["answer_text"],
                "is_correct": row["is_correct"],
                "bible_ref": row["bible_ref"]
            })
        
        all_questions = list(questions.values())
        if shuffle:
            random.shuffle(all_questions)
        if limit is not None:
            selected_questions = all_questions[:limit]
        else:
            selected_questions = all_questions
        
        return selected_questions  # Dictionary
    except mysql.connector.Error as e:
        print(f"Database error in fetch_all_questions: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def fetch_questions_by_ids(question_ids, selected_bible_version='NIV'):
    if not question_ids:
        return []

    if isinstance(question_ids, int):
        question_ids = [question_ids]

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

        # Organize answers under questions in a dictionary
        questions = {}
        for row in raw_data:
            q_id = row["question_id"]
            if q_id not in questions:
                questions[q_id] = {
                    "question_id": q_id,
                    "question_text": row["question_text"],
                    "answers": []
                }
            questions[q_id]["answers"].append({
                "answer_id": row["answer_id"],
                "answer_text": row["answer_text"],
                "is_correct": row["is_correct"],
                "bible_ref": row["bible_ref"]
            })
        
        # Return questions in the original order
        ordered_questions = [questions[qid] for qid in question_ids if qid in questions]
        return ordered_questions
    except mysql.connector.Error as e:
        debug_print(f"Database error in fetch_questions_by_ids: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

