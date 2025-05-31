
# SDF objects are now managed on a primitive-by-primitive basis. Not tested yet.

bl_info = {
    "name" : "Mesh from SDF",
    "description" : "",
    "author" : "TLabAltoh",
    "version" : (0, 0, 1),
    "blender" : (4, 3, 0),
    "location" : "View3D",
    "warning" : "",
    "support" : "COMMUNITY",
    "doc_url" : "",
    "category" : "3D View"
}

import bpy
import bmesh
import numpy as np
from bpy.app.handlers import persistent
from mesh_from_sdf.raymarching import *
from mesh_from_sdf.marching_cube import *
from mesh_from_sdf.marching_tables import *
from mesh_from_sdf.shader_factory import *
from mesh_from_sdf.shader_buffer_factory import *
from mesh_from_sdf.pointer import *
from mesh_from_sdf.gizmo.box import *
from mesh_from_sdf.gizmo.cylinder import *
from mesh_from_sdf.gizmo.torus import *
from mesh_from_sdf.util.material import *
from mesh_from_sdf.util.moderngl import *
from mesh_from_sdf.util.algorithm import *
from mesh_from_sdf.util.pointer_list import *
from bpy.app.handlers import persistent
from bpy.types import Panel, Operator, UIList, PropertyGroup
from bpy.props import PointerProperty, EnumProperty, FloatProperty, IntProperty, StringProperty, BoolProperty, CollectionProperty


