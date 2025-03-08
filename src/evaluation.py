import os
import difflib
import cohere
from dotenv import load_dotenv

load_dotenv()

def load_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

def generate_diff(file1, file2):
    lines1 = file1.splitlines()
    lines2 = file2.splitlines()
    diff = list(difflib.unified_diff(lines1, lines2, lineterm=""))
    return "\n".join(diff)

def evaluate_with_cohere(original_code, bugged_code, fixed_code, bug_report, fix_report):
    cohere_api_key = os.getenv("COHERE_API_KEY")
    if not cohere_api_key:
        print("Error: COHERE_API_KEY is not set in the .env file.")
        exit(1)

    co = cohere.Client(cohere_api_key)

    analyze_bugs_prompt = f"""
    Identify all bugs in the bug report.
    {bug_report}
    """
    bug_analysis_response = co.generate(model="command-r-plus", prompt=analyze_bugs_prompt, max_tokens=300, temperature=0.7)

    evaluate_fixes_prompt = f"""
    Analyze how well the developer fixed the bugs.
    {fix_report}
    """
    fix_analysis_response = co.generate(model="command-r-plus", prompt=evaluate_fixes_prompt, max_tokens=300, temperature=0.7)

    check_missed_bugs_prompt = f"""
    Identify any bugs that were not fixed.
    {bug_report}
    {fix_report}
    """
    missed_bugs_response = co.generate(model="command-r-plus", prompt=check_missed_bugs_prompt, max_tokens=300, temperature=0.7)

    scoring_feedback_prompt = f"""
    Provide a score (0-100%) and qualitative feedback.
    {bug_report}
    {fix_report}
    {missed_bugs_response.generations[0].text}
    """
    scoring_feedback_response = co.generate(model="command-r-plus", prompt=scoring_feedback_prompt, max_tokens=300, temperature=0)

    evaluation_result = {
        "bug_analysis": bug_analysis_response.generations[0].text,
        "fix_evaluation": fix_analysis_response.generations[0].text,
        "missed_bugs": missed_bugs_response.generations[0].text,
        "score_feedback": scoring_feedback_response.generations[0].text
    }
    return evaluation_result

def get_file_paths_from_os():
    file_paths = []
    sub_dirs = ['user_project', 'bugged', 'developer']
    base_dir = os.getcwd()
    sub_dirs_paths = {sub_dir: os.path.join(base_dir, sub_dir) for sub_dir in sub_dirs}
    user_project_files = {f: os.path.join(sub_dirs_paths['user_project'], f) for f in os.listdir(sub_dirs_paths['user_project']) if f.endswith(".py")}
    bugged_files = {f: os.path.join(sub_dirs_paths['bugged'], f) for f in os.listdir(sub_dirs_paths['bugged']) if f.endswith(".py")}
    developer_files = {f: os.path.join(sub_dirs_paths['developer'], f) for f in os.listdir(sub_dirs_paths['developer']) if f.endswith(".py")}

    for filename in user_project_files:
        if filename in bugged_files and filename in developer_files:
            file_paths.append((
                user_project_files[filename],
                bugged_files[filename],
                developer_files[filename]
            ))
    return file_paths

def generate_final_summary(all_results):
    cohere_api_key = os.getenv("COHERE_API_KEY")
    if not cohere_api_key:
        print("Error: COHERE_API_KEY is not set in the .env file.")
        exit(1)

    co = cohere.Client(cohere_api_key)

    summary_prompt = "Summarize the following AI-generated evaluations into a single comprehensive report:\n\n"
    for idx, result in enumerate(all_results, start=1):
        summary_prompt += f"Evaluation {idx}:\n"
        summary_prompt += f"- Bug Analysis: {result['bug_analysis']}\n"
        summary_prompt += f"- Fix Evaluation: {result['fix_evaluation']}\n"
        summary_prompt += f"- Missed Bugs: {result['missed_bugs']}\n"
        summary_prompt += f"- Score & Feedback: {result['score_feedback']}\n\n"

    summary_response = co.generate(model="command-r-plus", prompt=summary_prompt, max_tokens=500, temperature=0.5)

    return summary_response.generations[0].text

def evaluate():
    file_paths = get_file_paths_from_os()
    if not file_paths:
        print("No matching files found.")
        return

    all_results = []
    total_score = 0
    file_count = 0

    for original_file_path, bugged_file_path, fixed_file_path in file_paths:
        original_code = load_file(original_file_path)
        bugged_code = load_file(bugged_file_path)
        fixed_code = load_file(fixed_file_path)

        bug_report = generate_diff(original_code, bugged_code)
        fix_report = generate_diff(bugged_code, fixed_code)

        evaluation_result = evaluate_with_cohere(original_code, bugged_code, fixed_code, bug_report, fix_report)
        all_results.append(evaluation_result)

        score_line = evaluation_result['score_feedback'].split("\n")[0]
        try:
            score = int(''.join(filter(str.isdigit, score_line)))
            total_score += score
            file_count += 1
        except ValueError:
            pass

    avg_score = total_score / file_count if file_count > 0 else 0
    final_summary = generate_final_summary(all_results)

    summary_report = f"""
    # DevProbe Evaluation Summary:

    * Files Evaluated: {file_count}
    * Average Score: {avg_score:.2f}%
    
    {final_summary}
    """

    return summary_report

