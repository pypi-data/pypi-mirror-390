import copy
import json
import re
import uuid
from typing import Literal, cast

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import START, StateGraph
from langgraph.types import Command, RetryPolicy, StreamWriter
from universal_mcp.tools.registry import ToolRegistry
from universal_mcp.types import ToolFormat

from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.codeact0.llm_tool import smart_print
from universal_mcp.agents.codeact0.prompts import (
    AGENT_BUILDER_GENERATING_PROMPT,
    AGENT_BUILDER_META_PROMPT,
    AGENT_BUILDER_PLANNING_PROMPT,
    AGENT_BUILDER_PLAN_PATCH_PROMPT,
    AGENT_BUILDER_CODE_PATCH_PROMPT,
    build_tool_definitions,
    create_default_prompt,
)
from universal_mcp.agents.codeact0.sandbox import eval_unsafe, execute_ipython_cell, handle_execute_ipython_cell
from universal_mcp.agents.codeact0.state import AgentBuilderCode, AgentBuilderMeta, AgentBuilderPlan, AgentBuilderPatch, CodeActState
from universal_mcp.agents.codeact0.tools import (
    create_agent_builder_tools,
    create_meta_tools,
)
from universal_mcp.agents.codeact0.utils import build_anthropic_cache_message, extract_plan_parameters, get_connected_apps_string, strip_thinking
from universal_mcp.agents.codeact0.utils import apply_patch_or_use_proposed
from universal_mcp.agents.llm import load_chat_model
from universal_mcp.agents.utils import convert_tool_ids_to_dict, filter_retry_on


