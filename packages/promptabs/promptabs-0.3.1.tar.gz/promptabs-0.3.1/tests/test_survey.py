"""Tests for SurveyRunner and Page classes"""

import pytest
from promptabs.survey import SurveyRunner
from promptabs.types import Question, Survey
from promptabs.page import QuestionPage, SubmitPage
from promptabs.input_handler import InputHandler


def create_sample_survey():
    """Helper to create sample survey"""
    return Survey(
        questions=[
            Question(
                id="q1",
                title="Question 1",
                question="What is option 1?",
                options=["A", "B", "C"],
                type="single_choice"
            ),
            Question(
                id="q2",
                title="Question 2",
                question="What is option 2?",
                options=["X", "Y"],
                type="multiple_choice"
            ),
        ]
    )


def test_survey_creation():
    """Test survey creation"""
    survey_obj = create_sample_survey()
    runner = SurveyRunner(survey_obj)
    assert len(runner.questions) == 2
    assert runner.current_tab_index == 0


def test_survey_validation_empty_questions():
    """Test that empty questions list raises ValueError"""
    with pytest.raises(ValueError):
        SurveyRunner(Survey(questions=[]))


def test_survey_tab_navigation():
    """Test moving between tabs using handle_key"""
    survey_obj = create_sample_survey()
    runner = SurveyRunner(survey_obj)
    num_tabs = len(survey_obj.questions) + 1  # 2 questions + 1 submit tab = 3 tabs

    # Start at tab 0
    assert runner.current_tab_index == 0

    # Move to next tab using ARROW_RIGHT
    runner.handle_key(InputHandler.ARROW_RIGHT)
    assert runner.current_tab_index == 1

    # Move to next tab again (reaches submit tab)
    runner.handle_key(InputHandler.ARROW_RIGHT)
    assert runner.current_tab_index == 2

    # Move to next tab wraps around to first tab
    runner.handle_key(InputHandler.ARROW_RIGHT)
    assert runner.current_tab_index == 0

    # Move to previous tab using ARROW_LEFT
    runner.handle_key(InputHandler.ARROW_LEFT)
    assert runner.current_tab_index == 2  # Wraps to submit tab

    # Move to previous tab
    runner.handle_key(InputHandler.ARROW_LEFT)
    assert runner.current_tab_index == 1


def test_survey_enter_auto_advance_single_choice():
    """Test that ENTER on single choice question auto-advances to next tab"""
    survey_obj = create_sample_survey()
    runner = SurveyRunner(survey_obj)

    # Start at tab 0 (first single choice question)
    assert runner.current_tab_index == 0
    assert isinstance(runner.pages[0], QuestionPage)

    # Press ENTER on single choice question
    result = runner.handle_key(InputHandler.ENTER)
    assert result == True  # SurveyRunner handled it
    assert runner.current_tab_index == 1  # Auto-advanced to next tab


def test_survey_enter_no_advance_multiple_choice():
    """Test that ENTER on multiple choice question does not auto-advance"""
    survey_obj = create_sample_survey()
    runner = SurveyRunner(survey_obj)

    # Move to tab 1 (multiple choice question)
    runner.handle_key(InputHandler.ARROW_RIGHT)
    assert runner.current_tab_index == 1
    assert isinstance(runner.pages[1], QuestionPage)
    assert runner.pages[1].question.is_multiple_choice

    # Press ENTER on multiple choice question
    result = runner.handle_key(InputHandler.ENTER)
    assert result == False  # SurveyRunner did not handle it
    assert runner.current_tab_index == 1  # Did not advance


def test_question_page_option_navigation():
    """Test moving between options on QuestionPage"""
    survey_obj = create_sample_survey()
    q_page = QuestionPage(survey_obj.questions[0])

    # Start at option 0
    assert q_page.current_index == 0

    # Move to next option
    q_page.handle_key(InputHandler.ARROW_DOWN)
    assert q_page.current_index == 1

    # Move to next option
    q_page.handle_key(InputHandler.ARROW_DOWN)
    assert q_page.current_index == 2

    # Move to custom input field (4th item)
    q_page.handle_key(InputHandler.ARROW_DOWN)
    assert q_page.current_index == 3

    # Wrap around to first option
    q_page.handle_key(InputHandler.ARROW_DOWN)
    assert q_page.current_index == 0

    # Move to previous option
    q_page.handle_key(InputHandler.ARROW_UP)
    assert q_page.current_index == 3  # Wraps to custom input field


