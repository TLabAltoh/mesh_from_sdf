import bpy
import math
import mathutils
from mesh_from_sdf.pointer import *
from bpy.props import FloatVectorProperty
from bpy.types import Operator, GizmoGroup, PropertyGroup


class SDF2MESH_OT_Apply_Gizmo_To_SDF_Cylinder(Operator):
    bl_idname = 'mesh_from_sdf.apply_gizmo_to_sdf_cylinder'
    bl_label = 'Apply Gizmo to SDF Cylinder'
    bl_description = 'Reflect Gizmo changes in SDFCylinderProperty'
    
    def execute(self, context):
        global height, radius
        cylinder_pointer = context.scene.sdf_cylinder_pointer_list[context.object.sdf_prop.sub_index]
        cylinder_pointer.height = height * 2.0
        cylinder_pointer.radius = radius
        
        # Update mesh for primitive interactions
        prev_mode = SDFPrimitivePointer.update_primitive_mesh_begin(context)
        pointer = context.scene.sdf_object_pointer_list[context.object.sdf_prop.index]
        SDFCylinderPointer.update_cylinder_mesh(pointer)
        SDFPrimitivePointer.update_primitive_mesh_end(prev_mode)
        
        # Currently, each time Gizmo is updated, Undo is also recorded. Ideally, 
        # Undo should be performed when Gizmo is finished dragging.
        # bpy.ops.ed.undo_push(message='mesh_from_sdf.apply_gizmo_to_sdf_cylinder')
        return {'FINISHED'}
    

global height, radius
height = 0.5
radius = 1.0


class SDFCylinderWidgetGroup(GizmoGroup):
    bl_idname = "OBJECT_GGT_sdf_cylinder"
    bl_label = "SDF Cylinder Widget"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT'}

    @classmethod
    def poll(cls, context):
        return context.object and context.object.sdf_prop.enabled and (context.object.sdf_prop.primitive_type == 'Cylinder')

    def setup(self, context):
        
        global height, radius
        
        def move_get_height():
            global height
            value = bpy.context.scene.sdf_cylinder_pointer_list[context.object.sdf_prop.sub_index].height * 0.5
            # Apparently, it is not possible to write a value to sdf_cylinder_gizmo_prop in the setup function.
            # This function is called when an object is selected, so update the value of sdf_cylinder_gizmo_prop here.
            height = max(0, value)
            return value

        def move_set_height(value):
            global height
            height = max(0, value)
            bpy.ops.mesh_from_sdf.apply_gizmo_to_sdf_cylinder()
            
        def move_get_radius():
            global radius
            value = bpy.context.scene.sdf_cylinder_pointer_list[context.object.sdf_prop.sub_index].radius
            radius = max(0, value)
            return value

        def move_set_radius(value):
            global radius
            radius = max(0, value)
            bpy.ops.mesh_from_sdf.apply_gizmo_to_sdf_cylinder()

        ob = context.object
        scale_basis = 1.0 / ob.matrix_world.to_scale()[0]
        
#        pointer = bpy.context.scene.sdf_cylinder_pointer_list[ob.sdf_prop.sub_index]
#        height = pointer.height * 0.5
#        radius = pointer.radius
        
        # Gizmo Height
        gz_height = self.gizmos.new("GIZMO_GT_arrow_3d")
        gz_height.target_set_handler("offset", get=move_get_height, set=move_set_height)
        gz_height.matrix_basis = ob.matrix_world
        gz_height.draw_style = 'BOX'
        gz_height.length = 0.2
        gz_height.scale_basis = scale_basis

        gz_height.color = 0.0, 0.0, 1.0
        gz_height.alpha = 0.5
        gz_height.color_highlight = 1.0, 0.0, 1.0
        gz_height.alpha_highlight = 0.25
        
        # Gizmo Radius
        gz_radius = self.gizmos.new("GIZMO_GT_arrow_3d")
        gz_radius.target_set_handler("offset", get=move_get_radius, set=move_set_radius)
        gz_radius.matrix_basis = ob.matrix_world @ mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'X')
        gz_radius.draw_style = 'BOX'
        gz_radius.length = 0.2
        gz_radius.scale_basis = scale_basis

        gz_radius.color = 0.0, 1.0, 0.0
        gz_radius.alpha = 0.5
        gz_radius.color_highlight = 0.0, 1.0, 0.0
        gz_radius.alpha_highlight = 0.25

        self.gizmo_height = gz_height
        self.gizmo_radius = gz_radius

    def refresh(self, context):
        ob = context.object
        scale_basis = 1.0 / ob.matrix_world.to_scale()[0]
        
        gz_height = self.gizmo_height
        gz_height.scale_basis = scale_basis
        gz_height.matrix_basis = ob.matrix_world
        
        gz_radius = self.gizmo_radius
        gz_radius.scale_basis = scale_basis
        gz_radius.matrix_basis = ob.matrix_world @ mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'X')


classes = [
    SDF2MESH_OT_Apply_Gizmo_To_SDF_Cylinder,
    SDFCylinderWidgetGroup
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)