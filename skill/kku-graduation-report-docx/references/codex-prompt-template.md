# Codex prompt template

Use this prompt when the user wants Codex to execute the full workflow.

```text
You are working inside a university graduation project repository.

Your task is to generate a complete project report that strictly follows the professor's provided report sample format while improving quality, clarity, consistency, and completeness.

Inputs:
- GitHub repository: [INSERT REPOSITORY URL OR CONNECTED REPO]
- Any uploaded sample report/template `.docx`
- Any existing docs inside the repo

Core constraints:
- Build the report from the actual repository contents and uploaded sample files.
- Do not invent features that are not implemented.
- If the user supplied a professor sample, preserve its chapter order and section names.
- Produce a real editable local `.docx`, not a PDF conversion.

Required workflow:
1. Audit the repository and summarize:
   - project purpose
   - stack
   - folders/modules
   - routes/pages
   - models/entities
   - APIs
   - tests
   - run instructions
   - existing documentation
2. Classify docs as reusable, partially accurate, outdated, or missing.
3. Build a report outline aligned to the professor sample.
4. Write the report from code evidence.
5. Recreate UML and technical diagrams in one consistent style.
6. Run the project locally and capture real screenshots when possible.
7. Assemble a fully editable `.docx` with proper Word heading styles, figure captions, and table of contents.
8. Update repo docs if requested.
9. Produce a final completeness checklist.

If the sample is the King Khalid University applied project sample, use this required structure:

CHAPTER 1: INTRODUCTION
1.1 Introduction
1.2 Previous Work
1.3 Problem Statement
1.4 Scope
1.5 Objectives
1.6 Advantages
1.7 Disadvantages
1.8 Software Requirements
1.9 Hardware Requirements
1.10 Software Methodology
1.11 Project Plan

CHAPTER 2: LITERATURE REVIEW
2.1 Introduction
2.2 Related Work
2.2.1 Similar Apps and Websites

CHAPTER 3: SYSTEM ANALYSIS
3.1 Introduction
3.2 Data Collection
3.3 REQUIREMENTS ELICITATION
3.3.1 Functional Requirements
3.3.2 Non-Functional Requirements
3.4 REQUIREMENTS SPECIFICATION

CHAPTER 4: SYSTEM DESIGN
4.1 Introduction
4.2 Structural Static Models
4.2.1 Class Diagram
4.3 Dynamic Models
4.3.1 Sequence Diagrams
4.3.2 Activity Diagrams

CHAPTER 5: DATABASES
5.1 Data Modeling
5.2 Database Entities and Attributes
5.3 Database Relationships Description
5.4 Interfaces

CHAPTER 6: DATABASE DESIGN
6.1 Database Design

CHAPTER 7: USER INTERFACE

APPENDIX: CODE SNIPPETS

Diagram rules:
- use one diagramming approach consistently
- same font, spacing, alignment, and arrow logic across every diagram
- use real actors, entities, and workflows from code
- export editable sources plus report-ready images

Screenshot rules:
- use the real running app
- consistent browser size and zoom
- consistent cropping and captions
- include major user and admin pages when they exist

DOCX rules:
- editable `.docx`
- Word heading styles
- automatic table of contents
- consistent figure/table captions
- page numbering
- clean academic formatting
- prefer A4 and Times New Roman 12pt unless the sample or user says otherwise

Deliverables:
- submission/Project_Report.docx
- docs/00_project_audit.md
- docs/01_missing_documentation_gaps.md
- docs/REPORT_OUTLINE.md
- docs/UML_GUIDE.md
- docs/SCREENSHOT_GUIDE.md
- docs/DOCX_BUILD_GUIDE.md
- docs/PROJECT_SUBMISSION_CHECKLIST.md
- diagrams and screenshots folders

Goal:
Produce a submission-ready graduation project report that matches the professor's structure, is technically accurate, visually consistent, and fully editable.
```
