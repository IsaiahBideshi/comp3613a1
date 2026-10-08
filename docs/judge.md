# student-judge competency report

**Judged at:** 2026-10-08T20:05Z
**Evidence pass:** re-read all five Guide chats for this project, the current `docs/report.md`, `docs/diagrams/` and `docs/wireframes/` (prior judge.md ignored). Since the last export only the YouTube URL was added to the report, and no app file changed, so every metric scored the same on this pass.

**Student / session:** MyAdvisor (COMP 3613 Assignment 1), five Guide chats between 1 and 7 October 2026
**Artifact:** the five Guide chats for this project, read from the saved chats and written out as `docs/transcripts/*.md`
**Phases in evidence:** 1–6 (COMP 3613; Phase 5 polish, Phase 6 deploy)

### Totals

| | Count / value |
|--|--|
| Metrics on rubric | 12 (M1–M12) |
| N/A (excluded) | 0 |
| Metrics scored | 12 |
| Scoreable max | 48 |
| Awarded total | 46 / 48 |
| **Overall (avg of scored)** | **3.8 / 4** |
| Impression mark | 19 / 20 (last logged Guide confidence 0.96) |

## Scorecard

| ID | Metric | Score / 4 | In avg | Evidence |
|----|--------|----------:|:------:|----------|
| M1 | Phase discipline | 4 | yes | One chat per design phase, then one chat for Phases 5 and 6. No app code before the wireframes. The student held the gate themselves: "Option A but don't move on yet." and, only after polish, "Everything works locally, move on to Phase 6 deploy". |
| M2 | Problem framing | 4 | yes | Four `Feature (user)` lines in Phase 1, then reasons with each answer: "Plan courses <<include>> Track degree progress. When a user starts planning their courses for the semester they must always see their remaining courses so they can choose from it". Phase 3 opened with a full entity list, keys included, plus unprompted notes on why there is no Advisor table. |
| M3 | Decision ownership | 4 | yes | Reversed their own design when a case did not fit: "Remove the \"denied\" status. After an advisor denies a submission it goes back to \"draft\"." Added conditions of their own to choices: "Option A, but use only constant variables set in the academic.py file that is exported to other files that use them to avoid typos." Originated Check plan status and Remove Submission. |
| M4 | Artefact-before-code | 3 | yes | The wireframes and ERD were the spec for every workflow, and the student caught a mismatch against one: "the sidebar button \"Student Plans\" is still active, it should be disabled when on the review page". Several screens later moved away from the wireframes by the student's choice (closed dropdowns, year groups, required list), each recorded in the report rather than redrawn. Solid, not exceptional. |
| M5 | Verification habit | 4 | yes | Ran and reported after builds, and tested beyond what was asked: "I also tested the current_term env var, by changing it to 2027-S2 and it correctly shows semester 2 courses." Also "I tested everything as an advisor. Search works, approve works, deny works, see previous comment works." and a full-flow test before deploy and on the live site. Two early replies gave no "what I saw" when asked. |
| M6 | Assignment fit | 4 | yes | Every student route snippet is thin and calls a service, for example `plan = plan_service.add_course(user.id, course_code)`. All 17 `student-build:code-check` blocks in the report read `architecture_ok: yes` and `passed: yes`. Starter login and sessions reused; theme, build and polish came before deploy. |
| M7 | Slice explanation | 4 | yes | Own-words reasoning on their design: "It shows under year 1 sem 1 because the progress shows courses as a checklist rather than their history of courses." Eleven file snippets across five workflows passed on the first attempt, including a service method (`if (plan.status == STATUS_DRAFT and plan.comment): return STATUS_DENIED`) and a layer question answered correctly ("Option B", the service). |
| M8 | Prompt quality | 3 | yes | Phase-tagged prompts and concrete notes, at best with an example: "if the `current_term` env var is set to \"2026-S1\", then the required/remaining courses section should show Year 2 semester 1 courses and Year 3 depending on what courses are passed". A few requests were ambiguous and took extra turns: "It should be sorted by the current semester instead", and the glow request that named the wrong panel. |
| M9 | Response to pushback | 4 | yes | Kept refining instead of accepting a first build: "No the wrong text glows, the glow should be on the courses in the required courses section." and "Only show the current semester's courses, drop the second box". In Phase 3 they reworked the status and comment rules across three Guide challenges. |
| M10 | Integrity | 4 | yes | No answer-seeking and no paste-back flags in any chat. `python manage.py skills-verify` reports "Skill integrity: pass". The one pasted block (Phase 3) was the student's own Plan entity from the previous message with one field added. |
| M11 | Provenance continuity | 4 | yes | Ideas can be traced through the chats: Phase 2 "After a plan is denied, it goes back to being a plan rather than a submission", Phase 3 "A just denied plan would have an attached comment", the note on `student-plan.png`, and finally the student's own `_shown_status` in Phase 5. |
| M12 | Sincerity trajectory | 4 | yes | Suspicion was never raised. No `student-judge:sincerity` blocks exist in any chat. |

## Strengths

- Design answers come with reasons, not just picks, in Phases 2 to 4.
- Changed their own model when a concrete case broke it (the `denied` status, the unique constraint in place of an app rule).
- All snippets respect the layers: thin routes, rules in services, no queries in routers. They added route-level error handling without being asked.
- Sustained polish: about fifteen distinct refinements after the first builds, including a bug report that led to a real fix (stale stylesheet) and a data rule the Guide's seed broke.
- Tested configuration, not only the happy path (`CURRENT_TERM` at a Semester 2 value).
- Acted on review notes: a comment that mis-stated their own "denied" rule was corrected by the next turn.
- Deployed only after local polish, entered the production secrets themselves, and tested the live site.

## Gaps (priority order)

1. **Ambiguous change requests.** A few polish requests did not say which element or which rule, and cost extra turns: the required-courses list took three passes, and the glow went on the wrong panel first because the request named the planned section.
2. **One Guide question left unanswered at first.** What Submit should do with an empty plan was asked alongside a snippet hand-off and skipped; the student decided it one turn later when it was raised again.
3. **Thin "what I saw" notes early in Phase 5.** After the first two workflows the replies moved straight to the next request. Later workflows had clear verify notes.

## Phase gate status

| Phase | Status | Note |
|-------|--------|------|
| 1 | met | Project chosen and four `Feature (user)` workflows named by the student. |
| 2 | met | Include, extend and shared use cases decided with reasons; fifth use case added for the denial case; UML PNG embedded. Updated in Phase 5 with Remove submission. |
| 3 | met | Student-named entities and properties; relationships and status rules reworked under questioning. |
| 4 | met | Four annotated wireframes cover the five use cases; workflow clarifications and three model edits accepted. |
| 5 | met | Themed, five workflows built one at a time with student snippets, then extended polish with verify notes and model revisions. |
| 6 | met | Live at https://myadvisor-dn2r.onrender.com with marker logins in the report; the student tested the live site. |

## Recommended next practice

- For each UI change request, write one sentence naming the screen and element, one naming the rule, and one example of the expected result, as in the year-group request. Try it on the next three changes and count how many land first time.

## Integrity note

- Clean

## Provenance flags

- None

## Sincerity log summary

- Blocks found: 0 | max round: 0 | min/mean/final confidence: n/a | trend: n/a | cleared: not needed

## Skips

- Skips: 0/3 used. Skips are not an integrity failure.
