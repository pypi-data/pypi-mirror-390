# agent_graph_nodes.py - Node functions for the conversion graph

import asyncio
import json
from typing import Any

from . import agent_tools as tools
from .agent_graph_agents import (
    initialize_aggregator_agent,
    initialize_auth_analyzer,
    initialize_code_generator,
    initialize_code_validator,
    initialize_formatter_agent,
    initialize_header_analyzer,
    initialize_orchestrator_agent,
    initialize_parameter_analyzer,
    initialize_parser_agent,
    initialize_structure_analyzer,
    initialize_test_generator,
    initialize_validation_agent,
)
from .agent_graph_state import PostmanConversionState


async def orchestration_node(state: PostmanConversionState) -> dict[str, Any]:
    """Plan conversion strategy.

    This node analyzes the collection and creates a conversion plan.

    Args:
        state: Current graph state

    Returns:
        Updated state with conversion plan
    """
    print("🎯 Orchestrator: Planning conversion strategy...")

    orchestrator_agent = initialize_orchestrator_agent()

    # Load basic metadata about the collection
    metadata = tools.extract_collection_metadata(
        tools.load_collection_from_file(state["collection_path"])
    )

    prompt = f"""Plan conversion for Postman collection:
- Name: {metadata['name']}
- Total Requests: {metadata['total_requests']}
- Has Auth: {metadata['has_auth']}
- Has Variables: {metadata['has_variables']}

Determine the optimal processing strategy and complexity."""

    result = await orchestrator_agent.run(prompt)

    print(f"✅ Plan created: {result.data.processing_strategy} strategy")
    print(f"   Complexity: {result.data.estimated_complexity}")

    return {
        "conversion_plan": result.data.model_dump(),
        "current_phase": "parsing",
    }


async def parsing_node(state: PostmanConversionState) -> dict[str, Any]:
    """Parse Postman collection.

    This node loads and parses the collection into structured models.

    Args:
        state: Current graph state

    Returns:
        Updated state with parsed collection
    """
    print("📄 Parser: Loading and parsing collection...")

    parser_agent = initialize_parser_agent()

    # Load the collection
    collection_dict = tools.load_collection_from_file(state["collection_path"])
    metadata = tools.extract_collection_metadata(collection_dict)
    folder_structure = tools.extract_folder_structure(collection_dict)

    # Get collection variables
    variables = {}
    if "variable" in collection_dict:
        for var in collection_dict["variable"]:
            variables[var.get("key", "")] = var.get("value", "")

    # Get collection auth
    auth = collection_dict.get("auth")

    prompt = f"""Parse this Postman collection:
- Total Requests: {metadata['total_requests']}
- Folders: {len(folder_structure)}
- Variables: {len(variables)}
- Has Auth: {auth is not None}

Collection structure (first 500 chars):
{json.dumps(collection_dict, indent=2)[:500]}...

Identify any parsing issues or structural concerns."""

    result = await parser_agent.run(prompt)

    print(f"✅ Parsed: {result.data.total_requests} requests")
    if result.data.parsing_issues:
        print(f"⚠️  Issues found: {len(result.data.parsing_issues)}")

    return {
        "parsed_collection": collection_dict,
        "current_phase": "validation",
    }


async def validation_node(state: PostmanConversionState) -> dict[str, Any]:
    """Validate parsed collection.

    This node validates the collection structure and completeness.

    Args:
        state: Current graph state

    Returns:
        Updated state with validation report
    """
    print("✓ Validator: Checking collection validity...")

    validator_agent = initialize_validation_agent()

    collection = state["parsed_collection"]

    # Perform structure validation
    is_valid, issues = tools.validate_collection_structure(collection)

    # Extract requests for validation
    requests = tools.extract_all_requests(collection)

    prompt = f"""Validate this Postman collection:
- Total Requests: {len(requests)}
- Structure Valid: {is_valid}
- Issues Found: {len(issues)}

Check all requests for:
- Required fields (name, method, url)
- Valid HTTP methods
- Well-formed URLs
- Proper authentication
- Response examples

Sample request:
{json.dumps(requests[0] if requests else {}, indent=2)[:500]}..."""

    result = await validator_agent.run(prompt)

    if not result.data.is_valid:
        print(f"❌ Validation failed with {len(result.data.errors)} errors")
        for error in result.data.errors[:3]:  # Show first 3
            print(f"   • {error}")
        return {
            "errors": result.data.errors,
            "current_phase": "error",
        }

    print(f"✅ Validation passed: {len(result.data.passed_checks)} checks")
    if result.data.warnings:
        print(f"⚠️  Warnings: {len(result.data.warnings)}")

    return {
        "validation_report": result.data.model_dump(),
        "current_phase": "analysis",
    }


