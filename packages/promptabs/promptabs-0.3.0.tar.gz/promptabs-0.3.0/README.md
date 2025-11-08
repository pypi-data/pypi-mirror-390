# promptabs - Interactive Terminal Survey Module

A Python module for creating interactive terminal-based surveys with tab navigation and arrow key support.

## Features

- **Tab-based Navigation**: Use left/right arrow keys to navigate between questions
- **Arrow Key Selection**: Use up/down arrow keys to select answer options
- **Colorized Output**: Beautiful terminal UI with ANSI colors
- **Easy Integration**: Simple API for creating surveys
- **Response Collection**: Automatically collects user responses in a dictionary
- **Submit/Review Tab**: Review answers before submitting with validation
- **Required Field Validation**: Prevent submission if required questions are unanswered
- **Optional Questions**: Support both required and optional questions

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from promptabs import Survey, Question

# Create questions
questions = [
    Question(
        id="q1",
        title="What is your favorite programming language?",
        options=["Python", "JavaScript", "Go", "Rust"],
        description="Select one option"
    ),
    Question(
        id="q2",
        title="Which OS do you use?",
        options=["macOS", "Linux", "Windows"]
    ),
]

# Run the survey
survey = Survey(questions)
responses = survey.run()

# Access responses
print(responses)
# Output: {"q1": "Python", "q2": "Linux"}
```

## API Documentation

### Question

Data class representing a single survey question.

```python
@dataclass
class Question:
    id: str                    # Unique question identifier
    title: str                 # Question title/text
    options: List[str]         # Available answer options
    description: str = ""      # Optional question description
    required: bool = True      # Whether question must be answered
```

### Survey

Main class for managing and running surveys.

```python
survey = Survey(questions: List[Question])

# Run the survey and get responses
responses: Dict[str, str] = survey.run()
```

## Keyboard Controls

The tabs form a circular navigation ring - you can navigate freely between any tabs!

### Navigation
- **Left Arrow (←)**: Move to previous tab (wraps from Q1 to Submit)
- **Right Arrow (→)**: Move to next tab (wraps from Submit to Q1)

### On Question Tabs
- **Up/Down arrows**: Select answer options
- **Enter**: Confirm selection and move to next question
- **Esc / Ctrl+C**: Cancel survey

### On Submit/Review Tab
- **Up/Down arrows**: Select between Submit and Cancel buttons
- **Enter**: Submit survey (only if all required questions answered)
- **Esc / Ctrl+C**: Cancel survey

Example Navigation:
```
Q1 ← → Q2 ← → Q3 ← → Submit
↑_______________________________↓
(pressing ← on Q1 goes to Submit)
(pressing → on Submit goes to Q1)
```

## Architecture

- **question.py**: Question data model
- **terminal.py**: Terminal rendering and UI components
- **input_handler.py**: Raw keyboard input handling
- **survey.py**: Main survey conductor and interaction logic

## Example Output

```
☑ Version Storage  ☐ Build System  ☐ Package Format →

Version Storage Question
Select your preferred approach

❯ Unified version.txt
  Platform-specific
  Hybrid approach
  Other

Use ↑↓ to select · ← → to navigate tabs · Enter to confirm · Esc to cancel
```

## Requirements

- Python 3.10+
- Unix-like terminal (macOS, Linux) or Windows with compatible terminal

## License

MIT
