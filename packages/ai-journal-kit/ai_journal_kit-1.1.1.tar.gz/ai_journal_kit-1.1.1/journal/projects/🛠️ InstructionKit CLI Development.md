---
created: 2025-10-21
lastUpdated: 2025-10-21T05:15:00
contextDate: 2025-10-21
tags: [project, cli, ai-tools, python, pip-installable]
status: active
priority: high
---

# 🛠️ InstructionKit CLI Development

> [!project] **Active Project**
> A pip-installable CLI tool for installing AI coding tool instructions from repositories

---

## 📋 Project Overview

**Project Name:** InstructionKit CLI  
**Feature Branch:** `002-template-cli-installer`  
**Created:** 2025-10-20  
**Status:** Draft → Active Development  
**Priority:** High  

### **Core Value Proposition**
Enable developers to install pre-built instructions (code review guidelines, documentation standards, best practices) from remote repositories into their AI coding tools (Cursor, Winsurf, GitHub Copilot, Claude Code) with a single command.

**Real-World Problem:** At Freddie Mac, we're stuck with GPT-4.1 which "REALLY sucks" compared to modern LLMs (GPT-5/Claude 4.5). Better instructions can bridge this gap and make older models more effective.

### **Key Features**
- **Pip-installable CLI tool** for easy distribution
- **Multi-tool support** (Cursor, Winsurf, GitHub Copilot, Claude Code)
- **Repository-based instructions** (GitHub, Bitbucket, GitLab, self-hosted)
- **Bundle installation** (multiple related instructions at once)
- **Auto-detection** of installed AI coding tools
- **Conflict resolution** for existing instructions
- **Private repository support** with authentication

---

## 🎯 User Stories & Priorities

### **P1 - Core Installation (Priority: Critical)**
1. **Install Instructions from Repository** - Single command installation from any Git repo
2. **Install Instruction Bundles** - Multiple related instructions at once (e.g., Python stack)

### **P2 - Discovery & Management (Priority: High)**
3. **List Available Instructions** - Browse repository contents before installing
4. **View Installed Instructions** - See what's currently installed
5. **Detect AI Coding Tool Automatically** - Auto-detect installed tools

### **P3 - Lifecycle Management (Priority: Medium)**
6. **Uninstall Instructions** - Remove previously installed instructions

---

## 🏗️ Technical Architecture

### **Core Components**
- **CLI Interface** - Command-line interface with subcommands
- **Repository Handler** - Git repository cloning and instruction discovery
- **Tool Detector** - Auto-detect installed AI coding tools
- **File Manager** - Handle instruction file installation and conflicts
- **Authentication Manager** - Handle private repository access
- **Metadata Tracker** - Track installed instructions and their sources

### **Supported AI Coding Tools**
- **Cursor** - Configuration directory detection
- **Winsurf** - Configuration directory detection  
- **GitHub Copilot** - Configuration directory detection
- **Claude Code** - Configuration directory detection

### **Repository Support**
- **GitHub** - Public and private repositories
- **Bitbucket** - Public and private repositories
- **GitLab** - Public and private repositories
- **Self-hosted Git** - Custom Git servers

---

## 📊 Success Criteria

### **Performance Targets**
- **SC-001:** Single instruction installation in under 30 seconds
- **SC-002:** Correct configuration directory detection on Windows, macOS, Linux
- **SC-003:** 95% successful installations on first attempt
- **SC-004:** User can install without documentation after one example
- **SC-005:** Instruction listing in under 5 seconds (up to 50 instructions)
- **SC-006:** Bundle installation (5+ instructions) in under 60 seconds
- **SC-007:** Clear conflict resolution on first attempt
- **SC-008:** List installed instructions in under 10 seconds
- **SC-009:** Each instruction as separate, clearly-named file

### **Quality Targets**
- **Error Handling:** Clear, actionable error messages
- **User Experience:** Intuitive commands and prompts
- **Reliability:** Graceful handling of network issues and permissions
- **Security:** Secure handling of authentication credentials

---

## 🛠️ Development Plan

### **Phase 1: Core CLI Framework**
- [ ] Set up Python project structure
- [ ] Implement basic CLI interface with Click/argparse
- [ ] Add pip packaging configuration
- [ ] Create basic command structure (install, list, uninstall)