async def parallel_analysis_node(state: PostmanConversionState) -> dict[str, Any]:
    """Run all analyzers in parallel.

    This node executes structure, auth, parameter, and header analysis
    concurrently for efficiency.

    Args:
        state: Current graph state

    Returns:
        Updated state with all analysis results
    """
    print("🔍 Analysis: Running parallel analyses...")

    collection = state["parsed_collection"]
    requests = tools.extract_all_requests(collection)

    # Initialize all analyzer agents
    struct_agent = initialize_structure_analyzer()
    auth_agent = initialize_auth_analyzer()
    param_agent = initialize_parameter_analyzer()
    header_agent = initialize_header_analyzer()

    # Prepare analysis data
    auth_data = tools.analyze_authentication(collection)
    param_data = tools.analyze_parameters(requests)
    header_data = tools.analyze_headers(requests)
    folder_structure = tools.extract_folder_structure(collection)

    # Create prompts
    struct_prompt = f"""Analyze the structure of this collection:
- Total Requests: {len(requests)}
- Folders: {folder_structure}
- Request Distribution: {len(requests)} requests across {len(folder_structure)} folders

Suggest optimal Python module organization."""

    auth_prompt = f"""Analyze authentication patterns:
- Collection Auth: {auth_data['collection_auth'] is not None}
- Folder Auths: {len(auth_data['folder_auth'])}
- Request Auths: {len(auth_data['request_auth'])}
- Auth Types: {auth_data['auth_types']}

Recommend authentication class design."""

    param_prompt = f"""Analyze parameters across {len(requests)} requests:
- Total Unique Params: {len(param_data['all_params'])}
- Common Params: {list(param_data['common_params'].keys())}
- Param Types: {param_data['param_types']}

Recommend parameter handling strategy."""

    header_prompt = f"""Analyze headers across {len(requests)} requests:
- Total Unique Headers: {len(header_data['all_headers'])}
- Common Headers: {list(header_data['common_headers'].keys())}
- Content Types: {header_data['content_types']}
- Auth Headers: {header_data['auth_headers']}

Recommend header management approach."""

    # Run in parallel
    print("   • Structure analysis...")
    print("   • Authentication analysis...")
    print("   • Parameter analysis...")
    print("   • Header analysis...")

    struct_task = struct_agent.run(struct_prompt)
    auth_task = auth_agent.run(auth_prompt)
    param_task = param_agent.run(param_prompt)
    header_task = header_agent.run(header_prompt)

    # Wait for all to complete
    struct_result, auth_result, param_result, header_result = await asyncio.gather(
        struct_task, auth_task, param_task, header_task
    )

    print("✅ All analyses complete")

    return {
        "structure_analysis": struct_result.data.model_dump(),
        "auth_analysis": auth_result.data.model_dump(),
        "parameter_analysis": param_result.data.model_dump(),
        "header_analysis": header_result.data.model_dump(),
        "current_phase": "aggregation",
    }


async def aggregation_node(state: PostmanConversionState) -> dict[str, Any]:
    """Aggregate all analysis results.

    This node synthesizes insights from all analyzers into a unified
    code generation strategy.

    Args:
        state: Current graph state

    Returns:
        Updated state with aggregated analysis
    """
    print("🔗 Aggregator: Synthesizing analyses...")

    aggregator_agent = initialize_aggregator_agent()

    analyses = {
        "structure": state["structure_analysis"],
        "auth": state["auth_analysis"],
        "parameters": state["parameter_analysis"],
        "headers": state["header_analysis"],
    }

    prompt = f"""Aggregate these analyses into a unified code generation strategy:

STRUCTURE ANALYSIS:
- Complexity Score: {analyses['structure']['complexity_score']}
- Module Structure: {analyses['structure']['suggested_module_structure']}

AUTH ANALYSIS:
- Auth Types: {analyses['auth']['auth_types']}
- Suggested Class: {analyses['auth']['suggested_auth_class']}

PARAMETER ANALYSIS:
- Common Params: {list(analyses['parameters']['common_params'].keys())}
- Param Types: {analyses['parameters']['param_types']}

HEADER ANALYSIS:
- Required Headers: {analyses['headers']['required_headers']}
- Common Headers: {list(analyses['headers']['common_headers'].keys())}

Create a cohesive strategy that minimizes duplication and maximizes reusability."""

    result = await aggregator_agent.run(prompt)

    print(f"✅ Strategy: {result.data.code_generation_strategy}")
    print(f"   Complexity: {result.data.complexity_assessment}")

    return {
        "aggregated_analysis": result.data.model_dump(),
        "current_phase": "code_generation",
    }


