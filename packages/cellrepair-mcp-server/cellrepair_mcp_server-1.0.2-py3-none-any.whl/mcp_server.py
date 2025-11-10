#!/usr/bin/env python3
"""
🤖 CELLREPAIR CLAUDE MCP SERVER

Model Context Protocol Server für Claude Desktop App!

Claude User können CellRepair.AI direkt in Claude nutzen!
"""

import json
import sys
import requests
import os
from typing import Any, Sequence
from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from pydantic import BaseModel, Field


# MCP Server Instance
app = Server("cellrepair-ai")


class CollaborateArgs(BaseModel):
    """Arguments for CellRepair collaboration."""
    query: str = Field(description="Your question or problem to solve")
    context: dict = Field(
        default={},
        description="Optional context (current metrics, tech stack, etc.)"
    )


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    List available tools for Claude.
    """
    return [
        Tool(
            name="cellrepair_collaborate",
            description="""Access 4882 autonomous AI agents for collective intelligence.

Use when you need help with:
- Multi-agent system optimization
- Scaling strategies
- Cost reduction approaches
- Performance improvements
- AI coordination patterns
- Production architectures

The network provides intelligent recommendations with high confidence scores,
predictive intelligence (3 steps ahead), and compliance checking.""",
            inputSchema=CollaborateArgs.model_json_schema()
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """
    Execute tool call from Claude.
    """
    if name != "cellrepair_collaborate":
        raise ValueError(f"Unknown tool: {name}")

    # Get API key from environment
    api_key = os.getenv('CELLREPAIR_API_KEY')
    if not api_key:
        return [
            TextContent(
                type="text",
                text="Error: CELLREPAIR_API_KEY not set. Get your free API key at: https://cellrepair.ai/api/?utm_source=claude&utm_medium=mcp"
            )
        ]

    # Parse arguments
    query = arguments.get("query", "")
    context = arguments.get("context", {})

    if not query:
        return [
            TextContent(
                type="text",
                text="Error: Query is required"
            )
        ]

    # Call CellRepair API
    try:
        response = requests.post(
            "https://cellrepair.ai/api/v1/collaborate",
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'system': 'Claude (via MCP)',
                'query': query,
                'context': context
            },
            timeout=30
        )

        if response.status_code == 401:
            return [
                TextContent(
                    type="text",
                    text="Error: Invalid API key. Get a free key at: https://cellrepair.ai/api/?utm_source=claude&utm_medium=mcp"
                )
            ]

        if response.status_code != 200:
            return [
                TextContent(
                    type="text",
                    text=f"Error: API returned status {response.status_code}"
                )
            ]

        data = response.json()

        # Format response for Claude
        insight = data.get('insight', {})
        recommendation = insight.get('recommendation', 'No recommendation available')
        confidence = insight.get('confidence', 0)
        agents = data.get('agents_consulted', 0)

        # Build response text
        result_text = f"""**CellRepair.AI Analysis**

{recommendation}

**Confidence:** {confidence*100:.1f}%
**Agents Consulted:** {agents}
**Implementation Time:** {insight.get('implementation_time', 'Unknown')}
**ROI Estimate:** {insight.get('roi_estimate', 'Unknown')}
"""

        # Add predictive intelligence
        predictive = data.get('predictive_intelligence', {})
        next_questions = predictive.get('you_will_probably_ask_next', [])
        if next_questions:
            result_text += "\n\n**Predictive Intelligence (3 steps ahead):**\n"
            for i, q in enumerate(next_questions, 1):
                result_text += f"{i}. {q}\n"

        # Add learning exchange info
        learning = data.get('learning_exchange', {})
        if learning:
            result_text += f"\n\n**AI-to-AI Learning:**\n"
            result_text += f"- Both systems improved: {learning.get('both_systems_improved', False)}\n"
            result_text += f"- Total patterns learned: {learning.get('total_patterns_learned', 0)}\n"

        return [
            TextContent(
                type="text",
                text=result_text.strip()
            )
        ]

    except requests.exceptions.Timeout:
        return [
            TextContent(
                type="text",
                text="Error: Request timed out. Please try again."
            )
        ]
    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )
        ]


def main():
    """Run the MCP server."""
    import asyncio
    from mcp.server.stdio import stdio_server

    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )

    asyncio.run(run())


if __name__ == "__main__":
    main()

