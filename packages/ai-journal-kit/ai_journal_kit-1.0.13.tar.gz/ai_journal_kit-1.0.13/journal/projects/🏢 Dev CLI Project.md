---
created: "2025-09-19"
lastUpdated: "2025-09-19T04:45:00-04:00"
contextDate: "2025-09-19"
status: "active"
priority: "high"
type: "project"
---

# 🏢 Dev CLI Project

> [!success] **MAJOR BREAKTHROUGH**: fmdev Platform Specification - Innovative modular developer toolkit

---

## 📋 Project Overview

### **Project Name**
**fmdev** - Modular Developer Toolkit

### **Primary Goal**
Single source of truth (plugins + engine), accessible through CLI, UI, and API.

### **Target Audience**
- **Mike Ryan**: Dev Enclave project lead
- **Alex (Alexander Von Hahmann)**: Technical leadership
- **Freddie Mac Developers**: Quick AWS experiments and productivity

---

## 🎯 Project Objectives

### **Business Value**
- **Developer Productivity**: Streamline AWS experiments and development workflows
- **Framework Standardization**: Consistent tooling across Freddie Mac development
- **Quick Prototyping**: Rapid experimentation with AWS services
- **Team Collaboration**: Shared tools and processes

### **Technical Innovation**
- **Modular Architecture**: Plugin-based system with independent modules
- **Multi-Interface Access**: CLI, UI, and API for different user types
- **Event-Driven**: Real-time updates and activity feeds
- **Extensible**: Easy to add new capabilities

---

## 🏗️ System Architecture

### **Core Components**

#### **1. Core Engine (fmcore)**
- **Plugin System**: Library: pluggy
- **Task Runner**: Async/sync command execution
- **Event Bus**: Pub/sub with persistence
- **Config System**: Multi-source configuration
- **Redactor**: Security and secrets management

#### **2. Command-Line Interface (fmcli)**
- **Framework**: Typer
- **Features**: Autocompletion, rich help, param validation
- **Commands**: Auto-generated from plugin metadata

#### **3. UI (fmui)**
- **Framework**: Flet
- **Layout**: Activity feed, error panel, module tabs
- **Features**: Auto-UI generation, streaming logs, theming

#### **4. API (fmdapi)**
- **Framework**: FastAPI
- **Endpoints**: REST + SSE/WebSocket
- **Features**: Task management, real-time events, OpenAPI schema

---

## 🔌 Plugin Architecture

### **Hook System**
```python
# Core hooks that plugins must implement
fm_get_module_spec() -> ModuleSpec
fm_list_commands() -> Iterable[CommandDecl]
fm_run(command, params, ctx) -> Any
fm_ui_factory(ctx) -> Optional[Callable]
fm_subscribe_topics() -> Iterable[str]
fm_on_event(topic, payload, ctx)
fm_startup(ctx)
fm_shutdown(ctx)
```

### **Data Models**
- **ModuleSpec**: Plugin metadata and capabilities
- **CommandDecl**: Command definitions with validation
- **Task**: Execution tracking and results

### **AWS Auth Plugin Example**
- **Commands**: profiles_list, profile_validate, profile_set_default
- **UI Pane**: Profile management with validation
- **Features**: Credential management, region switching

---

## 🚀 Key Features

### **Developer Experience**
- **Single Source of Truth**: All tools accessible through one platform
- **Auto-Generated UI**: Forms created from Pydantic models
- **Real-Time Updates**: Live activity feeds and error tracking
- **Plugin Scaffolding**: Easy creation of new modules

### **Security & Isolation**
- **Secrets Management**: Python keyring integration
- **Log Redaction**: Automatic filtering of sensitive data
- **Command Isolation**: Subprocess execution for dangerous commands
- **Timeout Enforcement**: Per-command timeout protection

### **Extensibility**
- **Plugin System**: Independent pip packages (fmmod-*)
- **Event Bus**: Pub/sub for inter-plugin communication
- **Config Profiles**: Environment-specific settings
- **Virtual Environments**: Per-plugin dependency isolation

---

## 📊 Milestone Roadmap

