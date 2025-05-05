# Code created by Siddharth Ahuja: www.github.com/ahujasid © 2025

import bpy
import mathutils
import json
import threading
import socket
import time
import requests
import tempfile
import traceback
import os
import shutil
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty
import io
from contextlib import redirect_stdout

bl_info = {
    "name": "Casey MCP",
    "author": "Casey",
    "version": (1, 2),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > CaseyMCP",
    "description": "Blender geo nodes mcp addon",
    "category": "Interface",
}

OBJECT_NAME = "Object"


class BlenderMCPServer:
    def __init__(self, host='localhost', port=9876):
        self.host = host
        self.port = port
        self.running = False
        self.socket = None
        self.server_thread = None
    
    def start(self):
        if self.running:
            print("Server is already running")
            return
            
        self.running = True
        
        try:
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(1)
            
            # Start server thread
            self.server_thread = threading.Thread(target=self._server_loop)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            print(f"BlenderMCP server started on {self.host}:{self.port}")
        except Exception as e:
            print(f"Failed to start server: {str(e)}")
            self.stop()
            
    def stop(self):
        self.running = False
        
        # Close socket
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        # Wait for thread to finish
        if self.server_thread:
            try:
                if self.server_thread.is_alive():
                    self.server_thread.join(timeout=1.0)
            except:
                pass
            self.server_thread = None
        
        print("BlenderMCP server stopped")
    
    def _server_loop(self):
        """Main server loop in a separate thread"""
        print("Server thread started")
        self.socket.settimeout(1.0)  # Timeout to allow for stopping
        
        while self.running:
            try:
                # Accept new connection
                try:
                    client, address = self.socket.accept()
                    print(f"Connected to client: {address}")
                    
                    # Handle client in a separate thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client,)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except socket.timeout:
                    # Just check running condition
                    continue
                except Exception as e:
                    print(f"Error accepting connection: {str(e)}")
                    time.sleep(0.5)
            except Exception as e:
                print(f"Error in server loop: {str(e)}")
                if not self.running:
                    break
                time.sleep(0.5)
        
        print("Server thread stopped")
    
    def _handle_client(self, client):
        """Handle connected client"""
        print("Client handler started")
        client.settimeout(None)  # No timeout
        buffer = b''
        
        try:
            while self.running:
                # Receive data
                try:
                    data = client.recv(8192)
                    if not data:
                        print("Client disconnected")
                        break
                    
                    buffer += data
                    try:
                        # Try to parse command
                        command = json.loads(buffer.decode('utf-8'))
                        buffer = b''
                        
                        # Execute command in Blender's main thread
                        def execute_wrapper():
                            try:
                                response = self.execute_command(command)
                                response_json = json.dumps(response)
                                try:
                                    client.sendall(response_json.encode('utf-8'))
                                except:
                                    print("Failed to send response - client disconnected")
                            except Exception as e:
                                print(f"Error executing command: {str(e)}")
                                traceback.print_exc()
                                try:
                                    error_response = {
                                        "status": "error",
                                        "message": str(e)
                                    }
                                    client.sendall(json.dumps(error_response).encode('utf-8'))
                                except:
                                    pass
                            return None
                        
                        # Schedule execution in main thread
                        bpy.app.timers.register(execute_wrapper, first_interval=0.0)
                    except json.JSONDecodeError:
                        # Incomplete data, wait for more
                        pass
                except Exception as e:
                    print(f"Error receiving data: {str(e)}")
                    break
        except Exception as e:
            print(f"Error in client handler: {str(e)}")
        finally:
            try:
                client.close()
            except:
                pass
            print("Client handler stopped")

    def execute_command(self, command):
        """Execute a command in the main Blender thread"""
        try:            
            return self._execute_command_internal(command)
                
        except Exception as e:
            print(f"Error executing command: {str(e)}")
            traceback.print_exc()
            return {"status": "error", "message": str(e)}

    def _execute_command_internal(self, command):
        """Internal command execution with proper context"""
        cmd_type = command.get("type")
        params = command.get("params", {})

        # Base handlers that are always available
        handlers = {
            "get_scene_info": self.get_scene_info,
            "get_object_info": self.get_object_info,
            "execute_code": self.execute_code,
            "ping": self.ping,
        }
        
        handler = handlers.get(cmd_type)
        if handler:
            try:
                print(f"Executing handler for {cmd_type}")
                result = handler(**params)
                print(f"Handler execution complete")
                return {"status": "success", "result": result}
            except Exception as e:
                print(f"Error in handler: {str(e)}")
                traceback.print_exc()
                return {"status": "error", "message": str(e)}
        else:
            return {"status": "error", "message": f"Unknown command type: {cmd_type}"}

    def add_node(self, node_type):
        new_node = node_group.nodes.new(node_type)
        new_node.location = (-340,80)
        return new_node

    def ping(self):
        return {"status": "success", "message": "Pong"}

