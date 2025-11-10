import asyncio
from pprint import pprint
from QuantumCheck import HomeworkEvaluator

API_KEY = "AIzaSyDuFmw1Z6qHsQicYsb1XVV7EXPtCj7Kzro"

question = "Mark the answers below"
answer_path = "../tests/answers/sample_notebook.ipynb"

async def main():
    evaluator = HomeworkEvaluator()
    evaluation = await evaluator.evaluate_from_content(
        question_content=question,
        answer_path=answer_path,
        api_key=API_KEY,
        question_type="python"
    )

    print(f" | {answer_path}")
    print("✅ Evaluation result:")
    pprint(evaluation)
    print("-" * 40)

if __name__ == "__main__":
    asyncio.run(main())
