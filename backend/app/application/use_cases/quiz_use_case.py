import uuid
from typing import Any

from app.application.ports.outbound.quiz_repository import (
    IQuizRepository,
    IQuizAttemptRepository,
)
from app.domain.exceptions import (
    QuizNotFoundError,
    QuizAttemptNotFoundError,
    PermissionDeniedError,
    QuizAttemptAlreadySubmittedError,
)
from app.domain.models.quiz import QuizAttempt, StudentAnswer
from app.domain.models.user import User

import logging

logger = logging.getLogger(__name__)


class QuizUseCase:
    """
    Use Case cho Quiz Attempt logic.
    """

    def __init__(
        self, quiz_repo: IQuizRepository, attempt_repo: IQuizAttemptRepository
    ) -> None:
        self._quiz_repo = quiz_repo
        self._attempt_repo = attempt_repo

    async def start_attempt(self, quiz_id: uuid.UUID, student: User) -> QuizAttempt:
        """
        Học sinh bắt đầu làm bài quiz.
        """
        quiz = await self._quiz_repo.get_by_id(quiz_id)
        if not quiz:
            logger.warning(f"Failed to start attempt: Quiz {quiz_id} not found")
            raise QuizNotFoundError(f"Quiz {quiz_id} không tồn tại")
        
        attempt = await self._attempt_repo.create(
            student_id=student.id, quiz_id=quiz_id
        )
        logger.info(f"Student {student.id} started attempt {attempt.id} for quiz {quiz_id}")
        return attempt

    async def submit_attempt(
        self, attempt_id: uuid.UUID, student: User, answers: dict[uuid.UUID, uuid.UUID]
    ) -> QuizAttempt:
        """
        Học sinh nộp bài quiz.
        answers: dictionary mapping question_id -> answer_id.
        """
        attempt = await self._attempt_repo.get_by_id(attempt_id)
        if not attempt:
            logger.warning(f"Failed to submit attempt: Attempt {attempt_id} not found")
            raise QuizAttemptNotFoundError("Không tìm thấy lượt làm bài")
        if attempt.student_id != student.id:
            logger.warning(f"Permission denied: Student {student.id} tried to submit attempt {attempt_id}")
            raise PermissionDeniedError("Không có quyền nộp bài này")
        if attempt.completed_at is not None:
            logger.warning(f"Attempt already submitted: Attempt {attempt_id}")
            raise QuizAttemptAlreadySubmittedError("Lượt làm bài đã được nộp")

        quiz = await self._quiz_repo.get_by_id(attempt.quiz_id)
        if not quiz:
            logger.warning(f"Failed to submit attempt: Quiz {attempt.quiz_id} not found")
            raise QuizNotFoundError("Quiz không tồn tại")

        correct_count = 0
        total_questions = len(quiz.questions)

        # Lấy đáp án đúng cho mỗi câu
        correct_answers_map = {}
        for q in quiz.questions:
            for ans in q.answers:
                if ans.is_correct:
                    correct_answers_map[q.id] = ans.id
                    break

        for q in quiz.questions:
            selected_ans_id = answers.get(q.id)
            # Chú ý: Cần convert UUID nếu dạng string
            if isinstance(selected_ans_id, str):
                selected_ans_id = uuid.UUID(selected_ans_id)
                
            is_correct = False
            if selected_ans_id and correct_answers_map.get(q.id) == selected_ans_id:
                is_correct = True
                correct_count += 1
                
            student_answer = StudentAnswer(
                attempt_id=attempt.id,
                question_id=q.id,
                selected_answer_id=selected_ans_id,
                is_correct=is_correct,
            )
            attempt.student_answers.append(student_answer)

        score = (correct_count / total_questions) * 100 if total_questions > 0 else 0.0

        completed_attempt = await self._attempt_repo.complete(attempt, score)
        logger.info(f"Student {student.id} submitted attempt {attempt_id} with score {score}")
        return completed_attempt