# Blender UI Panel
class BLENDERMCP_PT_Panel(bpy.types.Panel):
    bl_label = "Casey MCP"
    bl_idname = "CASEYMCP_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CaseyMCP'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        layout.prop(scene, "blendermcp_port")

        if not scene.blendermcp_server_running:
            layout.operator("blendermcp.start_server", text="Connect to MCP server")
        else:
            layout.operator("blendermcp.stop_server", text="Disconnect from MCP server")
            layout.label(text=f"Running on port {scene.blendermcp_port}")

        layout.operator("blendermcp.initialize", text="Initialize")
        layout.operator("blendermcp.test", text="Test")

class BLENDERMCP_OT_StartServer(bpy.types.Operator):
    bl_idname = "blendermcp.start_server"
    bl_label = "Connect to Claude"
    bl_description = "Start the BlenderMCP server to connect with Claude"
    
    def execute(self, context):
        scene = context.scene
        
        # Create a new server instance
        if not hasattr(bpy.types, "blendermcp_server") or not bpy.types.blendermcp_server:
            bpy.types.blendermcp_server = BlenderMCPServer(port=scene.blendermcp_port)
        
        # Start the server
        bpy.types.blendermcp_server.start()
        scene.blendermcp_server_running = True
        
        return {'FINISHED'}

class BLENDERMCP_OT_Initialize(bpy.types.Operator):
    bl_idname = "blendermcp.initialize"
    bl_label = "Initialize"
    bl_description = "Initialize the blender scene"
    
    def execute(self, context):
        scene = context.scene

        collection = context.collection

        # removing all curent objects
        meshes = set()

        for obj in [o for o in collection.objects if o.type == 'MESH']:
            meshes.add( obj.data )
            bpy.data.objects.remove( obj )

        for mesh in [m for m in meshes if m.users == 0]:
            bpy.data.meshes.remove( mesh )

        for ob in context.selected_objects:
            ob.select_set(False)

        mesh = bpy.data.meshes.new(name="EmptyMesh")
        obj = bpy.data.objects.new(name=OBJECT_NAME, object_data=mesh)

        context.collection.objects.link(obj)

        obj.select_set(True)
        context.view_layer.objects.active = obj

        mod = obj.modifiers.new("Geo Node Modifier", type='NODES')
        node_group = bpy.data.node_groups.new("mcp nodes", type='GeometryNodeTree')
        node_group.interface.new_socket(name="Geo Out", in_out ="OUTPUT", socket_type="NodeSocketGeometry")

        node_in        = node_group.nodes.new("NodeGroupInput")
        node_transform = node_group.nodes.new("GeometryNodeTransform")
        node_out       = node_group.nodes.new("NodeGroupOutput")

        for node_type in node_types:
            node = node_group.nodes.new(node_type)
            print_node_data(node)

        node_group.links.new(node_in.outputs[0], node_transform.inputs[0])
        node_group.links.new(node_transform.outputs[0], node_out.inputs[0])

        node_transform.inputs["Translation"].default_value[2] = 1

        mod.node_group = node_group

        global geo_node_group
        geo_node_group = node_group

        return {'FINISHED'}

def print_node_data(node):
    nodeData = {}
    nodeData["inputs"] = []
    nodeData["outputs"] = []

    for i in range(len(node.inputs)):
        name = str(i) + ": " + str(node.inputs[i].name) + " [" + type(node.inputs[i]).__name__.replace("NodeSocket", "") + "]"
        nodeData["inputs"].append(name)

    for i in range(len(node.outputs)):
        name = str(i) + ": " + str(node.outputs[i].name) + " [" + type(node.outputs[i]).__name__.replace("NodeSocket", "") + "]"
        nodeData["outputs"].append(name)

    nodeData = {node.name: nodeData}

    print(json.dumps(nodeData))