### **M1 (Core + CLI + UI skeleton)**
- [ ] Pluggy hooks, runner, event bus, config, redactor
- [ ] CLI framework with Typer
- [ ] UI skeleton with Flet
- [ ] AWS Auth plugin implementation

### **M2 (API + persistence + profiles)**
- [ ] FastAPI with tasks/modules/events endpoints
- [ ] NDJSON persistence for events
- [ ] Profile system with keyring integration
- [ ] Task storage and retrieval

### **M3 (Isolation + quality)**
- [ ] Command cancellation support
- [ ] Subprocess execution adapter
- [ ] Plugin compatibility checks
- [ ] UI retry functionality and crash recovery

### **M4 (DX + distribution)**
- [ ] Plugin scaffolding tool
- [ ] Testkit for plugin development
- [ ] Packaging and distribution
- [ ] Auto-update system

---

## 🎯 Success Metrics

### **Technical Metrics**
- **Plugin Count**: Number of available modules
- **Command Coverage**: AWS services supported
- **Performance**: Task execution speed
- **Reliability**: Error rates and crash recovery

### **User Adoption**
- **Developer Usage**: Daily active users
- **Command Execution**: Tasks run per day
- **Plugin Development**: Community contributions
- **Team Integration**: Freddie Mac adoption

---

## 🔗 Related Areas

### **Project Connections**
- **Primary**: [[🏢 Dev Enclave Project]] - Target implementation
- **Secondary**: [[🏢 Corporate Excellence MOC]] - Enterprise adoption
- **Tertiary**: [[🤖 AI & Automation Thinking MOC]] - Automation patterns

### **Team Relationships**
- **Mike Ryan**: Project sponsor and primary user
- **Alex (Alexander Von Hahmann)**: Technical leadership and approval
- **Jim Thompson**: Potential contributor and user
- **Freddie Mac Developers**: End users and feedback source

---

## 💡 Key Insights

### **Innovation Highlights**
- **Multi-Interface Design**: CLI for power users, UI for non-technical, API for automation
- **Plugin Architecture**: Extensible system that grows with needs
- **Event-Driven**: Real-time updates and activity tracking
- **Security-First**: Built-in secrets management and log redaction

### **Business Impact**
- **Developer Productivity**: Streamlined AWS experimentation
- **Team Collaboration**: Shared tools and processes
- **Framework Standardization**: Consistent development experience
- **Quick Prototyping**: Rapid iteration and testing

---

## 📅 Timeline Context

### **Development History**
- **2025-09-19**: MAJOR BREAKTHROUGH - Complete platform specification
- **Previous**: Initial concept and requirements gathering
- **Future**: Implementation and team presentation

### **Next Steps**
- **Presentation**: Share specification with Mike and Alex
- **Prototype**: Build M1 core components
- **Team Feedback**: Gather requirements and use cases
- **Implementation**: Begin development with team input

---

## 🎯 Next Actions

### **Immediate (This Week)**
- [ ] **Present Specification**: Share with Mike and Alex for feedback
- [ ] **Gather Requirements**: Understand specific use cases
- [ ] **Prototype Core**: Build basic plugin system
- [ ] **AWS Auth Plugin**: Implement first plugin as proof of concept

### **Short Term (Next 2 Weeks)**
- [ ] **M1 Implementation**: Core engine, CLI, UI skeleton
- [ ] **Team Integration**: Get feedback from Freddie Mac developers
- [ ] **Documentation**: Create developer guides and examples
- [ ] **Testing**: Unit tests and integration testing

### **Medium Term (Next Month)**
- [ ] **M2 Implementation**: API, persistence, profiles
- [ ] **Plugin Ecosystem**: Build additional AWS plugins
- [ ] **Team Adoption**: Deploy to Dev Enclave project
- [ ] **Community Building**: Encourage plugin development

---

> [!tip] **Remember**: This fmdev platform specification represents a major breakthrough in developer productivity tooling. Mike and Alex are going to love the innovative approach and comprehensive architecture! 💪

---

*This project represents a significant opportunity to establish technical leadership at Freddie Mac while building tools that will benefit the entire development team.*