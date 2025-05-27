import bpy
import math
import mathutils
from bpy.props import FloatVectorProperty
from bpy.types import Operator, GizmoGroup, PropertyGroup


class SDF2MESH_OT_Apply_Gizmo_To_SDF_Box(Operator):
    bl_idname = 'mesh_from_sdf.apply_gizmo_to_sdf_box'
    bl_label = 'Apply Gizmo to SDF Box'
    bl_description = 'Reflect Gizmo changes in SDFBoxProperty'
    
    def execute(self, context):
        context.scene.sdf_box_gizmo_prop_out.bound = context.scene.sdf_box_gizmo_prop.bound
        
        # Currently, each time Gizmo is updated, Undo is also recorded. Ideally, 
        # Undo should be performed when Gizmo is finished dragging.
        bpy.ops.ed.undo_push(message='mesh_from_sdf.apply_gizmo_to_sdf_box')
        return {'FINISHED'}
    
    
class SDFBoxGizmoProperty(PropertyGroup):
    
    bound: bpy.props.FloatVectorProperty(
        name='Bound',
        description='Lengths of the three sides of a cube',
        size=3,
        default=(0,0,0))


class SDFBoxWidgetGroup(GizmoGroup):
    bl_idname = "OBJECT_GGT_sdf_box"
    bl_label = "SDF Box Widget"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT'}

    @classmethod
    def poll(cls, context):
        return context.object and context.object.sdf_prop.enabled and (context.object.sdf_prop.primitive_type == 'Box')

    def setup(self, context):
        
        def move_get_x():
            return bpy.context.scene.sdf_box_gizmo_prop_out.bound[0]

        def move_set_x(value):
            bpy.context.scene.sdf_box_gizmo_prop.bound[0] = value
            bpy.ops.mesh_from_sdf.apply_gizmo_to_sdf_box()
            
        def move_get_y():
            return bpy.context.scene.sdf_box_gizmo_prop_out.bound[1]

        def move_set_y(value):
            bpy.context.scene.sdf_box_gizmo_prop.bound[1] = value
            bpy.ops.mesh_from_sdf.apply_gizmo_to_sdf_box()
            
        def move_get_z():
            return bpy.context.scene.sdf_box_gizmo_prop_out.bound[2]

        def move_set_z(value):
            bpy.context.scene.sdf_box_gizmo_prop.bound[2] = value
            bpy.ops.mesh_from_sdf.apply_gizmo_to_sdf_box()

        ob = context.object
        
        # Gizmo X Axis
        gz_x = self.gizmos.new("GIZMO_GT_arrow_3d")
        gz_x.target_set_handler("offset", get=move_get_x, set=move_set_x)
        gz_x.matrix_offset = mathutils.Matrix.Translation((1, 0, 0))
        gz_x.matrix_basis = ob.matrix_world
        gz_x.matrix_basis = gz_x.matrix_basis @ mathutils.Matrix.Rotation(math.radians(90.0), 4, 'Z')
        gz_x.draw_style = 'BOX'
        gz_x.length = 0.2

        gz_x.color = 1.0, 0.0, 0.0
        gz_x.alpha = 0.5
        gz_x.color_highlight = 1.0, 0.0, 1.0
        gz_x.alpha_highlight = 0.25
        
        # Gizmo Y Axis
        gz_y = self.gizmos.new("GIZMO_GT_arrow_3d")
        gz_y.target_set_handler("offset", get=move_get_y, set=move_set_y)
        gz_y.matrix_offset = mathutils.Matrix.Translation((0, 0, 1))
        gz_y.matrix_basis = ob.matrix_world
        gz_y.matrix_basis = gz_y.matrix_basis @ mathutils.Matrix.Rotation(math.radians(90.0), 4, 'Z')
        gz_y.draw_style = 'BOX'
        gz_y.length = 0.2

        gz_y.color = 0.0, 1.0, 0.0
        gz_y.alpha = 0.5
        gz_y.color_highlight = 0.0, 1.0, 0.0
        gz_y.alpha_highlight = 0.25
        
        # Gizmo Z Axis
        gz_z = self.gizmos.new("GIZMO_GT_arrow_3d")
        gz_z.target_set_handler("offset", get=move_get_z, set=move_set_z)
        gz_z.matrix_offset = mathutils.Matrix.Translation((0, 0, 1))
        gz_z.matrix_basis = ob.matrix_world
        gz_z.matrix_basis = gz_y.matrix_basis
        gz_z.draw_style = 'BOX'
        gz_z.length = 0.2

        gz_z.color = 0.0, 0.0, 1.0
        gz_z.alpha = 0.5
        gz_z.color_highlight = 0.0, 1.0, 1.0
        gz_z.alpha_highlight = 0.25

        self.gizmo_x = gz_x
        self.gizmo_y = gz_y
        self.gizmo_z = gz_z

    def refresh(self, context):
        ob = context.object
        
        gz_x = self.gizmo_x
        gz_x.matrix_offset = mathutils.Matrix.Translation((0, 0, 1))
        gz_x.matrix_basis = ob.matrix_world
        gz_x.matrix_basis = gz_x.matrix_basis @ mathutils.Matrix.Rotation(math.radians(+90.0), 4, 'Y')
        
        gz_y = self.gizmo_y
        gz_y.matrix_offset = mathutils.Matrix.Translation((0, 0, 1))
        gz_y.matrix_basis = ob.matrix_world
        gz_y.matrix_basis = gz_y.matrix_basis @ mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'X')
        
        gz_z = self.gizmo_z
        gz_z.matrix_offset = mathutils.Matrix.Translation((0, 0, 1))
        gz_z.matrix_basis = ob.matrix_world
        gz_z.matrix_basis = gz_z.matrix_basis


classes = [
    SDF2MESH_OT_Apply_Gizmo_To_SDF_Box,
    SDFBoxGizmoProperty,
    SDFBoxWidgetGroup
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.sdf_box_gizmo_prop = bpy.props.PointerProperty(type=SDFBoxGizmoProperty)
    bpy.types.Scene.sdf_box_gizmo_prop_out = bpy.props.PointerProperty(type=SDFBoxGizmoProperty)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)