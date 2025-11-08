"""Tests for Question model"""

import pytest
from promptabs.types import Question


def test_question_creation():
    """Test basic question creation"""
    q = Question(
        id="test_q",
        title="Test Question",
        question="What is your test?",
        options=["Option 1", "Option 2"],
    )
    assert q.id == "test_q"
    assert q.title == "Test Question"
    assert q.question == "What is your test?"
    assert q.options == ["Option 1", "Option 2"]


def test_question_with_question_field():
    """Test question with question field"""
    q = Question(
        id="q1",
        title="Title",
        question="This is the question statement",
        options=["A", "B"],
    )
    assert q.question == "This is the question statement"


def test_question_validation_empty_id():
    """Test that empty ID raises validation error"""
    with pytest.raises(ValueError):
        Question(
            id="",
            title="Title",
            question="Question?",
            options=["A", "B"],
        )


def test_question_validation_empty_title():
    """Test that empty title raises validation error"""
    with pytest.raises(ValueError):
        Question(
            id="q1",
            title="",
            question="What is this?",
            options=["A", "B"],
        )


def test_question_validation_single_option():
    """Test that single option raises validation error"""
    with pytest.raises(ValueError):
        Question(
            id="q1",
            title="Title",
            question="What is this?",
            options=["A"],
        )


def test_question_validation_empty_options():
    """Test that empty options raises validation error"""
    with pytest.raises(ValueError):
        Question(
            id="q1",
            title="Title",
            question="What is this?",
            options=[],
        )
