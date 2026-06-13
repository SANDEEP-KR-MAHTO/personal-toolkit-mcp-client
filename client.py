# client.py
import asyncio
import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from groq import Groq
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# ── Load environment variables ───────────────────────────────────────────────
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")

# ── Setup Groq client ────────────────────────────────────────────────────────
groq_client = Groq(api_key=GROQ_API_KEY)
MODEL = "llama-3.3-70b-versatile"  # free, fast, supports tool calling

# ── FastAPI app ──────────────────────────────────────────────────────────────
app = FastAPI(title="MCP Web Client")

# ── Conversation history (in-memory) ────────────────────────────────────────
conversation_history = []


# ── Helper: fetch tools from MCP server ─────────────────────────────────────
async def get_mcp_tools():
    """Connect to MCP server and return tools in Groq/OpenAI format."""
    async with streamablehttp_client(MCP_SERVER_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools_result = await session.list_tools()
            groq_tools = []
            for tool in tools_result.tools:
                input_schema = tool.inputSchema or {}
                properties = {}
                for prop_name, prop_info in input_schema.get("properties", {}).items():
                    properties[prop_name] = {
                        "type": prop_info.get("type", "string"),
                        "description": prop_info.get("description", ""),
                    }
                groq_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": {
                            "type": "object",
                            "properties": properties,
                            "required": input_schema.get("required", []),
                        },
                    },
                })
            return groq_tools


# ── Helper: call a specific tool on MCP server ──────────────────────────────
async def call_mcp_tool(tool_name: str, tool_args: dict):
    """Call a tool on the MCP server and return the result."""
    async with streamablehttp_client(MCP_SERVER_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, tool_args)
            return result.content[0].text if result.content else "No result"


# ── Core chat logic ──────────────────────────────────────────────────────────
async def chat_with_tools(user_message: str):
    """Send message to Groq, handle tool calls, return final response."""

    # Fetch available tools from MCP server
    mcp_tools = await get_mcp_tools()

    # Add user message to history
    conversation_history.append({"role": "user", "content": user_message})

    # Build full messages with system prompt
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant with access to a personal utility toolkit. "
                "Use the available tools when relevant to answer user questions accurately."
            ),
        }
    ] + conversation_history.copy()

    # Send to Groq
    response = await asyncio.to_thread(
        groq_client.chat.completions.create,
        model=MODEL,
        messages=messages,
        tools=mcp_tools,
        tool_choice="auto",
    )

    # ── Handle tool calls in a loop ──────────────────────────────────────────
    while response.choices[0].message.tool_calls:
        tool_calls = response.choices[0].message.tool_calls

        # Add assistant message with tool calls to history
        messages.append(response.choices[0].message)

        # Process each tool call
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            # Call the tool on MCP server
            tool_result = await call_mcp_tool(tool_name, tool_args)

            # Add tool result to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(tool_result),
            })

        # Send tool results back to Groq
        response = await asyncio.to_thread(
            groq_client.chat.completions.create,
            model=MODEL,
            messages=messages,
            tools=mcp_tools,
            tool_choice="auto",
        )

    # Extract final text response
    final_response = response.choices[0].message.content

    # Update conversation history with assistant response
    conversation_history.append({"role": "assistant", "content": final_response})

    return final_response


# ── Routes ───────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def home():
    return FileResponse("templates/index.html")


@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message", "").strip()
    if not user_message:
        return JSONResponse({"error": "Empty message"}, status_code=400)
    try:
        response = await chat_with_tools(user_message)
        return JSONResponse({"response": response})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/clear")
async def clear_history():
    conversation_history.clear()
    return JSONResponse({"message": "Conversation cleared"})


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("client:app", host="0.0.0.0", port=7860, reload=True)
