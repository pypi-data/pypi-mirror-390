"""
Data type definitions for Promptabs

Defines all the data models used in the survey system:
- Question: Individual survey question
- Survey: Complete survey with metadata
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Literal, Optional, Dict, Any


class Question(BaseModel):
    """Represents a single survey question with multiple options"""

    id: str = Field(
        ...,
        min_length=1,
        description="Unique identifier for the question"
    )
    title: str = Field(
        ...,
        min_length=1,
        description="Question title/heading"
    )
    question: str = Field(
        ...,
        min_length=1,
        description="Question text/prompt"
    )
    options: List[str] = Field(
        ...,
        min_length=2,
        description="List of answer options"
    )
    required: bool = Field(
        True,
        description="Whether the question must be answered (default: True, set False only if optional)"
    )
    type: Literal["single_choice", "multiple_choice"] = Field(
        "single_choice",
        description="Type of question: single or multiple choice"
    )

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "q1",
                "title": "Favorite Color",
                "question": "What is your favorite color?",
                "options": ["Red", "Blue", "Green"],
                "type": "single_choice"
            }
        }
    )

    @field_validator('options')
    @classmethod
    def validate_options(cls, v: List[str]) -> List[str]:
        """Validate that options list is non-empty and contains valid strings"""
        if not v or len(v) < 2:
            raise ValueError('Question must have at least 2 options')

        for i, opt in enumerate(v):
            if not isinstance(opt, str):
                raise ValueError(f'Option {i} must be a string, got {type(opt).__name__}')
            if not opt.strip():
                raise ValueError(f'Option {i} cannot be empty')

        return v

    @field_validator('type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate that question type is one of the allowed types"""
        if v not in ("single_choice", "multiple_choice"):
            raise ValueError(
                f"Invalid question type: '{v}'. "
                f"Must be one of: single_choice, multiple_choice"
            )
        return v

    @property
    def is_multiple_choice(self) -> bool:
        """Check if question is multiple choice"""
        return self.type == "multiple_choice"

class Survey(BaseModel):
    """Complete survey configuration with questions and metadata"""

    questions: List[Question] = Field(
        ...,
        min_length=1,
        description="List of survey questions"
    )
    title: Optional[str] = Field(
        None,
        description="Survey title"
    )
    description: Optional[str] = Field(
        None,
        description="Survey description"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata (version, author, tags, etc.)"
    )

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "title": "Customer Feedback Survey",
                "description": "Collect feedback from our customers",
                "metadata": {
                    "version": "1.0",
                    "author": "John Doe",
                    "tags": ["feedback", "customer"]
                },
                "questions": [
                    {
                        "id": "q1",
                        "title": "Satisfaction",
                        "question": "How satisfied are you?",
                        "options": ["Very satisfied", "Satisfied", "Neutral"],
                        "type": "single_choice"
                    }
                ]
            }
        }
    )


class Results(BaseModel):
    """Survey results containing user answers and optional feedback"""

    answers: Dict[str, Any] = Field(
        ...,
        description="Map of question IDs to user answers (str for single choice, List[str] for multiple choice)"
    )
    feedback: Optional[str] = Field(
        None,
        description="Optional additional feedback from the user"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "answers": {
                    "q1": "Red",
                    "q2": ["Python", "JavaScript"],
                    "q3": "Yes"
                },
                "feedback": "Great survey!"
            }
        }
    )
