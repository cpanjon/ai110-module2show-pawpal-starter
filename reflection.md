# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.

- Thr initial UML Design has classes for Task, owner, Pet, Scheduler, and Owner

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

- Considers available daily time, task priority, task duration, completion, and scheduled time


- How did you decide which constraints mattered most?

- The priority mattered the most because the goal is to complete the prioritized task without exceeding time available

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

- Conflict detection warns but does not remove overlapping tasks from the plan

- Why is that tradeoff reasonable for this scenario?

- Correctness of the schedule is prioritized over schedule validity (no overlaps).

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

- I did most of the brainstorming i just used it to help me implement the best possible code


- What kinds of prompts or questions were most helpful?

- Asking how to simplify logic to help me understand it before implmenting it

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

- The Backend logic because its what makes the app function

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?


- I would make the app UI look better

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?


- Using AI as a tool to help me build a app quickly and accurate based on my brainstorming