class CodeActPlaybookAgent(BaseAgent):
    def __init__(
        self,
        name: str,
        instructions: str,
        model: str,
        memory: BaseCheckpointSaver | None = None,
        registry: ToolRegistry | None = None,
        agent_builder_registry: object | None = None,
        sandbox_timeout: int = 20,
        **kwargs,
    ):
        super().__init__(
            name=name,
            instructions=instructions,
            model=model,
            memory=memory,
            **kwargs,
        )
        self.model_instance = load_chat_model(model)
        self.agent_builder_model_instance = load_chat_model("anthropic:claude-sonnet-4-5-20250929", thinking=False, disable_streaming = True, tags=("quiet",))
        self.registry = registry
        self.agent_builder_registry = agent_builder_registry
        self.agent = agent_builder_registry.get_agent() if agent_builder_registry else None

        self.tools_config = self.agent.tools if self.agent else {}
        self.eval_fn = eval_unsafe
        self.sandbox_timeout = sandbox_timeout
        self.default_tools_config = {
            "llm": ["generate_text", "classify_data", "extract_data", "call_llm"],
        }
        self.final_instructions = ""
        self.tools_context = {}
        self.eval_mode = kwargs.get("eval_mode", False)

    async def _build_graph(self):  # noqa: PLR0915
        """Build the graph for the CodeAct Playbook Agent."""
        meta_tools = create_meta_tools(self.registry)
        agent_builder_tools = create_agent_builder_tools()
        self.additional_tools = [
            smart_print,
            meta_tools["web_search"],
            meta_tools["read_file"],
            meta_tools["save_file"],
            meta_tools["upload_file"],
        ]

        if self.tools_config:
            await self.registry.load_tools(self.tools_config)  # Load provided tools
        if self.default_tools_config:
            await self.registry.load_tools(self.default_tools_config)  # Load default tools

        async def call_model(state: CodeActState) -> Command[Literal["execute_tools"]]:
            """This node now only ever binds the four meta-tools to the LLM."""
            messages = build_anthropic_cache_message(self.final_instructions) + state["messages"]
            agent_facing_tools = [
                execute_ipython_cell,
                agent_builder_tools["plan_agent"],
                agent_builder_tools["code_and_save_agent"],
                meta_tools["search_functions"],
                meta_tools["load_functions"],
            ]

            if isinstance(self.model_instance, ChatAnthropic):
                model_with_tools = self.model_instance.bind_tools(
                    tools=agent_facing_tools,
                    tool_choice="auto",
                    cache_control={"type": "ephemeral", "ttl": "1h"},
                )
                if isinstance(messages[-1].content, str):
                    pass
                else:
                    last = copy.deepcopy(messages[-1])
                    last.content[-1]["cache_control"] = {"type": "ephemeral", "ttl": "5m"}
                    messages[-1] = last
            else:
                model_with_tools = self.model_instance.bind_tools(
                    tools=agent_facing_tools,
                    tool_choice="auto",
                )
            response = cast(AIMessage, await model_with_tools.ainvoke(messages))
            if response.tool_calls:
                return Command(goto="execute_tools", update={"messages": [response]})
            else:
                return Command(update={"messages": [response], "model_with_tools": model_with_tools})

        async def execute_tools(state: CodeActState, writer: StreamWriter) -> Command[Literal["call_model"]]:
            """Execute tool calls"""
            last_message = state["messages"][-1]
            tool_calls = last_message.tool_calls if isinstance(last_message, AIMessage) else []

            tool_messages = []
            new_tool_ids = []
            tool_result = ""
            ask_user = False
            ai_msg = None
            effective_previous_add_context = state.get("add_context", {})
            effective_existing_context = state.get("context", {})
            plan = state.get("plan", None)
            agent_name = state.get("agent_name", None)
            agent_description = state.get("agent_description", None)
            # logging.info(f"Initial new_tool_ids_for_context: {new_tool_ids_for_context}")

            for tool_call in tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                try:
                    if tool_name == "execute_ipython_cell":
                        code = tool_call["args"]["snippet"]
                        output, new_context, new_add_context = await handle_execute_ipython_cell(
                            code,
                            self.tools_context,  # Uses the dynamically updated context
                            self.eval_fn,
                            effective_previous_add_context,
                            effective_existing_context,
                        )
                        effective_existing_context = new_context
                        effective_previous_add_context = new_add_context
                        tool_result = output
                    elif tool_name == "load_functions":
                        # The tool now does all the work of validation and formatting.
                        tool_result, new_context_for_sandbox, valid_tools, unconnected_links = await meta_tools[
                            "load_functions"
                        ].ainvoke(tool_args)
                        # We still need to update the sandbox context for `execute_ipython_cell`
                        new_tool_ids.extend(valid_tools)
                        if new_tool_ids:
                            self.tools_context.update(new_context_for_sandbox)
                        if unconnected_links:
                            ask_user = True
                            ai_msg = f"Please login to the following app(s) using the following links and let me know in order to proceed:\n {unconnected_links} "

                    elif tool_name == "search_functions":
                        tool_result = await meta_tools["search_functions"].ainvoke(tool_args)
                    
                    elif tool_name == "plan_agent":
                        plan, tool_result = await self._create_or_update_plan(state=state, writer=writer, plan=plan)
                        ask_user = True

                    elif tool_name == "code_and_save_agent":
                        tool_result, effective_previous_add_context, agent_name, agent_description = await self._build_or_patch_code(
                            state=state,
                            writer=writer,
                            plan=plan,
                            agent_name=agent_name,
                            agent_description=agent_description,
                            effective_previous_add_context=effective_previous_add_context,
                        )    
                    else:
                        raise Exception(
                            f"Unexpected tool call: {tool_call['name']}. "
                            "tool calls must be one of 'execute_ipython_cell', 'load_functions', 'search_functions', 'plan_agent', or 'code_and_save_agent'. For using functions, call them in code using 'execute_ipython_cell'."
                        )
                except Exception as e:
                    tool_result = str(e)

                tool_message = ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
                tool_messages.append(tool_message)

            if ask_user:
                if ai_msg:
                    tool_messages.append(AIMessage(content=ai_msg))
                return Command(
                    update={
                        "messages": tool_messages,
                        "selected_tool_ids": new_tool_ids,
                        "context": effective_existing_context,
                        "add_context": effective_previous_add_context,
                        "agent_name": agent_name,
                        "agent_description": agent_description,
                        "plan": plan,
                    }
                )

            return Command(
                goto="call_model",
                update={
                    "messages": tool_messages,
                    "selected_tool_ids": new_tool_ids,
                    "context": effective_existing_context,
                    "add_context": effective_previous_add_context,
                    "agent_name": agent_name,
                    "agent_description": agent_description,
                    "plan": plan,
                },
            )

        async def route_entry(state: CodeActState) -> Command[Literal["call_model", "execute_tools"]]:
            """Route to either normal mode or agent builder creation"""
            pre_tools = await self.registry.export_tools(format=ToolFormat.NATIVE)

            # Create the initial system prompt and tools_context in one go
            self.final_instructions, self.tools_context = create_default_prompt(
                pre_tools,
                self.additional_tools,
                self.instructions,
                await get_connected_apps_string(self.registry),
                self.agent,
                is_initial_prompt=True,
            )
            self.preloaded_defs, _ = build_tool_definitions(pre_tools)
            self.preloaded_defs = "\n".join(self.preloaded_defs)
            await self.registry.load_tools(state["selected_tool_ids"])
            exported_tools = await self.registry.export_tools(
                state["selected_tool_ids"], ToolFormat.NATIVE
            )  # Get definition for only the new tools
            _, loaded_tools_context = build_tool_definitions(exported_tools)
            self.tools_context.update(loaded_tools_context)

            if (
                len(state["messages"]) == 1 and self.agent
            ):  # Inject the agent's script function into add_context for execution
                script = self.agent.instructions.get("script")
                add_context = {"functions": [script]}
                return Command(goto="call_model", update={"add_context": add_context})
            return Command(goto="call_model")

        agent = StateGraph(state_schema=CodeActState)
        agent.add_node(call_model, retry_policy=RetryPolicy(max_attempts=3, retry_on=filter_retry_on))
        agent.add_node(execute_tools)
        agent.add_node(route_entry)
        agent.add_edge(START, "route_entry")
        return agent.compile(checkpointer=self.memory)

    async def _create_or_update_plan(self, state: "CodeActState", writer: StreamWriter, plan: list[str] | None):
        """Sub-agent helper: create or patch-update the agent plan and emit UI updates.
        Returns: (plan: list[str], tool_result: str)
        """
        plan_id = str(uuid.uuid4())
        writer({"type": "custom", id: plan_id, "name": "planning", "data": {"update": bool(plan)}})

        # Determine existing plan (prefer persisted agent's plan) and base messages
        existing_plan_steps = (self.agent.instructions.get("plan") if self.agent and getattr(self.agent, "instructions", None) else None) or plan
        base = strip_thinking(state["messages"])
        def with_sys(text: str):
            return [{"role": "system", "content": text}] + base

        if existing_plan_steps:
            current = "\n".join(map(str, existing_plan_steps or []))
            sys_prompt = self.instructions + "\n" + AGENT_BUILDER_PLAN_PATCH_PROMPT + self.preloaded_defs
            msgs = with_sys(sys_prompt) + [HumanMessage(content=f"Current plan (one step per line):\n{current}")]
            patch_model = self.agent_builder_model_instance.with_structured_output(AgentBuilderPatch)
            proposed = cast(AgentBuilderPatch, await patch_model.ainvoke(msgs)).patch
            updated = apply_patch_or_use_proposed(current, proposed)
            plan = [line for line in updated.splitlines() if line.strip()]
        else:
            sys_prompt = self.instructions + AGENT_BUILDER_PLANNING_PROMPT + self.preloaded_defs
            plan_model = self.agent_builder_model_instance.with_structured_output(AgentBuilderPlan)
            plan = cast(AgentBuilderPlan, await plan_model.ainvoke(with_sys(sys_prompt))).steps

        writer({"type": "custom", id: plan_id, "name": "planning", "data": {"plan": plan}})
        tool_result = {"plan": plan, "update": bool(plan), "message": f"Successfully generated the agent plan."}
        return plan, tool_result

    async def _build_or_patch_code(
        self,
        state: "CodeActState",
        writer: StreamWriter,
        plan: list[str] | None,
        agent_name: str | None,
        agent_description: str | None,
        effective_previous_add_context: dict,
    ):
        """Sub-agent helper: generate new code or patch existing code, save, and emit UI updates.
        Returns: (tool_result: str, effective_previous_add_context: dict, agent_name: str | None, agent_description: str | None)
        """
        generation_id = str(uuid.uuid4())
        writer({"type": "custom", "id": generation_id, "name": "generating", "data": {"update": bool(self.agent)}})

        base = strip_thinking(state["messages"])
        def with_sys(text: str):
            return [{"role": "system", "content": text}] + base
        plan_text = "\n".join(map(str, plan)) if plan else None
        existing_code = self.agent.instructions.get("script") if self.agent and getattr(self.agent, "instructions", None) else None

        if self.agent:
            agent_name = getattr(self.agent, "name", None)
            agent_description = getattr(self.agent, "description", None)

        if not agent_name or not agent_description:
            meta_model = self.agent_builder_model_instance.with_structured_output(AgentBuilderMeta)
            meta = cast(AgentBuilderMeta, await meta_model.ainvoke(with_sys(self.instructions + AGENT_BUILDER_META_PROMPT)))
            agent_name, agent_description = meta.name, meta.description

        writer({"type": "custom", "id": generation_id, "name": "generating", "data": {"update": bool(self.agent), "name": agent_name, "description": agent_description}})

        if existing_code:
            generating_instructions = self.instructions + AGENT_BUILDER_CODE_PATCH_PROMPT + self.preloaded_defs
            messages = with_sys(generating_instructions)
            if plan_text:
                messages.append(HumanMessage(content=f"Confirmed plan (one step per line):\n{plan_text}"))
            messages.append(HumanMessage(content=f"Current code to update:\n```python\n{existing_code}\n```"))
            patch_model = self.agent_builder_model_instance.with_structured_output(AgentBuilderPatch)
            proposed = cast(AgentBuilderPatch, await patch_model.ainvoke(messages)).patch
            python_code = apply_patch_or_use_proposed(existing_code, proposed)
        else:
            code_model = self.agent_builder_model_instance.with_structured_output(AgentBuilderCode)
            python_code = cast(AgentBuilderCode, await code_model.ainvoke(with_sys(self.instructions + AGENT_BUILDER_GENERATING_PROMPT + self.preloaded_defs))).code

        try:
            if not self.agent_builder_registry:
                raise ValueError("AgentBuilder registry is not configured")

            plan_params = extract_plan_parameters(state["plan"])
            instructions_payload = {
                "plan": state["plan"],
                "script": python_code,
                "params": plan_params,
            }
            tool_dict = convert_tool_ids_to_dict(state["selected_tool_ids"])
            res = self.agent_builder_registry.upsert_agent(
                name=agent_name,
                description=agent_description,
                instructions=instructions_payload,
                tools=tool_dict,
            )
            writer({"type": "custom", "id": generation_id, "name": "generating", "data": {"id": str(res.id), "update": bool(self.agent), "name": agent_name, "description": agent_description}})
            tool_result = {
                "id": str(res.id),
                "update": bool(self.agent),
                "name": agent_name,
                "description": agent_description,
                "message": f"Successfully saved the agent code and plan.",
            }
        except Exception:
            tool_result = f"Displaying the final saved code:\n\n{python_code}\nFinal Name: {agent_name}\nDescription: {agent_description}"

        if "functions" not in effective_previous_add_context:
            effective_previous_add_context["functions"] = []
        effective_previous_add_context["functions"].append(python_code)

        return tool_result, effective_previous_add_context, agent_name, agent_description