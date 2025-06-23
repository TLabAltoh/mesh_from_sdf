import bpy
import math
import mathutils
from mesh_from_sdf.pointer import *
from bpy.props import FloatVectorProperty
from bpy.types import Operator, GizmoGroup, PropertyGroup


class SDF2MESH_OT_Apply_Gizmo_To_SDF_Quadratic_Bezier(Operator):
    bl_idname = 'mesh_from_sdf.apply_gizmo_to_sdf_quadratic_bezier'
    bl_label = 'Apply Gizmo to SDF Quadratic Bezier'
    bl_description = 'Reflect Gizmo changes in SDFQuadraticBezierProperty'
    
    def execute(self, context):
        global point_0, point_1, point_2
        
        quadratic_bezier_pointer = context.scene.sdf_quadratic_bezier_pointer_list[context.object.sdf_prop.sub_index]
        quadratic_bezier_pointer.point_0 = point_0
        quadratic_bezier_pointer.point_1 = point_1
        quadratic_bezier_pointer.point_2 = point_2
        
        # Update mesh for primitive interactions
        prev_mode = SDFPrimitivePointer.update_primitive_mesh_begin(context)
        pointer = context.scene.sdf_object_pointer_list[context.object.sdf_prop.index]
        SDFQuadraticBezierPointer.update_quadratic_bezier_mesh(pointer)
        SDFPrimitivePointer.update_primitive_mesh_end(prev_mode)
        
        # Currently, each time Gizmo is updated, Undo is also recorded. Ideally, 
        # Undo should be performed when Gizmo is finished dragging.
        # bpy.ops.ed.undo_push(message='mesh_from_sdf.apply_gizmo_to_sdf_quadratic_bezier')
        return {'FINISHED'}
    

global point_0, point_1, point_2
point_0 = [-1,0,0]
point_1 = [+0,0,0]
point_2 = [+1,0,0]


class SDFQuadraticBezierWidgetGroup(GizmoGroup):
    bl_idname = "OBJECT_GGT_sdf_quadratic_bezier"
    bl_label = "SDF Quadratic Bezier Widget"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT'}

    @classmethod
    def poll(cls, context):
        return context.object and context.object.sdf_prop.enabled and (context.object.sdf_prop.primitive_type == 'Quadratic Bezier')

    def setup(self, context):
        
        global point_0, point_1, point_2
        
        def move_get_point_0():
            value = bpy.context.scene.sdf_quadratic_bezier_pointer_list[context.object.sdf_prop.sub_index].point_0
            # Apparently, it is not possible to write a value to sdf_quadratic_bezier_gizmo_prop in the setup function.
            # This function is called when an object is selected, so update the value of sdf_quadratic_bezier_gizmo_prop here.
            point_0[0] = value[0]
            point_0[1] = value[1]
            point_0[2] = value[2]
            return value

        def move_point_0(value):
            point_0[0] = value[0]
            point_0[1] = value[1]
            point_0[2] = value[2]
            bpy.ops.mesh_from_sdf.apply_gizmo_to_sdf_quadratic_bezier()
            
        def move_get_point_1():
            value = bpy.context.scene.sdf_quadratic_bezier_pointer_list[context.object.sdf_prop.sub_index].point_1
            point_1[0] = value[0]
            point_1[1] = value[1]
            point_1[2] = value[2]
            return value

        def move_point_1(value):
            point_1[0] = value[0]
            point_1[1] = value[1]
            point_1[2] = value[2]
            bpy.ops.mesh_from_sdf.apply_gizmo_to_sdf_quadratic_bezier()
            
        def move_get_point_2():
            value = bpy.context.scene.sdf_quadratic_bezier_pointer_list[context.object.sdf_prop.sub_index].point_2
            point_2[0] = value[0]
            point_2[1] = value[1]
            point_2[2] = value[2]
            return value

        def move_point_2(value):
            point_2[0] = value[0]
            point_2[1] = value[1]
            point_2[2] = value[2]
            bpy.ops.mesh_from_sdf.apply_gizmo_to_sdf_quadratic_bezier()

        ob = context.object
        scale_basis = 0.25 * 1 / ob.matrix_world.to_scale()[0]
        
        # When Gizmo is reselected, the setup function and the reflesh function 
        # are not called and the values registered in the first setup are used ?
        # pointer = bpy.context.scene.sdf_quadratic_bezier_pointer_list[ob.sdf_prop.sub_index]
        # point_0 = pointer.point_0
        # point_1 = pointer.point_1
        # point_2 = pointer.point_2
        
        color_select = context.preferences.themes[0].view_3d.object_selected
        color_active = context.preferences.themes[0].view_3d.object_active
        
        # Gizmo Point 0
        gz_point_0 = self.gizmos.new("GIZMO_GT_move_3d")
        gz_point_0.target_set_handler("offset", get=move_get_point_0, set=move_point_0)
        gz_point_0.matrix_basis = ob.matrix_world
        gz_point_0.line_width = 3.0
        gz_point_0.scale_basis = scale_basis

        gz_point_0.color = color_active
        gz_point_0.alpha = 0.5
        gz_point_0.color_highlight = color_select
        gz_point_0.alpha_highlight = 0.25
        
        # Gizmo Y Axis
        gz_point_1 = self.gizmos.new("GIZMO_GT_move_3d")
        gz_point_1.target_set_handler("offset", get=move_get_point_1, set=move_point_1)
        gz_point_1.matrix_basis = ob.matrix_world
        gz_point_1.line_width = 3.0
        gz_point_1.scale_basis = scale_basis

        gz_point_1.color = color_active
        gz_point_1.alpha = 0.5
        gz_point_1.color_highlight = color_select
        gz_point_1.alpha_highlight = 0.25
        
        # Gizmo Z Axis
        gz_point_2 = self.gizmos.new("GIZMO_GT_move_3d")
        gz_point_2.target_set_handler("offset", get=move_get_point_2, set=move_point_2)
        gz_point_2.matrix_basis = ob.matrix_world
        gz_point_2.line_width = 3.0
        gz_point_2.scale_basis = scale_basis

        gz_point_2.color = color_active
        gz_point_2.alpha = 0.5
        gz_point_2.color_highlight = color_select
        gz_point_2.alpha_highlight = 0.25

        self.gizmo_point_0 = gz_point_0
        self.gizmo_point_1 = gz_point_1
        self.gizmo_point_2 = gz_point_2

    def refresh(self, context):
        ob = context.object
        
        scale_basis = 0.25 * 1 / ob.matrix_world.to_scale()[0]
        
        gz_point_0 = self.gizmo_point_0
        gz_point_0.scale_basis = scale_basis
        gz_point_0.matrix_basis = ob.matrix_world
        
        gz_point_1 = self.gizmo_point_1
        gz_point_1.scale_basis = scale_basis
        gz_point_1.matrix_basis = ob.matrix_world
        
        gz_point_2 = self.gizmo_point_2
        gz_point_2.scale_basis = scale_basis
        gz_point_2.matrix_basis = ob.matrix_world


classes = [
    SDF2MESH_OT_Apply_Gizmo_To_SDF_Quadratic_Bezier,
    SDFQuadraticBezierWidgetGroup
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)