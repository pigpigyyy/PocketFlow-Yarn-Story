from pocketflow import Flow
from nodes import (
    GetGameRequirementNode,
    BackgroundStoryNode,
    CharactersDesignNode,
    StoryFlowNode,
    YarnScriptNode,
    SummaryNode
)

def create_yarn_story_flow():
    """Create and return a Yarn Story Game development flow."""
    # Create nodes
    get_requirement_node = GetGameRequirementNode()
    background_story_node = BackgroundStoryNode()
    characters_design_node = CharactersDesignNode()
    story_flow_node = StoryFlowNode()
    yarn_script_node = YarnScriptNode()
    summary_node = SummaryNode()

    # Connect nodes in sequence
    get_requirement_node >> background_story_node >> characters_design_node >> story_flow_node >> yarn_script_node >> summary_node

    # Create flow starting with input node
    return Flow(start=get_requirement_node)

# Create the flow
yarn_story_flow = create_yarn_story_flow()