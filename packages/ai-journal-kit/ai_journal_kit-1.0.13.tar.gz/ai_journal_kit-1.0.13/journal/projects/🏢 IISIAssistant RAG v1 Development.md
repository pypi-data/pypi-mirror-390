---
created: 2025-09-15
tags: [project, active, ai, rag, doug-loud, iisiassistant]
rank: 8.5
status: active
---

# 🏢 IISIAssistant RAG v1 Development

> [!project] **AI-Powered Document Processing & Query System**
> Building scalable RAG (Retrieval-Augmented Generation) system for Doug Loud's IISIAssistant

---

## 🎯 Project Overview

### Objective
Develop a comprehensive RAG v1 system with modular workflows for document ingestion, auto-sync, and intelligent querying to replace the current problematic doc loader.

### Business Value
- **Scalability** - Modular architecture for future growth
- **Reliability** - Robust error handling and change detection
- **Efficiency** - Automated Google Drive sync with intelligent processing
- **User Experience** - Natural language querying with relevant results

---

## 🚀 Weekend Breakthrough - Architecture Complete!

### **✅ COMPLETED - Net-New Architecture Scaffolding**

#### **5 Modular Workflows Deployed (Inactive):**
1. **RAG v1 - File Processor Engine** (id: 41PI1CGEdSlt84kW)
2. **RAG v1 - Auto-Sync Handler (Polling)** (id: WL9ROHxAiHN3dGWN)
3. **RAG v1 - Chat Upload Orchestrator** (id: JObJUeMlXEQqFtMq)
4. **RAG v1 - Document Query Engine** (id: 08Z6qBk97cFxdfJp)
5. **RAG v1 - Assistant Tool Bridge** (id: RzycXd98mKHKfwbR)

#### **Documentation & Specs:**
- **Readme and design docs**: `/Users/troy/iisi-n8n/rag-v1/`
- **Importable JSON drafts**: `/Users/troy/CascadeProjects/rag-v1/exports/`
- **Qdrant payload schema, indexing plan, and Data Store schemas**

#### **Key Technical Decisions Locked:**
- **Qdrant collection**: IISIAssistant (reuse existing)
- **Embeddings**: OpenAI text-embedding-3-large (3072 dimensions)
- **Sync**: Google Drive Changes API polling (no webhooks)
- **File types**: PDFs + Google Docs (no OCR)
- **Deletions**: Moving files out of selected folders removes from Qdrant
- **Multi-folder support**: Via selector in n8n
- **No Slack alerts**: Skip in v1

---

## 🔥 Remaining Work to Production

### **Phase 1: Populate Real Nodes (0.5-1.0 day)**

#### **File Processor Engine:**
- [ ] **Drive Integration**: files.get and files.export (Docs → text)
- [ ] **Change Detection**: PDFs via md5Checksum; Docs via modifiedTime + export_hash
- [ ] **Chunking**: 3072-dim embeddings processing
- [ ] **Qdrant Operations**: delete-by-filter then upsert (wait=true)
- [ ] **Sync State**: Update n8n Data Store

#### **Auto-Sync Handler (Polling):**
- [ ] **Changes API**: Per-folder polling with stored pageToken
- [ ] **Routing**: Upsert/delete (including "moved-out → delete") to File Processor
- [ ] **Throttling**: Gentle throttling (low concurrency)

#### **Chat Upload Orchestrator:**
- [ ] **Name Resolution**: Resolve names → IDs across selected folders (fuzzy match)
- [ ] **Batch Execution**: Progress summary and batch processing

#### **Document Query Engine:**
- [ ] **Fast-path Parser**: Dates, project tags, file type parsing
- [ ] **Qdrant Integration**: Filter-only listing and vector search aggregation to doc-level

#### **Assistant Tool Bridge:**
- [ ] **Separation**: Keep separate until main assistant integration decision

### **Phase 2: Data Stores & Configuration (0.5 day)**

#### **Create n8n Data Stores:**
- [ ] **doc_sync_state_v1**: Per file_id:folder_id change status
- [ ] **drive_changes_page_tokens_v1**: Per folder_id polling token

#### **Configure Initial Folders:**
- [ ] **Seeded Folder**: 1iOrsj8LqOba-CzgujR0zT1D7l9MQ9Nuf
- [ ] **Multi-select**: Option to add others later

#### **Tagging & Taxonomy:**
- [ ] **Project Tags**: Confirm/extend project-tags.json for better query filters

