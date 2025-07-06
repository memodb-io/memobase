# Contributing to Memobase

Thank you for your interest in contributing to Memobase! This document provides guidelines and instructions for contributing to the project.

## Table of Contents
- [Development Setup](#development-setup)
  - [Server Development](#server-development)
  - [Client Development](#client-development)
- [Development Workflow](#development-workflow)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [PR or Issue?](#pr-or-issue?)
- [Communication](#communication)

## Development Setup

### Server Development

#### Prerequisites
- Python (>= 3.11)
- Docker
- Git

#### Setting Up the Environment
1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/memobase.git
   cd memobase
   ```

3. Set up the virtual environment:
   ```bash
   cd src/server/api
   python3 -m venv .venv
   source .venv/bin/activate
   pip3 install -r requirements.txt
   ```

4. Run the server:

For more detailed information, refer to the [server documentation](./src/server/readme.md#development).


## Development Workflow

1. Create a branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes with frequent commits:
   ```bash
   git commit -m "feat: add your feature"
   ```

   *[Recommended commit message style](https://www.conventionalcommits.org/en/v1.0.0/)*
   
3. Write tests for your changes

4. Update documentation as needed

## Pull Request Process

1. Rebase your branch onto the latest `dev` branch:
   ```bash
   git checkout dev
   git pull upstream dev
   git checkout your-branch
   git rebase dev
   ```

2. Fix up commits to maintain clean history:
   ```bash
   git rebase -i dev
   ```

3. Before submitting, ensure:
   - All tests pass
   - Code is properly formatted
   - Documentation is updated

4. Submit your PR with:
   - A clear title following the commit message format
   - A comprehensive description of your changes
   - References to any related issues



## PR or Issue?

- We will not accept document typo fix PR, just make an issue if you find any typo.

## Communication

If you have questions or need help, please:

- Check existing issues and documentation
- Create a new issue for discussion
- Join our [Discord](https://discord.com/invite/YdgwU4d9NB)

Thank you for contributing to Memobase!

