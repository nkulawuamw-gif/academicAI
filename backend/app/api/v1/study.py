from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.study import (
    QuizGenerateRequest, QuizResponse, QuizQuestionResponse, QuizAnswerSubmission,
    QuizResultResponse, FlashcardGenerateRequest, FlashcardSetResponse,
    FlashcardResponse, NoteSummarizeRequest, NoteSummarizeResponse,
    StudyPlanGenerateRequest, StudyPlanResponse, StudyTaskResponse,
)
from app.api.deps import get_current_user
from app.models.user import User
from app.services.study_service import StudyService

router = APIRouter(prefix="/study", tags=["Study Tools"])


@router.post("/quizzes/generate", response_model=QuizResponse)
async def generate_quiz(
    request: QuizGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = StudyService(db)
    quiz = await service.generate_quiz(
        user_id=current_user.id,
        topic=request.topic,
        difficulty=request.difficulty,
        question_count=request.question_count,
        question_types=request.question_types,
    )
    questions = []
    for q in quiz.questions:
        questions.append(QuizQuestionResponse(
            id=str(q.id), question_type=q.question_type.value if hasattr(q.question_type, 'value') else q.question_type,
            question_text=q.question_text, options=q.options,
            correct_answer=q.correct_answer, explanation=q.explanation,
            points=q.points, order=q.order,
        ))

    return QuizResponse(
        id=str(quiz.id), title=quiz.title, topic=quiz.topic,
        difficulty=quiz.difficulty.value if hasattr(quiz.difficulty, 'value') else quiz.difficulty,
        question_count=quiz.question_count, score=quiz.score,
        total_points=quiz.total_points, questions=questions,
        created_at=quiz.created_at,
    )


@router.post("/quizzes/{quiz_id}/submit", response_model=QuizResultResponse)
async def submit_quiz(
    quiz_id: str,
    request: QuizAnswerSubmission,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = StudyService(db)
    return await service.submit_quiz_answers(quiz_id, current_user.id, request.answers)


@router.get("/quizzes/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
    quiz_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = StudyService(db)
    quiz = await service.get_quiz(quiz_id, current_user.id)
    questions = []
    for q in quiz.questions:
        questions.append(QuizQuestionResponse(
            id=str(q.id), question_type=q.question_type.value if hasattr(q.question_type, 'value') else q.question_type,
            question_text=q.question_text, options=q.options,
            correct_answer=q.correct_answer, explanation=q.explanation,
            points=q.points, order=q.order,
        ))
    return QuizResponse(
        id=str(quiz.id), title=quiz.title, topic=quiz.topic,
        difficulty=quiz.difficulty.value if hasattr(quiz.difficulty, 'value') else quiz.difficulty,
        question_count=quiz.question_count, score=quiz.score,
        total_points=quiz.total_points, questions=questions,
        created_at=quiz.created_at,
    )


@router.post("/flashcards/generate", response_model=FlashcardSetResponse)
async def generate_flashcards(
    request: FlashcardGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = StudyService(db)
    fs = await service.generate_flashcards(current_user.id, request.topic, request.count)
    return FlashcardSetResponse(
        id=str(fs.id), title=fs.title, topic=fs.topic,
        flashcards=[
            FlashcardResponse(
                id=str(f.id), front=f.front, back=f.back,
                difficulty=f.difficulty.value if hasattr(f.difficulty, 'value') else f.difficulty,
            )
            for f in fs.flashcards
        ],
        created_at=fs.created_at,
    )


@router.get("/flashcards/{flashcard_set_id}", response_model=FlashcardSetResponse)
async def get_flashcard_set(
    flashcard_set_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = StudyService(db)
    fs = await service.get_flashcard_set(flashcard_set_id, current_user.id)
    return FlashcardSetResponse(
        id=str(fs.id), title=fs.title, topic=fs.topic,
        flashcards=[
            FlashcardResponse(
                id=str(f.id), front=f.front, back=f.back,
                difficulty=f.difficulty.value if hasattr(f.difficulty, 'value') else f.difficulty,
            )
            for f in fs.flashcards
        ],
        created_at=fs.created_at,
    )


@router.post("/summarize", response_model=NoteSummarizeResponse)
async def summarize_notes(
    request: NoteSummarizeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = StudyService(db)
    return await service.summarize_notes(request.text, request.format, request.detail_level)


@router.post("/study-plans/generate", response_model=StudyPlanResponse)
async def generate_study_plan(
    request: StudyPlanGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = StudyService(db)
    plan = await service.generate_study_plan(
        user_id=current_user.id,
        subject=request.subject,
        start_date=request.start_date,
        end_date=request.end_date,
        hours_per_day=request.hours_per_day,
        topics=request.topics,
    )
    return StudyPlanResponse(
        id=str(plan.id), title=plan.title, subject=plan.subject,
        start_date=plan.start_date, end_date=plan.end_date,
        hours_per_day=plan.hours_per_day,
        tasks=[
            StudyTaskResponse(
                id=str(t.id), title=t.title, description=t.description,
                scheduled_date=t.scheduled_date, duration_minutes=t.duration_minutes,
                is_completed=t.is_completed, order=t.order,
            )
            for t in plan.tasks
        ],
        created_at=plan.created_at,
    )


@router.get("/study-plans/{study_plan_id}", response_model=StudyPlanResponse)
async def get_study_plan(
    study_plan_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = StudyService(db)
    plan = await service.get_study_plan(study_plan_id, current_user.id)
    return StudyPlanResponse(
        id=str(plan.id), title=plan.title, subject=plan.subject,
        start_date=plan.start_date, end_date=plan.end_date,
        hours_per_day=plan.hours_per_day,
        tasks=[
            StudyTaskResponse(
                id=str(t.id), title=t.title, description=t.description,
                scheduled_date=t.scheduled_date, duration_minutes=t.duration_minutes,
                is_completed=t.is_completed, order=t.order,
            )
            for t in plan.tasks
        ],
        created_at=plan.created_at,
    )
