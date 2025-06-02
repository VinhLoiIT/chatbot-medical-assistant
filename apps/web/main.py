import streamlit as st
from agent import get_agentic_rag_agent
from agno.agent import Agent
from agno.document.reader.base import Reader
from agno.document.reader.pdf_reader import PDFReader
from agno.document.reader.text_reader import TextReader
from agno.utils.log import logger
from utils import (
    CUSTOM_CSS,
    add_message,
    clear_sessions_widget,
    display_tool_calls,
    export_chat_history,
    rename_session_widget,
    session_selector_widget,
)

# nest_asyncio.apply()
st.set_page_config(
    page_title="Agentic RAG",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add custom CSS

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def restart_agent():
    """Reset the agent and clear chat history"""
    logger.debug("---*--- Restarting agent ---*---")
    st.session_state["agentic_rag_agent"] = None
    st.session_state["agentic_rag_agent_session_id"] = None
    st.session_state["messages"] = []
    st.rerun()


def get_reader(file_type: str) -> Reader:
    """Return appropriate reader based on file type."""
    readers = {
        "pdf": PDFReader(),
        "txt": TextReader(),
    }
    return readers.get(file_type.lower(), None)


def main():
    ####################################################################
    # App header
    ####################################################################
    st.markdown("<h1 class='main-title'>Agentic RAG </h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='subtitle'>Your intelligent research assistant powered by Agno</p>",
        unsafe_allow_html=True,
    )

    ####################################################################
    # Initialize Agent
    ####################################################################
    agentic_rag_agent: Agent
    if (
        "agentic_rag_agent" not in st.session_state
        or st.session_state["agentic_rag_agent"] is None
    ):
        logger.info("---*--- Creating new Agentic RAG  ---*---")
        agentic_rag_agent = get_agentic_rag_agent()
        st.session_state["agentic_rag_agent"] = agentic_rag_agent
    else:
        agentic_rag_agent = st.session_state["agentic_rag_agent"]

    ####################################################################
    # Load Agent Session from the database
    ####################################################################
    # Check if session ID is already in session state
    session_id_exists = (
        "agentic_rag_agent_session_id" in st.session_state
        and st.session_state["agentic_rag_agent_session_id"]
    )

    if not session_id_exists:
        try:
            st.session_state["agentic_rag_agent_session_id"] = (
                agentic_rag_agent.load_session()
            )
        except Exception as e:
            logger.error(f"Session load error: {str(e)}")
            st.warning("Could not create Agent session, is the database running?")
            # Continue anyway instead of returning, to avoid breaking session switching
    elif (
        st.session_state["agentic_rag_agent_session_id"]
        and hasattr(agentic_rag_agent, "memory")
        and agentic_rag_agent.memory is not None
        and not agentic_rag_agent.memory.runs
    ):
        # If we have a session ID but no runs, try to load the session explicitly
        try:
            agentic_rag_agent.load_session(
                st.session_state["agentic_rag_agent_session_id"]
            )
        except Exception as e:
            logger.error(f"Failed to load existing session: {str(e)}")
            # Continue anyway

    ####################################################################
    # Load runs from memory
    ####################################################################
    agent_runs = []
    if hasattr(agentic_rag_agent, "memory") and agentic_rag_agent.memory is not None:
        agent_runs = agentic_rag_agent.memory.runs

    # Initialize messages if it doesn't exist yet
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Only populate messages from agent runs if we haven't already
    if len(st.session_state["messages"]) == 0 and len(agent_runs) > 0:
        logger.debug("Loading run history")
        for _run in agent_runs:
            # Check if _run is an object with message attribute
            if hasattr(_run, "message") and _run.message is not None:
                add_message(_run.message.role, _run.message.content)
            # Check if _run is an object with response attribute
            if hasattr(_run, "response") and _run.response is not None:
                add_message("assistant", _run.response.content, _run.response.tools)
    elif len(agent_runs) == 0 and len(st.session_state["messages"]) == 0:
        logger.debug("No run history found")

    if prompt := st.chat_input("👋 Ask me anything!"):
        add_message("user", prompt)

    # ####################################################################
    # # Track loaded URLs and files in session state
    # ####################################################################
    # if "loaded_files" not in st.session_state:
    #     st.session_state.loaded_files = set()
    # if "knowledge_base_initialized" not in st.session_state:
    #     st.session_state.knowledge_base_initialized = False

    # st.sidebar.markdown("#### 📚 Document Management")
    # uploaded_file = st.sidebar.file_uploader(
    #     "Add a Document (.pdf, .csv, or .txt)", key="file_upload"
    # )
    # if (
    #     uploaded_file and not prompt and not st.session_state.knowledge_base_initialized
    # ):  # Only load if KB not initialized
    #     file_identifier = f"{uploaded_file.name}_{uploaded_file.size}"
    #     if file_identifier not in st.session_state.loaded_files:
    #         alert = st.sidebar.info("Processing document...", icon="ℹ️")
    #         file_type = uploaded_file.name.split(".")[-1].lower()
    #         reader = get_reader(file_type)
    #         if reader:
    #             docs = reader.read(uploaded_file)
    #             agentic_rag_agent.knowledge.load_documents(docs, upsert=True)
    #             st.session_state.loaded_files.add(file_identifier)
    #             st.sidebar.success(f"{uploaded_file.name} added to knowledge base")
    #             st.session_state.knowledge_base_initialized = True
    #         alert.empty()
    #     else:
    #         st.sidebar.info(f"{uploaded_file.name} already loaded in knowledge base")

    # if st.sidebar.button("Clear Knowledge Base"):
    #     agentic_rag_agent.knowledge.vector_db.delete()
    #     st.session_state.loaded_files.clear()
    #     st.session_state.knowledge_base_initialized = False  # Reset initialization flag
    #     st.sidebar.success("Knowledge base cleared")
    ###############################################################
    # Sample Question
    ###############################################################
    st.sidebar.markdown("#### ❓ Sample Questions")
    if st.sidebar.button("📝 Summarize"):
        add_message(
            "user",
            "Can you summarize what is currently in the knowledge base (use `search_knowledge_base` tool)?",
        )

    ###############################################################
    # Utility buttons
    ###############################################################
    st.sidebar.markdown("#### 🛠️ Utilities")
    col1, col2 = st.sidebar.columns([1, 1])  # Equal width columns
    with col1:
        if st.sidebar.button(
            "🔄 New Chat", use_container_width=True
        ):  # Added use_container_width
            restart_agent()
    with col2:
        if st.sidebar.download_button(
            "💾 Export Chat",
            export_chat_history(),
            file_name="rag_chat_history.md",
            mime="text/markdown",
            use_container_width=True,  # Added use_container_width
        ):
            st.sidebar.success("Chat history exported!")

    ####################################################################
    # Display chat history
    ####################################################################
    for message in st.session_state["messages"]:
        if message["role"] in ["user", "assistant"]:
            _content = message["content"]
            if _content is not None:
                with st.chat_message(message["role"]):
                    # Display tool calls if they exist in the message
                    if "tool_calls" in message and message["tool_calls"]:
                        display_tool_calls(st.empty(), message["tool_calls"])
                    st.markdown(_content)

    ####################################################################
    # Generate response for user message
    ####################################################################
    last_message = (
        st.session_state["messages"][-1] if st.session_state["messages"] else None
    )
    if last_message and last_message.get("role") == "user":
        question = last_message["content"]
        with st.chat_message("assistant"):
            # Create container for tool calls
            tool_calls_container = st.empty()
            resp_container = st.empty()
            with st.spinner("🤔 Thinking..."):
                response = ""
                try:
                    # Run the agent and stream the response
                    run_response = agentic_rag_agent.run(question, stream=True)
                    for _resp_chunk in run_response:
                        # Display tool calls if available
                        if _resp_chunk.tools and len(_resp_chunk.tools) > 0:
                            display_tool_calls(tool_calls_container, _resp_chunk.tools)

                        # Display response
                        if _resp_chunk.content is not None:
                            response += _resp_chunk.content
                            resp_container.markdown(response)

                    add_message(
                        "assistant", response, agentic_rag_agent.run_response.tools
                    )
                except Exception as e:
                    error_message = f"Sorry, I encountered an error: {str(e)}"
                    add_message("assistant", error_message)
                    st.error(error_message)

    ####################################################################
    # Session selector
    ####################################################################
    session_selector_widget(agentic_rag_agent)
    rename_session_widget(agentic_rag_agent)
    clear_sessions_widget(agentic_rag_agent)


main()
