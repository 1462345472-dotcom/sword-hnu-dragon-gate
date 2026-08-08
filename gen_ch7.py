# -*- coding: utf-8 -*-
import json

questions = []
terms = []
qid = 0

def add_q(qtype, question, options, answer, explanation, difficulty, tags):
    global qid
    qid += 1
    if qtype == "short":
        questions.append({"id": qid, "type": qtype, "question": question, "answer": answer, "explanation": explanation, "difficulty": difficulty, "tags": tags})
    else:
        questions.append({"id": qid, "type": qtype, "question": question, "options": options, "answer": answer, "explanation": explanation, "difficulty": difficulty, "tags": tags})

print("Starting Ch7 generation...")
