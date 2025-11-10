"""
LangGraph integration for AgentWorks.

Automatically traces LangGraph executions with full visibility into:
- State transitions
- Node executions
- Edge traversals
- Conditional routing
- Parallel execution
"""

from typing import Any, Dict, Callable, Optional
from functools import wraps
import time

from agentworks.tracing import trace_agent, trace_tool, send_span, get_current_trace_id
from agentworks.utils import generate_span_id


def trace_langgraph(graph: Any, workflow_id: Optional[str] = None, agent_id: str = "langgraph-agent"):
    """
    Wrap a LangGraph instance with tracing.
    
    Args:
        graph: Compiled LangGraph instance
        workflow_id: Optional workflow identifier
        agent_id: Agent identifier for the graph
        
    Returns:
        Wrapped graph with automatic tracing
        
    Example:
        from langgraph.graph import StateGraph
        from agentworks.integrations.langgraph import trace_langgraph
        
        # Define your graph
        workflow = StateGraph(AgentState)
        workflow.add_node("agent", call_agent)
        workflow.add_node("tools", call_tools)
        graph = workflow.compile()
        
        # Wrap with tracing
        traced_graph = trace_langgraph(graph, workflow_id="research")
        result = traced_graph.invoke({"input": "research AI agents"})
    """
    
    class TracedLangGraph:
        def __init__(self, original_graph: Any, workflow_id: Optional[str], agent_id: str):
            self.graph = original_graph
            self.workflow_id = workflow_id
            self.agent_id = agent_id
        
        def invoke(self, *args: Any, **kwargs: Any) -> Any:
            """Traced invoke method."""
            wf_id = self.workflow_id or f"langgraph-{int(time.time())}"
            
            with trace_agent(self.agent_id, workflow_id=wf_id):
                # Trace the entire graph execution
                with trace_tool("langgraph_execution", graph_type="StateGraph"):
                    result = self.graph.invoke(*args, **kwargs)
                
                # Trace final state
                if isinstance(result, dict):
                    send_span(
                        kind="decision",
                        name="langgraph_complete",
                        latency_ms=0,
                        status="ok",
                        final_state=str(result),
                    )
                
                return result
        
        async def ainvoke(self, *args: Any, **kwargs: Any) -> Any:
            """Traced async invoke method."""
            wf_id = self.workflow_id or f"langgraph-{int(time.time())}"
            
            with trace_agent(self.agent_id, workflow_id=wf_id):
                with trace_tool("langgraph_async_execution", graph_type="StateGraph"):
                    result = await self.graph.ainvoke(*args, **kwargs)
                
                if isinstance(result, dict):
                    send_span(
                        kind="decision",
                        name="langgraph_complete",
                        latency_ms=0,
                        status="ok",
                        final_state=str(result),
                    )
                
                return result
        
        def stream(self, *args: Any, **kwargs: Any):
            """Traced stream method."""
            wf_id = self.workflow_id or f"langgraph-{int(time.time())}"
            
            with trace_agent(self.agent_id, workflow_id=wf_id):
                for chunk in self.graph.stream(*args, **kwargs):
                    # Trace each state update
                    if isinstance(chunk, dict):
                        for node_name, node_output in chunk.items():
                            send_span(
                                kind="decision",
                                name=f"node:{node_name}",
                                latency_ms=0,
                                status="ok",
                                node_output=str(node_output)[:200],
                            )
                    
                    yield chunk
    
    return TracedLangGraph(graph, workflow_id, agent_id)


def trace_node(func: Callable) -> Callable:
    """
    Decorator to trace individual LangGraph nodes.
    
    Example:
        @trace_node
        def call_agent(state: AgentState) -> AgentState:
            # Your node logic
            return updated_state
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        node_name = func.__name__
        
        with trace_tool(f"node:{node_name}", node_type="langgraph_node"):
            result = func(*args, **kwargs)
        
        return result
    
    return wrapper


def trace_edge(condition_func: Callable) -> Callable:
    """
    Decorator to trace conditional edges in LangGraph.
    
    Example:
        @trace_edge
        def should_continue(state: AgentState) -> str:
            if state.finished:
                return "end"
            return "continue"
    """
    @wraps(condition_func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        edge_name = condition_func.__name__
        
        with trace_tool(f"edge:{edge_name}", edge_type="conditional"):
            result = condition_func(*args, **kwargs)
            
            # Log the routing decision
            send_span(
                kind="decision",
                name=f"routing:{edge_name}",
                latency_ms=0,
                status="ok",
                next_node=str(result),
            )
        
        return result
    
    return wrapper