def test_question_page_confirm_selection():
    """Test confirming option selection on QuestionPage"""
    survey_obj = create_sample_survey()
    q_page = QuestionPage(survey_obj.questions[0])

    assert q_page.selected_indexes == set()

    # Select first option (A) using SPACE
    q_page.handle_key(InputHandler.SPACE)
    assert q_page.selected_indexes == {0}

    # Get result
    result = q_page.get_result()
    assert result["q1"] == "A"


def test_question_page_enter_single_choice():
    """Test ENTER key on single choice question (should not be handled by page)"""
    survey_obj = create_sample_survey()
    q_page = QuestionPage(survey_obj.questions[0])

    # ENTER on single choice returns False (to let SurveyRunner handle tab navigation)
    result = q_page.handle_key(InputHandler.ENTER)
    assert result == False
    # But it should still select the current option
    assert q_page.selected_indexes == {0}

    # Move to second option and press ENTER again
    q_page.handle_key(InputHandler.ARROW_DOWN)
    result = q_page.handle_key(InputHandler.ENTER)
    assert result == False
    assert q_page.selected_indexes == {1}


def test_question_page_enter_multiple_choice():
    """Test ENTER key on multiple choice question (should behave like SPACE)"""
    survey_obj = create_sample_survey()
    q_page = QuestionPage(survey_obj.questions[1])  # Multiple choice

    # ENTER on multiple choice returns True (handled by page)
    result = q_page.handle_key(InputHandler.ENTER)
    assert result == True
    assert q_page.selected_indexes == {0}

    # Move to next option and press ENTER again
    q_page.handle_key(InputHandler.ARROW_DOWN)
    result = q_page.handle_key(InputHandler.ENTER)
    assert result == True
    assert q_page.selected_indexes == {0, 1}


def test_question_page_selection_with_different_option():
    """Test selecting different option (single choice)"""
    survey_obj = create_sample_survey()
    q_page = QuestionPage(survey_obj.questions[0])

    # Select first option
    q_page.handle_key(InputHandler.SPACE)
    assert q_page.selected_indexes == {0}

    # Move to second option
    q_page.handle_key(InputHandler.ARROW_DOWN)
    assert q_page.current_index == 1

    # Select second option (should replace first)
    q_page.handle_key(InputHandler.SPACE)
    assert q_page.selected_indexes == {1}

    result = q_page.get_result()
    assert result["q1"] == "B"


def test_question_page_multiple_choice():
    """Test multiple choice selection"""
    survey_obj = create_sample_survey()
    q_page = QuestionPage(survey_obj.questions[1])  # Multiple choice question

    # Select first option (X) at index 0
    q_page.handle_key(InputHandler.SPACE)
    assert 0 in q_page.selected_indexes

    # Move to second option (Y)
    q_page.handle_key(InputHandler.ARROW_DOWN)
    assert q_page.current_index == 1

    # Select second option (Y) at index 1
    q_page.handle_key(InputHandler.SPACE)
    assert 1 in q_page.selected_indexes

    result = q_page.get_result()
    # Result should be sorted
    assert set(result["q2"]) == {"X", "Y"}


def test_question_page_toggle_selection():
    """Test toggling selection in multiple choice"""
    survey_obj = create_sample_survey()
    q_page = QuestionPage(survey_obj.questions[1])  # Multiple choice

    # Select first option
    q_page.handle_key(InputHandler.SPACE)
    assert q_page.selected_indexes == {0}

    # Toggle it off
    q_page.handle_key(InputHandler.SPACE)
    assert q_page.selected_indexes == set()

    # Select it again
    q_page.handle_key(InputHandler.SPACE)
    assert q_page.selected_indexes == {0}


