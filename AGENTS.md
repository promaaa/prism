# AGENTS.md - AI Agent Guidelines

## Documentation Policy
**❌ DO NOT create `.md` or `.txt` files** for documentation, summaries, or notes during development.

### Where to Put Documentation
- **Code Comments**: Use docstrings and inline comments
- **README.md**: Core project documentation
- **Commit Messages**: Explain changes in commits
- **Issues/PRs**: Use GitHub for discussion

### What to Do Instead
- Add to existing README.md for core functionality
- Use code comments for implementation details
- Update docstrings with examples
- Create unit tests as living documentation

## Code Quality Guidelines
### Always:
- Write comprehensive docstrings for public functions
- Include type hints
- Add inline comments for complex logic
- Keep functions focused and well-named
- Write tests for new functionality

### Never:
- Create separate documentation files
- Leave TODO comments (resolve or create issues)
- Commit temporary files or debug output

## Version Control Policy
**❌ NEVER commit to git without explicit user permission.**

### What to do instead:
- Make code changes as requested
- Explain what changes were made
- Ask user if they want to commit changes
- Wait for explicit permission before `git commit` or `git push`

## File Organization
Keep repository structure clean:
```
prism/
├── prism/          # Core application code
├── scripts/        # Utility scripts (minimal)
├── tests/          # Tests only
├── assets/         # Static assets only
├── README.md       # Main documentation
├── requirements.txt
└── LICENSE
```

Remove unnecessary files:
- Delete `.md` files created during sessions (except core ones)
- Delete `.txt` files that are not `requirements.txt`
- Clean up temporary scripts

## Communication
- Explain solutions in code comments
- Avoid creating separate documentation files
- Focus on code changes and commit messages
- Suggest updating README.md for extensive documentation needs