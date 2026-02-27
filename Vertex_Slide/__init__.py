
bl_info = {
    "name": "Vertex slide",
    "author": "Ung Choi",
    "version": (1, 5),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Vertex Slide",
    "description": "Slide vertices along a marked edge direction",
    "category": "Mesh",
}

import bpy
import bmesh
from bpy.props import FloatVectorProperty, FloatProperty

# scene 속성 보장
def ensure_scene_props():
    if not hasattr(bpy.types.Scene, "marked_edge_vector"):
        bpy.types.Scene.marked_edge_vector = FloatVectorProperty(
            name="Marked Edge Vector",
            size=3,
            default=(0.0, 0.0, 0.0)
        )

def store_edge_vector(context, vec):
    context.scene.marked_edge_vector = vec[:]

def get_edge_vector(context):
    return context.scene.marked_edge_vector[:]

class MESH_OT_mark_edge(bpy.types.Operator):
    bl_idname = "mesh.mark_edge_for_slide"
    bl_label = "Mark Edge for Slide"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        edges = [e for e in bm.edges if e.select]

        if len(edges) != 1:
            self.report({'WARNING'}, "Exactly one edge must be selected")
            return {'CANCELLED'}

        edge = edges[0]
        v1, v2 = edge.verts[0].co, edge.verts[1].co
        edge_vec = (v2 - v1).normalized()
        store_edge_vector(context, edge_vec)
        self.report({'INFO'}, "Edge direction stored")
        return {'FINISHED'}

class MESH_OT_slide_vertices(bpy.types.Operator):
    bl_idname = "mesh.slide_vertices_along_marked_edge"
    bl_label = "Slide Vertices Along Marked Edge"
    bl_options = {'REGISTER', 'UNDO'}

    distance: FloatProperty(name="Distance", default=0.0)

    def invoke(self, context, event):
        self.distance = 0.0  # 항상 기본값으로 초기화
        return self.execute(context)

    def execute(self, context):
        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        edge_vec = get_edge_vector(context)

        if edge_vec == (0.0, 0.0, 0.0):
            self.report({'WARNING'}, "No edge vector stored")
            return {'CANCELLED'}

        move_vec = [v * self.distance for v in edge_vec]
        for v in bm.verts:
            if v.select:
                v.co.x += move_vec[0]
                v.co.y += move_vec[1]
                v.co.z += move_vec[2]

        bmesh.update_edit_mesh(obj.data)
        return {'FINISHED'}

class VIEW3D_PT_vertex_slide(bpy.types.Panel):
    bl_label = "Vertex Slide Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Vertex Slide'

    def draw(self, context):
        layout = self.layout
        layout.operator("mesh.mark_edge_for_slide", text="1. Mark Edge")
        layout.operator("mesh.slide_vertices_along_marked_edge", text="2. Slide Vertices")

classes = (
    MESH_OT_mark_edge,
    MESH_OT_slide_vertices,
    VIEW3D_PT_vertex_slide,
)

def register():
    ensure_scene_props()
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
