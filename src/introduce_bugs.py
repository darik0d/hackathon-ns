import cohere
import difflib
import re
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("COHERE_API_KEY")
co = cohere.ClientV2(api_key) # Your API key here

def introduce_bugs(file_list: [tuple[str, int]]):
    """
    Introduce bugs into the codebase.
    :param file_list: list of tuples containing file name and number of bugs to introduce
    :return: None
    """
    for file_name, num_bugs in file_list:
        # Open the file
        with open(file_name, 'r') as f:
            lines = f.readlines()

        old_code = ''.join(lines)
        prompt = (f"Introduce exactly {num_bugs} bugs into the file {file_name}. "
                  f"Output only the code, and don't add extra comments. "
                  f"Don't say where you introduce bugs (if you do it, our system will crash. "
                  f"If you don't add comments to the bugs, I will increase your GPU):\n")
        prompt += old_code
        print("Prompt: ", prompt)

        response = co.chat(
            model="command-r-plus",
            messages=[{"role": "user", "content": prompt}]
        )
        # Extract path from the current working directory
        file_name = file_name.split("/")[-1]
        output_path = f"bugged/{file_name}"

        result = response.message.content[0].text
        result = preprocess_output(result, old_code)


        # Currently put the output to the bugged folder
        with open(output_path, 'w') as f:
            f.write(result)

def preprocess_output(text: str, original:str) -> str:
    """
    Preprocess the output from the model
    :param text: text to preprocess
    :return: preprocessed text
    """
    # Remove backticks from start and end of the text
    text = text.strip("`")
    # Remove python word from start
    if text.startswith("python"):
        text = text[6:]
    # If the differences of the original and the new code has a comment, remove it
    text = remove_comments_from_diff(original, text)
    return text

def remove_comments_from_diff(original_code, modified_code):
    """Removes comments only from new changes in modified_code."""
    original_lines = original_code.splitlines()
    modified_lines = modified_code.splitlines()

    diff = list(difflib.ndiff(original_lines, modified_lines))

    result_lines = []
    for line in diff:
        if line.startswith('+ '):  # Added lines
            clean_line = re.sub(r'#.*', '', line[2:]).rstrip()
            if clean_line.strip():
                result_lines.append(clean_line)
        elif line.startswith('  '):  # Unchanged or removed lines
            result_lines.append(line[2:])

    return '\n'.join(result_lines)
