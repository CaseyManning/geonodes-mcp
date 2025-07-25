#from   https://docs.blender.org/api/current/bpy.types.GeometryNode.html
class GeoNode(Enum):
    AccumulateField = "GeometryNodeAccumulateField"
    AttributeDomainSize = "GeometryNodeAttributeDomainSize"
    AttributeStatistic = "GeometryNodeAttributeStatistic"
    Bake = "GeometryNodeBake"
    BlurAttribute = "GeometryNodeBlurAttribute"
    BoundBox = "GeometryNodeBoundBox"
    CaptureAttribute = "GeometryNodeCaptureAttribute"
    CollectionInfo = "GeometryNodeCollectionInfo"
    ConvexHull = "GeometryNodeConvexHull"
    CornersOfEdge = "GeometryNodeCornersOfEdge"
    CornersOfFace = "GeometryNodeCornersOfFace"
    CornersOfVertex = "GeometryNodeCornersOfVertex"
    CurveArc = "GeometryNodeCurveArc"
    CurveEndpointSelection = "GeometryNodeCurveEndpointSelection"
    CurveHandleTypeSelection = "GeometryNodeCurveHandleTypeSelection"
    CurveLength = "GeometryNodeCurveLength"
    CurveOfPoint = "GeometryNodeCurveOfPoint"
    CurvePrimitiveBezierSegment = "GeometryNodeCurvePrimitiveBezierSegment"
    CurvePrimitiveCircle = "GeometryNodeCurvePrimitiveCircle"
    CurvePrimitiveLine = "GeometryNodeCurvePrimitiveLine"
    CurvePrimitiveQuadrilateral = "GeometryNodeCurvePrimitiveQuadrilateral"
    CurveQuadraticBezier = "GeometryNodeCurveQuadraticBezier"
    CurveSetHandles = "GeometryNodeCurveSetHandles"
    CurveSpiral = "GeometryNodeCurveSpiral"
    CurveSplineType = "GeometryNodeCurveSplineType"
    CurveStar = "GeometryNodeCurveStar"
    CurveToMesh = "GeometryNodeCurveToMesh"
    CurveToPoints = "GeometryNodeCurveToPoints"
    CurvesToGreasePencil = "GeometryNodeCurvesToGreasePencil"
    CustomGroup = "GeometryNodeCustomGroup"
    DeformCurvesOnSurface = "GeometryNodeDeformCurvesOnSurface"
    DeleteGeometry = "GeometryNodeDeleteGeometry"
    DistributePointsInGrid = "GeometryNodeDistributePointsInGrid"
    DistributePointsInVolume = "GeometryNodeDistributePointsInVolume"
    DistributePointsOnFaces = "GeometryNodeDistributePointsOnFaces"
    DualMesh = "GeometryNodeDualMesh"
    DuplicateElements = "GeometryNodeDuplicateElements"
    EdgePathsToCurves = "GeometryNodeEdgePathsToCurves"
    EdgePathsToSelection = "GeometryNodeEdgePathsToSelection"
    EdgesOfCorner = "GeometryNodeEdgesOfCorner"
    EdgesOfVertex = "GeometryNodeEdgesOfVertex"
    EdgesToFaceGroups = "GeometryNodeEdgesToFaceGroups"
    ExtrudeMesh = "GeometryNodeExtrudeMesh"
    FaceOfCorner = "GeometryNodeFaceOfCorner"
    FieldAtIndex = "GeometryNodeFieldAtIndex"
    FieldOnDomain = "GeometryNodeFieldOnDomain"
    FillCurve = "GeometryNodeFillCurve"
    FilletCurve = "GeometryNodeFilletCurve"
    FlipFaces = "GeometryNodeFlipFaces"
    ForeachGeometryElementInput = "GeometryNodeForeachGeometryElementInput"
    ForeachGeometryElementOutput = "GeometryNodeForeachGeometryElementOutput"
    GeometryToInstance = "GeometryNodeGeometryToInstance"
    GetNamedGrid = "GeometryNodeGetNamedGrid"
    GizmoDial = "GeometryNodeGizmoDial"
    GizmoLinear = "GeometryNodeGizmoLinear"
    GizmoTransform = "GeometryNodeGizmoTransform"
    GreasePencilToCurves = "GeometryNodeGreasePencilToCurves"
    GridToMesh = "GeometryNodeGridToMesh"
    Group = "GeometryNodeGroup"
    ImageInfo = "GeometryNodeImageInfo"
    ImageTexture = "GeometryNodeImageTexture"
    ImportOBJ = "GeometryNodeImportOBJ"
    ImportPLY = "GeometryNodeImportPLY"
    ImportSTL = "GeometryNodeImportSTL"
    IndexOfNearest = "GeometryNodeIndexOfNearest"
    IndexSwitch = "GeometryNodeIndexSwitch"
    InputActiveCamera = "GeometryNodeInputActiveCamera"
    InputCollection = "GeometryNodeInputCollection"
    InputCurveHandlePositions = "GeometryNodeInputCurveHandlePositions"
    InputCurveTilt = "GeometryNodeInputCurveTilt"
    InputEdgeSmooth = "GeometryNodeInputEdgeSmooth"
    InputID = "GeometryNodeInputID"
    InputImage = "GeometryNodeInputImage"
    InputIndex = "GeometryNodeInputIndex"
    InputInstanceRotation = "GeometryNodeInputInstanceRotation"
    InputInstanceScale = "GeometryNodeInputInstanceScale"
    InputMaterial = "GeometryNodeInputMaterial"
    InputMaterialIndex = "GeometryNodeInputMaterialIndex"
    InputMeshEdgeAngle = "GeometryNodeInputMeshEdgeAngle"
    InputMeshEdgeNeighbors = "GeometryNodeInputMeshEdgeNeighbors"
    InputMeshEdgeVertices = "GeometryNodeInputMeshEdgeVertices"
    InputMeshFaceArea = "GeometryNodeInputMeshFaceArea"
    InputMeshFaceIsPlanar = "GeometryNodeInputMeshFaceIsPlanar"
    InputMeshFaceNeighbors = "GeometryNodeInputMeshFaceNeighbors"
    InputMeshIsland = "GeometryNodeInputMeshIsland"
    InputMeshVertexNeighbors = "GeometryNodeInputMeshVertexNeighbors"
    InputNamedAttribute = "GeometryNodeInputNamedAttribute"
    InputNamedLayerSelection = "GeometryNodeInputNamedLayerSelection"
    InputNormal = "GeometryNodeInputNormal"
    InputObject = "GeometryNodeInputObject"
    InputPosition = "GeometryNodeInputPosition"
    InputRadius = "GeometryNodeInputRadius"
    InputSceneTime = "GeometryNodeInputSceneTime"
    InputShadeSmooth = "GeometryNodeInputShadeSmooth"
    InputShortestEdgePaths = "GeometryNodeInputShortestEdgePaths"
    InputSplineCyclic = "GeometryNodeInputSplineCyclic"
    InputSplineResolution = "GeometryNodeInputSplineResolution"
    InputTangent = "GeometryNodeInputTangent"
    InstanceOnPoints = "GeometryNodeInstanceOnPoints"
    InstanceTransform = "GeometryNodeInstanceTransform"
    InstancesToPoints = "GeometryNodeInstancesToPoints"
    InterpolateCurves = "GeometryNodeInterpolateCurves"
    IsViewport = "GeometryNodeIsViewport"
    JoinGeometry = "GeometryNodeJoinGeometry"
    MaterialSelection = "GeometryNodeMaterialSelection"
    MenuSwitch = "GeometryNodeMenuSwitch"
    MergeByDistance = "GeometryNodeMergeByDistance"
    MergeLayers = "GeometryNodeMergeLayers"
    MeshBoolean = "GeometryNodeMeshBoolean"
    MeshCircle = "GeometryNodeMeshCircle"
    MeshCone = "GeometryNodeMeshCone"
    MeshCube = "GeometryNodeMeshCube"
    MeshCylinder = "GeometryNodeMeshCylinder"
    MeshFaceSetBoundaries = "GeometryNodeMeshFaceSetBoundaries"
    MeshGrid = "GeometryNodeMeshGrid"
    MeshIcoSphere = "GeometryNodeMeshIcoSphere"
    MeshLine = "GeometryNodeMeshLine"
    MeshToCurve = "GeometryNodeMeshToCurve"
    MeshToDensityGrid = "GeometryNodeMeshToDensityGrid"
    MeshToPoints = "GeometryNodeMeshToPoints"
    MeshToSDFGrid = "GeometryNodeMeshToSDFGrid"
    MeshToVolume = "GeometryNodeMeshToVolume"
    MeshUVSphere = "GeometryNodeMeshUVSphere"
    ObjectInfo = "GeometryNodeObjectInfo"
    OffsetCornerInFace = "GeometryNodeOffsetCornerInFace"
    OffsetPointInCurve = "GeometryNodeOffsetPointInCurve"
    Points = "GeometryNodePoints"
    PointsOfCurve = "GeometryNodePointsOfCurve"
    PointsToCurves = "GeometryNodePointsToCurves"
    PointsToSDFGrid = "GeometryNodePointsToSDFGrid"
    PointsToVertices = "GeometryNodePointsToVertices"
    PointsToVolume = "GeometryNodePointsToVolume"
    Proximity = "GeometryNodeProximity"
    Raycast = "GeometryNodeRaycast"
    RealizeInstances = "GeometryNodeRealizeInstances"
    RemoveAttribute = "GeometryNodeRemoveAttribute"
    RepeatInput = "GeometryNodeRepeatInput"
    RepeatOutput = "GeometryNodeRepeatOutput"
    ReplaceMaterial = "GeometryNodeReplaceMaterial"
    ResampleCurve = "GeometryNodeResampleCurve"
    ReverseCurve = "GeometryNodeReverseCurve"
    RotateInstances = "GeometryNodeRotateInstances"
    SDFGridBoolean = "GeometryNodeSDFGridBoolean"
    SampleCurve = "GeometryNodeSampleCurve"
    SampleGrid = "GeometryNodeSampleGrid"
    SampleGridIndex = "GeometryNodeSampleGridIndex"
    SampleIndex = "GeometryNodeSampleIndex"
    SampleNearest = "GeometryNodeSampleNearest"
    SampleNearestSurface = "GeometryNodeSampleNearestSurface"
    SampleUVSurface = "GeometryNodeSampleUVSurface"
    ScaleElements = "GeometryNodeScaleElements"
    ScaleInstances = "GeometryNodeScaleInstances"
    SelfObject = "GeometryNodeSelfObject"
    SeparateComponents = "GeometryNodeSeparateComponents"
    SeparateGeometry = "GeometryNodeSeparateGeometry"
    SetCurveHandlePositions = "GeometryNodeSetCurveHandlePositions"
    SetCurveNormal = "GeometryNodeSetCurveNormal"
    SetCurveRadius = "GeometryNodeSetCurveRadius"
    SetCurveTilt = "GeometryNodeSetCurveTilt"
    SetGeometryName = "GeometryNodeSetGeometryName"
    SetID = "GeometryNodeSetID"
    SetInstanceTransform = "GeometryNodeSetInstanceTransform"
    SetMaterial = "GeometryNodeSetMaterial"
    SetMaterialIndex = "GeometryNodeSetMaterialIndex"
    SetPointRadius = "GeometryNodeSetPointRadius"
    SetPosition = "GeometryNodeSetPosition"
    SetShadeSmooth = "GeometryNodeSetShadeSmooth"
    SetSplineCyclic = "GeometryNodeSetSplineCyclic"
    SetSplineResolution = "GeometryNodeSetSplineResolution"
    SimulationInput = "GeometryNodeSimulationInput"
    SimulationOutput = "GeometryNodeSimulationOutput"
    SortElements = "GeometryNodeSortElements"
    SplineLength = "GeometryNodeSplineLength"
    SplineParameter = "GeometryNodeSplineParameter"
    SplitEdges = "GeometryNodeSplitEdges"
    SplitToInstances = "GeometryNodeSplitToInstances"
    StoreNamedAttribute = "GeometryNodeStoreNamedAttribute"
    StoreNamedGrid = "GeometryNodeStoreNamedGrid"
    StringJoin = "GeometryNodeStringJoin"
    StringToCurves = "GeometryNodeStringToCurves"
    SubdivideCurve = "GeometryNodeSubdivideCurve"
    SubdivideMesh = "GeometryNodeSubdivideMesh"
    SubdivisionSurface = "GeometryNodeSubdivisionSurface"
    Switch = "GeometryNodeSwitch"
    Tool3DCursor = "GeometryNodeTool3DCursor"
    ToolActiveElement = "GeometryNodeToolActiveElement"
    ToolFaceSet = "GeometryNodeToolFaceSet"
    ToolMousePosition = "GeometryNodeToolMousePosition"
    ToolSelection = "GeometryNodeToolSelection"
    ToolSetFaceSet = "GeometryNodeToolSetFaceSet"
    ToolSetSelection = "GeometryNodeToolSetSelection"
    Transform = "GeometryNodeTransform"
    TranslateInstances = "GeometryNodeTranslateInstances"
    Triangulate = "GeometryNodeTriangulate"
    TrimCurve = "GeometryNodeTrimCurve"
    UVPackIslands = "GeometryNodeUVPackIslands"
    UVUnwrap = "GeometryNodeUVUnwrap"
    VertexOfCorner = "GeometryNodeVertexOfCorner"
    Viewer = "GeometryNodeViewer"
    ViewportTransform = "GeometryNodeViewportTransform"
    VolumeCube = "GeometryNodeVolumeCube"
    VolumeToMesh = "GeometryNodeVolumeToMesh"
    Warning = "GeometryNodeWarning"


node_inputs = {
    
}
node_outputs = {

}