class SDFProperty(PropertyGroup):

    primitive_types = (('Box', 'Box', ''),
            ('Sphere', 'Sphere', ''),
            ('Cylinder','Cylinder',''),
            ('Cone','Cone',''),
            ('Torus','Torus',''),
            ('Pyramid', 'Pyramid', ''),
            ('Truncated Pyramid', 'Truncated Pyramid', ''),
            ('Hexagonal Prism', 'Hexagonal Prism', ''),
            ('Triangular Prism', 'Triangular Prism', ''),
            ('Ngon Prism','Ngon Prism',''),
            ('GLSL','GLSL',''),)
             
    boolean_types = (('Union', 'Union', ''),
            ('Difference', 'Difference', ''),
            ('Intersection', 'Intersection', ''),)
            
    blend_types = (('No Blending', 'No Blending', ''),
            ('Smooth', 'Smooth', ''),
            ('Champfer', 'Champfer', ''),
            ('Steps', 'Steps', ''),
            ('Round', 'Round', ''),)

    # Determine if an SDF object exists in the list
    @classmethod
    def contains_in_pointer_list(cls, list, object):
        for p in list:
            if p.object == object:
                return True
        return False

    # Update parentage relationships in the hierarchy according to the current state of nesting of SDF objects
    @classmethod
    def update_nest_prop(cls, context, self_index, self_nest):
        global ctx
        
        pointer = context.scene.sdf_object_pointer_list[self_index]
        if (self_index == 0) or (self_nest == False):
            pointer.object.parent = None
            print('nest: ', False)
        else:
            for index in reversed(range(0, self_index)):
                parent_pointer = context.scene.sdf_object_pointer_list[index]
                if parent_pointer.object.sdf_prop.nest == False:
                    pointer.object.parent = parent_pointer.object
                    print('nest: ', True)
                    break

    def on_prop_update(self, context):
        global ctx
        
        # Updateing Storage Buffre Objects
        ShaderBufferFactory.update_object_common_buffer(ctx, context, self.index)

    def on_merge_prop_update(self, context):
        global ctx
        
        # Updateing Storage Buffre Objects
        ShaderBufferFactory.update_object_common_buffer(ctx, context, self.index)
        
        # Generate shaders according to the current hierarchy
        f_dist = ShaderFactory.generate_distance_function(context.scene.sdf_object_pointer_list)
        print(f_dist)
        
    def on_nest_prop_update(self, context):
        global ctx
        
        # Update the parent-child relationship based on the current nesting properties of the SDFObject
        self.__class__.update_nest_prop(context, self.index, self.nest)
        
        # Updateing Storage Buffre Objects
        ShaderBufferFactory.update_object_common_buffer(ctx, context, self.index)
        
        # Generate shaders according to the current hierarchy
        f_dist = ShaderFactory.generate_distance_function(context.scene.sdf_object_pointer_list)
        print(f_dist)

    @classmethod
    def update_primitive_mesh_begin(cls, context):
        prev_mode = context.object.mode
        prev_mesh = context.object.data

        # Move to Edit mode to manipulate Mesh primitives
        bpy.ops.object.mode_set(mode='EDIT')
        
        bm = bmesh.from_edit_mesh(prev_mesh)
        bm.clear()
        bmesh.update_edit_mesh(prev_mesh)

        return prev_mode
    
    @classmethod
    def update_primitive_mesh_end(cls, prev_mode):
        bpy.ops.object.mode_set(mode=prev_mode)
        
    @classmethod
    def _add_new_pointer(cls, prv_pointer, new_pointer, blist):
        new_pointer = blist.add()
        new_pointer.object = prv_pointer.object
        PointerListUtil.recalc_sub_index(blist)

    def on_primitive_type_change(self, context):
        global ctx
        # Undo works for this operation
        prev_primitive_type = self.prev_primitive_type
        primitive_type = self.primitive_type
        if primitive_type != prev_primitive_type:
            object = context.object
            mesh = object.data
            if mesh:
                # Cache the current mode and enter edit mode to clear the mesh
                prev_mode = SDFPrimitivePointer.update_primitive_mesh_begin(context)

                # Delete objects to be updated from the list in advance.
                PointerListUtil.delete_from_sub_pointer_list(context, object)

                prv_pointer = None
                new_pointer = None
                for pointer in context.scene.sdf_object_pointer_list:
                    if pointer.object == object:
                        prv_pointer = pointer
                
                # Create a new property object and add it to the list of applicable primitive types
                # CollectionProperty does not have an alternative to the append function; the add function must be used.
                # Sorts the list of SDF Objects according to the order of the hierarchy.
                blist = None
                alloc = None
                if (primitive_type == 'Box') and (SDFProperty.contains_in_pointer_list(context.scene.sdf_box_pointer_list, prv_pointer.object) == False):
                    blist = context.scene.sdf_box_pointer_list
                    self.__class__._add_new_pointer(prv_pointer, new_pointer, blist)
                    SDFBoxPointer.update_box_mesh(prv_pointer)
                    alloc = lambda ctx, context: ShaderBufferFactory.generate_box_buffer(ctx, context)
                elif (primitive_type == 'Sphere') and (SDFProperty.contains_in_pointer_list(context.scene.sdf_sphere_pointer_list, prv_pointer.object) == False):
                    blist = context.scene.sdf_sphere_pointer_list
                    self.__class__._add_new_pointer(prv_pointer, new_pointer, blist)
                    SDFSpherePointer.update_sphere_mesh(prv_pointer)
                    alloc = lambda ctx, context: ShaderBufferFactory.generate_sphere_buffer(ctx, context)
                elif (primitive_type == 'Cylinder') and (SDFProperty.contains_in_pointer_list(context.scene.sdf_cylinder_pointer_list, prv_pointer.object) == False):
                    blist = context.scene.sdf_cylinder_pointer_list
                    self.__class__._add_new_pointer(prv_pointer, new_pointer, blist)
                    SDFCylinderPointer.update_cylinder_mesh(prv_pointer)
                    alloc = lambda ctx, context: ShaderBufferFactory.generate_cylinder_buffer(ctx, context)
                elif (primitive_type == 'Cone') and (SDFProperty.contains_in_pointer_list(context.scene.sdf_cone_pointer_list, prv_pointer.object) == False):
                    blist = context.scene.sdf_cone_pointer_list
                    self.__class__._add_new_pointer(prv_pointer, new_pointer, blist)
                    SDFConePointer.update_cone_mesh(prv_pointer)
                    alloc = lambda ctx, context: ShaderBufferFactory.generate_cone_buffer(ctx, context)
                elif (primitive_type == 'Torus') and (SDFProperty.contains_in_pointer_list(context.scene.sdf_torus_pointer_list, prv_pointer.object) == False):
                    # Torus has no argument to scale with primitive_add. Scaling is applied manually.
                    blist = context.scene.sdf_torus_pointer_list
                    self.__class__._add_new_pointer(prv_pointer, new_pointer, blist)
                    SDFTorusPointer.update_torus_mesh(prv_pointer)
                    alloc = lambda ctx, context: ShaderBufferFactory.generate_torus_buffer(ctx, context)
                elif (primitive_type == 'Pyramid') and (SDFProperty.contains_in_pointer_list(context.scene.sdf_pyramid_pointer_list, prv_pointer.object) == False):
                    blist = context.scene.sdf_pyramid_pointer_list
                    self.__class__._add_new_pointer(prv_pointer, new_pointer, blist)
                    SDFPyramidPointer.update_pyramid_mesh(prv_pointer)
                    alloc = lambda ctx, context: ShaderBufferFactory.generate_pyramid_buffer(ctx, context)
                elif (primitive_type == 'Truncated Pyramid') and (SDFProperty.contains_in_pointer_list(context.scene.sdf_truncated_pyramid_pointer_list, prv_pointer.object) == False):
                    blist = context.scene.sdf_truncated_pyramid_pointer_list
                    self.__class__._add_new_pointer(prv_pointer, new_pointer, blist)
                    SDFTruncatedPyramidPointer.update_truncated_pyramid_mesh(prv_pointer)
                    alloc = lambda ctx, context: ShaderBufferFactory.generate_truncated_pyramid_buffer(ctx, context)
                elif (primitive_type == 'Hexagonal Prism') and (SDFProperty.contains_in_pointer_list(context.scene.sdf_hex_prism_pointer_list, prv_pointer.object) == False):
                    blist = context.scene.sdf_hex_prism_pointer_list
                    self.__class__._add_new_pointer(prv_pointer, new_pointer, blist)
                    SDFPrismPointer.update_hex_prism_mesh(prv_pointer)
                    alloc = lambda ctx, context: ShaderBufferFactory.generate_hex_prism_buffer(ctx, context)
                elif (primitive_type == 'Triangular Prism') and (SDFProperty.contains_in_pointer_list(context.scene.sdf_tri_prism_pointer_list, prv_pointer.object) == False):
                    blist = context.scene.sdf_tri_prism_pointer_list
                    self.__class__._add_new_pointer(prv_pointer, new_pointer, blist)
                    SDFPrismPointer.update_tri_prism_mesh(prv_pointer)
                    alloc = lambda ctx, context: ShaderBufferFactory.generate_tri_prism_buffer(ctx, context)
                elif (primitive_type == 'Ngon Prism') and (SDFProperty.contains_in_pointer_list(context.scene.sdf_ngon_prism_pointer_list, prv_pointer.object) == False):
                    blist = context.scene.sdf_ngon_prism_pointer_list
                    self.__class__._add_new_pointer(prv_pointer, new_pointer, blist)
                    SDFPrismPointer.update_ngon_prism_mesh(prv_pointer)
                    alloc = lambda ctx, context: ShaderBufferFactory.generate_ngon_prism_buffer(ctx, context)
                elif (primitive_type == 'GLSL') and (SDFProperty.contains_in_pointer_list(context.scene.sdf_glsl_pointer_list, prv_pointer.object) == False):
                    blist = context.scene.sdf_glsl_pointer_list
                    self.__class__._add_new_pointer(prv_pointer, new_pointer, blist)
                    SDFGLSLPointer.update_glsl_mesh(prv_pointer)
                    alloc = lambda ctx, context: ShaderBufferFactory.generate_glsl_buffer(ctx, context)

                # Rebuild Storage Buffer Objects
                alloc(ctx, context)
                ShaderBufferFactory.generate_object_common_buffer(ctx, context)
                    
                # Return from Edit mode to the previous mode
                object.sdf_prop.prev_primitive_type = object.sdf_prop.primitive_type
                
                # Restore mode to previous mode
                SDFPrimitivePointer.update_primitive_mesh_end(prev_mode)
                
                # Generate shaders according to the current hierarchy
                f_dist = ShaderFactory.generate_distance_function(context.scene.sdf_object_pointer_list)
                print(f_dist)
        
    enabled: BoolProperty(
        description='Whether this object is treated as an SDF Object.',
        default=False)
    
    index: IntProperty(
       description='Index on the context.scene.sdf_object_pointer_list.',
       min=0,
       default=-1)
       
    sub_index: IntProperty(
       description='Index on the context.scene.sdf_{PRIMITIVE_TYPE}_pointer_list.',
       min=0,
       default=-1)
    
    nest: BoolProperty(
        name='Nest',
        description='',
        default=False,
        update=on_nest_prop_update)

    boolean_type: EnumProperty(
        name='Boolean',
        description='',
        items=boolean_types,
        update=on_merge_prop_update)
        
    blend_type: EnumProperty(
        name='Blend',
        description='',
        items=blend_types,
        update=on_merge_prop_update)

    blend_champfer_size: FloatProperty(
        name='Champfer Size',
        description='',
        min=0.0,
        default=0.0,
        update=on_prop_update)

    blend_step: IntProperty(
        name='Step',
        description='',
        min=1,
        default=1,
        update=on_prop_update)

    blend_round: FloatProperty(
        name='Round',
        description='',
        min=0.0,
        default=0.0,
        update=on_prop_update)

    blend_smooth: FloatProperty(
        name='Smooth',
        description='',
        min=0.0,
        max=1.0,
        default=0.5,
        update=on_prop_update)
           
    round: FloatProperty(
       name='Round',
       description='',
       min=0.0,
       max=1.0,
       default=0.0,
       update=on_prop_update)
           
    prev_primitive_type: EnumProperty(
        description='',
        items=primitive_types)
        
    primitive_type: EnumProperty(
        name='Primitive',
        description='',
        items=primitive_types,
        update=on_primitive_type_change)