### **Phase 2: Repository Integration**
- [ ] Implement Git repository cloning
- [ ] Add instruction discovery from repository structure
- [ ] Handle public repository access
- [ ] Add instruction file validation

### **Phase 3: AI Tool Integration**
- [ ] Implement AI coding tool detection
- [ ] Add configuration directory mapping
- [ ] Handle file installation and conflict resolution
- [ ] Test with each supported tool

### **Phase 4: Advanced Features**
- [ ] Add private repository authentication
- [ ] Implement bundle installation
- [ ] Add metadata tracking for installed instructions
- [ ] Create uninstall functionality

### **Phase 5: Polish & Distribution**
- [ ] Add comprehensive error handling
- [ ] Create user documentation
- [ ] Set up CI/CD pipeline
- [ ] Publish to PyPI

---

## 🔧 Technical Requirements

### **Dependencies**
- **Python 3.8+** - Core runtime
- **Git** - Repository access
- **Click/argparse** - CLI framework
- **requests** - HTTP operations
- **cryptography** - Checksum validation
- **pathlib** - Cross-platform path handling

### **Configuration Directories**
- **Cursor:** `~/.cursor/` (macOS/Linux), `%APPDATA%\Cursor\` (Windows)
- **Winsurf:** `~/.winsurf/` (macOS/Linux), `%APPDATA%\Winsurf\` (Windows)
- **GitHub Copilot:** `~/.github-copilot/` (macOS/Linux), `%APPDATA%\GitHub Copilot\` (Windows)
- **Claude Code:** `~/.claude-code/` (macOS/Linux), `%APPDATA%\Claude Code\` (Windows)

### **Repository Structure**
```
instruction-repo/
├── instructions/
│   ├── python-best-practices.md
│   ├── terraform-security.md
│   └── react-patterns.md
├── bundles/
│   ├── python-stack.json
│   └── web-development.json
└── metadata.json
```

---

## 🎯 Current Status

### **Next Steps**
1. **Set up project structure** - Python package with proper packaging
2. **Implement basic CLI** - Install, list, uninstall commands
3. **Add repository cloning** - Git integration for instruction discovery
4. **Test with Cursor** - Start with one AI tool for validation

### **Immediate Tasks**
- [ ] Create Python project structure
- [ ] Set up pip packaging (setup.py/pyproject.toml)
- [ ] Implement basic CLI interface
- [ ] Add Git repository cloning functionality
- [ ] Test instruction discovery from repository

---

## 🔗 Related Projects

### **Inspiration**
- **FM VS Code System Instructions** - Current manual process this tool would automate
- **Copilot Custom Prompts** - Existing instruction management in workspace
- **AI Development Patterns** - Knowledge area for best practices

### **Integration Points**
- **Rize MCP Server** - Could track time spent on instruction management
- **Daybreak AI Development** - Could use this tool for instruction distribution
- **Dev Enclave Project** - Could benefit from standardized instructions
- **Freddie Mac GPT-4.1 Problem** - Direct solution to current FM limitations
- **Personal Brand Building** - Could be a major project to get your name out there

---

## 📚 Resources & References

### **Documentation**
- [Python Packaging User Guide](https://packaging.python.org/)
- [Click Documentation](https://click.palletsprojects.com/)
- [GitPython Documentation](https://gitpython.readthedocs.io/)

### **Examples**
- **Cursor Configuration** - Current manual instruction management
- **VS Code Extensions** - Similar CLI tool patterns
- **Package Managers** - pip, npm, cargo as inspiration

---

## 💡 Future Enhancements

### **Potential Features**
- **Instruction Marketplace** - Centralized repository of instructions
- **Version Management** - Update installed instructions
- **Custom Transformations** - Instruction preprocessing during installation
- **Cross-machine Sync** - Synchronize instructions across devices
- **Instruction Validation** - Validate instruction format and content
- **Enterprise Solutions** - Corporate instruction management for teams
- **LLM Performance Optimization** - Instructions specifically designed to improve older model performance

### **Integration Opportunities**
- **CI/CD Integration** - Install instructions in build pipelines
- **Team Management** - Share instruction sets across teams
- **Analytics** - Track instruction usage and effectiveness

---

*Last updated: 2025-10-21 05:15 AM*
