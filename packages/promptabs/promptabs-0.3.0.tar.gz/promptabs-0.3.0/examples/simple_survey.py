#!/usr/bin/env python
"""
Simple survey example

Run with: python examples/simple_survey.py
"""

from promptabs import Question, SurveyRunner, Survey


def main():
    """Simple example with just one question"""

    survey = Survey(
        questions=[
            Question(
                id="favorite_language",
                title="编程语言",
                question="你最喜欢哪种编程语言？",
                options=[
                    "Python",
                    "JavaScript",
                    "Go",
                    "Rust",
                    "Java",
                ],
                required=True,
            ),
            Question(
                id="framework",
                title="框架",
                question="你最常用的框架是什么？",
                options=[
                    "Django",
                    "FastAPI",
                    "Flask",
                    "其他",
                ],
                required=False,
            ),
        ]
    )

    runner = SurveyRunner(survey)

    try:
        results = runner.run()
        print("\n" + "=" * 50)
        print("✅ 问卷已完成！")
        print("=" * 50)
        for question_id, answer in results.answers.items():
            print(f"  {question_id}: {answer}")
        if results.feedback:
            print(f"\n💬 反馈: {results.feedback}")
    except KeyboardInterrupt:
        print("\n❌ 问卷已取消")


if __name__ == "__main__":
    main()
