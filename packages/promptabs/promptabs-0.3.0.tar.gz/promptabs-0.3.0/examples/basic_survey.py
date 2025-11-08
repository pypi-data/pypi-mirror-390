#!/usr/bin/env python
"""
Basic survey example

Run with: python examples/basic_survey.py
Or after install: python -m promptabs
"""

from promptabs import Question, SurveyRunner, Survey


def main():
    """Example: Run a sample survey with review/submit functionality"""

    survey = Survey(
        questions=[
            Question(
                id="version_storage",
                title="版本号管理",
                question="对于 Windows 和 Linux，你希望如何存储和读取版本号？选择你认为最合适的版本号管理方式",
                options=[
                    "统一使用 version.txt",
                    "平台特定方案",
                    "混合方案",
                    "其他",
                ],
                required=True,
            ),
            Question(
                id="build_system",
                title="构建系统",
                question="你项目使用的构建系统是什么？",
                options=[
                    "CMake",
                    "Make",
                    "Gradle",
                    "其他",
                ],
                required=True,
            ),
            Question(
                id="package_format",
                title="打包方式",
                question="你更喜欢哪种打包和分发方式？",
                options=[
                    "Docker 容器",
                    "可执行文件",
                    "源代码分发",
                    "其他",
                ],
                required=False,  # Optional question
            ),
        ]
    )

    runner = SurveyRunner(survey)

    try:
        results = runner.run()
        print("\n✅ 感谢您完成问卷！您的答案已收集：")
        for question_id, answer in results.answers.items():
            print(f"  • {question_id}: {answer}")
        if results.feedback:
            print(f"\n📝 您的反馈：{results.feedback}")
    except KeyboardInterrupt:
        print("\n❌ 问卷已取消")


if __name__ == "__main__":
    main()
