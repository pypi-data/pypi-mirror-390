"""Prompts for conversation extension pipeline."""

DEFAULT_FOLLOWUP_PROMPT = """## Your Task
Your primary function is to generate intelligent follow-up user question that a USER would ask the AI assistant based on conversation history. These questions must ALWAYS be phrased as if the USER is asking the AI for help, continuing the conversation, providing instruction to complete the task, asking for the information, Q&A, or guidance.

------

## CRITICAL PERSPECTIVE RULE
- All questions must be written from the user's perspective, addressed to the AI assistant, and continue the conversation naturally (no resets).
- Do not always start a user query with "could," "please," or similar polite forms. It's okay to use them occasionally, but not every time. The tone should match the context, instructions, and flow of the conversation — not always sound like a request

## CONTINUITY & VARIETY GUIDELINES
- No repetition: Don't reuse the same openings or phrasing. Vary sentence structure and word choice.
- Next-step focus: Each question should feel like the next logical step in the dialogue, not a rehash.
- Context-aware: Adapt to the current mode—
- Casual chat: move the topic forward naturally.
- Task work: ask follow-ups that progress the task to completion.
- Instructions: confirm understanding, request specifics, or ask for edge cases.
- Q&A: probe deeper, clarify assumptions, or test alternatives.
- Human-like collaboration: Show problem-solving, prioritization, and decision-making; reference prior answers and constraints.
- Depth & breadth: Expand the horizon of the discussion when helpful (consider risks, trade-offs, metrics, timelines, dependencies).
- Actionable clarity: Request concrete outputs (checklists, drafts, code, steps) when the context calls for them.

------

### CONVERSATION HISTORY:
{history}

### INSTRUCTIONS:
- Generate a meaningful follow-up question that naturally continues this conversation
- Build on the assistant's last response - ask for details, clarification, examples, or related aspects
- Be conversational and natural - like a curious human having a real discussion
- DO NOT repeat the same question or use the same phrasing from previous questions
- Adapt your tone and style to match the conversation flow
- Ask something that moves the conversation forward meaningfully
- Keep it concise and focused
- Write every question as the user, directed to the assistant, moving the conversation forward with varied, context-aware wording—no repetition, always the next step, aiming for useful, human-like collaboration.

------

Return your follow-up question wrapped in XML tags like this:
<user>Your follow-up question here</user>"""


def get_default_prompts():
    """Get default prompts for conversation extension."""
    return {
        'followup_question': DEFAULT_FOLLOWUP_PROMPT
    }