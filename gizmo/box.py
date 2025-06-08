import bpy
import math
import mathutils
from mesh_from_sdf.pointer import *
from bpy.props import FloatVectorProperty
from bpy.types import Operator, GizmoGroup, PropertyGroup


class SDF2MESH_OT_Apply_Gizmo_To_SDF_Box(Operator):
    bl_idname = 'mesh_from_sdf.apply_gizmo_to_sdf_box'
    bl_label = 'Apply Gizmo to SDF Box'
    bl_description = 'Reflect Gizmo changes in SDFBoxProperty'
    
    def execute(self, context):
        global bound
        
        box_pointer = context.scene.sdf_box_pointer_list[context.object.sdf_prop.sub_index]
        box_pointer.bound = bound
        
        # Update mesh for primitive interactions
        prev_mode = SDFPrimitivePointer.update_primitive_mesh_begin(context)
        pointer = context.scene.sdf_object_pointer_list[context.object.sdf_prop.index]
        SDFBoxPointer.update_box_mesh(pointer)
        SDFPrimitivePointer.update_primitive_mesh_end(prev_mode)
        
        # Currently, each time Gizmo is updated, Undo is also recorded. Ideally, 
        # Undo should be performed when Gizmo is finished dragging.
        # bpy.ops.ed.undo_push(message='mesh_from_sdf.apply_gizmo_to_sdf_box')
        return {'FINISHED'}
    

global bound
bound = [1,1,1]


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
        
        global bound
        
        def move_get_bound_x():
            value = bpy.context.scene.sdf_box_pointer_list[context.object.sdf_prop.sub_index].bound[0]
            # Apparently, it is not possible to write a value to sdf_box_gizmo_prop in the setup function.
            # This function is called when an object is selected, so update the value of sdf_box_gizmo_prop here.
            bound[0] = max(0, value)
            return value

        def move_set_x(value):
            bound[0] = max(0, value)
            bpy.ops.mesh_from_sdf.apply_gizmo_to_sdf_box()
            
        def move_get_bound_y():
            value = bpy.context.scene.sdf_box_pointer_list[context.object.sdf_prop.sub_index].bound[1]
            bound[1] = max(0, value)
            return value

        def move_set_y(value):
            bound[1] = max(0, value)
            bpy.ops.mesh_from_sdf.apply_gizmo_to_sdf_box()
            
        def move_get_bound_z():
            value = bpy.context.scene.sdf_box_pointer_list[context.object.sdf_prop.sub_index].bound[2]
            bound[2] = max(0, value)
            return value

        def move_set_z(value):
            bound[2] = max(0, value)
            bpy.ops.mesh_from_sdf.apply_gizmo_to_sdf_box()

        ob = context.object
        scale_basis = 1 / ob.matrix_world.to_scale()[0]
        
        # When Gizmo is reselected, the setup function and the reflesh function 
        # are not called and the values registered in the first setup are used ?
        # pointer = bpy.context.scene.sdf_box_pointer_list[ob.sdf_prop.sub_index]
        # bound = pointer.bound
        
        # Gizmo X Axis
        gz_bound_x = self.gizmos.new("GIZMO_GT_arrow_3d")
        gz_bound_x.target_set_handler("offset", get=move_get_bound_x, set=move_set_x)
        gz_bound_x.matrix_basis = ob.matrix_world @ mathutils.Matrix.Rotation(math.radians(90.0), 4, 'Z')
        gz_bound_x.draw_style = 'BOX'
        gz_bound_x.length = 0.2
        gz_bound_x.scale_basis = scale_basis

        gz_bound_x.color = 1.0, 0.0, 0.0
        gz_bound_x.alpha = 0.5
        gz_bound_x.color_highlight = 1.0, 0.0, 1.0
        gz_bound_x.alpha_highlight = 0.25
        
        # Gizmo Y Axis
        gz_bound_y = self.gizmos.new("GIZMO_GT_arrow_3d")
        gz_bound_y.target_set_handler("offset", get=move_get_bound_y, set=move_set_y)
        gz_bound_y.matrix_basis = ob.matrix_world @ mathutils.Matrix.Rotation(math.radians(90.0), 4, 'Z')
        gz_bound_y.draw_style = 'BOX'
        gz_bound_y.length = 0.2
        gz_bound_y.scale_basis = scale_basis

        gz_bound_y.color = 0.0, 1.0, 0.0
        gz_bound_y.alpha = 0.5
        gz_bound_y.color_highlight = 0.0, 1.0, 0.0
        gz_bound_y.alpha_highlight = 0.25
        
        # Gizmo Z Axis
        gz_bound_z = self.gizmos.new("GIZMO_GT_arrow_3d")
        gz_bound_z.target_set_handler("offset", get=move_get_bound_z, set=move_set_z)
        gz_bound_z.matrix_basis = ob.matrix_world
        gz_bound_z.draw_style = 'BOX'
        gz_bound_z.length = 0.2
        gz_bound_z.scale_basis = scale_basis

        gz_bound_z.color = 0.0, 0.0, 1.0
        gz_bound_z.alpha = 0.5
        gz_bound_z.color_highlight = 0.0, 1.0, 1.0
        gz_bound_z.alpha_highlight = 0.25

        self.gizmo_bound_x = gz_bound_x
        self.gizmo_bound_y = gz_bound_y
        self.gizmo_bound_z = gz_bound_z

    def refresh(self, context):
        ob = context.object
        scale_basis = 1 / ob.matrix_world.to_scale()[0]
        
        gz_bound_x = self.gizmo_bound_x
        gz_bound_x.scale_basis = scale_basis
        gz_bound_x.matrix_basis = ob.matrix_world @ mathutils.Matrix.Rotation(math.radians(+90.0), 4, 'Y')
        
        gz_bound_y = self.gizmo_bound_y
        gz_bound_y.scale_basis = scale_basis
        gz_bound_y.matrix_basis = ob.matrix_world @ mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'X')
        
        gz_bound_z = self.gizmo_bound_z
        gz_bound_z.scale_basis = scale_basis
        gz_bound_z.matrix_basis = ob.matrix_world


classes = [
    SDF2MESH_OT_Apply_Gizmo_To_SDF_Box,
    SDFBoxWidgetGroup
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)