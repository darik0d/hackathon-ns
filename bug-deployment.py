import os
import git
import random
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from bug_generator import BugGenerator

class BugDeploymentSystem:
    def __init__(self, repo_path: str, config_path: str = None):
        """
        Initialize the bug deployment system.
        
        Args:
            repo_path: Path to the Git repository
            config_path: Path to the configuration file
        """
        self.repo_path = repo_path
        self.repo = git.Repo(repo_path)
        self.bug_generator = BugGenerator()
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration"""
        logger = logging.getLogger("bug_deployment")
        logger.setLevel(logging.INFO)
        
        # Create handlers
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler("bug_deployment.log")
        
        # Create formatters
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(formatter)
        f_handler.setFormatter(formatter)
        
        # Add handlers to the logger
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)
        
        return logger
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            "excluded_files": [".gitignore", "README.md", "LICENSE"],
            "excluded_directories": ["node_modules", "venv", ".git", ".github"],
            "file_extensions": [".py", ".js", ".ts", ".java", ".cpp", ".c", ".h"],
            "max_bugs_per_file": 2,
            "probability_of_file_selection": 0.3,
            "target_branch_prefix": "test/bug-review-",
            "severity_levels": {
                "minor": 0.5,
                "moderate": 0.3,
                "severe": 0.2
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    # Merge configs, with user config taking precedence
                    for key, value in user_config.items():
                        default_config[key] = value
            except Exception as e:
                self.logger.error(f"Error loading config file: {e}")
        
        return default_config
    
    def get_candidate_files(self) -> List[str]:
        """Get a list of files that are candidates for bug injection"""
        candidates = []
        
        for root, dirs, files in os.walk(self.repo_path):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in self.config["excluded_directories"]]
            
            for file in files:
                # Skip excluded files
                if file in self.config["excluded_files"]:
                    continue
                
                # Check file extension
                if not any(file.endswith(ext) for ext in self.config["file_extensions"]):
                    continue
                
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, self.repo_path)
                candidates.append(relative_path)
        
        return candidates
    
    def create_bug_branch(self) -> str:
        """Create a new branch for bug introduction"""
        # Make sure we're starting from the main branch
        main_branch = self.repo.active_branch.name
        self.repo.git.checkout(main_branch)
        
        # Create a new branch with timestamp
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        branch_name = f"{self.config['target_branch_prefix']}{timestamp}"
        self.repo.git.checkout('-b', branch_name)
        
        return branch_name
    
    def introduce_bugs(self, num_files: int = None) -> Dict[str, Any]:
        """
        Introduce bugs into the codebase.
        
        Args:
            num_files: Number of files to modify, or None to use probability-based selection
            
        Returns:
            Dictionary containing information about the introduced bugs
        """
        candidate_files = self.get_candidate_files()
        if not candidate_files:
            self.logger.error("No candidate files found")
            return {"success": False, "error": "No candidate files found"}
        
        # Create a new branch
        branch_name = self.create_bug_branch()
        
        # Select files to modify
        if num_files is None:
            # Use probability-based selection
            selected_files = [f for f in candidate_files 
                            if random.random() < self.config["probability_of_file_selection"]]
            # Ensure at least one file is selected
            if not selected_files and candidate_files:
                selected_files = [random.choice(candidate_files)]
        else:
            # Select specific number of files
            num_to_select = min(num_files, len(candidate_files))
            selected_files = random.sample(candidate_files, num_to_select)
        
        bug_report = {
            "branch_name": branch_name,
            "timestamp": datetime.now().isoformat(),
            "bugs_introduced": []
        }
        
        # Introduce bugs in selected files
        for file_path in selected_files:
            full_path = os.path.join(self.repo_path, file_path)
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    original_code = f.read()
                
                # Determine number of bugs to introduce in this file
                num_bugs = random.randint(1, self.config["max_bugs_per_file"])
                
                # Generate bugs
                modified_code, bugs = self.bug_generator.generate_bugs(
                    original_code, 
                    num_bugs=num_bugs
                )
                
                # Only write if bugs were successfully introduced
                successful_bugs = [bug for bug in bugs if bug.get("success", False)]
                if successful_bugs:
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(modified_code)
                    
                    # Add file information to bugs
                    for bug in successful_bugs:
                        bug["file"] = file_path
                    
                    bug_report["bugs_introduced"].extend(successful_bugs)
                    self.logger.info(f"Introduced {len(successful_bugs)} bugs in {file_path}")
            
            except Exception as e:
                self.logger.error(f"Error processing file {file_path}: {e}")
        
        # Commit changes
        if bug_report["bugs_introduced"]:
            self.repo.git.add(".")
            commit_message = f"Test: Introduce bugs for code review exercise"
            self.repo.git.commit("-m", commit_message)
            self.logger.info(f"Committed changes to branch {branch_name}")
            
            # Save bug report to file
            report_path = os.path.join(self.repo_path, ".bug_report.json")
            with open(report_path, 'w') as f:
                json.dump(bug_report, f, indent=2)
            
            bug_report["success"] = True
        else:
            self.logger.warning("No bugs were successfully introduced")
            # Discard the branch if no bugs were introduced
            self.repo.git.checkout(self.repo.active_branch.name)
            self.repo.git.branch("-D", branch_name)
            bug_report["success"] = False
            bug_report["error"] = "No bugs were successfully introduced"
        
        return bug_report
    
    def revert_to_main(self):
        """Revert to the main branch and clean up"""
        main_branch = "main"  # or "master" depending on your repository
        try:
            current_branch = self.repo.active_branch.name
            if current_branch.startswith(self.config["target_branch_prefix"]):
                self.repo.git.checkout(main_branch)
                self.logger.info(f"Reverted to {main_branch} branch")
        except Exception as e:
            self.logger.error(f"Error reverting to main branch: {e}")
