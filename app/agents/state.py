from typing import Any, TypedDict

class AgentState(TypedDict, total=False):
	query: str
	phone_name: str
	phone_names: list[str]
	phone_specs: list[dict[str, Any]]
	technical_dossier: str
	specs_result: str
	review: str
	error: str
	review_focus: str