def test_submit_page_navigation():
    """Test navigation on SubmitPage"""
    survey_obj = create_sample_survey()
    submit_page = SubmitPage(question_pages=[])

    # Start at option 1 (Submit button) - default selection
    assert submit_page.submit_option_index == 1

    # Move down to option 2 (Cancel button)
    submit_page.handle_key(InputHandler.ARROW_DOWN)
    assert submit_page.submit_option_index == 2

    # Move down wraps to option 0 (Feedback field)
    submit_page.handle_key(InputHandler.ARROW_DOWN)
    assert submit_page.submit_option_index == 0

    # Move down to option 1 (Submit button)
    submit_page.handle_key(InputHandler.ARROW_DOWN)
    assert submit_page.submit_option_index == 1

    # Move up to option 0 (Feedback field)
    submit_page.handle_key(InputHandler.ARROW_UP)
    assert submit_page.submit_option_index == 0


def test_submit_page_feedback_input():
    """Test feedback input on SubmitPage"""
    survey_obj = create_sample_survey()
    submit_page = SubmitPage(question_pages=[])

    # Navigate to feedback field (start at 1, go up to 0)
    submit_page.handle_key(InputHandler.ARROW_UP)  # 1 -> 0 (Feedback)

    # Activate feedback input
    submit_page.handle_key(InputHandler.ENTER)
    assert submit_page.feedback_field.input_active == True

    # Type some text
    submit_page.handle_key('H')
    submit_page.handle_key('i')
    assert submit_page.feedback_field.get_value() == "Hi"

    # Confirm feedback
    submit_page.handle_key(InputHandler.ENTER)
    assert submit_page.feedback_field.input_active == False
    assert submit_page.feedback_field.get_value() == "Hi"


def test_submit_page_feedback_cursor_movement():
    """Test cursor movement in feedback input"""
    survey_obj = create_sample_survey()
    submit_page = SubmitPage(question_pages=[])

    # Enter feedback mode (start at 1, go up to 0)
    submit_page.handle_key(InputHandler.ARROW_UP)  # 1 -> 0 (Feedback)
    submit_page.handle_key(InputHandler.ENTER)

    # Type text
    submit_page.handle_key('T')
    submit_page.handle_key('e')
    submit_page.handle_key('s')
    submit_page.handle_key('t')
    assert submit_page.feedback_field.get_value() == "Test"
    assert submit_page.feedback_field.cursor_pos == 4

    # Move cursor left (4 -> 3)
    submit_page.handle_key(InputHandler.ARROW_LEFT)
    assert submit_page.feedback_field.cursor_pos == 3

    # Move cursor left again (3 -> 2)
    submit_page.handle_key(InputHandler.ARROW_LEFT)
    assert submit_page.feedback_field.cursor_pos == 2

    # Type character 'X' at position 2 (between 'Te' and 'st')
    submit_page.handle_key('X')
    assert submit_page.feedback_field.get_value() == "TeXst"
    assert submit_page.feedback_field.cursor_pos == 3

    # Move cursor right
    submit_page.handle_key(InputHandler.ARROW_RIGHT)
    assert submit_page.feedback_field.cursor_pos == 4

    # Backspace at position 4 (delete 's')
    submit_page.handle_key(InputHandler.BACKSPACE)
    assert submit_page.feedback_field.get_value() == "TeXt"
    assert submit_page.feedback_field.cursor_pos == 3


def test_submit_page_feedback_esc_behavior():
    """Test that ESC in feedback mode exits edit mode without exception"""
    survey_obj = create_sample_survey()
    submit_page = SubmitPage(question_pages=[])

    # Enter feedback mode (start at 1, go up to 0)
    submit_page.handle_key(InputHandler.ARROW_UP)  # 1 -> 0 (Feedback)
    submit_page.handle_key(InputHandler.ENTER)
    assert submit_page.feedback_field.input_active == True

    # Type text
    submit_page.handle_key('H')
    submit_page.handle_key('i')

    # ESC should exit feedback mode, not raise exception
    result = submit_page.handle_key(InputHandler.ESC)
    assert submit_page.feedback_field.input_active == False
    assert result == True  # Key was handled


