import bpy
import math
import mathutils
from mesh_from_sdf.pointer import *
from bpy.props import FloatVectorProperty
from bpy.types import Operator, GizmoGroup, PropertyGroup


class SDF2MESH_OT_Apply_Gizmo_To_SDF_Pyramid(Operator):
    bl_idname = 'mesh_from_sdf.apply_gizmo_to_sdf_pyramid'
    bl_label = 'Apply Gizmo to SDF Pyramid'
    bl_description = 'Reflect Gizmo changes in SDFPyramidProperty'
    
    def execute(self, context):
        global width, depth, height
        pyramid_pointer = context.scene.sdf_pyramid_pointer_list[context.object.sdf_prop.sub_index]
        pyramid_pointer.width = width * 2.0
        pyramid_pointer.depth = depth * 2.0
        pyramid_pointer.height = height * 2.0
        
        # Update mesh for primitive interactions
        prev_mode = SDFPrimitivePointer.update_primitive_mesh_begin(context)
        pointer = context.scene.sdf_object_pointer_list[context.object.sdf_prop.index]
        SDFPyramidPointer.update_pyramid_mesh(pointer)
        SDFPrimitivePointer.update_primitive_mesh_end(prev_mode)
        
        # Currently, each time Gizmo is updated, Undo is also recorded. Ideally, 
        # Undo should be performed when Gizmo is finished dragging.
        # bpy.ops.ed.undo_push(message='mesh_from_sdf.apply_gizmo_to_sdf_pyramid')
        return {'FINISHED'}
    

global width, depth, height
width = 2.0
depth = 2.0
height = 2.0


class SDFPyramidWidgetGroup(GizmoGroup):
    bl_idname = "OBJECT_GGT_sdf_pyramid"
    bl_label = "SDF Pyramid Widget"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT'}

    @classmethod
    def poll(cls, context):
        return context.object and context.object.sdf_prop.enabled and (context.object.sdf_prop.primitive_type == 'Pyramid')

    def setup(self, context):
        
        global width, depth, height
        
        def move_get_width():
            global width
            value = bpy.context.scene.sdf_pyramid_pointer_list[context.object.sdf_prop.sub_index].width * 0.5
            # Apparently, it is not possible to write a value to sdf_pyramid_gizmo_prop in the setup function.
            # This function is called when an object is selected, so update the value of sdf_pyramid_gizmo_prop here.
            width = max(0, value)
            return value

        def move_set_width(value):
            global width
            width = max(0, value)
            bpy.ops.mesh_from_sdf.apply_gizmo_to_sdf_pyramid()
            
        def move_get_depth():
            global depth
            value = bpy.context.scene.sdf_pyramid_pointer_list[context.object.sdf_prop.sub_index].depth * 0.5
            depth = max(0, value)
            return value

        def move_set_depth(value):
            global depth
            depth = max(0, value)
            bpy.ops.mesh_from_sdf.apply_gizmo_to_sdf_pyramid()
            
        def move_get_height():
            global height
            value = bpy.context.scene.sdf_pyramid_pointer_list[context.object.sdf_prop.sub_index].height * 0.5
            height = max(0, value)
            return value

        def move_set_height(value):
            global height
            height = max(0, value)
            bpy.ops.mesh_from_sdf.apply_gizmo_to_sdf_pyramid()

        ob = context.object
        scale_basis = 1.0 / ob.matrix_world.to_scale()[0]
        
#        pointer = bpy.context.scene.sdf_pyramid_pointer_list[ob.sdf_prop.sub_index]
#        width = pointer.width * 0.5
#        depth = pointer.depth * 0.5
#        height = pointer.height * 0.5
        
        # Gizmo Width
        gz_width = self.gizmos.new("GIZMO_GT_arrow_3d")
        gz_width.target_set_handler("offset", get=move_get_width, set=move_set_width)
        gz_width.matrix_basis = ob.matrix_world @ mathutils.Matrix.Rotation(math.radians(+90.0), 4, 'Y')
        gz_width.draw_style = 'BOX'
        gz_width.length = 0.2
        gz_width.scale_basis = scale_basis

        gz_width.color = 1.0, 0.0, 0.0
        gz_width.alpha = 0.5
        gz_width.color_highlight = 1.0, 0.0, 1.0
        gz_width.alpha_highlight = 0.25
        
        # Gizmo Depth
        gz_depth = self.gizmos.new("GIZMO_GT_arrow_3d")
        gz_depth.target_set_handler("offset", get=move_get_depth, set=move_set_depth)
        gz_depth.matrix_basis = ob.matrix_world @ mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'X')
        gz_depth.draw_style = 'BOX'
        gz_depth.length = 0.2
        gz_depth.scale_basis = scale_basis

        gz_depth.color = 0.0, 1.0, 0.0
        gz_depth.alpha = 0.5
        gz_depth.color_highlight = 0.0, 1.0, 0.0
        gz_depth.alpha_highlight = 0.25
        
        # Gizmo Height
        gz_height = self.gizmos.new("GIZMO_GT_arrow_3d")
        gz_height.target_set_handler("offset", get=move_get_height, set=move_set_height)
        gz_height.matrix_basis = ob.matrix_world
        gz_height.draw_style = 'BOX'
        gz_height.length = 0.2
        gz_height.scale_basis = scale_basis

        gz_height.color = 0.0, 0.0, 1.0
        gz_height.alpha = 0.5
        gz_height.color_highlight = 0.0, 1.0, 1.0
        gz_height.alpha_highlight = 0.25

        self.gizmo_width = gz_width
        self.gizmo_depth = gz_depth
        self.gizmo_height = gz_height

    def refresh(self, context):
        
        global width, depth, height
        
        ob = context.object
        scale_basis = 1.0 / ob.matrix_world.to_scale()[0]
        
        gz_width = self.gizmo_width
        gz_width.scale_basis = scale_basis
        gz_width.matrix_basis = ob.matrix_world @ mathutils.Matrix.Rotation(math.radians(+90.0), 4, 'Y')
        gz_width.matrix_offset = mathutils.Matrix.Translation((+height,0,0))
        
        gz_depth = self.gizmo_depth
        gz_depth.scale_basis = scale_basis
        gz_depth.matrix_basis = ob.matrix_world @ mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'X')
        gz_depth.matrix_offset = mathutils.Matrix.Translation((0,+height,0))
        
        gz_height = self.gizmo_height
        gz_height.scale_basis = scale_basis
        gz_height.matrix_basis = ob.matrix_world


classes = [
    SDF2MESH_OT_Apply_Gizmo_To_SDF_Pyramid,
    SDFPyramidWidgetGroup
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)