class SDF2MESH_UL_List(UIList):
    bl_idname = 'SDF2MESH_UL_List'
    layout_type = 'DEFAULT'
    
    def draw_filter(self, context, layout):
        # Disable the filter because there is currently no string property in 
        # SDFProperty that could be used to sort items.
        pass

    def draw_item(self, context,
                    layout, # Layout to draw the item
                    data, # Data from which to take Collection property
                    item, # Item of the collection property
                    icon, # Icon of the item in the collection
                    active_data, # Data from which to take property for the active element
                    active_propname, # Identifier of property in active_data, for the active element
                    index, # Index of the item in the collection - default 0
                    flt_flag # The filter-flag result for this item - default 0
            ):

        self.use_filter_show = False
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item.object != None:
                prop = item.object.sdf_prop
                layout = layout.row()
                if index > 0 and prop.nest:
                    layout.separator()
                layout.label(text=str(item.object.name))
                layout.label(text=str(prop.primitive_type))
                layout.label(text=str(prop.boolean_type))
                layout.label(text=str(prop.blend_type))
                layout.label(text=str(prop.index))
                layout.label(text=str(prop.sub_index))
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="")


class SDF2MESH_OT_List_Reload(Operator):
    bl_idname = 'mesh_from_sdf.hierarchy_reload'
    bl_label = 'Reload'
    bl_description = 'Re-swing the index on the hierarchy.'
    
    @classmethod
    def poll(cls, context):
        return context.scene
    
    def execute(self, context):
        global ctx
        # Fix index properties.
        alist = context.scene.sdf_object_pointer_list
        for i, pointer in enumerate(alist):
            pointer.object.sdf_prop.index = i
        
        # Fix sub_index properties.
        PointerListUtil.recalc_sub_index(context.scene.sdf_box_pointer_list)
        PointerListUtil.recalc_sub_index(context.scene.sdf_sphere_pointer_list)
        PointerListUtil.recalc_sub_index(context.scene.sdf_cylinder_pointer_list)
        PointerListUtil.recalc_sub_index(context.scene.sdf_cone_pointer_list)
        PointerListUtil.recalc_sub_index(context.scene.sdf_torus_pointer_list)
        PointerListUtil.recalc_sub_index(context.scene.sdf_pyramid_pointer_list)
        PointerListUtil.recalc_sub_index(context.scene.sdf_truncated_pyramid_pointer_list)
        PointerListUtil.recalc_sub_index(context.scene.sdf_hex_prism_pointer_list)
        PointerListUtil.recalc_sub_index(context.scene.sdf_tri_prism_pointer_list)
        PointerListUtil.recalc_sub_index(context.scene.sdf_ngon_prism_pointer_list)
        PointerListUtil.recalc_sub_index(context.scene.sdf_glsl_pointer_list)

        # Update the parental relationship of an object
        for i, pointer in enumerate(alist):
            index = pointer.object.sdf_prop.index
            nest = pointer.object.sdf_prop.nest
            SDFProperty.update_nest_prop(context, index, nest)
            
        # Update Storage Buffre Objects
        ShaderBufferFactory.generate_all(ctx, context)
        
        # Generate shaders according to the current hierarchy
        f_dist = ShaderFactory.generate_distance_function(context.scene.sdf_object_pointer_list)
        print(f_dist)
        
        bpy.ops.ed.undo_push(message='mesh_from_sdf.hierarchy_reload')
        return {'FINISHED'}


