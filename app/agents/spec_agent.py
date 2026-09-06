import json
from typing import Any

from langchain_groq import ChatGroq

from app.agents.tools import get_phone_specs_from_db, list_available_phones
from app.config.settings import settings
from app.utils.logger import logger
from app.agents.prompts import (
    SPEC_AGENT_PROMPT_TEMPLATE,
    SPEC_SYNTHESIS_PROMPT_TEMPLATE,
)
from app.agents.state import AgentState

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


    def run_state(self, state: AgentState) -> AgentState:
        """Retrieve verified records and write the specification fields into state."""
        query = state.get("query", "")
        phone_name = state.get("phone_name", "").strip()
        logger.info(f"SpecRetrievalAgent: processing state query '{query}'")
        tool_outputs: list[str] = []
        phone_names: list[str] = []
        phone_specs: list[dict[str, Any]] = []

        try:
            # An explicit phone name is authoritative. Do not ask the LLM to infer it.
            if phone_name:
                output = get_phone_specs_from_db.invoke({"model_name": phone_name})
                tool_outputs.append(f"[{get_phone_specs_from_db.name} Result]:\n{output}")
                parsed = json.loads(output) if isinstance(output, str) else output
                if isinstance(parsed, dict) and parsed.get("model_name"):
                    phone_names.append(parsed["model_name"])
                    phone_specs.append(parsed)
                else:
                    phone_names.append(phone_name)
                dossier = "\n\n".join(tool_outputs)
                return {
                    **state,
                    "phone_names": phone_names,
                    "phone_specs": phone_specs,
                    "technical_dossier": dossier,
                    "specs_result": dossier,
                }

            ai_msg = (SPEC_AGENT_PROMPT_TEMPLATE | self.llm_with_tools).invoke({"request": query})
            for tool_call in ai_msg.tool_calls:
                selected_tool = self.tool_map.get(tool_call["name"])
                if not selected_tool:
                    continue
                args = tool_call.get("args", {})
                output = selected_tool.invoke(args)
                tool_outputs.append(f"[{tool_call['name']} Result]:\n{output}")
                if tool_call["name"] == get_phone_specs_from_db.name:
                    requested_name = args.get("model_name", "")
                    try:
                        parsed = json.loads(output) if isinstance(output, str) else output
                        if isinstance(parsed, dict) and parsed.get("model_name"):
                            phone_names.append(parsed["model_name"])
                            phone_specs.append(parsed)
                    except (TypeError, json.JSONDecodeError):
                        if requested_name:
                            phone_names.append(requested_name)
                    if requested_name and requested_name not in phone_names:
                        phone_names.append(requested_name)

            if not tool_outputs:
                tool_outputs.append(f"[Retriever Result]:\n{ai_msg.content}")

            specs_result = "\n\n".join(tool_outputs)
            if not phone_specs:
                phone_specs = [{"model_name": name} for name in phone_names]
            return {
                **state,
                "phone_names": phone_names,
                "phone_specs": phone_specs,
				"technical_dossier": specs_result,
                "specs_result": specs_result,
            }
        except Exception as error:
            logger.exception("Specification agent failed")
            return {
				**state,
				"phone_names": phone_names,
				"phone_specs": phone_specs,
				"technical_dossier": "",
				"specs_result": "",
				"error": str(error),
			}