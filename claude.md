# Kalilmod

This repository is a general teaching tool that utilizes Claude Code to construct it's content. It comes to solve a common problem in today's learning process: Today, since LLM's and the internet in general provide such good explanation for everything, one can easily read explanation, go over them very briefly, get the feeling of understanding, and then forget what they learned immediately afterward. Real learning can happen only when the student has to actively solve a problem. The solution is to force interactive learning, where the user has to stand small tests throughout the learning process. This way, the user must engage with the material, and learning is done properly.

The creator of the repository is Michael Kali. "Kalilmod" in Hebrew sounds like (קל ללמוד), which means "easy to learn"

Claude code serves two roles in this repository:
1) Building this repository
   1) Writing the tool.
   2) documenting it for the Claude Code of the second role:
2) In future sessions - Claude serves as the teacher that reads the content creation instructions and uses them to inject content into the tool and to create the teaching content. 

Currently the repository is in building stages, and so Claude Code serve the first role: It will write the tools, and document it properly so that future Claude Code sessions can easily and efficiently use them to inject content.

It's final workflow will work as follows:

- Each topic is saved as a different folder in the "subjects" subdirectory.
- When the user runs the main script, which opens as an HTML gui. This opens in the background a Claude Code session, which orchestrates the lesson. they can choose whether to return to an existing subject or to start a new one.
- If they choose to start a new subject, they are prompted to  specify a subject which they want to study (e.g. Roman empire early days, Bragg scattering, C# coding, etc.).
- Claude then prompts the user multiple questions, to understand what do they already know, and what do they need to learn (e.g., "Do you know where was the roman empire built?" "Which particles participate in a Compton Scattering process?", etc.).
  - Those questions can come both as free text questions, or choice questions.
- After Claude Code finalizing his evaluation of the user's understanding, it writes content to the teaching tool, constructed of explanations, links to external materials such as Wikipedia pages or YouTube videos, manim animations, and most importantly: frequent questions that make sure the user understood what they read/watched.
- For questions that can be automatically evaluated - the process of answering can be done within the tool's mechanism. For free text/Latex answers - the user's answer will be returned to Claude to evaluate it as LLMs do and feedback the user.
- The tool is used by people that actually want to learn, and so if the answer of some multi-choice question is encoded into the html or the subject's folder - it is fine: the tool does not have to be resilient to cheating by students.
- The main point of the tool is the interactive learning - instead of reading only/reading a lot and then having to complete a long test, the teaching tool (Kalilmod) alternates between explanation and quizzes frequently.
- Claude (serving as the teacher) does not have to create the entire content at once. If the user chooses to continue after the first few steps, then Claude can generate more content, indefinitely.
- In those early stages - styling the gui is not important, since we first want to make it work.