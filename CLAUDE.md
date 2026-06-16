# CLAUDE.md — LosAlamos Project

PROJECT_TYPE:      private
LANGUAGE:          Python
FRAMEWORK:         pygame
PACKAGE_MANAGER:   uv
TEST_FRAMEWORK:    pytest
STYLE_GUIDE:       PEP8
LINTER/FORMATTER:  ruff

## GitHub
- Use account: github-privat (Wolrak93 / joachimwingerning@gmail.com)
- Repo visibility: private

## Experiment Modifications (overrides global CLAUDE.md workflow)
1. Entire development cycle is programmed at once in the development branch.
   No feature-by-feature merge approval. User tests at the end of the cycle.
   Flow: development branch → plan cycle together → Claude programs the whole cycle → user tests → merge to master on success.
2. Use the superpowers brainstorming skill for all GUI tasks without asking for permission.