def test_survey_runner_collect_results():
    """Test collecting results from all pages"""
    survey_obj = create_sample_survey()
    runner = SurveyRunner(survey_obj)

    # Answer Q1: select 'B' (single choice)
    q1_page = runner.pages[0]
    q1_page.handle_key(InputHandler.ARROW_DOWN)
    q1_page.handle_key(InputHandler.SPACE)

    # Answer Q2: select 'Y' (multiple choice - q2 is now multiple choice)
    q2_page = runner.pages[1]
    q2_page.handle_key(InputHandler.ARROW_DOWN)
    q2_page.handle_key(InputHandler.SPACE)

    # Add feedback
    submit_page = runner.pages[2]
    submit_page.handle_key(InputHandler.ARROW_DOWN)
    submit_page.handle_key(InputHandler.ARROW_DOWN)
    submit_page.handle_key(InputHandler.ENTER)
    submit_page.handle_key('G')
    submit_page.handle_key('r')
    submit_page.handle_key('e')
    submit_page.handle_key('a')
    submit_page.handle_key('t')
    submit_page.handle_key(InputHandler.ENTER)

    # Collect results
    results = runner._collect_results()
    assert results.answers["q1"] == "B"
    # Q2 is multiple choice, so result is a list
    assert results.answers["q2"] == ["Y"]
    assert results.feedback == "Great"


def test_question_page_render():
    """Test QuestionPage rendering"""
    survey_obj = create_sample_survey()
    q_page = QuestionPage(survey_obj.questions[0])

    # Create a mock tab_renderer
    from promptabs.terminal import TerminalRenderer, TabRenderer
    renderer = TerminalRenderer()
    tab_renderer = TabRenderer(renderer)

    content = q_page.render(tab_renderer)
    assert len(content) > 0
    assert "A" in content
    assert "B" in content
    assert "C" in content


def test_submit_page_render():
    """Test SubmitPage rendering"""
    survey_obj = create_sample_survey()
    runner = SurveyRunner(survey_obj)
    submit_page = runner.pages[-1]

    from promptabs.terminal import TerminalRenderer, TabRenderer
    renderer = TerminalRenderer()
    tab_renderer = TabRenderer(renderer)

    content = submit_page.render(tab_renderer)
    assert len(content) > 0
    assert "Submit" in content or "答案" in content


def test_submit_page_review_display():
    """Test that SubmitPage displays review with all questions and answers"""
    survey_obj = create_sample_survey()
    runner = SurveyRunner(survey_obj)

    # Answer Q1: select 'B'
    q1_page = runner.pages[0]
    q1_page.handle_key(InputHandler.ARROW_DOWN)
    q1_page.handle_key(InputHandler.SPACE)

    # Answer Q2: select 'X' and 'Y'
    q2_page = runner.pages[1]
    q2_page.handle_key(InputHandler.SPACE)  # Select X
    q2_page.handle_key(InputHandler.ARROW_DOWN)
    q2_page.handle_key(InputHandler.SPACE)  # Select Y

    # Check SubmitPage review
    submit_page = runner.pages[2]
    from promptabs.terminal import TerminalRenderer, TabRenderer
    renderer = TerminalRenderer()
    tab_renderer = TabRenderer(renderer)

    content = submit_page.render(tab_renderer)

    # Verify review shows question titles
    assert "Question 1" in content
    assert "Question 2" in content

    # Verify answers are shown
    assert "B" in content
    assert "X" in content
    assert "Y" in content


def test_question_page_custom_input_single_choice_navigation():
    """Test navigating to custom input field on single choice question"""
    survey_obj = create_sample_survey()
    q_page = QuestionPage(survey_obj.questions[0])  # Single choice question

    # Navigate to custom input field (index 3)
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 1
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 2
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 3 (custom input)
    assert q_page.current_index == 3
    assert q_page.num_options == 3
    assert q_page.total_items == 4  # 3 options + 1 custom input


