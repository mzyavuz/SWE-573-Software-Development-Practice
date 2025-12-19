# Lessons Learned Report

**Project:** Hive - Community TimeBank Platform  
**Author:** M.Zeynep Çakmakcı  
**Course:** SWE 573 - Software Development Practice  
**Date:** December 19, 2025  
**Academic Institution:** Boğaziçi University

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Project Overview](#project-overview)
3. [What Went Well](#what-went-well)
4. [What Did Not Go So Well](#what-did-not-go-so-well)
5. [What Could Have Been Avoided](#what-could-have-been-avoided)
6. [How Could We Do Things Better Next Time](#how-could-we-do-things-better-next-time)
7. [Conclusion](#conclusion)

---

## Executive Summary

This report looks back at my experience developing the Hive project, a community TimeBank platform where people exchange services using time credits. I'll discuss what went well, what didn't go so well, what I could have prevented, and what I'll do differently next time. This reflection covers my personal experience, technology challenges, tools I used, customer interactions, and the TimeBank application itself.

**Main Takeaways:**
- Spending time on detailed requirements at the beginning saved me a lot of problems later
- Using AI tools like GitHub Copilot helped me work faster while keeping quality high
- Trying to restructure my code in the middle of the project was risky and caused delays
- Keeping my development and production environments the same is super important
- Being flexible and changing plans when needed (like switching from "Reserved Hours" to "Proposed Schedule") helped me succeed

---

## Project Overview

**The Hive Platform** is a web application where community members can exchange services using time credits instead of money. The main features include:

- User login and profiles
- Creating and managing service offers and needs
- Finding services on an interactive map
- TimeBank system that tracks time credits and balances
- Scheduling system for coordinating services
- Private messaging between users
- Community forum called "The Commons"
- Admin dashboard for managing the platform

**Technologies I Used:**
- **Backend:** Python with Flask framework
- **Frontend:** HTML/CSS, JavaScript, Bootstrap for styling
- **Database:** PostgreSQL
- **Deployment:** Docker containers, DigitalOcean cloud platform
- **Development Tools:** VS Code editor, GitHub for version control, DBeaver for database management, GitHub Copilot AI assistant

---

## What Went Well

### 1. Good Decisions About the Project Structure

#### Writing Detailed Requirements First
I spent a lot of time at the beginning writing a detailed Software Requirements Specification (SRS) document. This was one of the best decisions I made. Having everything written down before I started coding made development much faster and easier.

**Why This Helped:**
- I made fewer mistakes because I knew exactly what to build
- I managed my time better even though the project was big
- I had clear goals for when each feature was "done"
- It gave me a solid plan to follow

#### Thinking Through the Complete Service Process
I carefully mapped out every step of how services work in the system - from creating them, to matching users, to completing them. I thought about the possible edge cases and errors from the very beginning, not as an afterthought.

**What I Achieved:**
- Created a clear map of all possible service states
- Handled errors properly throughout the system
- Thought about edge cases during design, not after finding bugs
- Added validation checks at every important step

#### Changing from "Reserved Hours" to "Proposed Schedule"
Halfway through development, I realized my original "Reserved Hours" idea had problems. Two users could try to reserve hours at the same time and cause conflicts. So I changed the design to use a "Proposed Schedule" system instead where users suggest times and the other person confirms.

**Why This Change Helped:**
- Made the system simpler
- Fixed potential data problems
- Worked better when multiple people were using the system
- Eliminated the timing conflict bugs
- Made it clearer for users how scheduling works

### 2. Using AI Tools to Help Development

#### GitHub Copilot Helped Me Learn and Work Faster
Using GitHub Copilot was really helpful for both writing code and documentation. It didn't just make me faster - it actually taught me a lot about how web applications are usually structured.

**How Copilot Helped:**
- Generated repetitive code quickly (like routes, database models, and forms)
- Suggested good ways to write code that follow best practices
- Kept my documentation more consistent
- Helped me think of edge cases by generating tests

#### I Always Checked AI-Generated Code Carefully
Even though AI helped write code, I never just accepted what it gave me. I always reviewed everything carefully, tested it, and made sure it fit my project. This way, I stayed in control of the code quality.

**My Review Process:**
- Read every line of code the AI suggested before using it
- Tested everything thoroughly (both individual parts and the whole system)
- Used code quality tools (pylint and flake8) to check for problems
- Made sure it matched what my requirements document said

### 3. Good Tool Choices

#### VS Code Made Development Easy
I used VS Code as my code editor, which I was already familiar with. This made starting the project much smoother. VS Code has tons of helpful extensions that made working with different programming languages easier.

**Why VS Code Helped:**
- One place to write Python, HTML, CSS, and JavaScript
- Built-in terminal to run Git and Docker commands
- Extensions that check my code for errors and format it nicely
- Easy to edit multiple files and search through code

#### DBeaver Helped Me See What's in the Database
I used PostgreSQL as my database and DBeaver as a tool to look at and manage the data. DBeaver was really useful because I could see exactly what was in my database, both on my computer and on the production server.

**What DBeaver Let Me Do:**
- See my local database and production database (on DigitalOcean) in one tool
- Visualize the data to understand what was happening
- Check that my database structure was correct
- Write and test complex database queries

#### Docker and DigitalOcean Made Deployment Easier
I used Docker to package my application and DigitalOcean to host it online. Docker containers made sure my app would run the same way on any computer.

**Benefits:**
- Fixed the "it works on my computer but not yours" problem
- Made it easy to update my application quickly
- Kept my development and production environments the same
- Made managing dependencies (required libraries) simpler

### 4. Important Lessons I Learned

#### My Database Crashed During a Presentation
During the presentation to my class/instuctor (First Customer Presentation), my app crashed because my local database and production database were different - a column was missing in production. This taught me that keeping all environments synchronized is super important.

**What I Learned:**
- Database changes need to be exactly the same everywhere (local computer, production server)
- Updating databases manually is risky and leads to mistakes
- I should use automated tools to update databases

#### New Rules for Before Presentations
After that embarrassing crash, I created a safety protocol for future demos:

1. **Stop Making Changes:** No new code 48 hours before a presentation
2. **Test Everything:** Do thorough tests on the production server to make sure everything matches
3. **Have a Backup Plan:** Always keep a working version I can quickly switch back to if something breaks

#### Using GitHub Issues to Stay Organized
I used GitHub Issues to manage my tasks. This helped me break down big requirements into smaller, doable tasks.

**What This Gave Me:**
- **Clear To-Do List:** I could see all my pending work, bugs, and improvements in one place
- **Smart Prioritization:** I could rank tasks by importance and tackle the most critical ones first
- **Progress Tracking:** I could look back and see what I accomplished, which helped me estimate future work

#### Staying Flexible
My organized task list helped me work in an Agile way. When I needed to change from "Reserved Hours" to "Proposed Schedule," I just updated my task list and reprioritized. I stayed flexible without losing track of my main goals.

---

## What Did Not Go So Well

### My Biggest Challenges

### Top 3 Problems I Faced

#### 1. Too Many Features at Once
My project was really big. It included a Forum, Admin Dashboard, Map view with location services, scheduling system, and messaging. While I learned a lot, trying to handle all these different features at the same time was mentally exhausting.

**Problems This Caused:**
- I had to balance building complex features while also learning Docker and cloud deployment
- Created slowdowns because I couldn't focus on one thing
- I kept switching between very different technical areas (maps, databases, messaging)
- Increased the chance that different parts wouldn't work well together

**Why This Happened:**
- I was ambitious and didn't leave enough time for learning new technologies
- I tried to build too many advanced features at the same time
- I underestimated how hard it would be to connect all the pieces

#### 2. My Failed Code Reorganization Attempt
The biggest technical failure happened when I tried to reorganize my code to make it easier to test. I had all my code in one big file (`app.py`) and wanted to split it into organized folders. I followed AI suggestions, but it created a huge mess with errors everywhere.

**What Happened:**
- I tried to restructure my code in the middle of the project
- I trusted AI (restructure) suggestions without testing them properly first
- Got circular import errors (files trying to import each other)
- Wasted an entire day trying to fix the problems

**What I Did:**
After wasting a full day, I made the tough decision to **go back to the old code**. I needed to meet my deadline, and the old version worked.

**How I Recovered:**
Instead of the unit tests that needed the new structure, I changed my testing strategy. I wrote scenario-based tests that tested the whole API, which worked fine with my original code structure.

**What I Learned:**
- Changing your code structure is really risky once you have a lot of code
- Reorganizing mid-project needs a careful plan
- Sometimes "good enough and working" is better than "perfect but broken"

#### 3. Not Enough Time and Too Much Learning
Even though I managed my time well, learning new technologies took way longer than I expected. I had a strict schedule because of school and family, so I had no extra time when things took longer than planned.

**What This Meant:**
- I had to cut some features I originally wanted to build
- No extra time when unexpected problems came up
- Constantly choosing between finishing features or meeting deadlines
- No time to just explore and experiment with new ideas

**Why I Struggled:**
- Building both frontend and backend required knowing lots of different technologies
- Had to learn Docker, DigitalOcean, Flask, and PostgreSQL all at once
- Couldn't be flexible with my schedule due to school and family responsibilities
- Working alone meant I had to do everything myself

### What Frustrated Me Most

#### The Code Reorganization Wasted a Whole Day
Trying to reorganize my code was my biggest frustration. It's like when you start one task and it leads to another and another, and suddenly you've spent all day on something that doesn't work.

**Why It Was Frustrating:**
- Felt like I accomplished nothing after a full day of work
- It hurt to delete all the code changes I made
- Felt torn between writing "clean code" and just getting it done
- Felt like I was moving backwards even though reverting was the right choice

**The Good Side:**
Even though going back to my old code structure felt like failure, it was actually the right decision. I needed a working product by the deadline, and that's what mattered most.

### Looking at My Experience

#### Personal: Learning Slowed Me Down
My workload was heavy because I had to learn frontend, backend, database, and deployment all at once. Every new tool took time to learn before I could actually use it. Even though I worked consistently every day, I was slower than I expected because I was constantly learning.

**What Slowed Me Down:**
- Time spent learning wasn't time spent building
- Reading documentation and tutorials took many hours
- Trial and error with new tools was slow
- Switching between learning mode and building mode broke my concentration
- Creating wiki pages to document what I learned took additional time

**Why It Was Worth It:**
Even though writing wiki pages slowed me down initially, it made my learning permanent. When I needed to remember something later, I had my own documentation to refer back to instead of searching through tutorials again.

#### Technology: My Code Structure Was the Problem
The real issue wasn't the tools I chose, but how I organized my code. Having everything in one big file (`app.py`) was easy to start with but became hard to test as it grew. Trying to fix this halfway through was a mistake.

**Problems with My Code Structure:**
- Everything in one file made testing hard
- Everything was connected, so I couldn't test parts separately
- Hard to find things in one huge file
- Couldn't test individual pieces on their own

#### Main Lesson: Working Code Beats Perfect Code
Choosing to keep my old structure and write different tests let me finish on time, even though the code wasn't as organized as I wanted. Sometimes you have to accept "good enough" to meet a deadline.

**My Decision:**
- Made sure the app worked, even if the code wasn't perfect inside
- Knowingly accepted code that could be better organized ("technical debt")
- Focused on features users could see rather than perfect code organization
- Delivered something valuable to my stakeholders on time

---

## What Could Have Been Avoided

### Looking Back: What I Could Have Prevented

#### But Some Lessons Come From Experience
Yes, I could have avoided some problems with better planning. But honestly, the failures I experienced—especially the deployment crash and the code reorganization disaster—taught me lessons I couldn't have learned from reading. These experiences gave me a "safety-first" mindset that I'll never forget.

**Why Failure Teaches:**
- Some lessons you only learn by making mistakes
- Failing teaches you more deeply than just reading about it
- Painful experiences change your behavior permanently
- Experience builds intuition you can't get from books

### Things That Saved Me (and Would Help Next Time)

#### 1. Detailed Requirements Saved Me From Many Problems
Spending lots of time writing a detailed Software Requirements Specification (SRS) at the start was my best decision. Because I had everything clearly written down, I avoided most logic errors and kept my time management under control even though the project was huge.

**Why This Worked:**
This early work on requirements paid off throughout the entire project and prevented many problems that could have killed the project.

#### 2. Changing My Testing Approach
When I couldn't write unit tests for my big single-file structure, I switched to scenario-based testing instead (testing the whole API from start to finish).

**My Strategy:**
For future projects, I'll start with scenario-based tests that test the whole system before trying to write small unit tests. This way, I know the main functionality works even if I change how the code is organized internally.

**Why This Is Better:**
- Tests don't break when I reorganize code
- Tests focus on what users experience, not internal code details
- Easier to write for simple code structures
- Gives me confidence the system works

#### 3. New Rules After the Deployment Disaster
The deployment crash (database error) during my presentation taught me to always keep development and production environments exactly the same. Now I have rules to prevent this:

**My New Rules:**
1. **No Changes Before Demos:** No new code for 48 hours before important presentations
2. **Test Production Early:** Make sure production environment matches my local computer well before the presentation
3. **Automated Safety Checks:** Write scripts that automatically check if environments match

### If I Could Start Over

If I could start "The Hive" again from Day 1 with everything I know now, here's what I'd do differently:

#### Start With Organized Code From Day 1
Instead of putting everything in one `app.py` file, I'd organize my code into folders from the beginning. This would have prevented the reorganization disaster halfway through.

**Better File Organization:**
```
app/
├── __init__.py
├── models/         (database stuff)
├── routes/         (URL endpoints)
├── services/       (business logic)
├── forms/          (user input forms)
└── utils/          (helper functions)
```

**Why This Helps:**
- Code is organized from the start
- Easier to write tests
- Easier to maintain as it grows
- Each part has a clear purpose

#### Use a Database Migration Tool
I should have used a tool to automatically update my database. This would have prevented the database mismatch that crashed my presentation.

**What Migration Tools Do:**
- Keep track of all database changes like Git does for code
- Automatically update the production database
- Let you undo database changes if something breaks
- Document how your database evolved over time

#### Schedule Learning Time Separately
To handle the learning curve better, I should have scheduled dedicated "learning sprints" - short, focused time periods just for learning new tools before using them in my project.

**Learning Sprint Structure:**
- Set a time limit (like 2-4 hours)
- Focus on one technology at a time
- Goal: Figure out if it works, not build the real thing
- Write notes about what I learned and decided

---

## How I'll Do Things Better Next Time

### My Plan for Future Projects

#### 1. Write Tests While Writing Requirements
For my next project, I'll write test scenarios at the same time I write requirements, not after. This way, I'm thinking about testing from the very beginning.

**How I'll Do This:**
- For each requirement, write down exactly how I'll know it's done
- Write test scenarios before I start coding
- Think about "Can I test this?" when designing each feature
- Make sure every step of the service process has a test

**Why This Helps:**
- Makes sure I design code that can be tested
- Prevents creating code that's impossible to test
- Gives me a clear definition of "done"
- My tests become documentation of how the system should work

**Example:**
```
1. Write Requirement: "User can propose a schedule"
2. Define When It's Done: "User with enough credits can propose a time, and it gets saved"
3. Write Test: "POST /schedule/propose with valid data should return success"
4. Build the Feature: Write code that makes the test pass
5. Verify: Run the test to make sure it works
```

#### 2. Examine Technologies Before Starting Next Project
Now that I've already used Docker, cloud deployment, and testing in this project, I have a good foundation. For my next project, I'll take time to deeply examine these technologies before I start coding, reflecting on what worked and what didn't.

**What I'll Examine:**
1. **Docker & Kubernetes:** Review my container setup and explore scaling techniques
2. **CI/CD Pipelines:** Study automated testing and deployment patterns with tools like GitHub Actions
3. **Test Automation:** Explore advanced testing approaches based on what I learned
4. **Performance Testing:** Research how to test if my app can handle many users

**How I'll Examine:**
- Review my Hive implementation and identify what could be improved
- Study best practices and compare them to what I did
- Document lessons learned and create improved templates
- Experiment with alternative approaches in small test projects

**Goal:**
Build on my practical experience from Hive to make better technology choices and implementations from day one in my next project.

#### 3. Build in Extra Time for Problems
One of my biggest lessons is that I need to plan for things going wrong. In future projects, I'll add buffer time to my schedule.

**Adding Buffer Time:**
- Schedule time for unexpected problems
- Add 20-30% extra time to each major feature estimate
- Remember that new technologies take time to learn
- Expect that connecting different parts will have issues

**Breaking Down Work Better:**
- Break tasks into the right size - not too big, not too small
- Make sure I can actually estimate how long each task takes
- This helps me track if I'm on schedule
- Makes planning more realistic

**Task Size Rules:**
- Small tasks: 2-4 hours (finish in one sitting)
- Medium tasks: 1 day (finish in one day of work)
- Large tasks: 2-3 days (break it down if it's longer)
- Huge tasks: Split into several smaller tasks

#### 4. Plan the Code Structure Before Coding
Before I write any code, I need to plan how my code will be organized. After finishing requirements, I'll create a detailed plan for the code architecture and document it.

**What I'll Document:**
- Why I chose this particular structure
- Diagrams showing how components connect
- How data flows through the system
- Why I chose each technology
- How the system can grow larger

**Why This Matters:**
- Makes sure new features fit into a consistent structure
- Prevents the code becoming one huge mess
- Gives everyone a clear blueprint to follow
- Makes it easier to review and discuss the design

**My Process:**
1. Finish all requirements first
2. Choose the best code organization pattern (like MVC)
3. Draw diagrams of the components
4. Define clear boundaries between parts
5. Write down why I chose each technology
6. Get feedback from my advisor
7. Set up the initial file structure to match my plan

#### 5. Automate Testing and Deployment Early
I'll set up automated testing and deployment from the start of my next project. This means every time I push code, tests run automatically, and deployment happens automatically too. This prevents the manual deployment mistakes I made.

**Automated Testing Pipeline:**
1. **Automatic Tests:**
   - Tests run every time I commit code
   - Code quality checks run automatically
   - Verify the code builds successfully
   - Report how much of my code is tested

2. **Automatic Deployment:**
   - Deploy to a test server automatically
   - Run quick tests on the test server
   - Require my approval before going to production
   - Automatically undo deployment if something breaks

3. **Environment Management:**
   - Define infrastructure in code (not manual setup)
   - Create environments automatically
   - Manage environment settings systematically
   - Update database automatically

**What I'll Achieve:**
- No manual deployment steps (everything automatic)
- Confidence that deployment will work
- Fast feedback when something's wrong
- Fewer deployment crashes

---

## Conclusion

### What I Learned

The Hive project taught me valuable lessons in many areas:

#### Technical Lessons
- **Detailed requirements** are the foundation of success - they prevented so many problems
- **AI tools** make me faster when I review everything carefully
- **Early code structure decisions** affect the entire project
- **Testing approach** needs to match how my code is organized
- **Keeping environments the same** prevents deployment crashes

#### Project Management Lessons
- **Controlling scope** prevents trying to do too much at once
- **Extra time for problems** isn't optional - I need to plan for it
- **Being flexible** helps when I need to change plans
- **Breaking work into tasks** helps me see if I'm on track
- **Sometimes "good enough"** beats perfect when there's a deadline

#### Personal Growth
- **Full-stack is hard** - requires knowing many different things
- **Learning takes time** - I need to account for this in planning
- **Failing teaches best** - experience beats reading about it
- **Balance is essential** - I need to manage school, work, and family
- **Always improving** - challenges help me grow

### What I Did Well
1. ✅ **Writing Requirements** - My detailed SRS document prevented many problems
2. ✅ **Making Good Decisions** - Changing from "Reserved Hours" to "Proposed Schedule" when I saw problems
3. ✅ **Choosing Tools** - GitHub Copilot, DBeaver, and Docker all helped a lot
4. ✅ **Solving Problems** - I fixed deployment and architectural issues
5. ✅ **Meeting Deadlines** - I finished on time despite big challenges

### What I Need to Improve
1. 📈 **Managing Scope** - Better at saying "no" to extra features from the start
2. 📈 **Planning Structure** - Design organized code from day one
3. 📈 **Testing First** - Write tests while writing requirements
4. 📈 **Automating Deployment** - Set up automated testing and deployment early
5. 📈 **Planning Time** - Build in buffer time for learning and problems

### My Promise for Next Time

For my next project, I will:

1. **Requirements + Testing Together** - Write test scenarios while writing requirements
2. **Learn First** - Study Docker, CI/CD, and testing before I need them
3. **Add Buffer Time** - Plan 20-30% extra time for each feature
4. **Plan Architecture** - Document my code structure before coding
5. **Automate Early** - Set up automated testing and deployment from the start

### Final Thoughts

The Hive project taught me much more than just technical skills. I learned about the reality of building a complete web application alone, making practical decisions under time pressure, and the importance of learning from mistakes.

The big challenges I faced - especially trying to reorganize my code mid-project and the deployment crash during my presentation - taught me lessons I could never learn from a textbook. These experiences changed how I approach software development forever.

Despite the challenges, I succeeded because of:
- **Strong foundation** - detailed requirements document
- **Being flexible** - changing plans when I saw problems
- **Being practical** - delivering working software beats perfect code when time is tight
- **Learning continuously** - turning failures into knowledge

This project is both something I'm proud of and a guide for how to improve. Every lesson I learned here will help me in every future project.

---
