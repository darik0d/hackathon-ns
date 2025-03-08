import os
import difflib
import cohere
from dotenv import load_dotenv

load_dotenv()
# Function to load a file
def load_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

# Function to generate diff between two code files
def generate_diff(file1, file2):
    lines1 = file1.splitlines()
    lines2 = file2.splitlines()
    diff = list(difflib.unified_diff(lines1, lines2, lineterm=""))
    return "\n".join(diff)

# Function to evaluate the developer's fixes using Cohere AI
def evaluate_with_cohere(original_code, bugged_code, fixed_code, bug_report, fix_report):

    # Fetch the Cohere API key from environment variables
    cohere_api_key = os.getenv("COHERE_API_KEY")

    if not cohere_api_key:
        print("Error: COHERE_API_KEY is not set in the .env file.")
        exit(1)

    # Initialize Cohere API client
    co = cohere.Client(cohere_api_key)

    # Step 1: Analyze the bug report and list the introduced bugs
    analyze_bugs_prompt = f"""
    You are an AI evaluator for a coding challenge. 
    Your task is to analyze the 'Bug Report' (Original → Bugged Code) and identify all the bugs that were introduced by the AI. 

    Please identify all the bugs and list them in the following format:
    - Bug 1: [description of bug]
    - Bug 2: [description of bug]
    - ...

    Bug Report (Original → Bugged Code):
    {bug_report}
    """

    # Send request for bug analysis
    bug_analysis_response = co.generate(
        model="command-r-plus",
        prompt=analyze_bugs_prompt,
        max_tokens=300,
        temperature=0.2
    )

    # Step 2: Evaluate the developer's fixes and explain what was fixed
    evaluate_fixes_prompt = f"""
    Now, please analyze the 'Fix Report' (Bugged Code → Developer Fixed Code) and evaluate what the developer fixed. 

    For each change, indicate:
    - What was fixed.
    - How well it was fixed.
    - Provide a brief explanation for each fix.

    Fix Report (Bugged Code → Developer Fixed Code):
    {fix_report}
    """

    # Send request for fix evaluation
    fix_analysis_response = co.generate(
        model="command-r-plus",
        prompt=evaluate_fixes_prompt,
        max_tokens=300,
        temperature=0.3
    )

    # Step 3: Check if any bugs were missed and assess the quality of the fix
    check_missed_bugs_prompt = f"""
    After analyzing the fix report, check if any bugs from the bug report were missed. 

    - For each bug from the bug report, indicate whether it was fixed.
    - If it was missed, explain why the fix was not adequate.
    - Provide feedback on how the developer can improve the fix.

    Bug Report (Original → Bugged Code):
    {bug_report}

    Fix Report (Bugged Code → Developer Fixed Code):
    {fix_report}
    """

    # Send request for checking missed bugs
    missed_bugs_response = co.generate(
        model="command-r-plus",
        prompt=check_missed_bugs_prompt,
        max_tokens=300,
        temperature=0.3
    )

    # Step 4: Provide a score and qualitative feedback based on the evaluation
    scoring_feedback_prompt = f"""
    Based on the analysis of the bug report, the fix report, and the missed bugs:
    
    - Provide a score (0 to 100%) based on how many bugs were fixed correctly.
    - Provide qualitative feedback: "Well done," "Needs improvement," "Excellent," etc.
    - Offer a brief explanation in 2-3 sentences about the overall performance of the developer.
    
    Bug Report (Original → Bugged Code):
    {bug_report}
    
    Fix Report (Bugged Code → Developer Fixed Code):
    {fix_report}
    
    Missed Bugs Analysis:
    {missed_bugs_response.generations[0].text}
    """

    # Send request for scoring and qualitative feedback
    scoring_feedback_response = co.generate(
        model="command-r-plus",
        prompt=scoring_feedback_prompt,
        max_tokens=300,
        temperature=0
    )

    # Combine the responses into a final evaluation result
    evaluation_result = f"""
    Bug Analysis: 
    {bug_analysis_response.generations[0].text}

    Fix Evaluation:
    {fix_analysis_response.generations[0].text}

    Missed Bugs Analysis:
    {missed_bugs_response.generations[0].text}

    Final Score & Feedback:
    {scoring_feedback_response.generations[0].text}
    """

    return evaluation_result

# Function to gather files dynamically from directories
def get_file_paths_from_os():
    file_paths = []

    # Define the subdirectories we're interested in
    sub_dirs = ['user_project', 'bugged', 'developer']

    # Get the current working directory
    base_dir = os.getcwd()

    # Build the full paths for each subdirectory
    sub_dirs_paths = {sub_dir: os.path.join(base_dir, sub_dir) for sub_dir in sub_dirs}

    # List all files in the user_project, bugged, and developer folders
    user_project_files = {f: os.path.join(sub_dirs_paths['user_project'], f) for f in os.listdir(sub_dirs_paths['user_project']) if f.endswith(".py")}
    bugged_files = {f: os.path.join(sub_dirs_paths['bugged'], f) for f in os.listdir(sub_dirs_paths['bugged']) if f.endswith(".py")}
    developer_files = {f: os.path.join(sub_dirs_paths['developer'], f) for f in os.listdir(sub_dirs_paths['developer']) if f.endswith(".py")}

    # Match files by name
    for filename in user_project_files:
        if filename in bugged_files and filename in developer_files:
            file_paths.append((
                user_project_files[filename],
                bugged_files[filename],
                developer_files[filename]
            ))

    return file_paths

def evaluate():
    # Get the file paths dynamically from the folders
    file_paths = get_file_paths_from_os()

    if not file_paths:
        print("No matching files found.")
        return

    # Process each set of files (original, bugged, fixed)
    eval_results = []
    for original_file_path, bugged_file_path, fixed_file_path in file_paths:
        # Load the files
        original_code = load_file(original_file_path)
        bugged_code = load_file(bugged_file_path)
        fixed_code = load_file(fixed_file_path)

        # Generate diff reports
        bug_report = generate_diff(original_code, bugged_code)
        fix_report = generate_diff(bugged_code, fixed_code)

        # Evaluate with Cohere AI
        eval_results.append(evaluate_with_cohere(original_code, bugged_code, fixed_code, bug_report, fix_report))

    # Put the entire result into a single report for all the files
    results = "put the results here"

    return results