def test_question_page_custom_input_single_choice_activation():
    """Test that custom input requires explicit ENTER to activate in single choice"""
    survey_obj = create_sample_survey()
    q_page = QuestionPage(survey_obj.questions[0])  # Single choice

    # Start at option 0
    assert q_page.custom_input_field.input_active == False

    # Navigate to custom input field - no auto-activation
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 1
    assert q_page.custom_input_field.input_active == False  # Still on option 1

    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 2
    assert q_page.custom_input_field.input_active == False  # Still on option 2

    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 3 (custom input)
    # Not auto-activated - requires explicit ENTER
    assert q_page.custom_input_field.input_active == False
    assert q_page.current_index == 3

    # Press ENTER to toggle edit mode on
    q_page.handle_key(InputHandler.ENTER)
    assert q_page.custom_input_field.input_active == True


def test_question_page_custom_input_single_choice_exclusive():
    """Test that custom input is exclusive with predefined options in single choice"""
    survey_obj = create_sample_survey()
    q_page = QuestionPage(survey_obj.questions[0])  # Single choice

    # Select option A (index 0)
    q_page.handle_key(InputHandler.SPACE)
    assert q_page.selected_indexes == {0}

    # Navigate to custom input
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 1
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 2
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 3 (custom input)
    assert q_page.current_index == 3
    assert 3 in q_page.selected_indexes

    # Press ENTER to toggle edit mode on
    q_page.handle_key(InputHandler.ENTER)
    assert q_page.custom_input_field.input_active == True

    # Type some text
    q_page.handle_key('O')
    q_page.handle_key('t')
    q_page.handle_key('h')

    # Press ENTER to toggle edit mode off
    result = q_page.handle_key(InputHandler.ENTER)
    assert result == False  # Single choice returns False to trigger submission
    # Option A should be deselected, only custom input selected
    assert q_page.selected_indexes == {3}


def test_question_page_custom_input_single_choice_text_input():
    """Test typing text in custom input field (single choice)"""
    survey_obj = create_sample_survey()
    q_page = QuestionPage(survey_obj.questions[0])  # Single choice

    # Navigate to custom input
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 1
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 2
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 3
    assert q_page.custom_input_field.input_active == False

    # Press ENTER to toggle edit mode on
    q_page.handle_key(InputHandler.ENTER)
    assert q_page.custom_input_field.input_active == True

    # Type text directly (now in edit mode)
    q_page.handle_key('O')
    q_page.handle_key('t')
    q_page.handle_key('h')
    q_page.handle_key('e')
    q_page.handle_key('r')
    assert q_page.custom_input_field.get_value() == "Other"
    assert q_page.custom_input_field.cursor_pos == 5


def test_question_page_custom_input_single_choice_get_result():
    """Test get_result() includes custom input (single choice)"""
    survey_obj = create_sample_survey()
    q_page = QuestionPage(survey_obj.questions[0])  # Single choice

    # Navigate to custom input
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 1
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 2
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 3
    assert q_page.custom_input_field.input_active == False

    # Press ENTER to toggle edit mode on
    q_page.handle_key(InputHandler.ENTER)
    assert q_page.custom_input_field.input_active == True

    # Type custom text
    q_page.handle_key('C')
    q_page.handle_key('u')
    q_page.handle_key('s')
    q_page.handle_key('t')
    q_page.handle_key('o')
    q_page.handle_key('m')
    assert q_page.custom_input_field.get_value() == "Custom"

    # Toggle edit mode off
    result = q_page.handle_key(InputHandler.ENTER)
    assert result == False  # Single choice returns False to trigger submission
    assert 3 in q_page.selected_indexes  # Custom input should be selected

    # Get result
    result_dict = q_page.get_result()
    assert result_dict["q1"] == "[User Input] Custom"


