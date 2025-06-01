import bpy
import math
import mathutils
from mesh_from_sdf.pointer import *
from bpy.props import FloatVectorProperty
from bpy.types import Operator, GizmoGroup, PropertyGroup


class SDF2MESH_OT_Apply_Gizmo_To_SDF_Cone(Operator):
    bl_idname = 'mesh_from_sdf.apply_gizmo_to_sdf_cone'
    bl_label = 'Apply Gizmo to SDF Cone'
    bl_description = 'Reflect Gizmo changes in SDFConeProperty'
    
    def execute(self, context):
        global radius, height
        cone_pointer = context.scene.sdf_cone_pointer_list[context.object.sdf_prop.sub_index]
        cone_pointer.radius = radius
        cone_pointer.height = height * 2.0
        
        # Update mesh for primitive interactions
        prev_mode = SDFPrimitivePointer.update_primitive_mesh_begin(context)
        pointer = context.scene.sdf_object_pointer_list[context.object.sdf_prop.index]
        SDFConePointer.update_cone_mesh(pointer)
        SDFPrimitivePointer.update_primitive_mesh_end(prev_mode)
        
        # Currently, each time Gizmo is updated, Undo is also recorded. Ideally, 
        # Undo should be performed when Gizmo is finished dragging.
        # bpy.ops.ed.undo_push(message='mesh_from_sdf.apply_gizmo_to_sdf_cone')
        return {'FINISHED'}
    

global radius, fill
radius = [0.75,0.25]
height = 2.0


class SDFConeWidgetGroup(GizmoGroup):
    bl_idname = "OBJECT_GGT_sdf_cone"
    bl_label = "SDF Cone Widget"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT'}

    @classmethod
    def poll(cls, context):
        return context.object and context.object.sdf_prop.enabled and (context.object.sdf_prop.primitive_type == 'Cone')

    def setup(self, context):
        
        def move_get_radius_0():
            global radius
            value = bpy.context.scene.sdf_cone_pointer_list[context.object.sdf_prop.sub_index].radius[0]
            # Apparently, it is not possible to write a value to sdf_cone_gizmo_prop in the setup function.
            # This function is called when an object is selected, so update the value of sdf_cone_gizmo_prop here.
            radius[0] = max(0, value)
            return value

        def move_set_radius_0(value):
            global radius
            radius[0] = max(0, value)
            bpy.ops.mesh_from_sdf.apply_gizmo_to_sdf_cone()
            
        def move_get_radius_1():
            global radius
            value = bpy.context.scene.sdf_cone_pointer_list[context.object.sdf_prop.sub_index].radius[1]
            radius[1] = max(0, value)
            return value

        def move_set_radius_1(value):
            global radius
            radius[1] = max(0, value)
            bpy.ops.mesh_from_sdf.apply_gizmo_to_sdf_cone()
            
        def move_get_height():
            global height
            value = bpy.context.scene.sdf_cone_pointer_list[context.object.sdf_prop.sub_index].height * 0.5
            height = max(0, value)
            return value

        def move_set_height(value):
            global height
            height = max(0, value)
            bpy.ops.mesh_from_sdf.apply_gizmo_to_sdf_cone()

        ob = context.object
        
        # Gizmo Radius 0
        gz_radius_0 = self.gizmos.new("GIZMO_GT_arrow_3d")
        gz_radius_0.target_set_handler("offset", get=move_get_radius_0, set=move_set_radius_0)
        gz_radius_0.matrix_basis = ob.matrix_world @ mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'Y')
        gz_radius_0.draw_style = 'BOX'
        gz_radius_0.length = 0.2
        gz_radius_0.scale_basis = 1.0 / ob.scale[0]

        gz_radius_0.color = 1.0, 0.0, 0.0
        gz_radius_0.alpha = 0.5
        gz_radius_0.color_highlight = 1.0, 0.0, 1.0
        gz_radius_0.alpha_highlight = 0.25
        
        # Gizmo Radius 1
        gz_radius_1 = self.gizmos.new("GIZMO_GT_arrow_3d")
        gz_radius_1.target_set_handler("offset", get=move_get_radius_1, set=move_set_radius_1)
        gz_radius_1.matrix_basis = ob.matrix_world @ mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'Y')
        gz_radius_1.draw_style = 'BOX'
        gz_radius_1.length = 0.2
        gz_radius_1.scale_basis = 1.0 / ob.scale[0]

        gz_radius_1.color = 0.0, 1.0, 0.0
        gz_radius_1.alpha = 0.5
        gz_radius_1.color_highlight = 0.0, 1.0, 0.0
        gz_radius_1.alpha_highlight = 0.25
        
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

        self.gizmo_radius_0 = gz_radius_0
        self.gizmo_radius_1 = gz_radius_1
        self.gizmo_height = gz_height

    def refresh(self, context):
        
        global radius, height
        
        ob = context.object
        
        gz_radius_0 = self.gizmo_radius_0
        gz_radius_0.scale_basis = 1.0 / ob.scale[0]
        gz_radius_0.matrix_basis = ob.matrix_world @ mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'Y')
        gz_radius_0.matrix_offset = mathutils.Matrix.Translation((-height,0,0))
        
        gz_radius_1 = self.gizmo_radius_1
        gz_radius_1.scale_basis = 1.0 / ob.scale[0]
        gz_radius_1.matrix_basis = ob.matrix_world @ mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'Y')
        gz_radius_1.matrix_offset = mathutils.Matrix.Translation((+height,0,0))
        
        gz_height = self.gizmo_height
        gz_height.matrix_basis = ob.matrix_world


classes = [
    SDF2MESH_OT_Apply_Gizmo_To_SDF_Cone,
    SDFConeWidgetGroup
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)