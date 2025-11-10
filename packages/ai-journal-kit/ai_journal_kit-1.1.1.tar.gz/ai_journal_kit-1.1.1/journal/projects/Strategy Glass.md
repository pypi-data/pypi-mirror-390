---
created: "2025-09-16"
lastUpdated: "2025-09-16T04:45:00-04:00"
contextDate: "2025-09-16"
status: "active-in-use"
priority: "high"
type: "calvinware-product"
---

# 🏢 Strategy Glass

**Type:** Calvinware Product - Active in Use  
**Status:** 🚀 **ACTIVE IN USE** - Multi-tenant SaaS platform actively used by marketing teams  
**Category:** Marketing Campaign Management & AI Content Generation  
**Target Market:** Agencies and in-house marketing teams managing multiple brands

## 📋 Project Overview

**Core Concept:** Multi-tenant SaaS for marketing teams to plan campaigns, generate AI-driven content, and publish to social channels.

**Value Proposition:** Deeply integrated with GoHighLevel (CRM/social posting), OpenAI (content generation), Google Drive (media), and Short.io (links).

## 🎯 Target Market

**Who It's For:**
- **Agencies and in-house marketing teams** managing multiple brands/organizations
- **Power users of GoHighLevel** who need streamlined content workflows and governance
- **Teams that want AI assistance** without sacrificing data security and org-level controls

## 🚀 Core Capabilities

### **1. Campaign and Content Management**
- **Organize campaigns** with topics/avatars/offers
- **AI-assisted content generation** and editing
- **Publishing to social platforms** via GoHighLevel

### **2. Key Integrations**
- **GoHighLevel OAuth** with single location per organization; sync accounts and posts
- **Google Drive media management** for assets
- **Short.io link library** and synchronization for UTM governance and analytics alignment

### **3. Collaboration & Governance**
- **Multi-tenant org model** with members and roles
- **Role-based permissions** (Super Admin, Organization Admin, Member)
- **User simulation** for admins to test experiences safely

### **4. Reliability & UX**
- **Optimistic updates**, cache management, and robust error handling
- **Clear separation** of UI (React) vs backend logic (Supabase Edge Functions)

## 🏗️ Technical Architecture

### **Frontend Stack**
- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **UI Library:** shadcn/ui
- **Routing:** React Router
- **State Management:** React Query
- **Forms:** React Hook Form + Zod

### **Backend Infrastructure**
- **Database:** Supabase (Postgres + Auth)
- **Security:** Row-Level Security (RLS)
- **Functions:** Edge Functions (Deno) for secure integrations and workflows
- **Data Access:** Organization-scoped routing (/org/:orgId/...) and RLS policies ensure strict tenant isolation

### **Integration Pattern**
- **Sensitive operations** and third-party APIs handled in Edge Functions
- **UI handles** presentation, caching, and user interactions

## 🔐 Security and Compliance

### **Authentication & Authorization**
- **Supabase Auth** with RLS on all tables by default
- **Security-definer functions** for membership and role checks:
  - `public.is_organization_member(user_uuid, org_id)`
  - `public.get_user_role_in_org(user_uuid, org_id)`
  - `public.is_org_admin_or_higher(user_uuid, org_id)`

### **Data Protection**
- **Secrets isolated** in Edge Functions and environment variables
- **OAuth flows** implemented with state validation
- **Strict tenant isolation** through RLS policies

## 🔗 Key Integrations

### **GoHighLevel**
- **OAuth2 flow** captures selected Location ID and persists credentials and location in Supabase
- **Edge functions** handle token exchange, syncing locations, posts, and social accounts

### **Google Drive**
- **OAuth callback** and file/folder operations for media pipelines

### **Short.io**
- **Two-table design** (links, shortio_links) with a sync function to reconcile all short links per domain

## 🎯 Key Differentiators

- **Multi-tenant by design** with strong org-level security and role governance
- **Opinionated, end-to-end content pipeline** integrated with GoHighLevel
- **AI-first content generation** tuned to campaigns, avatars, offers
- **Operational reliability patterns:** optimistic UI, cache strategy, and atomic backend workflows

## 📊 Current Maturity and Recent Improvements

### **GoHighLevel Connection Flows**
- **Hardened:** Fixed stale UI state, corrected mutation payloads, and resolved cache invalidation race conditions
- **Consolidated** to a single GHL location per org to simplify state and reduce bugs
- **Added missing RLS policies** and hooks (e.g., useGHLSocialAccounts) to stabilize data flows
- **Improved resilience** around UI modals and user simulation

## 📈 KPIs to Watch

- **Time-to-first-publish** and content throughput per organization
- **OAuth connection success rate** and re-auth stability (GHL, Google)
- **Content approval cycle time** and AI-assisted content adoption
- **Short link sync completeness** and click attribution coverage

## 🗺️ High-Level Roadmap

- **Broader publishing coverage** (additional platforms via GHL or direct APIs)
- **Content performance insights** and recommendations
- **Advanced governance** (workflows, approval gates, content versioning)
- **Templating and brand guidelines** embedded into AI prompts and validation

## 💰 Business Model

- **Multi-tenant SaaS** with organization-based pricing
- **Integration-focused** revenue model
- **AI-powered** content generation as core value proposition
- **Enterprise features** for large marketing teams

## 🔗 Related Projects

- [[🏢 Product Glass]] - Related Calvinware product
- [[🏢 Smash OS]] - Platform for "Smashing the Plateau"
- [[🏢 Beeminder Development]] - Current active project
- [[🏢 Daybreak AI Development]] - Current active project

## 📝 Notes

**This platform represents a production-ready, multi-tenant SaaS solution that's actively being used by marketing teams. It showcases enterprise-grade architecture, AI integration, and real-world business value.**

**Perfect for LinkedIn content showcasing:**
- **Production SaaS** with real users
- **Multi-tenant architecture** with enterprise security
- **AI integration** in real business workflows
- **Complex integrations** (GoHighLevel, Google Drive, Short.io)
- **Modern tech stack** (React, Supabase, Edge Functions)
- **Business impact** - actual marketing teams using it

**This is GOLD for demonstrating real-world success beyond just technical capability!**











