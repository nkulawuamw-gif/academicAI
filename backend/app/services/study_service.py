import uuid
from datetime import datetime, timezone, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.study import (
    Quiz, QuizQuestion, QuestionType, Difficulty,
    FlashcardSet, Flashcard, StudyPlan, StudyTask,
)
from app.services.llm_service import LLMService
from app.core.exceptions import NotFoundException
from loguru import logger
from typing import Optional


class StudyService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm = LLMService()

    async def generate_quiz(self, user_id: uuid.UUID, topic: str, difficulty: str = "medium",
                             question_count: int = 10, question_types: list = None) -> Quiz:
        system_prompt = f"Generate a {difficulty} difficulty quiz on {topic} with {question_count} questions."
        prompt = f"Create {question_count} quiz questions about {topic}. Include questions, answers, and explanations."

        content = await self.llm.generate(prompt, system_prompt=system_prompt)

        quiz = Quiz(
            id=uuid.uuid4(),
            user_id=user_id,
            title=f"Quiz: {topic[:50]}",
            topic=topic,
            difficulty=Difficulty(difficulty),
            question_count=question_count,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.db.add(quiz)

        for i in range(question_count):
            question = QuizQuestion(
                id=uuid.uuid4(),
                quiz_id=quiz.id,
                question_type=QuestionType.MULTIPLE_CHOICE,
                question_text=f"Question {i+1} about {topic}?",
                options=[f"Option A for Q{i+1}", f"Option B for Q{i+1}", f"Option C for Q{i+1}", f"Option D for Q{i+1}"],
                correct_answer="A",
                explanation=f"This is the correct answer because...",
                points=1,
                order=i,
            )
            self.db.add(question)

        await self.db.flush()
        return quiz

    async def get_quiz(self, quiz_id: str, user_id: uuid.UUID) -> Quiz:
        result = await self.db.execute(
            select(Quiz).where(Quiz.id == quiz_id, Quiz.user_id == user_id)
        )
        quiz = result.scalar_one_or_none()
        if not quiz:
            raise NotFoundException("Quiz not found")
        return quiz

    async def submit_quiz_answers(self, quiz_id: str, user_id: uuid.UUID, answers: dict) -> dict:
        quiz = await self.get_quiz(quiz_id, user_id)
        questions = await self._get_questions(quiz_id)

        score = 0
        total = len(questions)
        results = {}

        for q in questions:
            q_id = str(q.id)
            user_answer = answers.get(q_id, "")
            correct = user_answer == q.correct_answer
            if correct:
                score += q.points
            results[q_id] = {
                "correct": correct,
                "user_answer": user_answer,
                "correct_answer": q.correct_answer,
            }

        quiz.score = score
        quiz.total_points = total
        await self.db.flush()

        return {
            "quiz_id": quiz_id,
            "score": score,
            "total_points": total,
            "percentage": round((score / total * 100), 2) if total > 0 else 0,
            "answers": results,
        }

    async def _get_questions(self, quiz_id: str) -> list[QuizQuestion]:
        result = await self.db.execute(
            select(QuizQuestion).where(QuizQuestion.quiz_id == quiz_id).order_by(QuizQuestion.order)
        )
        return result.scalars().all()

    async def generate_flashcards(self, user_id: uuid.UUID, topic: str, count: int = 10) -> FlashcardSet:
        flashcard_set = FlashcardSet(
            id=uuid.uuid4(),
            user_id=user_id,
            title=f"Flashcards: {topic[:50]}",
            topic=topic,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(flashcard_set)

        for i in range(count):
            flashcard = Flashcard(
                id=uuid.uuid4(),
                flashcard_set_id=flashcard_set.id,
                front=f"Term {i+1}: Key concept about {topic}",
                back=f"Definition {i+1}: Detailed explanation of the concept related to {topic}",
                difficulty=Difficulty.MEDIUM,
                times_reviewed=0,
            )
            self.db.add(flashcard)

        await self.db.flush()
        return flashcard_set

    async def get_flashcard_set(self, flashcard_set_id: str, user_id: uuid.UUID) -> FlashcardSet:
        result = await self.db.execute(
            select(FlashcardSet).where(FlashcardSet.id == flashcard_set_id, FlashcardSet.user_id == user_id)
        )
        fs = result.scalar_one_or_none()
        if not fs:
            raise NotFoundException("Flashcard set not found")
        return fs

    async def summarize_notes(self, text: str, format_type: str = "bullets", detail_level: str = "moderate") -> dict:
        system_prompt = f"Summarize the following text in {format_type} format with {detail_level} detail."
        prompt = f"Text to summarize:\n\n{text}"

        summary = await self.llm.generate(prompt, system_prompt=system_prompt)
        key_points = [line.strip("- ") for line in summary.split("\n") if line.strip().startswith("-")][:10]

        return {
            "original_length": len(text),
            "summary_length": len(summary),
            "summary": summary,
            "key_points": key_points or [summary[:200]],
        }

    async def generate_study_plan(self, user_id: uuid.UUID, subject: str, start_date: date,
                                   end_date: date, hours_per_day: float = 2.0, topics: list = None) -> StudyPlan:
        study_plan = StudyPlan(
            id=uuid.uuid4(),
            user_id=user_id,
            title=f"Study Plan: {subject}",
            subject=subject,
            start_date=start_date,
            end_date=end_date,
            hours_per_day=hours_per_day,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(study_plan)

        from datetime import timedelta
        total_days = (end_date - start_date).days
        for day in range(min(total_days, 30)):
            current_date = start_date + timedelta(days=day)
            topic_name = topics[day % len(topics)] if topics else f"Topic {day + 1}"
            task = StudyTask(
                id=uuid.uuid4(),
                study_plan_id=study_plan.id,
                title=f"Study: {topic_name}",
                description=f"Study session covering {topic_name}",
                scheduled_date=current_date,
                duration_minutes=int(hours_per_day * 60),
                is_completed=False,
                order=day,
            )
            self.db.add(task)

        await self.db.flush()
        return study_plan

    async def get_study_plan(self, study_plan_id: str, user_id: uuid.UUID) -> StudyPlan:
        result = await self.db.execute(
            select(StudyPlan).where(StudyPlan.id == study_plan_id, StudyPlan.user_id == user_id)
        )
        plan = result.scalar_one_or_none()
        if not plan:
            raise NotFoundException("Study plan not found")
        return plan
