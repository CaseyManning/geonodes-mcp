import asyncio
import json
import os
import sys
from contextlib import AsyncExitStack
from typing import Dict, List, Optional

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import AsyncOpenAI

load_dotenv()          # pulls OPENAI_API_KEY and anything else from .env


class MCPClient:
    """
    Same public surface as the original, but powered by OpenAI Chat Completions.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.openai = AsyncOpenAI()         # uses environment vars for auth
        self.exit_stack = AsyncExitStack()

        self.session: Optional[ClientSession] = None      # MCP transport/session
        self.stdio = None                                 # reader
        self.write = None                                 # writer

        self.messages: List[Dict] = []                    # chat history

        self.system_prompt = (
            "You are a blender geometry-nodes artist agent. "
            "Work with the tools provided to manipulate the geometry-nodes graph "
            "into the requested 3-D model. Add as many nodes as necessary. "
            "Use the visual-evaluation tool to confirm node output. "
            "When finished—or on persistent error—call end_loop."
        )

    async def connect_to_server(self, server_script_path: str):
        """Spin up / attach to the MCP server process and open a session."""
        if not server_script_path.endswith((".py", ".js")):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if server_script_path.endswith(".py") else "node"
        server_params = StdioServerParameters(command=command,
                                              args=[server_script_path],
                                              env=None)

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport

        # Open a ClientSession on the same stdio transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )
        await self.session.initialize()

        server_tools = (await self.session.list_tools()).tools
        print("Connected to server with tools:",
              [tool.name for tool in server_tools])

    async def cleanup(self):
        await self.exit_stack.aclose()

    async def get_openai_response(
        self,
        available_tools_for_openai: List[Dict],
    ):
        """
        Call the OpenAI chat endpoint with:
        * current message history (self.messages)
        * system prompt
        * tool definitions (OpenAI schema)
        """
        response = await self.openai.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": self.system_prompt},
                      *self.messages],
            tools=available_tools_for_openai,
            tool_choice="auto",          # let the model decide
            max_tokens=1000,
        )
        return response.choices[0].message

    @staticmethod
    def _tool_schema_for_openai(tool) -> Dict:
        """
        Translate an MCP ToolDescription -> OpenAI function-tool schema.
        MCP tool has .name, .description, .inputSchema (JSON Schema dict).
        """
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema,
            },
        }

    async def process_turn(self) -> Dict[str, object]:
        """
        One “assistant → user-visible action” cycle:
          1. Ask MCP for the latest set of tools.
          2. Feed chat + tools to OpenAI.
          3. Echo assistant text, call any tools it requests,
             then feed results back to the model.
        """
        mcp_tools = (await self.session.list_tools()).tools
        openai_tools = [self._tool_schema_for_openai(t) for t in mcp_tools]

        assistant_msg = await self.get_openai_response(openai_tools)

        final_text_chunks: List[str] = []

        if assistant_msg.content:
            final_text_chunks.append(assistant_msg.content)

        tool_calls = assistant_msg.tool_calls or []

        for call in tool_calls:
            tool_name = call.function.name
            tool_args = json.loads(call.function.arguments or "{}")

            # If the model wants to end the loop, honour it immediately
            if tool_name == "end_loop":
                return {"new_text": "\n".join(final_text_chunks), "is_done": True}

            # append the assistant's tool request into history
            self.messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [call.model_dump()],
            })

            final_text_chunks.append(f"calling tool {tool_name} with args {tool_args}")

            # Actually invoke the MCP tool
            try:
                result = await asyncio.wait_for(
                    self.session.call_tool(tool_name, tool_args),
                    timeout=10
                )
            except asyncio.TimeoutError:
                final_text_chunks.append(f"Tool '{tool_name}' timed out.")
                # Let the model know the call failed
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": "tool call failed: timeout",
                })
                continue

            result_text = (result.content[0].text
                           if getattr(result, "content", None) else str(result))
            final_text_chunks.append(f"[{tool_name} output] {result_text}")

            self.messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result_text,
            })

        return {"new_text": "\n".join(final_text_chunks), "is_done": False}

    async def agent_loop(self):
        """
        Interactive terminal loop.
        """
        print("\nMCP Client (OpenAI) started.  Type 'quit' to exit.")

        # Seed the assistant with available node types
        node_types = await self.session.call_tool("list_node_types", {})
        self.messages.append({
            "role": "user",
            "content": f"Available node types: {node_types.content[0].text}",
        })

        while True:
            query = input("\nQuery: ").strip()
            if query.lower() == "quit":
                break

            # record user question
            self.messages.append({"role": "user", "content": query})

            finished = False
            while not finished:
                turn = await self.process_turn()
                print("\n" + turn["new_text"])
                finished = turn["is_done"]

        print("Good-bye!")

async def main():
    if len(sys.argv) < 2:
        print("Usage: python client_openai.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.agent_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