### **Phase 3: Observability & Safety (0.25 day)**

#### **Safety Checks:**
- [ ] **Status Logging**: Basic per-file status logging in Data Store
- [ ] **Credential Audit**: Ensure no hardcoded keys in legacy nodes
- [ ] **Validation**: Single test folder end-to-end testing

---

## 🎯 Acceptance Criteria (Client-Friendly)

### **Auto-Sync:**
- ✅ New/updated files in chosen Drive folders reflected in Qdrant within minutes
- ✅ Moved-out or deleted files removed from Qdrant
- ✅ Unchanged files skipped (no unnecessary reprocessing)

### **Chat Upload:**
- ✅ "Upload single/multiple/all" processes correct files with progress feedback
- ✅ Supports fuzzy name matching and respects change detection

### **Querying:**
- ✅ Natural phrases like "softr documents from last week" return relevant files
- ✅ Results include file name, date, project tags, and useful snippets

---

## 🚀 Go-Live Checklist

### **Pre-Production Validation:**
- [ ] **Credentials**: Confirm mapped in new workflows (OpenAI, Qdrant, Google Drive)
- [ ] **Data Stores**: Create and test single file end-to-end
- [ ] **Deletion Behavior**: Validate deletion-before-upsert behavior
- [ ] **Polling Test**: Verify pageToken updates and action routing
- [ ] **Query Testing**: Run representative queries (date range + project filter, content + filter combo)

### **Rollout Plan:**
- [ ] **Phase 1**: Activate Auto-Sync for first folder
- [ ] **Phase 2**: Add more folders after 24-48 hours of clean runs
- [ ] **Phase 3**: Wire assistant tools to production assistant (optional)

---

## 📊 Timeline & Effort

### **Estimated Completion:**
- **Populate nodes and Data Stores**: 0.5-1.0 day
- **Single-folder validation and fixes**: 0.5 day
- **Assistant tools wiring (optional)**: 0.25 day
- **Total**: 1-2 days to production (excluding client review cycles)

### **Immediate Next Steps:**
1. **Create Data Stores** in n8n
2. **Fill File Processor Engine** nodes and run single-file dry run
3. **Report back** with screenshots and end-to-end status log for sign-off

---

## 🔗 Related Areas

- [[👨‍👦 Doug Loud Support]] - Client relationship and project management
- [[🤖 AI & Automation Thinking MOC]] - AI strategy and implementation
- [[🔧 Platform & Tool Building MOC]] - Platform development
- [[🧠 AI Development Patterns]] - Technical AI knowledge

---

## 📅 Recent Updates (September 2025)

### **Weekend Breakthrough (Sep 14-15, 2025)**
- ✅ **Complete Architecture**: 5 modular workflows designed and deployed
- ✅ **Documentation**: Comprehensive specs and schemas created
- ✅ **Technical Decisions**: All key decisions locked for v1
- ✅ **Safe Deployment**: All workflows inactive - ready for review and iteration

### **Current Status:**
- **Architecture**: Complete and deployed
- **Next Phase**: Populate real nodes and create Data Stores
- **Timeline**: 1-2 days to production
- **Client Impact**: Will solve IISIAssistant 400 errors and provide scalable solution

---

## 💡 Key Insights

### **Technical Insights:**
- **Modular Design**: Scalable architecture for future growth
- **Change Detection**: Robust file change tracking with multiple strategies
- **Error Handling**: Comprehensive error handling and status logging
- **Performance**: Optimized for efficiency with intelligent throttling

### **Business Insights:**
- **Client Satisfaction**: Addresses Doug's immediate technical needs
- **Scalability**: Foundation for future AI assistant enhancements
- **Reliability**: Replaces problematic doc loader with robust solution
- **User Experience**: Natural language querying with relevant results

---

> [!tip] **Remember**: This RAG v1 system will solve Doug's IISIAssistant 400 errors and provide a scalable foundation for future AI enhancements! 💪

---

## 🎯 Next Actions

### **Today (Sep 15, 2025)**
- [ ] **Create Data Stores** in n8n
- [ ] **Populate File Processor Engine** nodes
- [ ] **Run single-file dry run** and report back

### **This Week**
- [ ] **Complete node population** for all 5 workflows
- [ ] **Validate single-folder** end-to-end functionality
- [ ] **Client review** and sign-off

### **Next Week**
- [ ] **Production rollout** with first folder
- [ ] **Monitor and optimize** performance
- [ ] **Add additional folders** after validation