class SDF2MESH_OT_List_Add(Operator):
    bl_idname = 'mesh_from_sdf.hierarchy_add'
    bl_label = 'Add'
    bl_description = 'Add a new SDF Object to the hierarchy.'
    
    @classmethod
    def poll(cls, context):
        return context.scene
    
    def execute(self, context):
        global ctx
        
        pointer = context.scene.sdf_object_pointer_list.add()
        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='CURSOR', location=(0,0,0), rotation=(0,0,0), scale=(1,1,1))
        pointer.name = context.active_object.name
        pointer.object = context.active_object
        pointer.object.sdf_prop.enabled = True
        pointer.object.sdf_prop.index = len(context.scene.sdf_object_pointer_list) - 1
        
        # Add Box primitive by default
        pointer.object.sdf_prop.prev_primitive_type = 'Box'
        pointer.object.sdf_prop.primitive_type = 'Box'
        box_pointer = context.scene.sdf_box_pointer_list.add()
        box_pointer.object = pointer.object
        pointer.object.sdf_prop.sub_index = len(context.scene.sdf_box_pointer_list) - 1

        # In Solid View, objects drawn by ray-marching overlap with existing Blender 
        # meshes. Therefore, use Render View or Material View. Apply a transparent 
        # material to the object so that only the result of raymarting is rendered 
        # in Render View or Material View.
        confirm_to_transparent_mat_registed()
        pointer.object.data.materials.append(bpy.data.materials[get_name_of_transparent_mat()])

        # Update the parental relationship of an object
        index = pointer.object.sdf_prop.index
        nest = pointer.object.sdf_prop.nest
        SDFProperty.update_nest_prop(context, index, nest)

        # Updating Storage Buffer Objects
        ShaderBufferFactory.generate_box_buffer(ctx, context)
        ShaderBufferFactory.generate_object_common_buffer(ctx, context)

        # Generate shaders according to the current hierarchy
        f_dist = ShaderFactory.generate_distance_function(context.scene.sdf_object_pointer_list)
        print(f_dist)
        
        bpy.ops.ed.undo_push(message='mesh_from_sdf.hierarchy_add')
        return {'FINISHED'}


class SDF2MESH_OT_List_Remove(Operator):
        
    bl_idname = 'mesh_from_sdf.hierarchy_remove'
    bl_label = 'Remove'
    bl_description = 'Remove an SDF Object from the hierarchy.'
    
    @classmethod
    def poll(cls, context):
        return (context.scene and context.scene.sdf_object_pointer_list and (len(context.scene.sdf_object_pointer_list) > context.scene.sdf_object_pointer_list_index) and (context.scene.sdf_object_pointer_list_index >= 0))
    
    def execute(self, context):
        global ctx, sdf_object_pointer_list_by_primitive_type, generate_storage_buffer_by_primitive_type
        
        alist = context.scene.sdf_object_pointer_list
        index = context.scene.sdf_object_pointer_list_index
        deleted_index = index
        if deleted_index > -1:
            object = context.scene.sdf_object_pointer_list[deleted_index].object
            primitive_type = object.sdf_prop.primitive_type
            if object != None:
                # Delete mesh
                if object.data:
                    bpy.data.meshes.remove(object.data,do_unlink=True)
                    
            alist.remove(deleted_index)
            PointerListUtil.refresh_pointer_list(context, primitive_type)
            
            # Decrements the index by 1 from the item whose index is larger than the deleted item
            for i in range(deleted_index,len(alist)):
                alist[i].object.sdf_prop.index -= 1
            
            if len(alist) > context.scene.sdf_object_pointer_list_index:
                pass
            else:
                context.scene.sdf_object_pointer_list_index = -1
                
            # Update the order of CollectionProperty(type=SDFObjectPointer).
            blist = sdf_object_pointer_list_by_primitive_type[primitive_type](context)
            alloc = generate_storage_buffer_by_primitive_type[primitive_type]
                
            # Reassign sub-indexes
            PointerListUtil.recalc_sub_index_without_sort(blist)
            
            # Rebuild Storage Buffer Objects
            alloc(ctx, context)
            ShaderBufferFactory.generate_object_common_buffer(ctx, context)
            
            # Generate shaders according to the current hierarchy
            f_dist = ShaderFactory.generate_distance_function(context.scene.sdf_object_pointer_list)
            print(f_dist)
                
            bpy.ops.ed.undo_push(message='mesh_from_sdf.hierarchy_remove')
        return {'FINISHED'}


