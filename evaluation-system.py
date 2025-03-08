import json
import os
import git
import re
import difflib
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta

class DeveloperEvaluationSystem:
    def __init__(self, repo_path: str, report_path: str = None):
        """
        Initialize the evaluation system.
        
        Args:
            repo_path: Path to the Git repository
            report_path: Path to the bug report file
        """
        self.repo_path = repo_path
        self.repo = git.Repo(repo_path)
        self.report_path = report_path or os.path.join(repo_path, ".bug_report.json")
        self.bug_report = self._load_bug_report()
        
    def _load_bug_report(self) -> Dict[str, Any]:
        """Load the bug report from file"""
        if not os.path.exists(self.report_path):
            raise FileNotFoundError(f"Bug report not found at {self.report_path}")
        
        with open(self.report_path, 'r') as f:
            return json.load(f)
    
    def analyze_pull_request(self, pr_branch: str) -> Dict[str, Any]:
        """
        Analyze a pull request to evaluate developer's code review skills.
        
        Args:
            pr_branch: The name of the PR branch to analyze
            
        Returns:
            Evaluation results
        """
        # Get the base branch (where bugs were introduced)
        bug_branch = self.bug_report.get("branch_name")
        if not bug_branch:
            raise ValueError("Bug branch name not found in report")
        
        # Make sure both branches exist
        if bug_branch not in [b.name for b in self.repo.branches]:
            raise ValueError(f"Bug branch {bug_branch} not found")
        if pr_branch not in [b.name for b in self.repo.branches]:
            raise ValueError(f"PR branch {pr_branch} not found")
        
        # Get the diff between bug branch and PR branch
        self.repo.git.checkout(bug_branch)
        diff = self.repo.git.diff(pr_branch)
        
        # Evaluate each bug fix
        introduced_bugs = self.bug_report.get("bugs_introduced", [])
        evaluation_results = {
            "timestamp": datetime.now().isoformat(),
            "bug_branch": bug_branch,
            "pr_branch": pr_branch,
            "total_bugs": len(introduced_bugs),
            "bugs_found": 0,
            "bugs_fixed_correctly": 0,
            "bugs_fixed_incorrectly": 0,
            "bugs_missed": 0,
            "performance_score": 0.0,
            "bug_details": []
        }
        
        # Check each bug
        for bug in introduced_bugs:
            bug_file = bug.get("file")
            if not bug_file:
                continue
            
            bug_result = {
                "bug_id": bug.get("type") + "_" + str(bug.get("line", "")),
                "file": bug_file,
                "type": bug.get("type"),
                "severity": bug.get("severity", "unknown"),
                "status": "missed",
                "details": {}
            }
            
            # Check if the bug file was modified in the PR
            file_pattern = re.escape(bug_file)
            if re.search(r'diff --git a/' + file_pattern + r' b/' + file_pattern, diff):
                # File was modified, check if the specific line was changed
                file_diff_pattern = r'@@ .+? .+? @@[\s\S]+?(?=diff --git|\Z)'
                file_diffs = re.findall(file_diff_pattern, diff)
                
                for file_diff in file_diffs:
                    if bug_file in file_diff:
                        # Check for line-specific changes
                        line_num = bug.get("line")
                        if line_num:
                            line_pattern = r'[-+].+?' + re.escape(str(bug.get("original", "")))
                            if re.search(line_pattern, file_diff):
                                # Bug was identified and changed
                                bug_result["status"] = "fixed"
                                evaluation_results["bugs_found"] += 1
                                
                                # Check if the fix is correct
                                is_correct = self._verify_fix_correctness(bug, file_diff)
                                if is_correct:
                                    bug_result["status"] = "fixed_correctly"
                                    evaluation_results["bugs_fixed_correctly"] += 1
                                else:
                                    bug_result["status"] = "fixed_incorrectly"
                                    evaluation_results["bugs_fixed_incorrectly"] += 1
                                
                                bug_result["details"]["fix_correct"] = is_correct
            
            if bug_result["status"] == "missed":
                evaluation_results["bugs_missed"] += 1
            
            evaluation_results["bug_details"].append(bug_result)
        
        # Calculate performance score (weighted by severity)
        severity_weights = {"minor": 1, "moderate": 2, "severe": 3, "unknown": 1}
        weighted_found = 0
        weighted_total = 0
        
        for bug in evaluation_results["bug_details"]:
            weight = severity_weights.get(bug["severity"], 1)
            weighted_total += weight
            
            if bug["status"] == "fixed_correctly":
                weighted_found += weight
            elif bug["status"] == "fixed_incorrectly":
                weighted_found += weight * 0.5
        
        if weighted_total > 0:
            evaluation_results["performance_score"] = round((weighted_found / weighted_total) * 100, 2)
        
        return evaluation_results
    
    def _verify_fix_correctness(self, bug: Dict[str, Any], file_diff: str) -> bool:
        """
        Verify if the fix correctly addresses the bug.
        
        Args:
            bug: Bug information
            file_diff: Diff of the file containing the bug
            
        Returns:
            True if the fix is correct, False otherwise
        """
        # This is a simplified check that would need to be extended for real-world use
        bug_type = bug.get("type")
        
        if bug_type == "variable_typo":
            # Check if the original variable name is restored
            original_var = bug.get("original")
            if original_var and re.search(r'\+[^+]*\b' + re.escape(original_var) + r'\b', file_diff):
                return True
        
        elif bug_type == "boolean_flip":
            # Check if the correct operator is restored
            original_op = bug.get("original")
            if original_op and re.search(r'\+[^+]*' + re.escape(original_op), file_diff):
                return True
        
        elif bug_type == "security_vulnerability":
            # For security vulnerabilities, check for specific fixes
            subtype = bug.get("subtype")
            if subtype == "hardcoded_credentials":
                # Check if the hardcoded credential is removed
                return "api_key" in file_diff and re.search(r'[-][^-]*"S3CR3T_K3Y_', file_diff)
        
        elif bug_type == "off_by_one":
            # Check if the original range/index is restored
            original = bug.get("original")
            if original and re.search(r'\+[^+]*' + re.escape(original), file_diff):
                return True
        
        elif bug_type == "removed_comment":
            # Check if the comment is restored
            original = bug.get("original")
            if original and re.search(r'\+[^+]*' + re.escape(original), file_diff):
                return True
        
        # Default to more lenient checking for other bug types:
        # If there's a change on the relevant line and it's not just whitespace
        return bool(re.search(r'\+[^+\s]+', file_diff))
    
    def generate_evaluation_report(self, evaluation_results: Dict[str, Any]) -> str:
        """
        Generate a human-readable evaluation report.
        
        Args:
            evaluation_results: Results from analyze_pull_request
            
        Returns:
            Formatted report as a string
        """
        report = [
            "# Developer Code Review Evaluation Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            f"- Total bugs introduced: {evaluation_results['total_bugs']}",
            f"- Bugs found and fixed correctly: {evaluation_results['bugs_fixed_correctly']}",
            f"- Bugs found but fixed incorrectly: {evaluation_results['bugs_fixed_incorrectly']}",
            f"- Bugs missed entirely: {evaluation_results['bugs_missed']}",
            f"- Overall performance score: {evaluation_results['performance_score']}%",
            "",
            "## Bug Details"
        ]
        
        # Group bugs by status
        bugs_