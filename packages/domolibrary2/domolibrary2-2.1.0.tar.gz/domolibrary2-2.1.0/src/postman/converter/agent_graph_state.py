# agent_graph_state.py - State definition for the conversion graph

from typing import Optional

from typing_extensions import TypedDict


class PostmanConversionState(TypedDict, total=False):
    """State for the Postman to Python conversion graph.

    This state is passed between all nodes in the graph and tracks
    the entire conversion process from input to output.
    """

    # Input
    collection_path: str
    export_folder: str
    customize_config: Optional[dict]

    # Orchestration
    conversion_plan: Optional[dict]
    current_phase: str

    # Parsing
    parsed_collection: Optional[dict]
    validation_report: Optional[dict]

    # Parallel Analysis Results
    structure_analysis: Optional[dict]
    auth_analysis: Optional[dict]
    parameter_analysis: Optional[dict]
    header_analysis: Optional[dict]

    # Aggregated Analysis
    aggregated_analysis: Optional[dict]

    # Code Generation
    generated_functions: list[dict]
    generated_tests: list[dict]

    # Validation
    validation_results: list[dict]

    # Final Output
    formatted_code: dict[str, str]  # filename -> code
    export_paths: list[str]

    # Error Handling
    errors: list[str]
    warnings: list[str]
