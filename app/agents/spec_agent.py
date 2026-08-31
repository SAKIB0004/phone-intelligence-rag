from langchain_groq import ChatGroq
from app.agents.tools import get_phone_specs_from_db, list_available_phones
from app.config.settings import settings
from app.utils.logger import logger
from app.agents.prompts import (
    SPEC_AGENT_PROMPT_TEMPLATE,
    SPEC_SYNTHESIS_PROMPT_TEMPLATE,
)

class SpecRetrievalAgent:
    """Specialist Agent responsible for querying and compiling verified technical specifications."""

    def __init__(self):
        self.llm = ChatGroq(
            model=settings.GROQ_MODEL,
            api_key=settings.GROQ_API_KEY,
            temperature=0.0,
        )
        self.tools = [get_phone_specs_from_db, list_available_phones]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.tool_map = {tool.name: tool for tool in self.tools}


    def run(self, phone_query):
        """Executes tool calling and synthesizes the finalized technical dossier."""
        logger.info(f"SpecRetrievalAgent: Processing query '{phone_query}'")

        # 1. Routing pass: Determine and invoke tools
        routing_chain = SPEC_AGENT_PROMPT_TEMPLATE | self.llm_with_tools
        ai_msg = routing_chain.invoke({"request": phone_query})

        if not ai_msg.tool_calls:
            return str(ai_msg.content)

        # 2. Execute selected tools
        tool_outputs = []
        for tool_call in ai_msg.tool_calls:
            tool_name = tool_call["name"]
            selected_tool = self.tool_map.get(tool_name)

            if selected_tool:
                output = selected_tool.invoke(tool_call["args"])
                tool_outputs.append(f"[{tool_name} Result]:\n{output}")

        # 3. Synthesis pass: Format raw tool outputs into the structured dossier
        synthesis_chain = SPEC_SYNTHESIS_PROMPT_TEMPLATE | self.llm
        final_dossier = synthesis_chain.invoke({"query": phone_query, "tool_data": "\n\n".join(tool_outputs)})

        return str(final_dossier.content)