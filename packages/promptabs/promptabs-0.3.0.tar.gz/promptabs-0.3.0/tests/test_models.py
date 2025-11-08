"""Tests for Question, Survey, and Results models"""

import json
import tempfile
from pathlib import Path
import pytest
from promptabs import Survey, Question, Results, SurveyRunner


# Question tests

def test_question_from_json():
    """Test loading a question from JSON dict"""
    q_data = {
        "id": "q1",
        "title": "Language",
        "question": "What is your favorite programming language?",
        "options": ["Python", "JavaScript", "Go"]
    }
    q = Question.model_validate(q_data)
    assert q.id == "q1"
    assert q.title == "Language"
    assert q.question == "What is your favorite programming language?"
    assert q.options == ["Python", "JavaScript", "Go"]
    assert q.type == "single_choice"
    assert q.required is True  # default value


def test_multiple_choice_question():
    """Test loading multiple choice question"""
    q_data = {
        "id": "languages",
        "title": "Languages",
        "question": "Which languages do you know?",
        "type": "multiple_choice",
        "options": ["Python", "JavaScript", "Go", "Rust"]
    }
    q = Question.model_validate(q_data)
    assert q.type == "multiple_choice"
    assert q.required is True  # default value
    assert len(q.options) == 4


def test_question_validation_missing_fields():
    """Test that missing required fields raises error"""
    with pytest.raises(ValueError):
        Question.model_validate({
            "id": "q1",
            "title": "Q1",
            # missing "question" and "options"
        })


def test_question_validation_invalid_options():
    """Test that invalid options raise error"""
    with pytest.raises(ValueError):
        Question.model_validate({
            "id": "q1",
            "title": "Q1",
            "question": "Q?",
            "options": ["A"]  # Only 1 option, need at least 2
        })


def test_question_validation_invalid_type():
    """Test that invalid question type raises error"""
    with pytest.raises(ValueError):
        Question.model_validate({
            "id": "q1",
            "title": "Q1",
            "question": "Q?",
            "options": ["A", "B"],
            "type": "invalid_type"
        })


# Survey tests

def test_survey_from_json_string():
    """Test loading a survey from JSON string"""
    json_str = '''
    {
      "title": "My Survey",
      "description": "A test survey",
      "questions": [
        {
          "id": "q1",
          "title": "Language",
          "question": "What is your favorite programming language?",
          "options": ["Python", "JavaScript", "Go"]
        }
      ]
    }
    '''
    survey = Survey.model_validate_json(json_str)
    assert survey.title == "My Survey"
    assert survey.description == "A test survey"
    assert len(survey.questions) == 1
    assert survey.questions[0].id == "q1"


def test_survey_minimal_json():
    """Test loading survey with just questions (minimal format)"""
    json_str = '''
    {
      "questions": [
        {
          "id": "q1",
          "title": "Language",
          "question": "What is your favorite programming language?",
          "options": ["Python", "JavaScript", "Go"]
        }
      ]
    }
    '''
    survey = Survey.model_validate_json(json_str)
    assert survey.title is None
    assert survey.description is None
    assert len(survey.questions) == 1


def test_survey_with_metadata():
    """Test loading survey with metadata"""
    json_str = '''
    {
      "title": "Feedback Survey",
      "description": "Customer feedback",
      "metadata": {
        "version": "1.0",
        "author": "John Doe",
        "tags": ["feedback", "survey"]
      },
      "questions": [
        {
          "id": "q1",
          "title": "Satisfaction",
          "question": "How satisfied are you?",
          "options": ["Very", "OK", "Not"],
          "required": true
        }
      ]
    }
    '''
    survey = Survey.model_validate_json(json_str)
    assert survey.metadata["version"] == "1.0"
    assert survey.metadata["author"] == "John Doe"
    assert survey.metadata["tags"] == ["feedback", "survey"]
    assert survey.questions[0].required is True


def test_multiple_questions():
    """Test loading survey with multiple questions"""
    json_str = '''
    {
      "questions": [
        {
          "id": "q1",
          "title": "Q1",
          "question": "First?",
          "options": ["A", "B"]
        },
        {
          "id": "q2",
          "title": "Q2",
          "question": "Second?",
          "options": ["X", "Y"]
        }
      ]
    }
    '''
    survey = Survey.model_validate_json(json_str)
    assert len(survey.questions) == 2
    assert survey.questions[0].id == "q1"
    assert survey.questions[1].id == "q2"


def test_survey_validation_empty_questions():
    """Test that survey with no questions raises error"""
    with pytest.raises(ValueError):
        Survey.model_validate({
            "questions": []
        })


def test_survey_validation_missing_questions():
    """Test that survey without questions key raises error"""
    with pytest.raises(ValueError):
        Survey.model_validate({
            "title": "Survey"
        })


def test_survey_file_loading(tmp_path):
    """Test loading survey from file"""
    json_data = {
        "title": "File Survey",
        "questions": [
            {
                "id": "q1",
                "title": "Q1",
                "question": "Question 1?",
                "options": ["A", "B"]
            }
        ]
    }

    # Use pytest's tmp_path fixture
    json_file = tmp_path / "survey.json"
    json_file.write_text(json.dumps(json_data))

    runner = SurveyRunner.from_json_file(str(json_file))
    assert len(runner.questions) == 1
    assert runner.questions[0].id == "q1"


# Results tests

def test_results_creation():
    """Test creating Results object"""
    results = Results(
        answers={
            "q1": "Python",
            "q2": ["A", "B"]
        },
        feedback="Great survey!"
    )
    assert results.answers["q1"] == "Python"
    assert results.answers["q2"] == ["A", "B"]
    assert results.feedback == "Great survey!"


def test_results_without_feedback():
    """Test Results object without feedback"""
    results = Results(
        answers={
            "q1": "Option A",
            "q2": "Option B"
        }
    )
    assert results.answers["q1"] == "Option A"
    assert results.feedback is None


def test_results_json_serialization():
    """Test Results object can be serialized to JSON"""
    results = Results(
        answers={
            "q1": "Python",
            "q2": ["JavaScript", "Go"]
        },
        feedback="Good questions"
    )
    json_str = results.model_dump_json()
    assert isinstance(json_str, str)

    # Verify JSON contains expected data
    data = json.loads(json_str)
    assert data["answers"]["q1"] == "Python"
    assert data["answers"]["q2"] == ["JavaScript", "Go"]
    assert data["feedback"] == "Good questions"


def test_results_json_deserialization():
    """Test Results object can be created from JSON"""
    json_data = {
        "answers": {
            "q1": "Choice A",
            "q2": ["Option 1", "Option 2"]
        },
        "feedback": "Helpful feedback"
    }
    results = Results.model_validate(json_data)
    assert results.answers["q1"] == "Choice A"
    assert results.answers["q2"] == ["Option 1", "Option 2"]
    assert results.feedback == "Helpful feedback"