def test_question_page_custom_input_multiple_choice_activation():
    """Test that custom input can be activated with ENTER in multiple choice"""
    survey_obj = create_sample_survey()
    q_page = QuestionPage(survey_obj.questions[1])  # Multiple choice (has 2 options)

    # Navigate to custom input field
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 1
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 2 (custom input)

    # Verify navigation and auto-selection, but no auto-activation
    assert q_page.current_index == 2
    assert 2 in q_page.selected_indexes  # Auto-selected
    assert q_page.custom_input_field.input_active == False  # Not auto-activated

    # Press ENTER to toggle edit mode on
    q_page.handle_key(InputHandler.ENTER)
    assert q_page.custom_input_field.input_active == True  # Now activated


def test_question_page_custom_input_multiple_choice_coexistent():
    """Test that custom input coexists with predefined options in multiple choice"""
    survey_obj = create_sample_survey()
    q_page = QuestionPage(survey_obj.questions[1])  # Multiple choice

    # Select option X (index 0)
    q_page.handle_key(InputHandler.SPACE)
    assert q_page.selected_indexes == {0}

    # Navigate to custom input - auto-selected when navigating to it
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 1
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 2 (custom input, auto-selected)

    # Both X and custom input should be selected from navigation
    assert q_page.selected_indexes == {0, 2}


def test_question_page_custom_input_multiple_choice_text_and_result():
    """Test typing text and getting result in custom input field (multiple choice)"""
    survey_obj = create_sample_survey()
    q_page = QuestionPage(survey_obj.questions[1])  # Multiple choice

    # Select option X (index 0)
    q_page.handle_key(InputHandler.SPACE)
    assert 0 in q_page.selected_indexes

    # Navigate to custom input - auto-selected when navigating
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 1
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 2
    assert q_page.custom_input_field.input_active == False  # Not auto-activated
    assert 2 in q_page.selected_indexes  # Auto-selected

    # Press ENTER to toggle edit mode on
    q_page.handle_key(InputHandler.ENTER)
    assert q_page.custom_input_field.input_active == True

    # Type text (now in edit mode)
    q_page.handle_key('Z')
    assert q_page.custom_input_field.get_value() == "Z"

    # Deactivate with ENTER
    q_page.handle_key(InputHandler.ENTER)
    assert q_page.custom_input_field.input_active == False

    # Get result - should include X and custom input
    result = q_page.get_result()
    assert "X" in result["q2"]
    assert "[User Input] Z" in result["q2"]


def test_question_page_custom_input_empty_string_result():
    """Test that empty custom input is not included in result (single choice)"""
    survey_obj = create_sample_survey()
    q_page = QuestionPage(survey_obj.questions[0])  # Single choice

    # Navigate to custom input
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 1
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 2
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 3
    assert q_page.custom_input_field.input_active == False

    # Press ENTER to toggle edit mode on
    q_page.handle_key(InputHandler.ENTER)
    assert q_page.custom_input_field.input_active == True

    # Don't type anything, just toggle edit mode off
    result = q_page.handle_key(InputHandler.ENTER)
    assert result == False  # Single choice returns False

    # Get result - empty custom input should not appear in answer
    result_dict = q_page.get_result()
    answer = result_dict.get("q1")
    assert answer is None


def test_question_page_custom_input_backspace():
    """Test backspace operation in custom input field"""
    survey_obj = create_sample_survey()
    q_page = QuestionPage(survey_obj.questions[0])  # Single choice

    # Navigate to custom input
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 1
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 2
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 3
    assert q_page.custom_input_field.input_active == False

    # Press ENTER to toggle edit mode on
    q_page.handle_key(InputHandler.ENTER)
    assert q_page.custom_input_field.input_active == True

    # Type text
    q_page.handle_key('T')
    q_page.handle_key('e')
    q_page.handle_key('s')
    q_page.handle_key('t')
    assert q_page.custom_input_field.get_value() == "Test"

    # Delete last character
    q_page.handle_key(InputHandler.BACKSPACE)
    assert q_page.custom_input_field.get_value() == "Tes"
    assert q_page.custom_input_field.cursor_pos == 3