class SDF2MESH_OT_List_Reorder(Operator):
        
    bl_idname = 'mesh_from_sdf.hierarchy_reorder'
    bl_label = 'Reorder'
    bl_description = 'Sort SDF Object in the specified direction.'
    
    direction: EnumProperty(items=(('UP', 'Up', ''),('DOWN', 'Down', ''),))
    
    @classmethod
    def poll(cls, context):
        return (context.scene and context.scene.sdf_object_pointer_list and len(context.scene.sdf_object_pointer_list) > 1)

    def move_index(self):
        index = bpy.context.scene.sdf_object_pointer_list_index
        list_length = len(bpy.context.scene.sdf_object_pointer_list) - 1
        new_index = index + (-1 if self.direction == 'UP' else 1)

        bpy.context.scene.sdf_object_pointer_list_index = max(0, min(new_index, list_length))

    def execute(self, context):
        global ctx, sdf_object_pointer_list_by_primitive_type, update_storage_buffer_by_primitive_type
        
        alist = context.scene.sdf_object_pointer_list
        index = context.scene.sdf_object_pointer_list_index

        neighbor = index + (-1 if self.direction == 'UP' else 1)
        alist[neighbor].object.sdf_prop.index = index # Exchange index property values with each other
        alist[index].object.sdf_prop.index = neighbor
        alist.move(neighbor, index)
        self.move_index()
        
        # Update the order of CollectionProperty(type=SDFObjectPointer).
        item_0 = alist[neighbor].object.sdf_prop
        item_1 = alist[index].object.sdf_prop
        if item_0.primitive_type == item_1.primitive_type:
            blist = None
            
            primitive_type = alist[neighbor].object.sdf_prop.primitive_type
            blist = sdf_object_pointer_list_by_primitive_type[primitive_type](context)
            
            blist.move(item_0.sub_index, item_1.sub_index)
            tmp = int(item_0.sub_index)
            item_0.sub_index = int(item_1.sub_index)
            item_1.sub_index = tmp

        # Update the parental relationship of an object
        index_0, index_1 = item_0.index, item_1.index
        nest_0, nest_1 = item_0.nest, item_1.nest
        SDFProperty.update_nest_prop(context, index_0, nest_0)
        SDFProperty.update_nest_prop(context, index_1, nest_1)

        # Updating Storage Buffer Objects
        sub_index_0, sub_index_1 = item_0.sub_index, item_1.sub_index
        alloc_0, alloc_1 = update_storage_buffer_by_primitive_type[item_0.primitive_type], update_storage_buffer_by_primitive_type[item_1.primitive_type]
        alloc_0(ctx, context, index_0, sub_index_0)
        alloc_1(ctx, context, index_1, sub_index_1)
        ShaderBufferFactory.update_object_common_buffer(ctx, context, index_0)
        ShaderBufferFactory.update_object_common_buffer(ctx, context, index_1)
            
        # Generate shaders according to the current hierarchy
        f_dist = ShaderFactory.generate_distance_function(context.scene.sdf_object_pointer_list)
        print(f_dist)
        
        bpy.ops.ed.undo_push(message='mesh_from_sdf.hierarchy_reorder')
        return {'FINISHED'}
    
    
class SDF2MESH_OT_Select_On_The_List(Operator):
    bl_idname = 'mesh_from_sdf.select_on_the_hierarchy'
    bl_label = 'Select on the hierarchy'
    bl_description = 'Select the objects displayed in Object Properties, also on the tallbox hierarchy.'
    
    def execute(self, context):
        context.scene.sdf_object_pointer_list_index = context.object.sdf_prop.index
        
        # Try redraw panel
        try:
            bpy.utils.unregister_class(SDF2MESH_PT_Panel)
        except:
            pass
        bpy.utils.register_class(SDF2MESH_PT_Panel)
        
        bpy.ops.ed.undo_push(message='mesh_from_sdf.hierarchy_select')
        return {'FINISHED'}


class SDF2MESH_OT_Select_On_The_Properties(Operator):
    bl_idname = 'mesh_from_sdf.select_on_the_properties'
    bl_label = 'Select on the properties'
    bl_description = 'Open the selected object in the hierarchy of the Toolbox with the Object Properties.'
    
    @classmethod
    def poll(cls, context):
        return (context.scene and context.scene.sdf_object_pointer_list and len(context.scene.sdf_object_pointer_list) > 1 and context.scene.sdf_object_pointer_list_index > -1)
    
    def execute(self, context):
        alist = context.scene.sdf_object_pointer_list
        index = context.scene.sdf_object_pointer_list_index
        pointer = alist[index]
        if pointer.object != None:
            bpy.context.view_layer.objects.active = pointer.object
            pointer.object.select_set(True)
            bpy.ops.ed.undo_push(message='mesh_from_sdf.properties_open')
        return {'FINISHED'}


class SDF2MESH_PT_Panel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'SDF2Mesh'
    bl_idname = 'SDF2MESH_PT_Panel'
    bl_label = 'Hierarchy'
    bl_description = 'Manage SDF Objects on the toolbox. Add, delete, and reorder objects in the hierarchy.'

    @classmethod
    def is_pointer_list_index_validity(cls, scene):
        return (scene.sdf_object_pointer_list_index > -1) and (scene.sdf_object_pointer_list_index < len(scene.sdf_object_pointer_list))

    def draw(self, context):
        scene = context.scene
        row = self.layout.row()
        col_l = row.column(align=True)
        col_l.template_list('SDF2MESH_UL_List', 'The_List', scene, 'sdf_object_pointer_list', scene, 'sdf_object_pointer_list_index')
        col_r = row.column(align=True)
        col_r.operator('mesh_from_sdf.hierarchy_add', text='', icon='ADD')
        col_r.operator('mesh_from_sdf.hierarchy_remove', text='', icon='REMOVE')
        
        if scene:
            if len(scene.sdf_object_pointer_list) > 1:
                
                col_r_0 = col_r.column()
                col_r_0.enabled = context.scene.sdf_object_pointer_list_index > 0
                col_r_0.operator('mesh_from_sdf.hierarchy_reorder', text='', icon='TRIA_UP').direction = 'UP'
                    
                col_r_1 = col_r.column()
                col_r_1.enabled = (context.scene.sdf_object_pointer_list_index > -1) and (context.scene.sdf_object_pointer_list_index < len(context.scene.sdf_object_pointer_list) - 1)
                col_r_1.operator('mesh_from_sdf.hierarchy_reorder', text='', icon='TRIA_DOWN').direction = 'DOWN'
                    
                if SDF2MESH_PT_Panel.is_pointer_list_index_validity(scene):
                    col_l.separator()
                    row_l = col_l.row()
                    pointer = scene.sdf_object_pointer_list[scene.sdf_object_pointer_list_index]
                    if (pointer.object != None) and (scene.sdf_object_pointer_list_index > 0):
                        prop = pointer.object.sdf_prop
                        row_l.prop(prop, "nest")
                    row_l.operator('mesh_from_sdf.select_on_the_properties', text='Select on the properties')
            
            col_r.separator()
            col_r = col_r.column()
            col_r.operator('mesh_from_sdf.hierarchy_reload', text='', icon='FILE_REFRESH')


