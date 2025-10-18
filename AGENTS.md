<file_path>
prism/AGENTS.md
</file_path>

<edit_description>
Create AGENTS.md file to instruct agents not to create markdown files
</edit_description>

# AGENTS.md - Instructions for AI Agents

## Purpose

This file contains specific instructions for AI agents (like GitHub Copilot, Claude, or other coding assistants) working on the Prism codebase. These guidelines ensure clean, maintainable code without unnecessary documentation clutter.

## Documentation Policy

### ❌ DO NOT Create Markdown Files

**Under no circumstances should you create new `.md` or `.txt` files** for documentation, summaries, or notes during development sessions.

#### What NOT to do:
- Create `SOLUTION_SUMMARY.md`
- Create `IMPLEMENTATION_GUIDE.md`
- Create `FIX_DOCUMENTATION.md`
- Create `QUICK_START.md` (unless it's a core project file)
- Create any `.txt` files for notes, summaries, or temporary documentation

#### Why this matters:
- The repository becomes cluttered with temporary files
- Documentation should be integrated into code comments, docstrings, and official README files
- Markdown files created during conversations are often redundant and not maintained
- This keeps the repository clean and focused on code

### ✅ Where to Put Documentation

1. **Code Comments**: Use inline comments and docstrings for function/class documentation
2. **README.md**: Core project documentation goes here
3. **Code Examples**: Include usage examples in docstrings
4. **Commit Messages**: Explain changes in commit messages, not separate files
5. **Issues/PRs**: Use GitHub issues and pull requests for discussion

### ✅ What to Do Instead

When documenting solutions or fixes:

1. **Add to existing README.md** if it's core functionality
2. **Use code comments** for implementation details
3. **Update docstrings** with examples and parameter descriptions
4. **Create unit tests** that serve as living documentation
5. **Use GitHub issues/PRs** for discussion and planning

## Code Quality Guidelines

### Always:
- Write comprehensive docstrings for public functions
- Include type hints
- Add inline comments for complex logic
- Keep functions focused and well-named
- Write tests for new functionality

### Never:
- Create separate documentation files during development
- Leave TODO comments in code (resolve or create issues)
- Commit temporary files or debug output

## Version Control Policy

### ❌ NEVER Commit to Git Without User Permission

**Under no circumstances should you commit changes to git** without explicit permission from the user.

#### What NOT to do:
- Auto-commit changes after making edits
- Push changes to remote repositories
- Create commits for "cleanup" or "fixes" without asking
- Stage files for commit without user approval

#### Why this matters:
- Users maintain control over their codebase
- Prevents accidental commits of incomplete work
- Allows users to review changes before committing
- Maintains proper version control workflow

#### What to do instead:
- Make code changes as requested
- Explain what changes were made
- Ask the user if they want to commit the changes
- Wait for explicit permission before running `git commit` or `git push`

## File Organization

### Keep the repository structure clean:
```
prism/
├── prism/          # Core application code
├── scripts/        # Utility scripts (keep minimal)
├── tests/          # Tests only
├── assets/         # Static assets only
├── README.md       # Main documentation
├── requirements.txt
└── LICENSE
```

### Remove unnecessary files:
- Delete any `.md` files created during sessions (except core ones)
- Delete `.txt` files that are not `requirements.txt`
- Clean up temporary scripts after use

## Communication

When working with users:
- Explain solutions verbally or in code comments
- Avoid creating separate documentation files
- Focus on code changes and commit messages
- If extensive documentation is needed, suggest updating README.md

## Enforcement

If you find yourself wanting to create a markdown file:
1. Stop and reconsider if it's truly necessary
2. If it is, add it to README.md or create a proper documentation structure
3. If it's temporary, use comments in the code instead
4. Remember: clean repositories are better than documented ones

---

**This file serves as a reminder to keep the codebase clean and focused. Thank you for following these guidelines!** 🚀