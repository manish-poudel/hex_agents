from hex_agents.graph.state import WorkflowState




def get_storage_node(node_id: str):

    async def action(state: WorkflowState) -> WorkflowState:
        state['output'] = f"Accessing storage node with ID: {node_id} OK"
        return state

       
    return action