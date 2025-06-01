import bpy
import math
import mathutils
from mesh_from_sdf.pointer import *
from bpy.props import FloatVectorProperty
from bpy.types import Operator, GizmoGroup, PropertyGroup


class SDF2MESH_OT_Apply_Gizmo_To_SDF_Truncated_Pyramid(Operator):
    bl_idname = 'mesh_from_sdf.apply_gizmo_to_sdf_truncated_pyramid'
    bl_label = 'Apply Gizmo to SDF Truncated_Pyramid'
    bl_description = 'Reflect Gizmo changes in SDFTruncated_PyramidProperty'
    
    def execute(self, context):
        global width, depth, height
        truncated_pyramid_pointer = context.scene.sdf_truncated_pyramid_pointer_list[context.object.sdf_prop.sub_index]
        truncated_pyramid_pointer.width_0 = width_0 * 2.0
        truncated_pyramid_pointer.depth_0 = depth_0 * 2.0
        truncated_pyramid_pointer.width_1 = width_1 * 2.0
        truncated_pyramid_pointer.depth_1 = depth_1 * 2.0
        truncated_pyramid_pointer.height = height * 2.0
        
        # Update mesh for primitive interactions
        prev_mode = SDFPrimitivePointer.update_primitive_mesh_begin(context)
        pointer = context.scene.sdf_object_pointer_list[context.object.sdf_prop.index]
        SDFTruncatedPyramidPointer.update_truncated_pyramid_mesh(pointer)
        SDFPrimitivePointer.update_primitive_mesh_end(prev_mode)
        
        # Currently, each time Gizmo is updated, Undo is also recorded. Ideally, 
        # Undo should be performed when Gizmo is finished dragging.
        # bpy.ops.ed.undo_push(message='mesh_from_sdf.apply_gizmo_to_sdf_truncated_pyramid')
        return {'FINISHED'}
    

global width_0, depth_0, width_1, depth_1, height
width_0 = 2.0
width_1 = 1.5
depth_0 = 2.0
depth_1 = 1.5
height = 2.0


