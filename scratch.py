import cohere

co = cohere.ClientV2("4fcYCoYe6SCRWfYOIbpK3SNYKs5fOttEa3fcpttM") # Your API key here

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

        prompt = f"Introduce {num_bugs} bugs into the file {file_name}. Output only the code!:\n"
        prompt += ''.join(lines)
        print("Prompt: ", prompt)

        response = co.chat(
            model="command-r-plus",
            messages=[{"role": "user", "content": prompt}]
        )
        # Extract path from the current working directory
        file_name = file_name.split("/")[-1]
        output_path = f"bugged/{file_name}"

        # Currently put the output to the bugged folder
        with open(output_path, 'w') as f:
            f.write(response.message.content[0].text)


if __name__ == "__main__":
    introduce_bugs([
        ("user_project/app.py", 1),
        ("user_project/routes.py", 3),
        ("user_project/models.py", 1),
        ("user_project/config.py", 1),
    ])
