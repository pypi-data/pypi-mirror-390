import asyncio
import os
import psutil
from pprint import pprint
from QuantumCheck import HomeworkEvaluator

API_KEY = "AIzaSyDw76DEINpfBVgwIEZLShhy97tvWg7BmzY"

question_sets = {
    "python": "Write a Python function to calculate factorial.\nWrite a Python script to reverse a string.",
    "powerbi": "Create a Power BI report with a bar chart.\nExplain DAX measures for sales analysis.",
    "sql": "Write a SQL query to join two tables.\nWrite a SQL query for aggregate functions.",
    "ssis": "Design an SSIS package for data import.\nExplain SSIS control flow tasks."
}

answer_paths = {
    "python": ["../tests/answer/python1.zip"],
    "powerbi": ["../tests/answer/homework2_last.pdf"],
    "sql": ["../tests/answer/sql3.zip"],
    "ssis": ["../tests/answer/answer.dtsx"]
}

async def main():
    evaluator = HomeworkEvaluator()
    process = psutil.Process(os.getpid())

    for qtype, question in question_sets.items():
        for ans in answer_paths[qtype]:
            mem_before = process.memory_info().rss
            evaluation = await evaluator.evaluate_from_content(
                question_content=question,
                answer_path=ans,
                api_key=API_KEY,
                question_type=qtype
            )
            mem_after = process.memory_info().rss
            delta_mb = (mem_after - mem_before) / 1024**2

            print(f"{qtype} | {ans}")
            print(f"📈 Memory used for evaluation: {delta_mb:.2f} MB")
            print(f"✅ Evaluation result: {pprint(evaluation)}")
            print("-" * 40)

if __name__ == "__main__":
    asyncio.run(main())
