from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP, Context
from dataclasses import dataclass
from contextlib import asynccontextmanager
import socket
import json
import asyncio
import logging
from typing import AsyncIterator, Dict, Any, List, Annotated
from gemini_image import describe_image, evaluate_image

mcp = FastMCP("weather")

data_filepath = "node_data.json"

# Global connection for resources (since resources can't access context)
_blender_connection = None

@dataclass
class BlenderConnection:
    host: str
    port: int
    sock: socket.socket = None  # Changed from 'socket' to 'sock' to avoid naming conflict
    
    def connect(self) -> bool:
        """Connect to the Blender addon socket server"""
        if self.sock:
            return True
            
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            print(f"Connected to Blender at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Failed to connect to Blender: {str(e)}")
            self.sock = None
            return False
    
    def disconnect(self):
        """Disconnect from the Blender addon"""
        if self.sock:
            try:
                self.sock.close()
            except Exception as e:
                print(f"Error disconnecting from Blender: {str(e)}")
            finally:
                self.sock = None

    def receive_full_response(self, sock, buffer_size=8192):
        """Receive the complete response, potentially in multiple chunks"""
        chunks = []
        # Use a consistent timeout value that matches the addon's timeout
        sock.settimeout(15.0)  # Match the addon's timeout
        
        try:
            while True:
                try:
                    chunk = sock.recv(buffer_size)
                    if not chunk:
                        # If we get an empty chunk, the connection might be closed
                        if not chunks:  # If we haven't received anything yet, this is an error
                            raise Exception("Connection closed before receiving any data")
                        break
                    
                    chunks.append(chunk)
                    
                    # Check if we've received a complete JSON object
                    try:
                        data = b''.join(chunks)
                        json.loads(data.decode('utf-8'))
                        # If we get here, it parsed successfully
                        print(f"Received complete response ({len(data)} bytes)")
                        return data
                    except json.JSONDecodeError:
                        # Incomplete JSON, continue receiving
                        continue
                except socket.timeout:
                    # If we hit a timeout during receiving, break the loop and try to use what we have
                    print("Socket timeout during chunked receive")
                    break
                except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
                    print(f"Socket connection error during receive: {str(e)}")
                    raise  # Re-raise to be handled by the caller
        except socket.timeout:
            print("Socket timeout during chunked receive")
        except Exception as e:
            print(f"Error during receive: {str(e)}")
            raise
            
        # If we get here, we either timed out or broke out of the loop
        # Try to use what we have
        if chunks:
            data = b''.join(chunks)
            print(f"Returning data after receive completion ({len(data)} bytes)")
            try:
                # Try to parse what we have
                json.loads(data.decode('utf-8'))
                return data
            except json.JSONDecodeError:
                # If we can't parse it, it's incomplete
                raise Exception("Incomplete JSON response received")
        else:
            raise Exception("No data received")

    def send_command(self, command_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a command to Blender and return the response"""
        if not self.sock and not self.connect():
            raise ConnectionError("Not connected to Blender")
        
        command = {
            "type": command_type,
            "params": params or {}
        }
        
        try:
            # Log the command being sent
            print(f"Sending command: {command_type} with params: {params}")
            
            # Send the command
            self.sock.sendall(json.dumps(command).encode('utf-8'))
            print(f"Command sent, waiting for response...")
            
            # Set a timeout for receiving - use the same timeout as in receive_full_response
            self.sock.settimeout(15.0)  # Match the addon's timeout
            
            # Receive the response using the improved receive_full_response method
            response_data = self.receive_full_response(self.sock)
            print(f"Received {len(response_data)} bytes of data")
            
            response = json.loads(response_data.decode('utf-8'))
            print(f"Response parsed, status: {response.get('status', 'unknown')}")
            
            if response.get("status") == "error":
                print(f"Blender error: {response.get('message')}")
                raise Exception(response.get("message", "Unknown error from Blender"))
            
            return response.get("result", {})
        except socket.timeout:
            print("Socket timeout while waiting for response from Blender")
            # Don't try to reconnect here - let the get_blender_connection handle reconnection
            # Just invalidate the current socket so it will be recreated next time
            self.sock = None
            raise Exception("Timeout waiting for Blender response - try simplifying your request")
        except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
            print(f"Socket connection error: {str(e)}")
            self.sock = None
            raise Exception(f"Connection to Blender lost: {str(e)}")
        except json.JSONDecodeError as e:
            print(f"Invalid JSON response from Blender: {str(e)}")
            # Try to log what was received
            if 'response_data' in locals() and response_data:
                print(f"Raw response (first 200 bytes): {response_data[:200]}")
            raise Exception(f"Invalid response from Blender: {str(e)}")
        except Exception as e:
            print(f"Error communicating with Blender: {str(e)}")
            # Don't try to reconnect here - let the get_blender_connection handle reconnection
            self.sock = None
            raise Exception(f"Blender error: {str(e)}")

@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Manage server startup and shutdown lifecycle"""
    # We don't need to create a connection here since we're using the global connection
    # for resources and tools
    
    try:
        # Just log that we're starting up
        print("BlenderMCP server starting up")
        
        # Try to connect to Blender on startup to verify it's available
        try:
            # This will initialize the global connection if needed
            blender = get_blender_connection()
            print("Successfully connected to Blender on startup")
        except Exception as e:
            print(f"Could not connect to Blender on startup: {str(e)}")
            print("Make sure the Blender addon is running before using Blender resources or tools")
        
        # Return an empty context - we're using the global connection
        yield {}
    finally:
        # Clean up the global connection on shutdown
        global _blender_connection
        if _blender_connection:
            print("Disconnecting from Blender on shutdown")
            _blender_connection.disconnect()
            _blender_connection = None
        print("BlenderMCP server shut down")

def get_blender_connection():
    """Get or create a persistent Blender connection"""
    global _blender_connection
    
    # If we have an existing connection, check if it's still valid
    if _blender_connection is not None:
        try:
            result = _blender_connection.send_command("ping")
            return _blender_connection
        except Exception as e:
            print(f"Existing connection is no longer valid: {str(e)}")
            try:
                _blender_connection.disconnect()
            except:
                pass
            _blender_connection = None
    
    if _blender_connection is None:
        print("Creating new connection to Blender")
        _blender_connection = BlenderConnection(host="localhost", port=9876)
        if not _blender_connection.connect():
            print("Failed to connect to Blender")
            _blender_connection = None
            raise Exception("Could not connect to Blender. Make sure the Blender addon is running.")
        print("Created new persistent connection to Blender")
    
    return _blender_connection

def send_blender_command(command: str, params: Dict[str, Any] = None):
    try:
        blender = get_blender_connection()
        result = blender.send_command(command, params)
        
        return json.dumps(result)
    except Exception as e:
        return f"Error with command {command}: {str(e)}"


@mcp.tool()
def list_node_types(ctx: Context) -> str:
    """List all the available geometry node types in a category
    
    Parameters:
    - category: Any of [Hair, Material, Object, Texture, Utility]
    """

    if(node_data is None):
        load_node_data()

    return str(list(node_data.keys()))

@mcp.tool()
def get_node_type_info(ctx: Context, node_type: str) -> str:
    """Get detailed information about a specific geometry node type"""
    if(node_data is None):
        load_node_data()

    return json.dumps(node_data[node_type])

@mcp.tool()
def get_current_graph(ctx: Context) -> str:
    """see the current node graph"""
    return send_blender_command("get_current_graph")

@mcp.tool()
def add_node(ctx: Context, node_type: str, inputValues: Dict[str, Any]) -> str:
    """Add a node to the geometry nodes graph
    
    Parameters:
    - node_type: The type of node to add
    - inputValues: Dictionary of default values for the node inputs

    Returns:
    - New node id
    """
    if(not node_type in node_data.keys()):
        raise Exception(f"Node type {node_type} not found, use an exact key from the list of node types")

    return send_blender_command("add_node", {"node_type": node_type, "inputValues": inputValues})

@mcp.tool()
def set_node_values(ctx: Context, node_id: int, inputValues: Dict[str, Any]) -> str:
    """Set the values of a node
    Parameters:
    - node_id: The id of the node to set the values of
    - inputValues: Dictionary of default values for the node inputs
    """
    return send_blender_command("set_node_values", {"node_id": node_id, "inputValues": inputValues})

@mcp.tool()
def add_link(ctx: Context, from_node: int, from_socket: str, to_node: int, to_socket: str) -> str:
    """Add a link between two nodes
    Parameters:
    - from_node: The id of the node to link from
    - from_socket: The socket to link from
    - to_node: The id of the node to link to
    - to_socket: The socket to link to
    """
    return send_blender_command("add_link", {"from_node": from_node, "from_socket": from_socket, "to_node": to_node, "to_socket": to_socket})

@mcp.tool()
def get_node_state(ctx: Context, node_id: int) -> str:
    """Get the values and connections of a node in the graph
    Parameters:
    - node_id: The id of the node to get the values of
    """
    return send_blender_command("get_node_state", {"node_id": node_id})

@mcp.tool()
def get_current_graph(ctx: Context) -> str:
    """Get the current graph"""
    return send_blender_command("get_current_graph")

@mcp.tool()
def test_blender_connection(ctx: Context) -> str:
    """Test the Blender connection"""
    return get_blender_connection()

@mcp.tool()
def set_output_node(ctx: Context, node_id: int) -> str:
    """Set the output node
    Parameters:
    - node_id: The id of the node to set as the output node
    """
    return send_blender_command("set_output_node", {"node_id": node_id})

@mcp.tool()
def end_loop(ctx: Context) -> str:
    """End the loop"""
    return "trying to end the loop"

@mcp.tool()
def set_node_property(ctx: Context, node_id: int, name: Annotated[str, "non-input property to set. use get_node_type_info to see available properties"], value: any) -> str:
    return send_blender_command("set_node_property", {"node_id": node_id, "name": name, "value": value})

@mcp.tool()
def visually_evaluate_node(ctx: Context, node_id: int, expected_output_description: str) -> str:
    """Visually evaluate a node
    Parameters:
    - node_id: The id of the node to visually evaluate
    - expected_output_description: A description of the expected visual output of that node
    """
    blender_out = send_blender_command("visually_evaluate_node", {"node_id": node_id})
    # return "got blender out: " + blender_out

    blender_out = json.loads(blender_out)

    if not blender_out["status"] == "success":
        return blender_out
    
    filepath = blender_out["message"]
    # return "got filepath: " + filepath
    result = evaluate_image(filepath, expected_output_description)
    return result

def load_node_data():
    global node_data
    with open(data_filepath, "r") as f:
        node_data = json.load(f)

if __name__ == "__main__":
    load_node_data()
    get_blender_connection()
    mcp.run(transport='stdio')