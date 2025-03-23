"""Service for handling LLM (Large Language Model) interactions.

This module provides functionality for creating and configuring LLM instances,
managing chat workflows with tool integration, and handling streaming responses.
It uses LangChain and LangGraph to create conversational agents with tool-calling
capabilities.

Dependencies:
    - langchain_core: For message handling and prompt templates
    - langchain_openai: For Azure OpenAI integration
    - langgraph: For creating conversational agent workflows
"""
from typing import Any, Callable, Generator
import logging

from django.conf import settings
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import AzureChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from langchain_core.output_parsers import StrOutputParser

from ..utils.template_loader import render_template
from ..utils.llm_helpers import truncate_messages_to_token_limit

logger = logging.getLogger(__name__)


# Create a persistent memory store
memory = MemorySaver()


class LLMService:
    """Service for handling LLM interactions.
    
    This class provides methods for configuring LLM instances, creating chat workflows
    with tool integrations, and generating streaming responses from the language model.
    It serves as the core interface for AI capabilities in the application.
    """

    @staticmethod
    def get_system_prompt(use_summarization) -> str:
        """Returns the system prompt template for the LLM.
        
        Returns:
            The rendered system prompt template as a string.
        """
        template = render_template("system_prompt.j2", use_summarization=use_summarization)
        return template

    @staticmethod
    def create_llm(deployment_name: str, temperature: float) -> AzureChatOpenAI:
        """Creates and configures an LLM instance using Azure OpenAI.
        
        Args:
            deployment_name: The Azure OpenAI deployment name to use.
            temperature: The temperature setting for response randomness (0.0-1.0).
            
        Returns:
            A configured AzureChatOpenAI instance ready for use.
        """
        return AzureChatOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            azure_deployment=deployment_name,
            openai_api_version=settings.AZURE_OPENAI_API_VERSION,
            temperature=temperature,
            streaming=True,
        )

    @staticmethod
    def create_chat_workflow(llm: AzureChatOpenAI, tools: list[Callable], use_summarization: bool) -> Any:
        """Creates a workflow for the chat interaction with integrated tools.
        
        This method constructs a state graph for conversational flow, enabling
        the LLM to decide when to use tools and process their outputs.
        
        Args:
            llm: The configured AzureChatOpenAI instance.
            tools: A list of callable functions that will be exposed as tools to the LLM.
            
        Returns:
            A compiled LangGraph workflow with persistent state management.
        """

        llm_with_tools = llm.bind_tools(tools)

        # Create prompt template
        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", LLMService.get_system_prompt(use_summarization)),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        # trimmer = trim_messages(
        #     max_tokens=16000,
        #     strategy="last",
        #     token_counter=llm,
        #     include_system=True,
        #     allow_partial=False,
        #     start_on="human",
        # )

        def call_model(state: MessagesState):
            # BUG: This is not working as expected. trimmer is used exactly as in the docs (https://python.langchain.com/docs/how_to/trim_messages/),
            # but invoke() is not working. Seems to be a bug on the library side.
            #
            # trimmed_messages = trimmer.invoke(state["messages"])
            # prompt = prompt_template.invoke("messages", trimmed_messages)
            #
            # instead we use a custom truncate_messages_to_token_limit function
            messages = truncate_messages_to_token_limit(state["messages"])

            prompt = prompt_template.invoke(messages)
            response = llm_with_tools.invoke(prompt)
            return {"messages": response}

        def should_use_tool(state: MessagesState):
            """Determine if we should call tools or end the conversation turn."""
            messages = state["messages"]
            last_message = messages[-1]
            return bool(last_message.tool_calls)

        # Define the workflow graph
        workflow = StateGraph(state_schema=MessagesState)
        workflow.add_node("llm", call_model)
        workflow.add_node("tools", ToolNode(tools))

        workflow.add_edge(START, "llm")
        workflow.add_conditional_edges(
            "llm",
            should_use_tool,
            {
                True: "tools",  # If tools are called, go to tools node
                False: END,  # If no tools needed, end the conversation
            },
        )
        workflow.add_edge("tools", "llm")  # After tools execute, go back to LLM

        return workflow.compile(checkpointer=memory)

    @staticmethod
    def generate_stream(
        app: Any, input_messages: list[HumanMessage], thread_id: str
    ) -> Generator[tuple[str, dict], None, None]:
        """Generates a stream of responses from the LLM.
        
        This method handles streaming responses from the language model,
        providing real-time content as it's generated by the AI.
        
        Args:
            app: The compiled LangGraph application workflow.
            input_messages: A list of HumanMessage objects containing the conversation history.
            thread_id: A unique identifier for the conversation thread.
            
        Returns:
            A generator yielding tuples of (content, metadata) as the response is streamed.
        """
        config = {"configurable": {"thread_id": thread_id}}

        stream = app.stream(
            {"messages": input_messages}, config, stream_mode="messages"
        )

        for chunk, metadata in stream:
            if isinstance(chunk, AIMessageChunk) and chunk.content:
                yield chunk.content, metadata


    @staticmethod
    def invoke_summarization_chain(chat_summarization: str, user_question: str, contents: str):
        """Creates and invokes a LangChain pipeline for summarizing arXiv papers.
        
        Args:
            chat_summarization: A summary of the chat history for context
            user_question: The current user question to focus the summary on
            contents: The paper contents to summarize
            
        Returns:
            A summary of the paper focused on the user's question
        """       

        # Get the prompt template
        template_content = render_template(
            'summarization_prompt.j2',
            chat_summarization=chat_summarization,
            user_question=user_question,
            contents=contents
        )
        try:
            prompt_template = ChatPromptTemplate.from_template(template_content)

            llm = LLMService.create_llm("gpt-4o-mini", 0.3)
            llm = llm.with_config(streaming=False)  # Disable streaming
            chain = prompt_template | llm | StrOutputParser()
            result = chain.invoke({})
        except Exception as e:
            logger.debug(f"Error summarizing paper content: {e}")
            return "Error summarizing paper content"

        return result
