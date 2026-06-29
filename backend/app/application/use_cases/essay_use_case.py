import json
import logging
from uuid import UUID

from app.application.ports.outbound.quiz_repository import IEssaySubmissionRepository
from app.application.ports.outbound.ai_repository import IAITaskRepository
from app.application.ports.outbound.llm_service import ILLMService

logger = logging.getLogger(__name__)


class EssayUseCase:
    def __init__(
        self,
        essay_repo: IEssaySubmissionRepository,
        task_repo: IAITaskRepository,
        llm_service: ILLMService,
    ):
        self._essay_repo = essay_repo
        self._task_repo = task_repo
        self._llm_service = llm_service

    async def grade_submission_async(self, submission_id: UUID, ai_task_id: UUID | None) -> dict:
        """
        Process the grading using AI.
        """
        # 1. Idempotency Check & Status Update
        if ai_task_id:
            task = await self._task_repo.get_by_id(ai_task_id)
            if task and task.status == "completed":
                return {"status": "already_completed"}
            if task:
                await self._task_repo.update_status(task, status="processing")

        # 2. Fetch Submission & Rubric
        submission = await self._essay_repo.get_by_id(submission_id)
        if not submission:
            raise ValueError(f"EssaySubmission {submission_id} not found")

        rubric = submission.rubric
        if not rubric:
            raise ValueError("Submission has no associated rubric")

        # 3. Prepare Prompt & Call LLM
        criteria_str = json.dumps(rubric.criteria_matrix, ensure_ascii=False, indent=2)
        prompt = (
            "You are an expert teacher grading a student's essay based on a specific rubric.\n"
            f"Rubric Title: {rubric.title}\n"
            f"Criteria Matrix:\n{criteria_str}\n\n"
            f"Student Essay Content:\n{submission.content}\n\n"
            "Task: Grade the essay according to the criteria matrix. For each criterion, provide detailed feedback and a score.\n"
            "Then, provide a final total score.\n"
            "You MUST respond with ONLY a valid JSON object in the exact format below, with no markdown formatting, no comments, and no extra text:\n"
            "{\n"
            '  "criteria_feedback": { "criterion_name": "feedback string" },\n'
            '  "score": 8.5,\n'
            '  "general_comment": "overall feedback"\n'
            "}"
        )

        response_text = await self._llm_service.generate(prompt, temperature=0.1)

        # Clean markdown JSON block
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "", 1)
        if response_text.endswith("```"):
            response_text = response_text.rsplit("```", 1)[0]
        
        try:
            ai_feedback = json.loads(response_text.strip())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {response_text}")
            raise ValueError(f"LLM did not return valid JSON: {e}")

        score = float(ai_feedback.get("score", 0.0))
        
        # 4. Save results
        await self._essay_repo.update_feedback(submission, ai_feedback, score)

        # 5. Update Task
        if ai_task_id and task:
            await self._task_repo.update_status(
                task, status="completed", result_payload={"score": score}
            )

        return {"status": "success", "score": score}