# I changed the property drawing process from if else to lambda + dictionary approach. 
# For the same n elements, the lambda + dictionary approach is expected to reduce the 
# computational complexity to n / 2 (supposedly ...).

draw_sdf_object_property_by_primitive_type = {'Box': lambda context, col, item: (
                                                sub_item := context.scene.sdf_box_pointer_list[item.sub_index],
                                                col.prop(sub_item, 'bound'),
                                                col.prop(sub_item, 'round'),
                                                col.prop(item, 'round')),
                                              'Sphere': lambda context, col, item: (
                                                sub_item := context.scene.sdf_sphere_pointer_list[item.sub_index],
                                                col.prop(sub_item, 'radius'),
                                                col.prop(item, 'round')),
                                              'Cylinder': lambda context, col, item: (
                                                sub_item := context.scene.sdf_cylinder_pointer_list[item.sub_index],
                                                col.prop(sub_item, 'height'),
                                                col.prop(sub_item, 'radius'),
                                                col.prop(item, 'round')),
                                              'Torus': lambda context, col, item: (
                                                sub_item := context.scene.sdf_torus_pointer_list[item.sub_index],
                                                col.prop(sub_item, 'radius'),
                                                col.prop(sub_item, 'fill')),
                                              'Cone': lambda context, col, item: (
                                                sub_item := context.scene.sdf_cone_pointer_list[item.sub_index],
                                                col.prop(sub_item, 'height'),
                                                col.prop(sub_item, 'radius'),
                                                col.prop(item, 'round')),
                                              'Pyramid': lambda context, col, item: (
                                                sub_item := context.scene.sdf_pyramid_pointer_list[item.sub_index],
                                                col.prop(sub_item, 'width'),
                                                col.prop(sub_item, 'depth'),
                                                col.prop(sub_item, 'height'),
                                                col.prop(item, 'round')),
                                              'Truncated Pyramid': lambda context, col, item: (
                                                sub_item := context.scene.sdf_truncated_pyramid_pointer_list[item.sub_index],
                                                col.prop(sub_item, 'width_0'),
                                                col.prop(sub_item, 'depth_0'),
                                                col.prop(sub_item, 'width_1'),
                                                col.prop(sub_item, 'depth_1'),
                                                col.prop(sub_item, 'height'),
                                                col.prop(item, 'round')),
                                              'Hexagonal Prism': lambda context, col, item: (
                                                sub_item := context.scene.sdf_hex_prism_pointer_list[item.sub_index],
                                                col.prop(sub_item, 'radius'),
                                                col.prop(sub_item, 'height'),
                                                col.prop(item, 'round')),
                                              'Triangular Prism': lambda context, col, item: (
                                                sub_item := context.scene.sdf_tri_prism_pointer_list[item.sub_index],
                                                col.prop(sub_item, 'radius'),
                                                col.prop(sub_item, 'height'),
                                                col.prop(item, 'round')),
                                              'Ngon Prism': lambda context, col, item: (
                                                sub_item := context.scene.sdf_ngon_prism_pointer_list[item.sub_index],
                                                col.prop(sub_item, 'radius'),
                                                col.prop(sub_item, 'height'),
                                                col.prop(sub_item, 'nsides'),
                                                col.prop(item, 'round')),
                                              'GLSL': lambda context, col, item: (
                                                sub_item := context.scene.sdf_glsl_pointer_list[item.sub_index],
                                                col.prop(sub_item, 'shader_path'),
                                                col.prop(sub_item, 'bound'),
                                                col.prop(item, 'round'))}
                                                
draw_blend_property_by_blend_type = {'No Blending': lambda col, item: (),
                                     'Smooth': lambda col, item: col.prop(item, 'blend_smooth'),
                                     'Champfer': lambda col, item: col.prop(item, 'blend_champfer_size'),
                                     'Steps': lambda col, item: (
                                        col.prop(item, 'blend_step'),
                                        col.prop(item, 'blend_champfer_size')),
                                     'Round': lambda col, item: col.prop(item, 'blend_round')}                                                    


class SDFOBJECT_PT_Panel(Panel):
    bl_label = 'SDF Object'
    bl_idname = 'SDFOBJECT_PT_Panel'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_description = 'When the object is an SDF Object, each property for defining the shape is displayed.'

    def draw(self, context):
        global draw_sdf_object_property_by_primitive_type, draw_blend_property_by_blend_type
        
        object = context.active_object
        if object.sdf_prop.enabled:
            item = object.sdf_prop
            col = self.layout.column()
            col.prop(item, 'primitive_type')
            
            draw_sdf_object_property_by_primitive_type[item.primitive_type](context, col, item)

            col.separator()            
            col.prop(item, 'boolean_type')
            col.prop(item, 'blend_type')
            
            draw_blend_property_by_blend_type[item.blend_type](col, item)
            
            col.separator()
            col.operator('mesh_from_sdf.select_on_the_hierarchy', text='Select on the hierarchy')
        else:
            col = self.layout.column()
            col.label(text='This object is not an SDF object')


