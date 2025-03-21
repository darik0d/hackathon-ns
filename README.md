# Bugify

Bugify is a powerful developer auditing tool that strategically introduces controlled bugs into codebases to help companies evaluate their development teams and improve their quality assurance processes.

Check out our video: https://youtu.be/xrtWyPhH30s?si=Jf7_IbmXW9oNcGTJ

## Make malicious code easier
Bugify specializes in generating sophisticated bugs and code vulnerabilities directly into your codebase:

Insert complex logical errors that bypass typical static analysis
Create subtle memory leaks and resource management issues
Introduce edge-case vulnerabilities that only manifest under specific conditions
Generate time-delayed bugs that activate after deployment
Plant security weaknesses that mimic common developer oversights

Our advanced bug generation engine creates realistic issues ranging from simple syntax errors to sophisticated multi-component failures, giving you complete control over the complexity and severity of introduced vulnerabilities.

## Wait - why would I want bugs in my code?

It may seem counterintuitive to intentionally add bugs to your codebase, but DevProbe serves multiple valuable purposes:

1. **Developer Evaluation**: Assess how effectively your developers identify, report, and fix different types of issues.
2. **Process Improvement**: Discover gaps in your code review, testing, and deployment workflows.
3. **Training**: Create safe, realistic scenarios for developers to practice troubleshooting.
4. **Metrics Gathering**: Gather concrete data about bug detection rates, resolution times, and process effectiveness.
5. **Security Hardening**: Test your team's ability to identify potential security issues before they become real problems.

All bugs introduced by Bugify are fully tracked, documented, and can be automatically removed if needed - no permanent damage to your codebase.

Check it out on Github: https://github.com/darik0d/hackathon-ns

## Ok, sounds useful - how do I get started?

Getting started with Bugify is straightforward:

```bash
# Clone the repository
git clone <repository_url>

# Navigate to the repository folder
cd Bugify

# Install dependencies
pip install -r requirements.txt   # or python setup.py install, pipenv install, poetry install

# Make the script executable (e.g., myscript.py)
chmod +x src/main.py

# Add the directory to PATH (edit ~/.bashrc or ~/.zshrc)
export PATH=$PATH:/path/to/your/repo

# Refresh the terminal session
source ~/.bashrc  # Or source ~/.zshrc for Zsh users

# Run the script from anywhere
bugify
```

Bugify supports multiple languages and frameworks including JavaScript, Python, Java, Ruby, and more. 

Soon we will make a documentation for the project.

## You are a genius - where can I find more information about the team?

Our team consists of seasoned software engineers and security professionals with decades of combined experience in code quality, security testing, and developer training.

* Samuel Berton
* Alperen Doganci
* Daria Matviichuk

---

*Bugify: Why introduce bugs occasionally when you can do it on purpose?*