class SDFTruncatedPyramidWidgetGroup(GizmoGroup):
    bl_idname = "OBJECT_GGT_sdf_truncated_pyramid"
    bl_label = "SDF Truncated Pyramid Widget"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT'}

    @classmethod
    def poll(cls, context):
        return context.object and context.object.sdf_prop.enabled and (context.object.sdf_prop.primitive_type == 'Truncated Pyramid')

    def setup(self, context):
        
        global width_0, depth_0, width_1, depth_1, height
        
        def move_get_width_0():
            global width_0
            value = bpy.context.scene.sdf_truncated_pyramid_pointer_list[context.object.sdf_prop.sub_index].width_0 * 0.5
            # Apparently, it is not possible to write a value to sdf_truncated_pyramid_gizmo_prop in the setup function.
            # This function is called when an object is selected, so update the value of sdf_truncated_pyramid_gizmo_prop here.
            width_0 = max(0, value)
            return value

        def move_set_width_0(value):
            global width_0
            width_0 = max(0, value)
            bpy.ops.mesh_from_sdf.apply_gizmo_to_sdf_truncated_pyramid()
            
        def move_get_depth_0():
            global depth_0
            value = bpy.context.scene.sdf_truncated_pyramid_pointer_list[context.object.sdf_prop.sub_index].depth_0 * 0.5
            depth_0 = max(0, value)
            return value

        def move_set_depth_0(value):
            global depth_0
            depth_0 = max(0, value)
            bpy.ops.mesh_from_sdf.apply_gizmo_to_sdf_truncated_pyramid()
            
        def move_get_width_1():
            global width_1
            value = bpy.context.scene.sdf_truncated_pyramid_pointer_list[context.object.sdf_prop.sub_index].width_1 * 0.5
            # Apparently, it is not possible to write a value to sdf_truncated_pyramid_gizmo_prop in the setup function.
            # This function is called when an object is selected, so update the value of sdf_truncated_pyramid_gizmo_prop here.
            width_1 = max(0, value)
            return value

        def move_set_width_1(value):
            global width_1
            width_1 = max(0, value)
            bpy.ops.mesh_from_sdf.apply_gizmo_to_sdf_truncated_pyramid()
            
        def move_get_depth_1():
            global depth_1
            value = bpy.context.scene.sdf_truncated_pyramid_pointer_list[context.object.sdf_prop.sub_index].depth_1 * 0.5
            depth_1 = max(0, value)
            return value

        def move_set_depth_1(value):
            global depth_1
            depth_1 = max(0, value)
            bpy.ops.mesh_from_sdf.apply_gizmo_to_sdf_truncated_pyramid()
            
        def move_get_height():
            global height
            value = bpy.context.scene.sdf_truncated_pyramid_pointer_list[context.object.sdf_prop.sub_index].height * 0.5
            height = max(0, value)
            return value

        def move_set_height(value):
            global height
            height = max(0, value)
            bpy.ops.mesh_from_sdf.apply_gizmo_to_sdf_truncated_pyramid()

        ob = context.object
        
        pointer = bpy.context.scene.sdf_truncated_pyramid_pointer_list[ob.sdf_prop.sub_index]
        width_0 = pointer.width_0 * 0.5
        depth_0 = pointer.depth_0 * 0.5
        width_1 = pointer.width_1 * 0.5
        depth_1 = pointer.depth_1 * 0.5
        height = pointer.height * 0.5
        
        # Gizmo Width 0
        gz_width_0 = self.gizmos.new("GIZMO_GT_arrow_3d")
        gz_width_0.target_set_handler("offset", get=move_get_width_0, set=move_set_width_0)
        gz_width_0.matrix_basis = ob.matrix_world @ mathutils.Matrix.Rotation(math.radians(+90.0), 4, 'Y')
        gz_width_0.draw_style = 'BOX'
        gz_width_0.length = 0.2
        gz_width_0.scale_basis = 1.0 / ob.scale[0]

        gz_width_0.color = 1.0, 0.0, 0.0
        gz_width_0.alpha = 0.5
        gz_width_0.color_highlight = 1.0, 0.0, 1.0
        gz_width_0.alpha_highlight = 0.25
        
        # Gizmo Depth 0
        gz_depth_0 = self.gizmos.new("GIZMO_GT_arrow_3d")
        gz_depth_0.target_set_handler("offset", get=move_get_depth_0, set=move_set_depth_0)
        gz_depth_0.matrix_basis = ob.matrix_world @ mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'X')
        gz_depth_0.draw_style = 'BOX'
        gz_depth_0.length = 0.2
        gz_depth_0.scale_basis = 1.0 / ob.scale[0]

        gz_depth_0.color = 0.0, 1.0, 0.0
        gz_depth_0.alpha = 0.5
        gz_depth_0.color_highlight = 0.0, 1.0, 0.0
        gz_depth_0.alpha_highlight = 0.25
        
        # Gizmo Width 1
        gz_width_1 = self.gizmos.new("GIZMO_GT_arrow_3d")
        gz_width_1.target_set_handler("offset", get=move_get_width_1, set=move_set_width_1)
        gz_width_1.matrix_basis = ob.matrix_world @ mathutils.Matrix.Rotation(math.radians(+90.0), 4, 'Y')
        gz_width_1.draw_style = 'BOX'
        gz_width_1.length = 0.2
        gz_width_1.scale_basis = 1.0 / ob.scale[0]

        gz_width_1.color = 1.0, 0.0, 0.0
        gz_width_1.alpha = 0.5
        gz_width_1.color_highlight = 1.0, 0.0, 1.0
        gz_width_1.alpha_highlight = 0.25
        
        # Gizmo Depth 1
        gz_depth_1 = self.gizmos.new("GIZMO_GT_arrow_3d")
        gz_depth_1.target_set_handler("offset", get=move_get_depth_1, set=move_set_depth_1)
        gz_depth_1.matrix_basis = ob.matrix_world @ mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'X')
        gz_depth_1.draw_style = 'BOX'
        gz_depth_1.length = 0.2
        gz_depth_1.scale_basis = 1.0 / ob.scale[0]

        gz_depth_1.color = 0.0, 1.0, 0.0
        gz_depth_1.alpha = 0.5
        gz_depth_1.color_highlight = 0.0, 1.0, 0.0
        gz_depth_1.alpha_highlight = 0.25
        
        # Gizmo Height
        gz_height = self.gizmos.new("GIZMO_GT_arrow_3d")
        gz_height.target_set_handler("offset", get=move_get_height, set=move_set_height)
        gz_height.matrix_basis = ob.matrix_world
        gz_height.draw_style = 'BOX'
        gz_height.length = 0.2
        gz_height.scale_basis = 1.0 / ob.scale[0]

        gz_height.color = 0.0, 0.0, 1.0
        gz_height.alpha = 0.5
        gz_height.color_highlight = 0.0, 1.0, 1.0
        gz_height.alpha_highlight = 0.25

        self.gizmo_width_0 = gz_width_0
        self.gizmo_depth_0 = gz_depth_0
        self.gizmo_width_1 = gz_width_1
        self.gizmo_depth_1 = gz_depth_1
        self.gizmo_height = gz_height

    def refresh(self, context):

        global width_0, depth_0, width_1, depth_1, height

        ob = context.object
        
        gz_width_0 = self.gizmo_width_0
        gz_width_0.scale_basis = 1.0 / ob.scale[0]
        gz_width_0.matrix_basis = ob.matrix_world @ mathutils.Matrix.Rotation(math.radians(+90.0), 4, 'Y')
        gz_width_0.matrix_offset = mathutils.Matrix.Translation((+height,0,0))
        
        gz_depth_0 = self.gizmo_depth_0
        gz_depth_0.scale_basis = 1.0 / ob.scale[0]
        gz_depth_0.matrix_basis = ob.matrix_world @ mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'X')
        gz_depth_0.matrix_offset = mathutils.Matrix.Translation((0,+height,0))
        
        gz_width_1 = self.gizmo_width_1
        gz_width_1.scale_basis = 1.0 / ob.scale[0]
        gz_width_1.matrix_basis = ob.matrix_world @ mathutils.Matrix.Rotation(math.radians(+90.0), 4, 'Y')
        gz_width_1.matrix_offset = mathutils.Matrix.Translation((-height,0,0))
        
        gz_depth_1 = self.gizmo_depth_1
        gz_depth_1.scale_basis = 1.0 / ob.scale[0]
        gz_depth_1.matrix_basis = ob.matrix_world @ mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'X')
        gz_depth_1.matrix_offset = mathutils.Matrix.Translation((0,-height,0))
        
        gz_height = self.gizmo_height
        gz_height.matrix_basis = ob.matrix_world


classes = [
    SDF2MESH_OT_Apply_Gizmo_To_SDF_Truncated_Pyramid,
    SDFTruncatedPyramidWidgetGroup
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)