async def code_generation_node(state: PostmanConversionState) -> dict[str, Any]:
    """Generate Python functions.

    This node generates API client functions for each request in the collection.

    Args:
        state: Current graph state

    Returns:
        Updated state with generated functions
    """
    print("💻 Code Generator: Creating Python functions...")

    code_gen_agent = initialize_code_generator()

    collection = state["parsed_collection"]
    analysis = state["aggregated_analysis"]
    requests = tools.extract_all_requests(collection)

    generated_functions = []

    # Generate code for each request (show progress)
    total = len(requests)
    for idx, request in enumerate(requests, 1):
        print(f"   Generating {idx}/{total}: {request['name']}")

        context = {
            "request": request,
            "analysis": analysis,
            "strategy": analysis["code_generation_strategy"],
            "module_org": analysis["module_organization"],
            "shared_components": analysis["shared_components"],
        }

        prompt = f"""Generate a Python async function for this API request:

Request Name: {request['name']}
Method: {request['request']['method']}
URL: {request['request']['url']['raw'][:100]}...

Code Generation Strategy: {analysis['code_generation_strategy']}

Create a function that:
- Uses async/await
- Has comprehensive type hints
- Includes detailed docstring
- Handles errors gracefully
- Follows the aggregated analysis recommendations

Context:
{json.dumps(context, indent=2)[:500]}..."""

        result = await code_gen_agent.run(prompt)
        generated_functions.append(result.data.model_dump())

    print(f"✅ Generated {len(generated_functions)} functions")

    return {
        "generated_functions": generated_functions,
        "current_phase": "test_generation",
    }


async def test_generation_node(state: PostmanConversionState) -> dict[str, Any]:
    """Generate test functions.

    This node creates test functions for all generated code.

    Args:
        state: Current graph state

    Returns:
        Updated state with generated tests
    """
    print("🧪 Test Generator: Creating test functions...")

    test_gen_agent = initialize_test_generator()

    generated_tests = []

    # Generate tests for each function
    total = len(state["generated_functions"])
    for idx, func in enumerate(state["generated_functions"], 1):
        print(f"   Generating test {idx}/{total}: test_{func['function_name']}")

        prompt = f"""Generate a comprehensive pytest test for this function:

Function Name: {func['function_name']}
Function Code:
{func['function_code'][:300]}...

Create tests that:
- Use pytest with async support
- Test success cases
- Test error cases
- Include fixtures
- Use meaningful assertions

Include mock data based on the function's expected inputs/outputs."""

        result = await test_gen_agent.run(prompt)
        generated_tests.append(result.data.model_dump())

    print(f"✅ Generated {len(generated_tests)} test functions")

    return {
        "generated_tests": generated_tests,
        "current_phase": "validation",
    }


async def code_validation_node(state: PostmanConversionState) -> dict[str, Any]:
    """Validate generated code.

    This node checks all generated code for correctness and quality.

    Args:
        state: Current graph state

    Returns:
        Updated state with validation results
    """
    print("✓ Code Validator: Checking generated code...")

    validator_agent = initialize_code_validator()

    validation_results = []

    # Validate each function
    total = len(state["generated_functions"])
    for idx, func in enumerate(state["generated_functions"], 1):
        # Perform syntax check
        is_valid_syntax, syntax_errors = tools.validate_python_syntax(
            func["function_code"]
        )

        prompt = f"""Validate this generated Python code:

Function: {func['function_name']}
Syntax Valid: {is_valid_syntax}
Syntax Errors: {syntax_errors}

Code:
{func['function_code']}

Check for:
- Type consistency
- Style compliance (PEP 8)
- Security issues
- Best practices
- Import availability

Provide detailed feedback."""

        result = await validator_agent.run(prompt)
        validation_results.append(result.data.model_dump())

        if not result.data.is_valid:
            print(f"   ⚠️  Issue in function {idx}/{total}: {func['function_name']}")

    # Check if any validation failed
    has_errors = any(not r["is_valid"] for r in validation_results)

    if has_errors:
        error_count = sum(1 for r in validation_results if not r["is_valid"])
        print(f"❌ Validation failed: {error_count} functions have issues")
        return {
            "validation_results": validation_results,
            "current_phase": "error",
            "errors": [f"{error_count} functions failed validation"],
        }

    print(f"✅ All {total} functions validated successfully")

    return {
        "validation_results": validation_results,
        "current_phase": "formatting",
    }


async def formatting_node(state: PostmanConversionState) -> dict[str, Any]:
    """Format and prepare for export.

    This node applies final formatting and prepares code for writing to files.

    Args:
        state: Current graph state

    Returns:
        Updated state with formatted code ready for export
    """
    print("✨ Formatter: Polishing code...")

    formatter_agent = initialize_formatter_agent()

    formatted_code = {}

    # Format each function with its test
    total = len(state["generated_functions"])
    for idx, (func, test) in enumerate(
        zip(state["generated_functions"], state["generated_tests"]), 1
    ):
        print(f"   Formatting {idx}/{total}: {func['function_name']}.py")

        context = {"function": func, "test": test}

        prompt = f"""Format and prepare this code for production:

Function Code:
{func['function_code']}

Test Code:
{test['test_code']}

Apply:
- Black formatting
- Import organization (isort)
- Module docstring
- Consistent style

Create a complete, production-ready Python file."""

        result = await formatter_agent.run(prompt)

        filename = f"{func['function_name']}.py"
        formatted_code[filename] = result.data.formatted_function

    print(f"✅ Formatted {len(formatted_code)} files")

    return {
        "formatted_code": formatted_code,
        "current_phase": "complete",
    }