class BLENDERMCP_OT_Test(bpy.types.Operator):
    bl_idname = "blendermcp.test"
    bl_label = "Test"
    bl_description = "Test operation"
    
    def execute(self, context):
        scene = context.scene

        # Create an empty mesh and object
        mesh = bpy.data.meshes.new(name="EmptyMesh")
        obj = bpy.data.objects.new(name=OBJECT_NAME, object_data=mesh)

        # Link the object to the active context's collection
        context.collection.objects.link(obj)

        # Deselect all objects in view layer
        for ob in context.selected_objects:
            ob.select_set(False)

        # Select and activate the new object
        obj.select_set(True)
        context.view_layer.objects.active = obj

        return {'FINISHED'}


class BLENDERMCP_OT_StopServer(bpy.types.Operator):
    bl_idname = "blendermcp.stop_server"
    bl_label = "Stop the connection to Claude"
    bl_description = "Stop the connection to Claude"
    
    def execute(self, context):
        scene = context.scene
        
        # Stop the server if it exists
        if hasattr(bpy.types, "blendermcp_server") and bpy.types.blendermcp_server:
            bpy.types.blendermcp_server.stop()
            del bpy.types.blendermcp_server
        
        scene.blendermcp_server_running = False
        
        return {'FINISHED'}


node_types = [
    "GeometryNodeAccumulateField",
    "GeometryNodeAttributeDomainSize",
    "GeometryNodeAttributeStatistic",
    "GeometryNodeBake",
    "GeometryNodeBlurAttribute",
    "GeometryNodeBoundBox",
    "GeometryNodeCaptureAttribute",
    "GeometryNodeCollectionInfo",
    "GeometryNodeConvexHull",
    "GeometryNodeCornersOfEdge",
    "GeometryNodeCornersOfFace",
    "GeometryNodeCornersOfVertex",
    "GeometryNodeCurveArc",
    "GeometryNodeCurveEndpointSelection",
    "GeometryNodeCurveHandleTypeSelection",
    "GeometryNodeCurveLength",
    "GeometryNodeCurveOfPoint",
    "GeometryNodeCurvePrimitiveBezierSegment",
    "GeometryNodeCurvePrimitiveCircle",
    "GeometryNodeCurvePrimitiveLine",
    "GeometryNodeCurvePrimitiveQuadrilateral",
    "GeometryNodeCurveQuadraticBezier",
    "GeometryNodeCurveSetHandles",
    "GeometryNodeCurveSpiral",
    "GeometryNodeCurveSplineType",
    "GeometryNodeCurveStar",
    "GeometryNodeCurveToMesh",
    "GeometryNodeCurveToPoints",
    "GeometryNodeCurvesToGreasePencil",
    "GeometryNodeDeformCurvesOnSurface",
    "GeometryNodeDeleteGeometry",
    "GeometryNodeDistributePointsInGrid",
    "GeometryNodeDistributePointsInVolume",
    "GeometryNodeDistributePointsOnFaces",
    "GeometryNodeDualMesh",
    "GeometryNodeDuplicateElements",
    "GeometryNodeEdgePathsToCurves",
    "GeometryNodeEdgePathsToSelection",
    "GeometryNodeEdgesOfCorner",
    "GeometryNodeEdgesOfVertex",
    "GeometryNodeEdgesToFaceGroups",
    "GeometryNodeExtrudeMesh",
    "GeometryNodeFaceOfCorner",
    "GeometryNodeFieldAtIndex",
    "GeometryNodeFieldOnDomain",
    "GeometryNodeFillCurve",
    "GeometryNodeFilletCurve",
    "GeometryNodeFlipFaces",
    "GeometryNodeForeachGeometryElementInput",
    "GeometryNodeForeachGeometryElementOutput",
    "GeometryNodeGeometryToInstance",
    "GeometryNodeGetNamedGrid",
    "GeometryNodeGizmoDial",
    "GeometryNodeGizmoLinear",
    "GeometryNodeGizmoTransform",
    "GeometryNodeGreasePencilToCurves",
    "GeometryNodeGridToMesh",
    "GeometryNodeGroup",
    "GeometryNodeImageInfo",
    "GeometryNodeImageTexture",
    "GeometryNodeImportOBJ",
    "GeometryNodeImportPLY",
    "GeometryNodeImportSTL",
    "GeometryNodeIndexOfNearest",
    "GeometryNodeIndexSwitch",
    "GeometryNodeInputActiveCamera",
    "GeometryNodeInputCollection",
    "GeometryNodeInputCurveHandlePositions",
    "GeometryNodeInputCurveTilt",
    "GeometryNodeInputEdgeSmooth",
    "GeometryNodeInputID",
    "GeometryNodeInputImage",
    "GeometryNodeInputIndex",
    "GeometryNodeInputInstanceRotation",
    "GeometryNodeInputInstanceScale",
    "GeometryNodeInputMaterial",
    "GeometryNodeInputMaterialIndex",
    "GeometryNodeInputMeshEdgeAngle",
    "GeometryNodeInputMeshEdgeNeighbors",
    "GeometryNodeInputMeshEdgeVertices",
    "GeometryNodeInputMeshFaceArea",
    "GeometryNodeInputMeshFaceIsPlanar",
    "GeometryNodeInputMeshFaceNeighbors",
    "GeometryNodeInputMeshIsland",
    "GeometryNodeInputMeshVertexNeighbors",
    "GeometryNodeInputNamedAttribute",
    "GeometryNodeInputNamedLayerSelection",
    "GeometryNodeInputNormal",
    "GeometryNodeInputObject",
    "GeometryNodeInputPosition",
    "GeometryNodeInputRadius",
    "GeometryNodeInputSceneTime",
    "GeometryNodeInputShadeSmooth",
    "GeometryNodeInputShortestEdgePaths",
    "GeometryNodeInputSplineCyclic",
    "GeometryNodeInputSplineResolution",
    "GeometryNodeInputTangent",
    "GeometryNodeInstanceOnPoints",
    "GeometryNodeInstanceTransform",
    "GeometryNodeInstancesToPoints",
    "GeometryNodeInterpolateCurves",
    "GeometryNodeIsViewport",
    "GeometryNodeJoinGeometry",
    "GeometryNodeMaterialSelection",
    "GeometryNodeMenuSwitch",
    "GeometryNodeMergeByDistance",
    "GeometryNodeMergeLayers",
    "GeometryNodeMeshBoolean",
    "GeometryNodeMeshCircle",
    "GeometryNodeMeshCone",
    "GeometryNodeMeshCube",
    "GeometryNodeMeshCylinder",
    "GeometryNodeMeshFaceSetBoundaries",
    "GeometryNodeMeshGrid",
    "GeometryNodeMeshIcoSphere",
    "GeometryNodeMeshLine",
    "GeometryNodeMeshToCurve",
    "GeometryNodeMeshToDensityGrid",
    "GeometryNodeMeshToPoints",
    "GeometryNodeMeshToSDFGrid",
    "GeometryNodeMeshToVolume",
    "GeometryNodeMeshUVSphere",
    "GeometryNodeObjectInfo",
    "GeometryNodeOffsetCornerInFace",
    "GeometryNodeOffsetPointInCurve",
    "GeometryNodePoints",
    "GeometryNodePointsOfCurve",
    "GeometryNodePointsToCurves",
    "GeometryNodePointsToSDFGrid",
    "GeometryNodePointsToVertices",
    "GeometryNodePointsToVolume",
    "GeometryNodeProximity",
    "GeometryNodeRaycast",
    "GeometryNodeRealizeInstances",
    "GeometryNodeRemoveAttribute",
    "GeometryNodeRepeatInput",
    "GeometryNodeRepeatOutput",
    "GeometryNodeReplaceMaterial",
    "GeometryNodeResampleCurve",
    "GeometryNodeReverseCurve",
    "GeometryNodeRotateInstances",
    "GeometryNodeSDFGridBoolean",
    "GeometryNodeSampleCurve",
    "GeometryNodeSampleGrid",
    "GeometryNodeSampleGridIndex",
    "GeometryNodeSampleIndex",
    "GeometryNodeSampleNearest",
    "GeometryNodeSampleNearestSurface",
    "GeometryNodeSampleUVSurface",
    "GeometryNodeScaleElements",
    "GeometryNodeScaleInstances",
    "GeometryNodeSelfObject",
    "GeometryNodeSeparateComponents",
    "GeometryNodeSeparateGeometry",
    "GeometryNodeSetCurveHandlePositions",
    "GeometryNodeSetCurveNormal",
    "GeometryNodeSetCurveRadius",
    "GeometryNodeSetCurveTilt",
    "GeometryNodeSetGeometryName",
    "GeometryNodeSetID",
    "GeometryNodeSetInstanceTransform",
    "GeometryNodeSetMaterial",
    "GeometryNodeSetMaterialIndex",
    "GeometryNodeSetPointRadius",
    "GeometryNodeSetPosition",
    "GeometryNodeSetShadeSmooth",
    "GeometryNodeSetSplineCyclic",
    "GeometryNodeSetSplineResolution",
    "GeometryNodeSimulationInput",
    "GeometryNodeSimulationOutput",
    "GeometryNodeSortElements",
    "GeometryNodeSplineLength",
    "GeometryNodeSplineParameter",
    "GeometryNodeSplitEdges",
    "GeometryNodeSplitToInstances",
    "GeometryNodeStoreNamedAttribute",
    "GeometryNodeStoreNamedGrid",
    "GeometryNodeStringJoin",
    "GeometryNodeStringToCurves",
    "GeometryNodeSubdivideCurve",
    "GeometryNodeSubdivideMesh",
    "GeometryNodeSubdivisionSurface",
    "GeometryNodeSwitch",
    "GeometryNodeTool3DCursor",
    "GeometryNodeToolActiveElement",
    "GeometryNodeToolFaceSet",
    "GeometryNodeToolMousePosition",
    "GeometryNodeToolSelection",
    "GeometryNodeToolSetFaceSet",
    "GeometryNodeToolSetSelection",
    "GeometryNodeTransform",
    "GeometryNodeTranslateInstances",
    "GeometryNodeTriangulate",
    "GeometryNodeTrimCurve",
    "GeometryNodeUVPackIslands",
    "GeometryNodeUVUnwrap",
    "GeometryNodeVertexOfCorner",
    "GeometryNodeViewer",
    "GeometryNodeViewportTransform",
    "GeometryNodeVolumeCube",
    "GeometryNodeVolumeToMesh",
]

