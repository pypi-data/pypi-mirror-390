"""
SurveyRunner class for managing and running surveys
"""

import json
from typing import List, Dict, Optional, Any
from .types import Question, Results, Survey
from .terminal import TerminalRenderer, TabRenderer
from .input_handler import InputHandler
from .page import Page, QuestionPage, SubmitPage


class SurveyRunner:
    """Main survey conductor for managing questions and collecting responses"""

    def __init__(self, survey: Survey):
        """
        Initialize a survey runner with a Survey object

        Args:
            survey: Survey object containing questions and metadata
        """
        if not survey.questions:
            raise ValueError("Survey must contain at least one question")

        self.survey = survey
        self.questions = survey.questions
        self.pages = self._create_pages(self.questions)
        self.renderer = TerminalRenderer()
        self.tab_renderer = TabRenderer(self.renderer)
        self.input_handler = InputHandler()

        self.tab_titles = [q.title for q in self.questions] + ["Submit"]
        self.current_tab_index = 0


    @staticmethod
    def from_json_file(filepath: str) -> "SurveyRunner":
        """
        Create a SurveyRunner from a JSON file

        Args:
            filepath: Path to JSON file containing survey

        Returns:
            SurveyRunner instance

        Example:
            runner = SurveyRunner.from_json_file('survey.json')
            responses = runner.run()
        """
        with open(filepath) as f:
            data = json.load(f)
        survey = Survey.model_validate(data)
        return SurveyRunner(survey)


    @staticmethod
    def from_json_string(json_string: str) -> "SurveyRunner":
        """
        Create a SurveyRunner from a JSON string

        Args:
            json_string: JSON string containing survey

        Returns:
            SurveyRunner instance
        """
        survey = Survey.model_validate_json(json_string)
        return SurveyRunner(survey)


    def handle_key(self, key: str) -> bool:
        """
        Handle global keyboard input

        Args:
            key: Key pressed by the user

        Returns:
            True if the key was handled by SurveyRunner, False otherwise
        """
        if key == InputHandler.CTRL_C or key == InputHandler.ESC:
            # Exit on Ctrl+C or Escape
            raise KeyboardInterrupt

        if key == InputHandler.ARROW_LEFT:
            self.current_tab_index = (self.current_tab_index - 1) % len(self.pages)
            return True
        elif key == InputHandler.ARROW_RIGHT:
            self.current_tab_index = (self.current_tab_index + 1) % len(self.pages)
            return True
        elif key == InputHandler.ENTER:
            # ENTER on single choice question moves to next tab
            page = self.pages[self.current_tab_index]
            if isinstance(page, QuestionPage) and not page.question.is_multiple_choice:
                # Move to next tab
                self.current_tab_index = (self.current_tab_index + 1) % len(self.pages)
                return True

        return False  # Key not handled here

    def run(self) -> Optional[Results]:
        """
        Run the interactive survey

        Returns:
            Results object containing responses and optional feedback
        """
        try:
            self.renderer.hide_cursor()

            # Main event loop - continues until successful submit
            while True:
                self._render_survey()

                key = self.input_handler.read_single_key()

                # First, try Page.handle_key()
                page = self.pages[self.current_tab_index]
                if page.handle_key(key):
                    continue  # Page handled the key

                # If Page didn't handle it, try SurveyRunner.handle_key()
                if self.handle_key(key):
                    continue  # SurveyRunner handled the key

                # Check if SubmitPage was submitted
                if isinstance(page, SubmitPage) and page.submitted:
                    # Collect results and return
                    return self._collect_results()

        except KeyboardInterrupt:
            # User cancelled
            return None
        finally:
            self.renderer.show_cursor()
            self.renderer.clear_screen()

    def _create_pages(self, questions: List[Question]) -> List[Page]:
        """Create page instances for all questions and submit page"""
        pages: List[Page] = []
        question_pages: List[Page] = []

        # Create question pages
        for question in questions:
            page = QuestionPage(question)
            pages.append(page)
            question_pages.append(page)

        # Add submit page with reference to all question pages
        pages.append(SubmitPage(question_pages=question_pages))
        return pages

    def _render_survey(self):
        """Render the current survey state"""
        self.renderer.clear_screen()
        tab_header = self.tab_renderer.render_tab_header(self.tab_titles, self.current_tab_index)
        print(tab_header)
        print()

        page = self.pages[self.current_tab_index]
        content = page.render(self.tab_renderer)
        print(content)

    def _collect_results(self) -> Results:
        """Collect results from all pages and return Results object"""
        answers: Dict[str, Any] = {}
        feedback = None

        # Collect answers from all QuestionPage objects
        for page in self.pages[:-1]:  # Exclude SubmitPage
            if isinstance(page, QuestionPage):
                result = page.get_result()
                answers.update(result)

        # Collect feedback from SubmitPage
        submit_page = self.pages[-1]
        if isinstance(submit_page, SubmitPage):
            fb_result = submit_page.get_result()
            feedback = fb_result.get('feedback')

        return Results(answers=answers, feedback=feedback)
