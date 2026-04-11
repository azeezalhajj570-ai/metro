---
name: kku-graduation-report-docx
description: generate a full university graduation project report from a github repository and local files, producing a fully editable local .docx that follows the king khalid university applied project sample structure. use when a user wants chatgpt/codex to audit a graduation-project codebase, align the report to a professor-provided sample, create consistent uml diagrams, update repo documentation, and assemble a submission-ready microsoft word document.
---

Build the report from the actual repository contents and any provided sample report or template. Never invent unimplemented features.

Use this workflow:

1. Identify the inputs
   - GitHub repository URL or connected repository
   - Any uploaded sample `.docx` report, university template, or existing report draft
   - Any extra requirements from the user such as APA preferences, UML expectations, screenshots, or chapter names

2. Audit the repository first
   - Inspect project purpose, architecture, stack, folders, routes/pages, models, APIs, tests, run instructions, and existing docs
   - Produce a concise evidence-based inventory before drafting the report
   - Classify existing docs as reusable, partially accurate, outdated, or missing

3. Lock the report structure to the professor sample
   - If the user supplied a sample report, mirror its chapter order and section names
   - Preserve required academic structure even if it is imperfect
   - Improve quality without changing required chapter numbering or headings
   - For the King Khalid University applied project sample, default to:
     - Chapter 1 Introduction
     - Chapter 2 Literature Review
     - Chapter 3 System Analysis
     - Chapter 4 System Design
     - Chapter 5 Databases
     - Chapter 6 Database Design
     - Chapter 7 User Interface
     - Appendix: Code snippets

4. Write from code evidence
   - Map code modules and implemented features into the required chapters
   - Use formal academic English with one consistent voice
   - Keep terminology stable across entities, actors, modules, pages, and features
   - When something is missing, describe it as a limitation or future enhancement instead of fabricating it

5. Standardize diagrams
   - Recreate diagrams in one consistent style, not mixed screenshots from different tools
   - Preferred set:
     - use case diagram
     - class diagram
     - sequence diagrams for key workflows
     - activity diagrams for key workflows
     - architecture diagram if supported by the code
   - Apply one visual standard across all diagrams:
     - same font family
     - same spacing and alignment
     - same arrow styles per relationship type
     - same naming conventions
     - balanced layout on white background
   - Save editable source files when possible, plus exported images for insertion into the report

6. Capture real interface screenshots when the environment supports it
   - Run the project locally
   - Use browser automation or a playground/browser tool when available
   - Capture actual pages, not mockups
   - Keep browser size, zoom, cropping, and captions consistent
   - Typical targets:
     - home
     - login
     - register
     - dashboard/user pages
     - major feature pages
     - admin pages when implemented

7. Create the `.docx`
   - Produce a real editable Microsoft Word `.docx`, not a PDF conversion
   - Use Word styles for headings and captions so the table of contents works
   - Use consistent page numbering and figure/table captions
   - Keep figure captions as text, not baked into images
   - Prefer A4, Times New Roman 12 pt, consistent spacing, and a clean academic layout unless the user specifies otherwise
   - When the sample dictates a different style, follow the sample first

8. Update repository docs too
   - Improve or create README and supporting docs if the user asked for repo documentation updates
   - Add guides for UML, screenshots, and report generation when useful

9. Final deliverables
   - local editable `.docx`
   - exported diagrams
   - screenshot set if captured
   - updated repo docs if requested
   - a short completeness checklist

Quality rules:
- Do not claim a feature exists unless visible in the code or user-provided materials.
- Keep chapter content aligned with actual implementation evidence.
- Remove repetition and filler.
- Explain each figure and table near where it appears.
- Make all diagrams look like they were prepared by the same person.
- Treat the professor sample as the controlling structure whenever provided.

Recommended output structure for the generated work:
- submission/Project_Report.docx
- docs/00_project_audit.md
- docs/01_missing_documentation_gaps.md
- docs/REPORT_OUTLINE.md
- docs/UML_GUIDE.md
- docs/SCREENSHOT_GUIDE.md
- docs/DOCX_BUILD_GUIDE.md
- docs/PROJECT_SUBMISSION_CHECKLIST.md

Use the reference files in `references/` for the concrete prompt template and KKU chapter mapping when the user wants a Codex-ready execution prompt or a strict outline.
