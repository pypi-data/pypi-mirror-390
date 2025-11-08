"""
Page abstraction for survey pages
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Set, TYPE_CHECKING

from .types import Question
from .input_handler import InputHandler

if TYPE_CHECKING:
    from .terminal import TabRenderer


class Page(ABC):
    """Abstract base class for survey pages"""

    def __init__(self, title: str):
        """Initialize page"""
        self.title = title

    @abstractmethod
    def render(self, tab_renderer: "TabRenderer") -> str:
        """
        Render the page content.

        Args:
            tab_renderer: Tab renderer for rendering UI elements

        Returns:
            String representation of the page content
        """
        pass

    @abstractmethod
    def handle_key(self, key: str) -> bool:
        """
        Handle keyboard input.

        Args:
            key: The key pressed

        Returns:
            True if the key was handled by this page, False otherwise
        """
        pass

    @abstractmethod
    def get_result(self) -> Dict[str, Any]:
        """
        Get the result from this page.

        Returns:
            Dictionary of responses from this page
        """
        pass


class TextInputField:
    """
    A reusable text input field with unified rendering style.

    Provides text editing with cursor navigation, character insertion/deletion,
    and rendering consistent with render_options style (arrow indicator, colors, etc.)
    """

    def __init__(self, placeholder: str = ""):
        """
        Initialize text input field.

        Args:
            placeholder: Placeholder text to show when empty
        """
        self.text: str = ""
        self.cursor_pos: int = 0
        self.input_active: bool = False
        self.placeholder: str = placeholder

    def activate(self) -> None:
        """Enter edit mode"""
        self.input_active = True

    def deactivate(self) -> None:
        """Exit edit mode"""
        self.input_active = False

    def handle_key(self, key: str) -> bool:
        """
        Handle keyboard input while in edit mode.

        Args:
            key: The key pressed

        Returns:
            True if key was handled, False otherwise
        """
        if key == InputHandler.ARROW_LEFT:
            # Move cursor left
            if self.cursor_pos > 0:
                self.cursor_pos -= 1
            return True
        elif key == InputHandler.ARROW_RIGHT:
            # Move cursor right
            if self.text and self.cursor_pos < len(self.text):
                self.cursor_pos += 1
            return True
        elif key == InputHandler.BACKSPACE:
            # Delete character at cursor position
            if self.text and self.cursor_pos > 0:
                self.text = (self.text[:self.cursor_pos - 1] +
                            self.text[self.cursor_pos:])
                self.cursor_pos -= 1
            return True
        elif key and len(key) == 1 and ord(key) >= 32:
            # Insert printable character at cursor position
            self.text = (self.text[:self.cursor_pos] + key +
                        self.text[self.cursor_pos:])
            self.cursor_pos += 1
            return True

        return False

    def render(self, tab_renderer: "TabRenderer", prompt: str,
               is_selected: bool, show_indicator: bool = True) -> str:
        """
        Render the text input field with unified style.

        Rendering style matches render_options:
        - Selected: ❯ [prompt] (GREEN, BOLD)
        - Unselected: [indent] [prompt]
        - Edit mode: shows cursor |
        - Display mode: shows content or placeholder

        Args:
            tab_renderer: Tab renderer for styling
            prompt: Prompt text to display
            is_selected: Whether this field is currently selected
            show_indicator: Whether to show arrow indicator (default True)

        Returns:
            Multi-line rendered string
        """
        lines = []

        # Render the prompt line (title)
        if show_indicator and is_selected:
            # Selected: use arrow indicator and green bold style
            indicator = tab_renderer.render_text("❯ ", color=tab_renderer.GREEN, bold=True)
            styled_prompt = tab_renderer.render_text(prompt, color=tab_renderer.GREEN, bold=True)
            lines.append(f"{indicator}{styled_prompt}")
        else:
            # Unselected: use indent and normal style
            indent = "  " if show_indicator else ""
            lines.append(f"{indent}{prompt}")

        # Render the input/content line
        if self.input_active:
            # Edit mode: show cursor
            if self.text:
                text_display = (self.text[:self.cursor_pos] + "|" +
                               self.text[self.cursor_pos:])
            else:
                text_display = "|"
            lines.append(tab_renderer.render_text(f"  {text_display}", color=tab_renderer.DIM))
        else:
            # Display mode: show content or placeholder
            if self.text:
                lines.append(f"  {tab_renderer.render_text(self.text, bold=is_selected)}")
            else:
                lines.append(tab_renderer.render_text("  (未填写)", color=tab_renderer.DIM))

        return "\n".join(lines)

    def get_value(self) -> str:
        """Get current text value"""
        return self.text

    def set_value(self, value: str) -> None:
        """Set text value"""
        self.text = value
        self.cursor_pos = 0

    def clear(self) -> None:
        """Clear text value"""
        self.text = ""
        self.cursor_pos = 0


class QuestionPage(Page):
    """Page for displaying a question and its options"""

    def __init__(self, question: Question):
        """
        Initialize question page.

        Args:
            question: The question to display
        """
        super().__init__(question.title)
        self.question = question
        self.current_index: int = 0
        self.selected_indexes: Set[int] = set()
        self.num_options = len(question.options)
        # Add custom input field for all questions
        self.custom_input_field = TextInputField(placeholder="请输入其他内容...")
        # Total selectable items: predefined options + custom input
        self.total_items = self.num_options + 1

    def updown(self, direction: int):
        """Move selection up or down"""
        self.current_index = (self.current_index + direction) % self.total_items

    def _handle_selection(self) -> bool:
        """
        Handle option selection for both SPACE and ENTER keys.

        Returns:
            True if Page should handle subsequent processing,
            False if SurveyRunner should handle tab navigation (single choice only)
        """
        question = self.question

        # Check if custom input field is selected (index == num_options)
        if self.current_index == self.num_options:
            # Custom input field selected
            if question.is_multiple_choice:
                # Multiple choice: toggle custom input selection
                if self.current_index in self.selected_indexes:
                    self.selected_indexes.remove(self.current_index)
                else:
                    self.selected_indexes.add(self.current_index)
                return True
            else:
                # Single choice: select custom input field only
                self.selected_indexes.clear()
                self.selected_indexes.add(self.current_index)
                return False
        else:
            # Regular predefined option selected
            if question.is_multiple_choice:
                # Toggle selection for current option
                if self.current_index in self.selected_indexes:
                    self.selected_indexes.remove(self.current_index)
                else:
                    self.selected_indexes.add(self.current_index)
                return True
            else:
                # Single choice: select current option (clear custom input)
                self.selected_indexes.clear()
                self.selected_indexes.add(self.current_index)
                self.custom_input_field.clear()
                # Return False to let SurveyRunner handle tab navigation for ENTER
                return False

    def handle_key(self, key: str) -> bool:
        """Handle keyboard input for question page"""
        # If custom input field is in edit mode, handle navigation and special keys
        if self.custom_input_field.input_active:
            if key == InputHandler.ARROW_UP:
                # Exit edit mode and navigate up (preserve text)
                self.custom_input_field.deactivate()
                self.updown(-1)
                # If navigated to custom input, keep it selected but don't re-activate
                if self.current_index == self.num_options:
                    if self.current_index not in self.selected_indexes:
                        if not self.question.is_multiple_choice:
                            self.selected_indexes.clear()
                        self.selected_indexes.add(self.current_index)
                return True
            elif key == InputHandler.ARROW_DOWN:
                # Exit edit mode and navigate down (preserve text)
                self.custom_input_field.deactivate()
                self.updown(1)
                # If navigated to custom input, keep it selected but don't re-activate
                if self.current_index == self.num_options:
                    if self.current_index not in self.selected_indexes:
                        if not self.question.is_multiple_choice:
                            self.selected_indexes.clear()
                        self.selected_indexes.add(self.current_index)
                return True
            elif key == InputHandler.ENTER:
                # Exit edit mode (toggle off)
                self.custom_input_field.deactivate()
                # For single-choice, return False to trigger submission like normal options
                if not self.question.is_multiple_choice:
                    return False
                # For multiple-choice, return True to stay on page
                return True
            elif key == InputHandler.ESC:
                # Cancel edit mode, don't clear the text
                self.custom_input_field.deactivate()
                return True
            else:
                # Delegate text editing to custom input field
                return self.custom_input_field.handle_key(key)

        # Normal navigation mode
        if key == InputHandler.ARROW_UP:
            self.updown(-1)
            # If navigated to custom input, auto-select it
            if self.current_index == self.num_options:
                if self.current_index not in self.selected_indexes:
                    if not self.question.is_multiple_choice:
                        self.selected_indexes.clear()
                    self.selected_indexes.add(self.current_index)
            return True
        elif key == InputHandler.ARROW_DOWN:
            self.updown(1)
            # If navigated to custom input, auto-select it
            if self.current_index == self.num_options:
                if self.current_index not in self.selected_indexes:
                    if not self.question.is_multiple_choice:
                        self.selected_indexes.clear()
                    self.selected_indexes.add(self.current_index)
            return True
        elif key == InputHandler.SPACE:
            # SPACE: select current option/field
            result = self._handle_selection()
            # For space key, always return True to stay on page
            return True
        elif key == InputHandler.ENTER:
            # ENTER key behavior depends on location
            if self.current_index == self.num_options:
                # On custom input field: toggle edit mode
                self.custom_input_field.activate()
                return True
            # Otherwise delegate to _handle_selection for proper return value
            return self._handle_selection()

        return False

    def render(self, tab_renderer: "TabRenderer") -> str:
        """Render a single question with its options"""
        question = self.question
        lines = []

        # Render question text
        question_text = tab_renderer.render_text(question.question, color=tab_renderer.DIM)
        lines.append(question_text)
        lines.append("")

        # For multiple choice, pass selected options
        if question.is_multiple_choice:
            multiple = True
            foot = tab_renderer.render_text(
                "Use ↑↓ to select · Space/Enter to toggle · → to continue · ← → to navigate tabs · Esc to cancel",
                color=tab_renderer.DIM,
            )
        else:
            multiple = False
            foot = tab_renderer.render_text(
                "Use ↑↓ to select · Enter to confirm & continue · ← → to navigate tabs · Esc to cancel",
                color=tab_renderer.DIM,
            )

        # Render predefined options
        # Only pass indices < num_options to render_options
        options_for_render = question.options
        selected_for_render = {i for i in self.selected_indexes if i < self.num_options}
        current_index_for_render = self.current_index if self.current_index < self.num_options else -1

        options_display = tab_renderer.render_options(
            options_for_render,
            current_index_for_render,
            selected_for_render,
            multiple
        )
        lines.append(options_display)
        lines.append("")

        # Render custom input field
        is_custom_selected = (self.current_index == self.num_options)
        is_custom_checked = (self.num_options in self.selected_indexes)

        # Render with custom styling
        custom_input_lines = []
        if is_custom_selected:
            # Selected: show arrow indicator
            indicator = tab_renderer.render_text("❯ ", color=tab_renderer.GREEN, bold=True)
            styled_prompt = tab_renderer.render_text("[输入其他答案]", color=tab_renderer.GREEN, bold=True)
            if multiple and is_custom_checked:
                checkbox = "☑ "
            elif multiple:
                checkbox = "☐ "
            else:
                checkbox = ""
            custom_input_lines.append(f"{indicator}{checkbox}{styled_prompt}")
        else:
            # Unselected: no arrow
            if multiple and is_custom_checked:
                checkbox = "☑ "
            elif multiple:
                checkbox = "☐ "
            else:
                checkbox = ""
            styled_prompt = tab_renderer.render_text("[输入其他答案]", color=tab_renderer.DIM)
            custom_input_lines.append(f"  {checkbox}{styled_prompt}")

        # Show input content if in edit mode or has content
        if self.custom_input_field.input_active or self.custom_input_field.get_value():
            if self.custom_input_field.input_active:
                # Edit mode: show cursor
                if self.custom_input_field.text:
                    text_display = (self.custom_input_field.text[:self.custom_input_field.cursor_pos] + "|" +
                                   self.custom_input_field.text[self.custom_input_field.cursor_pos:])
                else:
                    text_display = "|"
                custom_input_lines.append(tab_renderer.render_text(f"  {text_display}", color=tab_renderer.DIM))
            else:
                # Display mode: show content
                custom_input_lines.append(f"  {tab_renderer.render_text(self.custom_input_field.get_value(), bold=is_custom_selected)}")

        lines.append("\n".join(custom_input_lines))
        lines.append("")
        lines.append(foot)

        return "\n".join(lines)

    def get_result(self) -> Dict[str, Any]:
        """Get the response for this question"""
        question = self.question
        custom_input_value = self.custom_input_field.get_value().strip()

        if question.is_multiple_choice:
            # Multiple choice: collect all selected options
            answers = []
            for i in sorted(self.selected_indexes):
                if i < self.num_options:
                    # Predefined option
                    answers.append(question.options[i])
                elif i == self.num_options and custom_input_value:
                    # Custom input
                    answers.append(f"[User Input] {custom_input_value}")
            answers = answers if answers else None
        else:
            # Single choice: return either predefined option or custom input
            if self.num_options in self.selected_indexes and custom_input_value:
                # Custom input is selected and has value
                answers = f"[User Input] {custom_input_value}"
            elif self.selected_indexes:
                # Predefined option is selected
                selected_idx = next(iter(self.selected_indexes))
                if selected_idx < self.num_options:
                    answers = question.options[selected_idx]
                else:
                    answers = None
            else:
                answers = None

        return {question.id: answers}


class SubmitPage(Page):
    """Page for reviewing answers and submitting"""

    def __init__(self, question_pages: List[Page], title="Submit"):
        """
        Initialize submit page.

        Args:
            question_pages: List of QuestionPage objects (for displaying answers in review)
            title: Title of the submit page
        """
        super().__init__(title)
        self.question_pages = question_pages
        # Index mapping: 0=Feedback, 1=Submit answers, 2=Cancel
        # Default to Submit answers (index 1)
        self.submit_option_index: int = 1
        self.feedback_field = TextInputField(placeholder="还有其他想补充的信息吗？")
        self.submitted: bool = False

    def render(self, tab_renderer: "TabRenderer") -> str:
        """Render the submit page"""
        lines = []

        # Render review content
        review_content = self._render_review_content(tab_renderer)
        lines.append(review_content)
        lines.append("")

        # Render feedback field first (index 0) with unified style (consistent with options)
        is_feedback_selected = (self.submit_option_index == 0)
        feedback_content = self.feedback_field.render(
            tab_renderer,
            "还有其他想补充的信息吗？ (可选)",
            is_feedback_selected,
            show_indicator=True
        )
        lines.append(feedback_content)
        lines.append("")

        # Render submit options (Submit answers=1, Cancel=2)
        submit_options = ["Submit answers", "Cancel"]
        # Map index: 0=Feedback (skip and don't highlight any option), 1=Submit answers, 2=Cancel
        if self.submit_option_index == 0:
            # Feedback selected, don't highlight any option
            display_index = -1
        else:
            # Map internal index to display index (1->0, 2->1)
            display_index = self.submit_option_index - 1
        options_display = tab_renderer.render_options(
            submit_options,
            display_index,
            set(),
            False
        )
        lines.append(options_display)
        lines.append("")

        # Render help text
        if self._get_missing_required():
            warning_msg = tab_renderer.render_text(
                "⚠ Cannot submit: Please answer all required questions",
                color=tab_renderer.RED,
            )
            lines.append(warning_msg)
        else:
            help_text = tab_renderer.render_text(
                "Use ↑↓ to select · ← → to navigate tabs · Enter to confirm · Esc to cancel",
                color=tab_renderer.DIM,
            )
            lines.append(help_text)

        return "\n".join(lines)

    def handle_key(self, key: str) -> bool:
        """Handle keyboard input for submit page"""
        if self.feedback_field.input_active:
            return self._handle_feedback_input(key)
        else:
            return self._handle_submit_navigation(key)

    def _handle_feedback_input(self, key: str) -> bool:
        """Handle keyboard input while editing feedback"""
        if key == InputHandler.ENTER:
            # Confirm feedback and move back to Submit button
            self.feedback_field.deactivate()
            self.submit_option_index = 1
            return True
        elif key == InputHandler.ESC:
            # Cancel feedback input (only clear edit mode, not exit survey)
            self.feedback_field.deactivate()
            return True
        else:
            # Delegate to feedback field for text editing
            return self.feedback_field.handle_key(key)

    def _handle_submit_navigation(self, key: str) -> bool:
        """Handle keyboard input for submit button/feedback navigation"""
        if key == InputHandler.ARROW_UP:
            self._submit_move_up()
            return True
        elif key == InputHandler.ARROW_DOWN:
            self._submit_move_down()
            return True
        elif key == InputHandler.ENTER:
            # Check which option is selected
            if self.submit_option_index == 0:
                # Feedback field is selected - activate input mode
                self.feedback_field.activate()
            elif self.submit_option_index == 1:
                # Submit button
                if not self._get_missing_required():
                    self.submitted = True
                    return False  # Signal to SurveyRunner that we're done
            elif self.submit_option_index == 2:
                # Cancel button - exit the survey
                raise KeyboardInterrupt
            return True

        # Left/Right arrows are handled by SurveyRunner, return False
        return False

    def _render_review_content(self, tab_renderer: "TabRenderer") -> str:
        """Render the review content with all questions and answers"""
        lines = []
        lines.append(tab_renderer.render_text("Review your answers", bold=True))
        lines.append("")

        missing = self._get_missing_required()
        if missing:
            warning = tab_renderer.render_text(
                "⚠ You have not answered all required questions",
                color=tab_renderer.RED,
            )
            lines.append(warning)
            lines.append("")

        # Display all questions and their answers
        for page in self.question_pages:
            if isinstance(page, QuestionPage):
                question = page.question
                # Get answer from QuestionPage
                result = page.get_result()
                answer = result.get(question.id)

                # Check if answer is actually provided (not None and not empty list)
                has_answer = answer is not None and (not isinstance(answer, list) or len(answer) > 0)

                # Color question title based on answer status
                if has_answer:
                    # Question has been answered - green
                    question_title = tab_renderer.render_text(
                        f"● {question.title}",
                        color=tab_renderer.GREEN,
                    )
                elif question.required:
                    # Required but not answered - red
                    question_title = tab_renderer.render_text(
                        f"● {question.title}",
                        color=tab_renderer.RED,
                    )
                else:
                    # Optional and not answered - dim
                    question_title = tab_renderer.render_text(
                        f"● {question.title}",
                        color=tab_renderer.DIM,
                    )
                lines.append(question_title)

                if has_answer:
                    # Question has been answered
                    if isinstance(answer, list):
                        # Multiple choice - show each selected option
                        for selected_option in answer:
                            lines.append(f"  ☑ {selected_option}")
                    else:
                        # Single choice or custom input
                        lines.append(f"  → {answer}")
                else:
                    # Question not answered
                    if question.required:
                        status = tab_renderer.render_text(
                            "  → (not answered)",
                            color=tab_renderer.RED,
                        )
                    else:
                        status = tab_renderer.render_text(
                            "  → (not answered, optional)",
                            color=tab_renderer.DIM,
                        )
                    lines.append(status)

                #lines.append("")

        return "\n".join(lines)

    def _submit_move_up(self):
        """Move up in submit options (circular navigation)"""
        # Navigate: Feedback (0) ↔ Submit (1) ↔ Cancel (2)
        self.submit_option_index = (self.submit_option_index - 1) % 3

    def _submit_move_down(self):
        """Move down in submit options (circular navigation)"""
        # Navigate: Feedback (0) ↔ Submit (1) ↔ Cancel (2)
        self.submit_option_index = (self.submit_option_index + 1) % 3

    def _get_missing_required(self) -> List[str]:
        """
        Get list of required questions that haven't been answered.

        Returns:
            List of missing required question IDs
        """
        missing = []

        for page in self.question_pages:
            if isinstance(page, QuestionPage):
                question = page.question
                if not question.required:
                    continue

                result = page.get_result()
                answer = result.get(question.id)

                # Check if answer is actually provided (not None and not empty list)
                has_answer = answer is not None and (not isinstance(answer, list) or len(answer) > 0)

                if not has_answer:
                    missing.append(question.id)

        return missing

    def get_result(self) -> Dict[str, Any]:
        """Get the result from this page (feedback if provided)"""
        result = {}
        feedback_value = self.feedback_field.get_value().strip()
        if feedback_value:
            result['feedback'] = feedback_value
        return result
