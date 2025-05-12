import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from modelprovider import ModelProvider

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.model_provider = ModelProvider()
        self.messages = []

        self.system_prompt = "You are a blender geometry nodes artist agent. Work with the tools provided to manipulate the geometry nodes graph into the requested 3d model. Add as many nodes as necessary to achieve the end result. While iterating, use the visual evaluation tool to get a description of any node to check if you're on the right track. When finished, or if you encounter a persistent error, call the end_loop tool to finish."

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_turn(self) -> dict:
        """Process a query using Claude and available tools"""
        # messages = [
        #     {
        #         "role": "user",
        #         "content": query
        #     }
        # ]

        response = await self.session.list_tools()
        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]

        # available_tools.append({
        #     "name": "end_loop",
        #     "description": "end the agent loop",
        #     "input_schema": {'properties': {}, 'title': 'end_loopArguments', 'type': 'object'}
        # })

        response = self.model_provider.get_response(self.messages, self.system_prompt, available_tools)

        final_text = []

        assistant_message_content = []
        for content in response.content:
            if content.type == 'text':
                final_text.append(content.text)
                assistant_message_content.append(content)
            elif content.type == 'tool_use':
                tool_name = content.name
                tool_args = content.input

                if tool_name == "end_loop":
                    return {
                        "new_text": "\n".join(final_text),
                        "is_done": True
                    }


                assistant_message_content.append(content)
                self.messages.append({
                    "role": "assistant",
                    "content": assistant_message_content
                })

                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                try:
                    result = await asyncio.wait_for(
                        self.session.call_tool(tool_name, tool_args),
                        timeout=10
                    )
                except asyncio.TimeoutError:
                    final_text.append(f"Tool {tool_name} timed out after 10 seconds")
                    self.messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": content.id,
                                "content": "tool call failed: timeout"
                            }
                        ]
                    })
                    continue

                self.messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": result.content
                        }
                    ]
                })

                final_text.append(f"Got tool output: {[content.text for content in result.content]}")


                # # Get next response from Claude
                # response = self.anthropic.messages.create(
                #     model="claude-3-5-sonnet-20241022",
                #     max_tokens=1000,
                #     messages=self.messages,
                #     tools=available_tools
                # )

                # final_text.append(response.content[0].text)

        return {
            "new_text": "\n".join(final_text),
            "is_done": False
        }

    async def agent_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        self.messages = []

        available_node_types = await self.session.call_tool("list_node_types", {})

        self.messages.append({
            "role": "user",
            "content": "Available node types: " + str(available_node_types.content[0].text)
        })

        while True:
            query = input("\nQuery: ").strip()
            finished_loop = False
            if query.lower() == 'quit':
                return
            self.messages.append({
                "role": "user",
                "content": query
            })

            while not finished_loop:
                # try:
                turn = await self.process_turn()
                response = turn["new_text"]
                finished_loop = turn["is_done"]

                print("\n" + response)

                # except Exception as e:
                #     print(f"\nError: {str(e)}")
                #     finished_loop = True

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.agent_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())