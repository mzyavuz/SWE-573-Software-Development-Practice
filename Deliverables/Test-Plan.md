# Test Plan
## The Hive - Community TimeBank Platform

**Date:** December 18, 2025  
**Author:** M. Zeynep Çakmakcı  
**Project:** SWE 573 - Software Development Practice

---

## 1. Introduction

### 1.1 Purpose
This document describes the test plan for The Hive, a community-based TimeBank platform that facilitates skill and service exchanges using time credits as currency. The purpose of this test plan is to define the testing approach, scope, resources, schedule, and deliverables required to ensure that all functional and non-functional requirements are validated before the final release.

### 1.2 Project Background
The Hive is a web-based application developed as part of the SWE 573 Software Development Practice course. The platform enables users to:
- Exchange services using time-based currency
- Create and manage service Offers and Needs
- Discover services through an interactive map
- Communicate via private messaging
- Participate in community forums
- Propose and accept service schedules with balance validation

### 1.3 Document Scope
This test plan covers all testing activities for The Hive application version 1.0, including functional testing, integration testing, usability testing, and performance testing.

### 1.4 References
- Software Requirements Specification (SRS) v3.0
- Installation Guide (INSTALL.md)
- API Documentation
- Database Models (models.py)

---

## 2. Test Objectives

### 2.1 Primary Objectives
- Verify all functional requirements specified in the SRS are correctly implemented
- Ensure the application meets non-functional requirements (performance, security, usability)
- Validate the TimeBank currency system and balance management
- Confirm schedule proposal and acceptance workflow functions correctly
- Verify data integrity across all database operations
- Ensure proper error handling and user feedback

---

## 3. Scope

### 3.1 In Scope

#### 3.1.1 Functional Features
- **User Management** (FR-1.x)
  - User registration with age verification
  - Email verification
  - User authentication (login/logout)
  - Profile management
  - Password reset

- **Service Management** (FR-3.x, FR-4.x)
  - Create/Edit/Delete Offers
  - Create/Edit/Delete Needs
  - Service tagging and categorization
  - Service status management

- **Service Discovery** (FR-5.x)
  - Map-based service display
  - Service filtering (tags, distance, hours)
  - Search functionality
  - List and map views

- **Application Workflow** (FR-6.x, FR-7.x)
  - Provider application to Needs
  - Consumer selection of Provider
  - Application status management

- **Schedule Management** (FR-11.x)
  - Schedule proposal creation
  - Balance validation on acceptance
  - Schedule acceptance workflow
  - Schedule modification

- **TimeBank System** (FR-8.x)
  - Initial credit allocation
  - Balance tracking
  - Balance validation
  - Hour transfer on completion
  - Maximum balance enforcement

- **Communication** (FR-10.x)
  - Private messaging
  - Message notifications
  - Proposal messages

- **Rating and Evaluation** (FR-9.x)
  - Mutual rating system
  - Review submission
  - Survey completion

- **Forum System** (FR-13.x)
  - Category browsing
  - Thread creation and viewing
  - Comment posting
  - Forum moderation

- **Administration** (FR-12.x)
  - User management
  - Service moderation
  - Report handling
  - Tag management

#### 3.1.2 Non-Functional Requirements
- Performance testing
- Security testing
- Usability testing
- Browser compatibility testing
- Responsive design testing
---

## 4. Test Strategy

### 4.1 Test Levels

#### 4.1.1 Unit Testing
- **Scope**: Individual functions and methods
- **Tools**: Manual testing, Python unittest framework (where applicable)
- **Coverage**: Critical business logic, validation functions, data models
- **Responsibility**: Developer

#### 4.1.2 Integration Testing
- **Scope**: Interaction between components (backend-database, frontend-backend)
- **Approach**: Test API endpoints with various inputs
- **Focus Areas**:
  - Database CRUD operations
  - Authentication flow
  - Service creation and management
  - TimeBank transactions
  - Message delivery

#### 4.1.3 System Testing
- **Scope**: Complete end-to-end workflows
- **Approach**: Execute user scenarios from Demo Scenario document
- **Focus Areas**:
  - Complete service exchange workflow
  - Schedule proposal and acceptance
  - User registration to service completion
  - Admin moderation workflows

#### 4.1.4 User Acceptance Testing (UAT)
- **Scope**: Real user scenarios
- **Participants**: Academic instructor, peer reviewers, potential users
- **Approach**: Guided walkthrough of main user stories
- **Success Criteria**: Users can complete tasks without confusion or errors


**End of Test Plan**
