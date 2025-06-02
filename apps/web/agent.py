from typing import Optional

from agno.agent import Agent
from agno.models.google import Gemini
from agno.storage.agent.sqlite import SqliteAgentStorage
from configs.db import knowledge_base
from configs.settings import settings


def get_agentic_rag_agent(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = True,
) -> Agent:
    """Get an Agentic RAG Agent with Memory."""
    # Select appropriate model class based on provider
    model = Gemini(id="gemini-2.5-flash-preview-05-20", api_key=settings.GEMINI_API_KEY)
    # Define persistent memory for chat history

    # Create the Agent
    return Agent(
        name="agentic_rag_agent",
        session_id=session_id,  # Track session ID for persistent conversations
        user_id=user_id,
        model=model,
        storage=SqliteAgentStorage(
            table_name="agentic_rag_agent_sessions",
            db_file="./data/session.sqlite",
        ),
        knowledge=knowledge_base,  # Add knowledge base
        description="You are a helpful Agent called 'Agentic RAG' and your goal is to assist the user in the best way possible.",
        instructions=[
            "1. Knowledge Base Search:",
            "   - ALWAYS start by searching the knowledge base using search_knowledge_base tool",
            "   - Analyze ALL returned documents thoroughly before responding",
            "   - If multiple documents are returned, synthesize the information coherently",
            "2. Context Management:",
            "   - Use get_chat_history tool to maintain conversation continuity",
            "   - Reference previous interactions when relevant",
            "   - Keep track of user preferences and prior clarifications",
            "3. Response Quality:",
            "   - Provide specific citations and sources for claims",
            "   - Structure responses with clear sections and bullet points when appropriate",
            "   - Include relevant quotes from source materials",
            "   - Avoid hedging phrases like 'based on my knowledge' or 'depending on the information'",
            "4. User Interaction:",
            "   - Ask for clarification if the query is ambiguous",
            "   - Break down complex questions into manageable parts",
            "   - Proactively suggest related topics or follow-up questions",
            "5. Error Handling:",
            "   - If no relevant information is found, clearly state this",
            "   - Suggest alternative approaches or questions",
            "   - Be transparent about limitations in available information",
        ],
        search_knowledge=True,  # This setting gives the model a tool to search the knowledge base for information
        read_chat_history=True,  # This setting gives the model a tool to get chat history
        markdown=True,  # This setting tellss the model to format messages in markdown
        # add_chat_history_to_messages=True,
        show_tool_calls=True,
        add_history_to_messages=True,  # Adds chat history to messages
        add_datetime_to_instructions=True,
        debug_mode=debug_mode,
        read_tool_call_history=True,
        num_history_responses=3,
    )
