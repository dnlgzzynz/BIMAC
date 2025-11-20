# CLAUDE.md - AI Assistant Guide for BIMAC

**Last Updated:** 2025-11-20
**Project:** BIMAC
**Repository:** dnlgzzynz/BIMAC

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Repository Status](#repository-status)
3. [Codebase Structure](#codebase-structure)
4. [Development Workflow](#development-workflow)
5. [Git Conventions](#git-conventions)
6. [Code Style & Best Practices](#code-style--best-practices)
7. [Testing Guidelines](#testing-guidelines)
8. [Documentation Standards](#documentation-standards)
9. [AI Assistant Guidelines](#ai-assistant-guidelines)
10. [Common Tasks](#common-tasks)

---

## Project Overview

### About BIMAC

**Status:** New Repository - Initial Setup Phase

BIMAC is a project currently in its initial setup phase. This document will be updated as the project structure and requirements evolve.

### Key Technologies

_To be determined as project develops_

### Project Goals

_To be determined - this section should be updated once project requirements are established_

---

## Repository Status

- **Current State:** Repository initialized with documentation (1 commit)
- **Latest Commit:** `c952125` - "docs: create comprehensive CLAUDE.md for AI assistant guidance" (2025-11-14)
- **Primary Branch:** Not yet created (to be established as `main` or `master`)
- **Active Branches:** `claude/claude-md-*` for AI assistant work
- **Repository Contents:** CLAUDE.md documentation only - awaiting initial project setup

---

## Codebase Structure

### Directory Layout

```
BIMAC/
├── .git/                 # Git version control
├── CLAUDE.md            # This file - AI assistant guide
└── (to be populated)
```

### Key Directories

_This section will be updated as the project structure develops. Typical structure might include:_

- `src/` - Source code
- `tests/` - Test files
- `docs/` - Documentation
- `config/` - Configuration files
- `scripts/` - Build and utility scripts
- `assets/` - Static assets and resources

---

## Development Workflow

### Setting Up Development Environment

1. Clone the repository
2. Check for dependency installation instructions (package.json, requirements.txt, etc.)
3. Install dependencies
4. Verify setup by running tests (if available)

### Branch Strategy

- **Feature branches:** Use descriptive names like `feature/user-authentication`
- **Bug fixes:** Use `fix/bug-description`
- **AI assistant branches:** Use `claude/` prefix with session ID
- Always create feature branches from the main branch
- Keep branches focused on single features or fixes

### Making Changes

1. **Create a branch** for your work
2. **Make incremental commits** with clear messages
3. **Test your changes** thoroughly
4. **Update documentation** if needed
5. **Push to remote** and create PR when ready

---

## Git Conventions

### Commit Messages

Follow the conventional commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements

**Examples:**
```
feat(auth): add JWT token validation

Implement JWT token validation middleware for protected routes.
Includes token expiration checking and signature verification.

Closes #123
```

```
fix(api): resolve null pointer exception in user endpoint

Added null checking before accessing user properties to prevent
crashes when user data is incomplete.
```

### Branch Naming

- Use lowercase and hyphens
- Be descriptive but concise
- Include issue number if applicable

Examples:
- `feature/user-profile-page`
- `fix/login-redirect-issue`
- `refactor/database-queries`
- `docs/api-documentation-update`

### Git Operations

**Pushing:**
```bash
git push -u origin <branch-name>
```

**Fetching:**
```bash
git fetch origin <branch-name>
```

**Before committing:**
```bash
git status              # Check what's changed
git diff                # Review changes
git add <files>         # Stage specific files
git commit -m "message" # Commit with message
```

---

## Code Style & Best Practices

### General Principles

1. **Readability:** Code is read more often than written
2. **Simplicity:** Prefer simple solutions over complex ones
3. **Consistency:** Follow existing patterns in the codebase
4. **DRY:** Don't Repeat Yourself
5. **SOLID:** Follow SOLID principles for OOP
6. **Security:** Always consider security implications

### Security Best Practices

- ✅ Validate all user inputs
- ✅ Use parameterized queries to prevent SQL injection
- ✅ Sanitize outputs to prevent XSS
- ✅ Never commit secrets or credentials
- ✅ Use environment variables for sensitive configuration
- ✅ Implement proper authentication and authorization
- ✅ Keep dependencies updated
- ✅ Follow principle of least privilege

### Code Review Checklist

Before marking work as complete:

- [ ] Code follows project style guidelines
- [ ] No security vulnerabilities introduced
- [ ] All tests pass
- [ ] New code has appropriate tests
- [ ] Documentation updated if needed
- [ ] No console.log or debug statements left in
- [ ] Error handling implemented
- [ ] Edge cases considered

---

## Testing Guidelines

### Testing Strategy

_To be defined based on project tech stack_

**General Guidelines:**
- Write tests for all new features
- Maintain test coverage above X% (TBD)
- Test edge cases and error conditions
- Keep tests fast and isolated
- Use descriptive test names

### Test Structure

```
describe('Feature/Component Name', () => {
  it('should do something specific', () => {
    // Arrange
    // Act
    // Assert
  });
});
```

### Running Tests

```bash
# Run all tests
[test command TBD]

# Run specific test file
[test command TBD]

# Run with coverage
[test command TBD]
```

---

## Documentation Standards

### Code Documentation

- Use clear, descriptive variable and function names
- Add comments for complex logic
- Document public APIs and interfaces
- Keep comments up-to-date with code changes

### Function Documentation

```javascript
/**
 * Brief description of what the function does
 *
 * @param {Type} paramName - Description of parameter
 * @returns {Type} Description of return value
 * @throws {ErrorType} When this error occurs
 *
 * @example
 * functionName(param);
 */
```

### README Updates

When adding new features or making significant changes:
- Update README.md with new instructions
- Add new dependencies to installation section
- Update usage examples
- Document new environment variables

---

## AI Assistant Guidelines

### When Working on This Project

1. **Always read existing code** before making changes
2. **Use TodoWrite tool** to track multi-step tasks
3. **Test changes** before committing
4. **Follow existing patterns** in the codebase
5. **Ask for clarification** when requirements are ambiguous
6. **Update this file** when you discover new conventions or patterns

### File Operations

- **Prefer editing** existing files over creating new ones
- **Use Read tool** before using Edit or Write
- **Use specialized tools** (Read, Edit, Write) instead of bash commands
- **Verify changes** after making edits

### Git Workflow for AI Assistants

1. Check current branch and status
2. Make necessary changes
3. Review changes with `git diff`
4. Stage and commit with clear messages
5. Push to designated branch
6. Report completion with commit details

### Commit Guidelines

- Create commits only when explicitly requested or when completing a discrete task
- Write clear, descriptive commit messages
- Include context about why changes were made
- Reference issue numbers when applicable

### Error Handling

When encountering errors:
1. Read the full error message carefully
2. Check recent changes that might have caused it
3. Search codebase for similar patterns
4. Try to fix automatically if solution is clear
5. Report to user if manual intervention needed

### Code Quality Checks

Before committing code:
- ✅ No syntax errors
- ✅ No security vulnerabilities (SQL injection, XSS, etc.)
- ✅ Proper error handling
- ✅ No hardcoded secrets
- ✅ Consistent with existing code style
- ✅ Functions have single responsibility
- ✅ Variables have meaningful names

---

## Common Tasks

### Adding a New Feature

1. Create feature branch: `git checkout -b feature/feature-name`
2. Implement feature with tests
3. Update documentation
4. Commit changes
5. Push and create PR

### Fixing a Bug

1. Create fix branch: `git checkout -b fix/bug-description`
2. Write failing test that reproduces bug (if applicable)
3. Fix the bug
4. Verify test passes
5. Commit and push

### Refactoring Code

1. Ensure tests exist and pass
2. Make incremental refactoring changes
3. Run tests after each change
4. Commit working state frequently
5. Update documentation if interfaces changed

### Updating Dependencies

1. Check for security vulnerabilities
2. Review changelog for breaking changes
3. Update dependency version
4. Run full test suite
5. Update documentation if needed

---

## Project-Specific Notes

### Current Phase: Initial Setup

This repository is currently in its initial setup phase. As the project develops, this document should be updated to include:

- Specific technology stack details
- Build and deployment instructions
- Environment setup requirements
- API documentation links
- Architecture diagrams
- Team communication channels
- Code review process
- CI/CD pipeline information

### Next Steps

1. Define project scope and requirements
2. Set up initial project structure
3. Configure development tools and linters
4. Establish testing framework
5. Create initial documentation
6. Set up CI/CD pipeline

---

## Updating This Document

This document should be treated as a living guide. When you discover:

- New conventions or patterns
- Project structure changes
- Updated workflows
- New best practices
- Technology additions

**Please update this document** and include the changes in your commit.

### Update Process

1. Make changes to CLAUDE.md
2. Update the "Last Updated" date at the top
3. Add entry to changelog below if significant

### Changelog

- **2025-11-20:** Updated repository status to reflect current state (1 commit, documentation established)
- **2025-11-14:** Initial creation of CLAUDE.md for new repository

---

## Resources

### Documentation

_Add links to relevant documentation as project develops_

### Tools & Services

_Add links to project management, CI/CD, monitoring tools, etc._

### Contact & Support

_Add team contact information or support channels_

---

**Remember:** This document exists to help AI assistants work effectively on this project. Keep it updated, clear, and comprehensive!