class OBJECT_OT_Delete_SDF(Operator):
    
    # TODO: Supports decrementing of indexes
    # STATE: Not tested yet
    
    bl_idname = 'object.delete_sdf'
    bl_label = 'Delete SDF Object'
    bl_description = 'Delete SDF object from the right-click context menu of the selected object. This operator can delete multiple SDF objects at once.'
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        alist = context.scene.sdf_object_pointer_list
        index = context.scene.sdf_object_pointer_list_index
        indexed_object = alist[index] if index > -1 else None
        indexed_object_deleted = False
        delete_target_objects = []
        for object in context.selected_objects:
            if object.sdf_prop.enabled:
                delete_target_objects.append(object)
        
        # TODO: Replace the order of the group of objects to be deleted in ascending order of index (use quic sort).
        # STATE:  Not tested yet
        # NOTE: Is this process really necessary? I don't think there will be a case where the order of index properties of items in AABB will be shifted.
        Algorithm.quick_sort_by_index(context.scene.sdf_object_pointer_list)

        # Delete mesh and update index properties of SDFObject.
        refresh_required_primitive_types = []
        decrement = 1
        for i,object in enumerate(delete_target_objects):
            if (indexed_object != None) and (object == indexed_object):
                indexed_object_deleted = True            
            if object.data:
                
                # Update the CollectionProperty(type=SDFObjectPointer) that references the deleted SDFObject.
                refresh_required_primitive_types.append(str(object.sdf_prop.prev_primitive_type))
                
                deleted_index = object.sdf_prop.index
                alist.remove(deleted_index)

                bpy.data.meshes.remove(object.data,do_unlink=True) # Delete mesh
                
                # Decrement the index because the object was deleted
                if (deleted_index > -1) and (len(alist) > 0) and (len(alist) > deleted_index):
                    next_neighbors_index = len(alist) - 1 if (i > len(delete_target_objects) - 2) else delete_target_objects[i + 1].object.sdf_prop.index
                    # Update index properties to include the following targets to be excluded.
                    for j in range(deleted_index, next_neighbors_index + 1):
                        alist[j].object.sdf_prop.index = alist[j].object.sdf_prop.index - decrement
                        
                    decrement = decrement + 1
                
        refresh_required_primitive_types = set(refresh_required_primitive_types) # Remove duplicates
        PointerListUtil.refresh_pointer_lists(context, refresh_required_primitive_types)
                
        if indexed_object_deleted == False:
            context.scene.sdf_object_pointer_list_index = -1
        else:
            context.scene.sdf_object_pointer_list_index = indexed_object.object.sdf_prop.index

        # Updating Storage Buffer Objects
        ShaderBufferFactory.generate_all(ctx, context)
            
        # Generate shaders according to the current hierarchy
        f_dist = ShaderFactory.generate_distance_function(context.scene.sdf_object_pointer_list)
        print(f_dist)
            
        bpy.ops.ed.undo_push(message='object.delete_sdf')
        return {'FINISHED'}


def sdf_object_delete_handler(self, context):
    self.layout.operator(OBJECT_OT_Delete_SDF.bl_idname, text='Delete (SDF Object)')


classes = [
    SDFProperty,
    SDFObjectPointer,
    SDFPrimitivePointer,
    SDFBoxPointer,
    SDFSpherePointer,
    SDFCylinderPointer,
    SDFConePointer,
    SDFTorusPointer,
    SDFPyramidPointer,
    SDFTruncatedPyramidPointer,
    SDFPrismPointer,
    SDFGLSLPointer,
    
    SDF2MESH_UL_List,
    SDF2MESH_OT_List_Reload,
    SDF2MESH_OT_List_Add,
    SDF2MESH_OT_List_Remove,
    SDF2MESH_OT_List_Reorder,
    SDF2MESH_OT_Select_On_The_List,
    SDF2MESH_OT_Select_On_The_Properties,
    SDF2MESH_PT_Panel,
    SDFOBJECT_PT_Panel,
    OBJECT_OT_Delete_SDF,
]

# List of lambda functions to build Storage Buffer Objects, keyed by primitive_type
# example: alloc = generate_storage_buffer_by_primitive_type[primitive_type](ctx, context)
global generate_storage_buffer_by_primitive_type
generate_storage_buffer_by_primitive_type = {'Box': lambda ctx, context: ShaderBufferFactory.generate_box_buffer(ctx, context),
                                             'Sphere': lambda ctx, context: ShaderBufferFactory.generate_sphere_buffer(ctx, context),
                                             'Cylinder': lambda ctx, context: ShaderBufferFactory.generate_cylinder_buffer(ctx, context),
                                             'Torus': lambda ctx, context: ShaderBufferFactory.generate_torus_buffer(ctx, context),
                                             'Cone': lambda ctx, context: ShaderBufferFactory.generate_cone_buffer(ctx, context),
                                             'Pyramid': lambda ctx, context: ShaderBufferFactory.generate_pyramid_buffer(ctx, context),
                                             'Truncated Pyramid': lambda ctx, context: ShaderBufferFactory.generate_truncated_pyramid_buffer(ctx, context),
                                             'Hexagonal Prism': lambda ctx, context: ShaderBufferFactory.generate_hex_prism_buffer(ctx, context),
                                             'Triangular Prism': lambda ctx, context: ShaderBufferFactory.generate_tri_prism_buffer(ctx, context),
                                             'Ngon Prism': lambda ctx, context: ShaderBufferFactory.generate_ngon_prism_buffer(ctx, context),
                                             'GLSL': lambda context: lambda ctx, context: ShaderBufferFactory.generate_glsl_buffer(ctx, context)}
                                             