def test_question_page_custom_input_escape_deactivate():
    """Test that ESC deactivates custom input field"""
    survey_obj = create_sample_survey()
    q_page = QuestionPage(survey_obj.questions[0])  # Single choice

    # Navigate to custom input
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 1
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 2
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 3
    assert q_page.custom_input_field.input_active == False

    # Press ENTER to toggle edit mode on
    q_page.handle_key(InputHandler.ENTER)
    assert q_page.custom_input_field.input_active == True

    # Type some text
    q_page.handle_key('T')
    q_page.handle_key('e')
    q_page.handle_key('x')
    q_page.handle_key('t')

    # Press ESC to deactivate
    result = q_page.handle_key(InputHandler.ESC)
    assert result == True  # Key was handled
    assert q_page.custom_input_field.input_active == False
    # Text should be preserved
    assert q_page.custom_input_field.get_value() == "Text"


def test_question_page_custom_input_edit_mode_arrow_navigation():
    """Test that arrow keys in edit mode exit edit and navigate while preserving text"""
    survey_obj = create_sample_survey()
    q_page = QuestionPage(survey_obj.questions[0])  # Single choice

    # Navigate to custom input
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 1
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 2
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 3
    assert q_page.custom_input_field.input_active == False

    # Press ENTER to toggle edit mode on
    q_page.handle_key(InputHandler.ENTER)
    assert q_page.custom_input_field.input_active == True

    # Type some text
    q_page.handle_key('T')
    q_page.handle_key('e')
    q_page.handle_key('s')
    q_page.handle_key('t')
    assert q_page.custom_input_field.get_value() == "Test"

    # Press DOWN arrow in edit mode - should exit edit and navigate
    result = q_page.handle_key(InputHandler.ARROW_DOWN)
    assert result == True
    assert q_page.custom_input_field.input_active == False  # Exited edit mode
    assert q_page.current_index == 0  # Wrapped to option 0
    assert q_page.custom_input_field.get_value() == "Test"  # Text preserved


def test_question_page_custom_input_edit_mode_arrow_up_navigation():
    """Test arrow up in edit mode exits and navigates without re-activation when returning"""
    survey_obj = create_sample_survey()
    q_page = QuestionPage(survey_obj.questions[0])  # Single choice

    # Navigate to custom input
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 1
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 2
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 3
    assert q_page.custom_input_field.input_active == False

    # Press ENTER to toggle edit mode on
    q_page.handle_key(InputHandler.ENTER)
    assert q_page.custom_input_field.input_active == True

    # Type text
    q_page.handle_key('H')
    q_page.handle_key('i')
    assert q_page.custom_input_field.get_value() == "Hi"

    # Press UP arrow in edit mode - should exit and go to option 2
    q_page.handle_key(InputHandler.ARROW_UP)
    assert q_page.custom_input_field.input_active == False  # Exited edit mode
    assert q_page.current_index == 2  # Moved to option 2
    assert q_page.custom_input_field.get_value() == "Hi"  # Text preserved

    # Navigate back down to custom input
    q_page.handle_key(InputHandler.ARROW_DOWN)
    assert q_page.current_index == 3  # Back at custom input
    # No auto-activation when returning - consistent behavior
    assert q_page.custom_input_field.input_active == False
    assert q_page.custom_input_field.get_value() == "Hi"  # Text still preserved


def test_question_page_custom_input_multiple_choice_toggle_behavior():
    """Test that multiple choice auto-selects but requires ENTER to activate in edit mode"""
    survey_obj = create_sample_survey()
    q_page = QuestionPage(survey_obj.questions[1])  # Multiple choice

    # Navigate to custom input
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 1
    q_page.handle_key(InputHandler.ARROW_DOWN)  # -> 2
    assert q_page.current_index == 2
    # Auto-selected when navigating to custom input
    assert 2 in q_page.selected_indexes
    # NOT auto-activated anymore - requires explicit ENTER
    assert q_page.custom_input_field.input_active == False

    # Press ENTER to toggle edit mode on
    q_page.handle_key(InputHandler.ENTER)
    assert q_page.custom_input_field.input_active == True

    # Can type now
    q_page.handle_key('M')
    q_page.handle_key('u')
    q_page.handle_key('l')
    q_page.handle_key('t')
    assert q_page.custom_input_field.get_value() == "Mult"