# Registration functions
def register():
    bpy.types.Scene.blendermcp_port = IntProperty(
        name="Port",
        description="Port for the BlenderMCP server",
        default=9876,
        min=1024,
        max=65535
    )
    
    bpy.types.Scene.blendermcp_server_running = bpy.props.BoolProperty(
        name="Server Running",
        default=False
    )

    bpy.utils.register_class(BLENDERMCP_PT_Panel)
    bpy.utils.register_class(BLENDERMCP_OT_StartServer)
    bpy.utils.register_class(BLENDERMCP_OT_StopServer)
    bpy.utils.register_class(BLENDERMCP_OT_Initialize)
    bpy.utils.register_class(BLENDERMCP_OT_Test)
    print("CaseyMCP addon registered")

def unregister():
    # Stop the server if it's running
    if hasattr(bpy.types, "blendermcp_server") and bpy.types.blendermcp_server:
        bpy.types.blendermcp_server.stop()
        del bpy.types.blendermcp_server
    
    bpy.utils.unregister_class(BLENDERMCP_PT_Panel)
    bpy.utils.unregister_class(BLENDERMCP_OT_StartServer)
    bpy.utils.unregister_class(BLENDERMCP_OT_StopServer)
    bpy.utils.unregister_class(BLENDERMCP_OT_Initialize)
    bpy.utils.unregister_class(BLENDERMCP_OT_Test)

    del bpy.types.Scene.blendermcp_port
    del bpy.types.Scene.blendermcp_server_running

    print("CaseyMCP addon unregistered")


if __name__ == "__main__":
    register()