# List of lambda functions to update Storage Buffer Objects, keyed by primitive_type
# example: alloc = update_storage_buffer_by_primitive_type[primitive_type](ctx, context, index, sub_index)
global update_storage_buffer_by_primitive_type
update_storage_buffer_by_primitive_type = {'Box': lambda ctx, context, index, sub_index: ShaderBufferFactory.update_box_buffer(ctx, context, index, sub_index),
                                           'Sphere': lambda ctx, context, index, sub_index: ShaderBufferFactory.update_sphere_buffer(ctx, context, index, sub_index),
                                           'Cylinder': lambda ctx, context, index, sub_index: ShaderBufferFactory.update_cylinder_buffer(ctx, context, index, sub_index),
                                           'Torus': lambda ctx, context, index, sub_index: ShaderBufferFactory.update_torus_buffer(ctx, context, index, sub_index),
                                           'Cone': lambda ctx, context, index, sub_index: ShaderBufferFactory.update_cone_buffer(ctx, context, index, sub_index),
                                           'Pyramid': lambda ctx, context, index, sub_index: ShaderBufferFactory.update_pyramid_buffer(ctx, context, index, sub_index),
                                           'Truncated Pyramid': lambda ctx, context, index, sub_index: ShaderBufferFactory.update_truncated_pyramid_buffer(ctx, context, index, sub_index),
                                           'Hexagonal Prism': lambda ctx, context, index, sub_index: ShaderBufferFactory.update_hex_prism_buffer(ctx, context, index, sub_index),
                                           'Triangular Prism': lambda ctx, context, index, sub_index: ShaderBufferFactory.update_tri_prism_buffer(ctx, context, index, sub_index),
                                           'Ngon Prism': lambda ctx, context, index, sub_index: ShaderBufferFactory.update_ngon_prism_buffer(ctx, context, index, sub_index),
                                           'GLSL': lambda ctx, context, index, sub_index: ShaderBufferFactory.update_glsl_buffer(ctx, context, index, sub_index)}


def deinit_shader():
    # Release Storage Buffer Objects
    ShaderBufferFactory.release_all()


# When an object's transform is updated, it is reflected in the Shader Buffer.
@persistent
def on_depsgraph_update(scene):
    global ctx
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for update in depsgraph.updates:
        if update.is_updated_transform:
            for obj in bpy.context.selected_objects:
                if obj.sdf_prop.enabled:
                    ShaderBufferFactory.update_object_common_buffer(ctx, bpy.context, obj.sdf_prop.index)
            print('[on_depsgraph_update] update transform')


global ctx, test_global
def register():
            
    global ctx
    ctx = create_context()
    pointer.set_context(ctx)
    Raymarching.set_context(ctx)
    MarchingCube.set_context(ctx)
    
    for c in classes:
        bpy.utils.register_class(c)

    raymarching.register()
    marching_cube.register()
    
    gizmo.box.register()
    gizmo.cylinder.register()
    gizmo.torus.register()

    bpy.types.OUTLINER_MT_object.append(sdf_object_delete_handler)
    bpy.types.VIEW3D_MT_object.append(sdf_object_delete_handler)
    bpy.types.VIEW3D_MT_object_context_menu.append(sdf_object_delete_handler)
    
    # Add the sdf property to the bpy.types.object
    bpy.types.Object.sdf_prop = PointerProperty(type = SDFProperty)
    
    # Display this list in the UI hierarchy on the scene view
    bpy.types.Scene.sdf_object_pointer_list = CollectionProperty(type = SDFObjectPointer)
    bpy.types.Scene.sdf_object_pointer_list_index = IntProperty(name = 'Index for sdf_object_pointer_list', default = 0)
    
    # List for sorting objects for each primitive when sdf_object_pointer_list is updated
    bpy.types.Scene.sdf_box_pointer_list = CollectionProperty(type = SDFBoxPointer)
    bpy.types.Scene.sdf_sphere_pointer_list = CollectionProperty(type = SDFSpherePointer)
    bpy.types.Scene.sdf_cylinder_pointer_list = CollectionProperty(type = SDFCylinderPointer)
    bpy.types.Scene.sdf_cone_pointer_list = CollectionProperty(type = SDFConePointer)
    bpy.types.Scene.sdf_torus_pointer_list = CollectionProperty(type = SDFTorusPointer)
    bpy.types.Scene.sdf_pyramid_pointer_list = CollectionProperty(type = SDFPyramidPointer)
    bpy.types.Scene.sdf_truncated_pyramid_pointer_list = CollectionProperty(type = SDFTruncatedPyramidPointer)
    bpy.types.Scene.sdf_hex_prism_pointer_list = CollectionProperty(type = SDFPrismPointer)
    bpy.types.Scene.sdf_tri_prism_pointer_list = CollectionProperty(type = SDFPrismPointer)
    bpy.types.Scene.sdf_ngon_prism_pointer_list = CollectionProperty(type = SDFPrismPointer)
    bpy.types.Scene.sdf_glsl_pointer_list = CollectionProperty(type = SDFGLSLPointer)
    
    print('[mesh_from_sdf] The add-on has been activated.')
    
    bpy.app.handlers.depsgraph_update_post.append(on_depsgraph_update)
    
    
def unregister():
    del bpy.types.Object.sdf_prop
    del bpy.types.Scene.sdf_object_pointer_list
    del bpy.types.Scene.sdf_object_pointer_list_index
    
    bpy.types.OUTLINER_MT_object.remove(sdf_object_delete_handler)
    bpy.types.VIEW3D_MT_object.remove(sdf_object_delete_handler)
    bpy.types.VIEW3D_MT_object_context_menu.remove(sdf_object_delete_handler)

    gizmo.box.unregister()
    gizmo.cylinder.unregister()
    gizmo.torus.register()

    marching_cube.unregister()
    raymarching.unregister()
    
    for c in classes:
        bpy.utils.unregister_class(c)
    
    deinit_shader()
        
    print('[mesh_from_sdf] Add-on has been disabled.')
    
    bpy.app.handlers.depsgraph_update_post.remove(on_depsgraph_update)

        
if __name__ == '__main__':
    register()