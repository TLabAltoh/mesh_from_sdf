
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
from mesh_from_sdf.material_util import *
from mesh_from_sdf.moderngl_util import *
from mesh_from_sdf.raymarching import *
from mesh_from_sdf.marching_cube import *
from mesh_from_sdf.marching_tables import *
from mesh_from_sdf.shader_factory import *
from mesh_from_sdf.shader_buffer_factory import *
from bpy.app.handlers import persistent
from bpy.types import Panel, Operator, UIList, PropertyGroup
from bpy.props import PointerProperty, EnumProperty, FloatProperty, IntProperty, StringProperty, BoolProperty, CollectionProperty


class SDFProperty(PropertyGroup):

    primitive_types = (('Box', 'Box', ''),
            ('Sphere', 'Sphere', ''),
            ('Cylinder','Cylinder',''),
            ('Cone','Cone',''),
            ('Torus','Torus',''),
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

    # -----------------------------------------------------
    # Callback process called when a property is changed
    # 

    def property_event_on_object_prop_updated(self, context):
        global ctx
        
        # Updateing Storage Buffre Objects
        ShaderBufferFactory.update_object_common_buffer(ctx, context, self.index)
        
        # Generate shaders according to the current hierarchy
        f_dist = ShaderFactory.generate_distance_function(context.scene.sdf_object_pointer_list)
        print(f_dist)
        
    def property_event_on_object_nest_prop_updated(self, context):
        global ctx
        
        # Update the parent-child relationship based on the current nesting properties of the SDFObject
        self.__class__.update_nest_prop(context, self.index, self.nest)
        
        # Updateing Storage Buffre Objects
        ShaderBufferFactory.update_object_common_buffer(ctx, context, self.index)
        
        # Generate shaders according to the current hierarchy
        f_dist = ShaderFactory.generate_distance_function(context.scene.sdf_object_pointer_list)
        print(f_dist)

    def property_event_on_box_prop_updated(self, context):
        global ctx

        # Update mesh for primitive interactions
        prev_mode = self.__class__.update_primitive_mesh_begin(context)
        self.__class__.update_box_mesh(context.scene.sdf_object_pointer_list[self.index])
        self.__class__.update_primitive_mesh_end(prev_mode)
        
        # Updateing Storage Buffre Objects
        ShaderBufferFactory.update_box_buffer(ctx, context, self.index, self.sub_index)
        
        # Generate shaders according to the current hierarchy
        f_dist = ShaderFactory.generate_distance_function(context.scene.sdf_object_pointer_list)
        print(f_dist)
    
    def property_event_on_sphere_prop_updated(self, context):
        global ctx

        # Update mesh for primitive interactions
        prev_mode = self.__class__.update_primitive_mesh_begin(context)
        self.__class__.update_sphere_mesh(context.scene.sdf_object_pointer_list[self.index])
        self.__class__.update_primitive_mesh_end(prev_mode)
        
        # Updateing Storage Buffre Objects
        ShaderBufferFactory.update_sphere_buffer(ctx, context, self.index, self.sub_index)
        
        # Generate shaders according to the current hierarchy
        f_dist = ShaderFactory.generate_distance_function(context.scene.sdf_object_pointer_list)
        print(f_dist)
    
    def property_event_on_cylinder_prop_updated(self, context):
        global ctx
        
        # Update mesh for primitive interactions
        prev_mode = self.__class__.update_primitive_mesh_begin(context)
        self.__class__.update_cylinder_mesh(context.scene.sdf_object_pointer_list[self.index])
        self.__class__.update_primitive_mesh_end(prev_mode)
        
        # Updateing Storage Buffre Objects
        ShaderBufferFactory.update_cylinder_buffer(ctx, context, self.index, self.sub_index)
        
        # Generate shaders according to the current hierarchy
        f_dist = ShaderFactory.generate_distance_function(context.scene.sdf_object_pointer_list)
        print(f_dist)
    
    def property_event_on_cone_prop_updated(self, context):
        global ctx

        # Update mesh for primitive interactions
        prev_mode = self.__class__.update_primitive_mesh_begin(context)
        self.__class__.update_cone_mesh(context.scene.sdf_object_pointer_list[self.index])
        self.__class__.update_primitive_mesh_end(prev_mode)
        
        # Updateing Storage Buffre Objects
        ShaderBufferFactory.update_cone_buffer(ctx, context, self.index, self.sub_index)
        
        # Generate shaders according to the current hierarchy
        f_dist = ShaderFactory.generate_distance_function(context.scene.sdf_object_pointer_list)
        print(f_dist)
    
    def property_event_on_torus_prop_updated(self, context):
        global ctx

        # Update mesh for primitive interactions
        prev_mode = self.__class__.update_primitive_mesh_begin(context)
        self.__class__.update_torus_mesh(context.scene.sdf_object_pointer_list[self.index])
        self.__class__.update_primitive_mesh_end(prev_mode)
        
        # Updateing Storage Buffre Objects
        ShaderBufferFactory.update_torus_buffer(ctx, context, self.index, self.sub_index)
        
        # Generate shaders according to the current hierarchy
        f_dist = ShaderFactory.generate_distance_function(context.scene.sdf_object_pointer_list)
        print(f_dist)

    # List of SDFProperty.update_{nsides}_mesh and ShaderBufferFactory.update_{nsides_prism}_buffer, keyed by prism_type
    # example: update = update_prism_mesh_and_buffer_by_prism_type[primitive_type]
    #          update(ctx, context, self.index, self.sub_index) # execute
    global update_prism_mesh_and_buffer_by_prism_type
    update_prism_mesh_and_buffer_by_prism_type = {'Hexagonal Prism': lambda ctx, context, index, sub_index: (
                                                SDFProperty.update_hex_prism_mesh(context.scene.sdf_object_pointer_list[index]),
                                                ShaderBufferFactory.update_hex_prism_buffer(ctx, context, index, sub_index)),
                                                  'Triangular Prism': lambda ctx, context, index, sub_index: (
                                                SDFProperty.update_tri_prism_mesh(context.scene.sdf_object_pointer_list[index]),
                                                ShaderBufferFactory.update_tri_prism_buffer(ctx, context, index, sub_index)),
                                                  'Ngon Prism': lambda ctx, context, index, sub_index: (
                                                SDFProperty.update_ngon_prism_mesh(context.scene.sdf_object_pointer_list[index]),
                                                ShaderBufferFactory.update_ngon_prism_buffer(ctx, context, index, sub_index))}
    
    def property_event_on_prism_prop_updated(self, context):
        global ctx, update_prism_mesh_and_buffer_by_prism_type
        
        # Updateing Prism Mesh and Storage Buffre Objects
        # Determine how many angles you are with an if statement.    
        prev_mode = self.__class__.update_primitive_mesh_begin(context)
        update_prism_mesh_and_buffer_by_prism_type[self.primitive_type](ctx, context, self.index, self.sub_index)
        self.__class__.update_primitive_mesh_end(prev_mode)
        
        # Generate shaders according to the current hierarchy
        f_dist = ShaderFactory.generate_distance_function(context.scene.sdf_object_pointer_list)
        print(f_dist)
    
    def property_event_on_ngon_prism_prop_updated(self, context):
        global ctx
        
        # Update mesh for primitive interactions
        prev_mode = self.__class__.update_primitive_mesh_begin(context)
        self.__class__.update_ngon_prism_mesh(context.scene.sdf_object_pointer_list[self.index])
        self.__class__.update_primitive_mesh_end(prev_mode)
        
        # Updateing Storage Buffre Objects
        ShaderBufferFactory.update_ngon_prism_buffer(ctx, context, self.index, self.sub_index)
        
        # Generate shaders according to the current hierarchy
        f_dist = ShaderFactory.generate_distance_function(context.scene.sdf_object_pointer_list)
        print(f_dist)
    
    def property_event_on_glsl_prop_updated(self, context):
        pass

    # -----------------------------------------------------
    # Update mesh for editing SDF objects
    # 

    @classmethod
    def update_box_mesh(cls, object):
        sdf_prop = object.sdf_prop
                
        bound = sdf_prop.prop_box_bound
        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='CURSOR', location=object.location, rotation=object.rotation_euler, scale=object.scale)

        mesh = object.data
        bm = bmesh.from_edit_mesh(mesh)
        for i, vert in enumerate(bm.verts):
            vert.co[0] = vert.co[0] * bound[0]
            vert.co[1] = vert.co[1] * bound[1]
            vert.co[2] = vert.co[2] * bound[2]
        bmesh.update_edit_mesh(mesh)

    @classmethod
    def update_sphere_mesh(cls, pointer):
        sdf_prop = pointer.object.sdf_prop
        
        radius = sdf_prop.prop_sphere_radius
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='CURSOR', location=object.location, rotation=object.rotation_euler, scale=object.scale)

    @classmethod
    def update_cylinder_mesh(cls, pointer):
        sdf_prop = pointer.object.sdf_prop
        
        height = sdf_prop.prop_cylinder_height
        radius = sdf_prop.prop_cylinder_radius
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=height, enter_editmode=False, align='CURSOR', location=object.location, rotation=object.rotation_euler, scale=object.scale)
        
    @classmethod
    def update_cone_mesh(cls, pointer):
        sdf_prop = pointer.object.sdf_prop
        
        height = sdf_prop.prop_cone_height
        radius = sdf_prop.prop_cone_radius
        bpy.ops.mesh.primitive_cone_add(radius1=radius[0], radius2=radius[1], depth=height, enter_editmode=False, align='CURSOR', location=object.location, rotation=object.rotation_euler, scale=object.scale)
        
    @classmethod
    def update_torus_mesh(cls, pointer):
        sdf_prop = pointer.object.sdf_prop
        
        prv_scale = (object.scale[0], object.scale[1], object.scale[2])
        object.scale = (1,1,1)
        radius = sdf_prop.prop_torus_radius
        bpy.ops.mesh.primitive_torus_add(major_radius=radius[0], minor_radius=radius[1], abso_major_rad=1.25, abso_minor_rad=0.75, align='CURSOR', location=object.location, rotation=object.rotation_euler)
        object.scale = prv_scale
        
    @classmethod
    def update_hex_prism_mesh(cls, pointer):
        sdf_prop = pointer.object.sdf_prop
        
        height = sdf_prop.prop_prism_height
        radius = sdf_prop.prop_prism_radius
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=radius, depth=height, enter_editmode=False, align='CURSOR', location=object.location, rotation=object.rotation_euler, scale=object.scale)
        
    @classmethod
    def update_tri_prism_mesh(cls, pointer):
        sdf_prop = pointer.object.sdf_prop
        
        height = sdf_prop.prop_prism_height
        radius = sdf_prop.prop_prism_radius
        bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=radius, depth=height, enter_editmode=False, align='CURSOR', location=object.location, rotation=object.rotation_euler, scale=object.scale)
        
    @classmethod
    def update_ngon_prism_mesh(cls, pointer):
        sdf_prop = pointer.object.sdf_prop
        
        nsides = sdf_prop.prop_prism_nsides
        height = sdf_prop.prop_prism_height
        radius = sdf_prop.prop_prism_radius
        bpy.ops.mesh.primitive_cylinder_add(vertices=nsides, radius=radius, depth=height, enter_editmode=False, align='CURSOR', location=object.location, rotation=object.rotation_euler, scale=object.scale)
        
    @classmethod
    def update_glsl_mesh(cls, pointer):
        sdf_prop = pointer.object.sdf_prop
        
        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='CURSOR', location=object.location, rotation=object.rotation_euler, scale=object.scale)

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

    def property_event_on_primitive_type_changed(self, context):
        global ctx
        # Undo works for this operation
        prev_primitive_type = self.prev_primitive_type
        primitive_type = self.primitive_type
        if primitive_type != prev_primitive_type:
            object = context.object
            mesh = object.data
            if mesh:
                # Cache the current mode and enter edit mode to clear the mesh
                prev_mode = self.__class__.update_primitive_mesh_begin(context)

                # Delete objects to be updated from the list in advance.
                SDFOBJECT_UTILITY.delete_from_sub_pointer_list(context, object)

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
                    self.__class__.update_box_mesh(prv_pointer)
                    blist = context.scene.sdf_box_pointer_list
                    alloc = lambda ctx, context: ShaderBufferFactory.generate_box_buffer(ctx, context)
                elif (primitive_type == 'Sphere') and (SDFProperty.contains_in_pointer_list(context.scene.sdf_sphere_pointer_list, prv_pointer.object) == False):
                    self.__class__.update_sphere_mesh(prv_pointer)
                    blist = context.scene.sdf_sphere_pointer_list
                    alloc = lambda ctx, context: ShaderBufferFactory.generate_sphere_buffer(ctx, context)
                elif (primitive_type == 'Cylinder') and (SDFProperty.contains_in_pointer_list(context.scene.sdf_cylinder_pointer_list, prv_pointer.object) == False):
                    self.__class__.update_cylinder_mesh(prv_pointer)
                    blist = context.scene.sdf_cylinder_pointer_list
                    alloc = lambda ctx, context: ShaderBufferFactory.generate_cylinder_buffer(ctx, context)
                elif (primitive_type == 'Cone') and (SDFProperty.contains_in_pointer_list(context.scene.sdf_cone_pointer_list, prv_pointer.object) == False):
                    self.__class__.update_cone_mesh(prv_pointer)
                    blist = context.scene.sdf_cone_pointer_list
                    alloc = lambda ctx, context: ShaderBufferFactory.generate_cone_buffer(ctx, context)
                elif (primitive_type == 'Torus') and (SDFProperty.contains_in_pointer_list(context.scene.sdf_torus_pointer_list, prv_pointer.object) == False):
                    # Torus has no argument to scale with primitive_add. Scaling is applied manually.
                    self.__class__.update_torus_mesh(prv_pointer)
                    blist = context.scene.sdf_torus_pointer_list
                    alloc = lambda ctx, context: ShaderBufferFactory.generate_torus_buffer(ctx, context)
                elif (primitive_type == 'Hexagonal Prism') and (SDFProperty.contains_in_pointer_list(context.scene.sdf_hex_prism_pointer_list, prv_pointer.object) == False):
                    self.__class__.update_hex_prism_mesh(prv_pointer)
                    blist = context.scene.sdf_hex_prism_pointer_list
                    alloc = lambda ctx, context: ShaderBufferFactory.generate_hex_prism_buffer(ctx, context)
                elif (primitive_type == 'Triangular Prism') and (SDFProperty.contains_in_pointer_list(context.scene.sdf_tri_prism_pointer_list, prv_pointer.object) == False):
                    self.__class__.update_tri_prism_mesh(prv_pointer)
                    blist = context.scene.sdf_tri_prism_pointer_list
                    alloc = lambda ctx, context: ShaderBufferFactory.generate_tri_prism_buffer(ctx, context)
                elif (primitive_type == 'Ngon Prism') and (SDFProperty.contains_in_pointer_list(context.scene.sdf_ngon_prism_pointer_list, prv_pointer.object) == False):
                    self.__class__.update_ngon_prism_mesh(prv_pointer)
                    blist = context.scene.sdf_ngon_prism_pointer_list
                    alloc = lambda ctx, context: ShaderBufferFactory.generate_ngon_prism_buffer(ctx, context)
                elif (primitive_type == 'GLSL') and (SDFProperty.contains_in_pointer_list(context.scene.sdf_glsl_pointer_list, prv_pointer.object) == False):
                    self.__class__.update_glsl_mesh(prv_pointer)
                    blist = context.scene.sdf_glsl_pointer_list
                    alloc = lambda ctx, context: ShaderBufferFactory.generate_glsl_buffer(ctx, context)

                # Add new SDFObject to list
                if blist != None:
                    new_pointer = blist.add()
                    new_pointer.object = prv_pointer.object
                    SDFOBJECT_UTILITY.recalc_sub_index(blist)                    
                    # Rebuild Storage Buffer Objects
                    alloc(ctx, context)
                    ShaderBufferFactory.generate_object_common_buffer(ctx, context)
                    
                # Return from Edit mode to the previous mode
                object.sdf_prop.prev_primitive_type = object.sdf_prop.primitive_type
                
                # Restore mode to previous mode
                self.__class__.update_primitive_mesh_end(prev_mode)
                
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
        update=property_event_on_object_nest_prop_updated)
    
    # common
    boolean_type: EnumProperty(
        name='Boolean',
        description='',
        items=boolean_types,
        update=property_event_on_object_prop_updated)
        
    blend_type: EnumProperty(
        name='Blend',
        description='',
        items=blend_types,
        update=property_event_on_object_prop_updated)

    blend_champfer_size: FloatProperty(
        name='Champfer Size',
        description='',
        min=0.0,
        default=0.0,
        update=property_event_on_object_prop_updated)

    blend_step: IntProperty(
        name='Step',
        description='',
        min=1,
        default=1,
        update=property_event_on_object_prop_updated)

    blend_round: FloatProperty(
        name='Round',
        description='',
        min=0.0,
        default=0.0,
        update=property_event_on_object_prop_updated)

    blend_smooth: FloatProperty(
        name='Smooth',
        description='',
        min=0.0,
        max=1.0,
        default=0.5,
        update=property_event_on_object_prop_updated)
           
    round: FloatProperty(
       name='Round',
       description='',
       min=0.0,
       max=1.0,
       default=0.0,
       update=property_event_on_object_prop_updated)
           
    prev_primitive_type: EnumProperty(
        description='',
        items=primitive_types)
        
    primitive_type: EnumProperty(
        name='Primitive',
        description='',
        items=primitive_types,
        update=property_event_on_primitive_type_changed)

    # box    
    prop_box_bound: bpy.props.FloatVectorProperty(
        name='Bound',
        description='Radius',
        size=3,
        min=0.0,
        default=(1.0,1.0,1.0),
        update=property_event_on_box_prop_updated)
    
    # sphere
    prop_sphere_radius: bpy.props.FloatProperty(
        name='Radius',
        description='',
        min=0.0,
        default=1.0,
        update=property_event_on_sphere_prop_updated)
    
    # cylinder
    prop_cylinder_height: bpy.props.FloatProperty(
        name='Height',
        description='',
        min=0.0,
        default=2.0,
        update=property_event_on_cylinder_prop_updated)
        
    prop_cylinder_radius: bpy.props.FloatProperty(
        name='Radius',
        description='',
        min=0.0,
        default=1.0,
        update=property_event_on_cylinder_prop_updated)
    
    # torus
    prop_torus_radius: bpy.props.FloatVectorProperty(
        name='Radius',
        description='',
        size=2,
        min=0.0,
        default=(1.00,0.25),
        update=property_event_on_torus_prop_updated)

    # cone
    prop_cone_height: bpy.props.FloatProperty(
        name='Height',
        description='',
        min=0.0,
        default=2.0,
        update=property_event_on_cone_prop_updated)
    
    prop_cone_radius: bpy.props.FloatVectorProperty(
        name='Radius',
        description='',
        size=2,
        min=0.0,
        default=(0.25,0.75),
        update=property_event_on_cone_prop_updated)
    
    # prism
    prop_prism_radius: bpy.props.FloatProperty(
        name='Radius',
        description='',
        min=0.0,
        default=1.0,
        update=property_event_on_prism_prop_updated)
        
    prop_prism_height: bpy.props.FloatProperty(
        name='Height',
        description='',
        min=0.0,
        default=3.0,
        update=property_event_on_prism_prop_updated)
        
    prop_prism_nsides: bpy.props.IntProperty(
        name='N',
        description='',
        min=3,
        default=6,
        update=property_event_on_ngon_prism_prop_updated)
    
    # glsl
    prop_glsl_bound: bpy.props.FloatVectorProperty(
        name='Bound',
        description='',
        size=3,
        min=0.0,
        default=(1.0,1.0,1.0),
        update=property_event_on_glsl_prop_updated)
    
    prop_glsl_shader_path: StringProperty(
        name='Shader PATH',
        description='',
        default='C:\\',
        update=property_event_on_glsl_prop_updated)
           
           
class SDFObjectPointer(PropertyGroup):
    object: PointerProperty(type=bpy.types.Object)


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
        SDFOBJECT_UTILITY.recalc_sub_index(context.scene.sdf_box_pointer_list)
        SDFOBJECT_UTILITY.recalc_sub_index(context.scene.sdf_sphere_pointer_list)
        SDFOBJECT_UTILITY.recalc_sub_index(context.scene.sdf_cylinder_pointer_list)
        SDFOBJECT_UTILITY.recalc_sub_index(context.scene.sdf_cone_pointer_list)
        SDFOBJECT_UTILITY.recalc_sub_index(context.scene.sdf_torus_pointer_list)
        SDFOBJECT_UTILITY.recalc_sub_index(context.scene.sdf_hex_prism_pointer_list)
        SDFOBJECT_UTILITY.recalc_sub_index(context.scene.sdf_tri_prism_pointer_list)
        SDFOBJECT_UTILITY.recalc_sub_index(context.scene.sdf_ngon_prism_pointer_list)
        SDFOBJECT_UTILITY.recalc_sub_index(context.scene.sdf_glsl_pointer_list)

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
            SDFOBJECT_UTILITY.refresh_pointer_list(context, primitive_type)
            
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
            SDFOBJECT_UTILITY.recalc_sub_index_without_sort(blist)
            
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

draw_sdf_object_property_by_primitive_type = {'Box': lambda col, item: (
                                                col.prop(item, 'prop_box_bound'),
                                                col.prop(item, 'round')),
                                              'Sphere': lambda col, item: (
                                                col.prop(item, 'prop_sphere_radius'),
                                                col.prop(item, 'round')),
                                              'Cylinder': lambda col, item: (
                                                col.prop(item, 'prop_cylinder_height'),
                                                col.prop(item, 'prop_cylinder_radius'),
                                                col.prop(item, 'round')),
                                              'Torus': lambda col, item: (
                                                col.prop(item, 'prop_torus_radius')),
                                              'Hexagonal Prism': lambda col, item: (
                                                col.prop(item, 'prop_prism_radius'),
                                                col.prop(item, 'prop_prism_height')),
                                              'Triangular Prism': lambda col, item: (
                                                col.prop(item, 'prop_prism_radius'),
                                                col.prop(item, 'prop_prism_height'),
                                                col.prop(item, 'round')),
                                              'Ngon Prism': lambda col, item: (
                                                col.prop(item, 'prop_prism_radius'),
                                                col.prop(item, 'prop_prism_height'),
                                                col.prop(item, 'prop_prism_nsides'),
                                                col.prop(item, 'round')),
                                              'Cone': lambda col, item: (
                                                col.prop(item, 'prop_cone_height'),
                                                col.prop(item, 'prop_cone_radius'),
                                                col.prop(item, 'round')),
                                              'GLSL': lambda col, item: (
                                                col.prop(item, 'prop_glsl_shader_path'),
                                                col.prop(item, 'prop_glsl_bound'))}
                                                
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
            
            draw_sdf_object_property_by_primitive_type[item.primitive_type](col, item)

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
        Algorithms.quick_sort_by_index(context.scene.sdf_object_pointer_list)

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
        SDFOBJECT_UTILITY.refresh_pointer_lists(context, refresh_required_primitive_types)
                
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


class Algorithms(object):
    
    # Only sorting algorithm for now.

    @classmethod
    def __quick_sort_by_index(cls, alist, l, r):
        # https://zenn.dev/yutabeee/articles/e8fb2847cfc980
        
        i = l
        j = r
        p = (l + r) // 2
        
        while True:
            while alist[i].object.sdf_prop.index < alist[p].object.sdf_prop.index:
                i = i + 1
            while alist[j].object.sdf_prop.index > alist[p].object.sdf_prop.index:
                j = j - 1
                
            if i >= j:
                break
            
            alist.move(i,j)
            
            if l < i - 1:
                cls.__quick_sort_by_index(alist, l, i - 1)
            if r > j + 1:
                cls.__quick_sort_by_index(alist, j + 1, r)
    
    @classmethod
    def quick_sort_by_index(cls, alist):
        # Algorithms.quick_sort_by_index(cls, alist)
        if len(alist) == 0:
            return;
        cls.__quick_sort_by_index(alist, 0, len(alist) - 1)


class SDFOBJECT_UTILITY(object):
    
    @classmethod
    def recalc_sub_index_without_sort(cls, alist):
        # SDFOBJECT_UTILITY.recalc_sub_index_without_sort(alist)
        cls.__refresh_pointer_list(alist)
        
        for i, pointer in enumerate(alist):
            pointer.object.sdf_prop.sub_index = i
    
    @classmethod
    def recalc_sub_index(cls, alist):
        # SDFOBJECT_UTILITY.recalc_sub_index(alist)
        cls.__refresh_pointer_list(alist)
             
        Algorithms.quick_sort_by_index(alist)
        
        for i, pointer in enumerate(alist):
            pointer.object.sdf_prop.sub_index = i
    
    @classmethod
    def __refresh_pointer_list(cls, alist):

        len_ = len(alist)
        if len_ == 0:
            return
        
        # Items with no referenced object and duplicated SDFObject are removed from the list.        
        cache = []
        i = -1
        while i < len_:
            i += 1
            pointer = alist[i]
            if pointer.object == None or (pointer.object in cache):
                alist.remove(i)
                i -= 1
                len_ -= 1
                continue
            cache.append(pointer.object)

    @classmethod
    def refresh_pointer_list(cls, context, primitive_type):
        global sdf_object_pointer_list_by_primitive_type
        cls.__refresh_pointer_list(sdf_object_pointer_list_by_primitive_type[primitive_type](context))
            
    @classmethod
    def refresh_pointer_lists(cls, context, primitive_types):
        for primitive_type in primitive_types:
            cls.refresh_pointer_list(context, primitive_type)
            
    @classmethod
    def __delete_from_sub_pointer_list(cls, alist, target):
        delete_index = -1
        for i,pointer in enumerate(alist):
            if (pointer.object == None) or (pointer.object == target):
                delete_index = i
                break
        if delete_index > -1:
            alist.remove(delete_index)
            # After deleting an object, update the sub-indexes of the currently existing objects
            for i in range(delete_index, len(alist)):
                alist[i].object.sdf_prop.sub_index = alist[i].object.sdf_prop.sub_index - 1

    @classmethod
    def delete_from_sub_pointer_list(cls, context, target):
        global sdf_object_pointer_list_by_primitive_type
        primitive_type = target.sdf_prop.prev_primitive_type
        cls.__delete_from_sub_pointer_list(sdf_object_pointer_list_by_primitive_type[primitive_type](context), target)


def sdf_object_delete_handler(self, context):
    self.layout.operator(OBJECT_OT_Delete_SDF.bl_idname, text='Delete (SDF Object)')


classes = [
    SDFProperty,
    SDFObjectPointer,
    
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


# List of SDFProperty, keyed by primitive_type
# example: alist = sdf_object_pointer_list_by_primitive_type[primitive_type](context)
global sdf_object_pointer_list_by_primitive_type
sdf_object_pointer_list_by_primitive_type = {'Box': lambda context: context.scene.sdf_box_pointer_list,
                                     'Sphere': lambda context: context.scene.sdf_sphere_pointer_list,
                                     'Cylinder': lambda context: context.scene.sdf_cylinder_pointer_list,
                                     'Torus': lambda context: context.scene.sdf_torus_pointer_list,
                                     'Cone': lambda context: context.scene.sdf_cone_pointer_list,
                                     'Hexagonal Prism': lambda context: context.scene.sdf_hex_prism_pointer_list,
                                     'Triangular Prism': lambda context: context.scene.sdf_tri_prism_pointer_list,
                                     'Ngon Prism': lambda context: context.scene.sdf_ngon_prism_pointer_list,
                                     'GLSL': lambda context: context.scene.sdf_glsl_prism_pointer_list}

# List of lambda functions to build Storage Buffer Objects, keyed by primitive_type
# example: alloc = generate_storage_buffer_by_primitive_type[primitive_type](ctx, context)
global generate_storage_buffer_by_primitive_type
generate_storage_buffer_by_primitive_type = {'Box': lambda ctx, context: ShaderBufferFactory.generate_box_buffer(ctx, context),
                                             'Sphere': lambda ctx, context: ShaderBufferFactory.generate_sphere_buffer(ctx, context),
                                             'Cylinder': lambda ctx, context: ShaderBufferFactory.generate_cylinder_buffer(ctx, context),
                                             'Torus': lambda ctx, context: ShaderBufferFactory.generate_torus_buffer(ctx, context),
                                             'Cone': lambda ctx, context: ShaderBufferFactory.generate_cone_buffer(ctx, context),
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


global ctx
def register():
        
    global ctx
    ctx = moderngl_util.create_context()
    Raymarching.set_context(ctx)
    MarchingCube.set_context(ctx)
    
    for c in classes:
        bpy.utils.register_class(c)

    raymarching.register()
    marching_cube.register()

    bpy.types.OUTLINER_MT_object.append(sdf_object_delete_handler)
    bpy.types.VIEW3D_MT_object.append(sdf_object_delete_handler)
    bpy.types.VIEW3D_MT_object_context_menu.append(sdf_object_delete_handler)
    
    # Add the sdf property to the bpy.types.object
    bpy.types.Object.sdf_prop = PointerProperty(type = SDFProperty)
    
    # Display this list in the UI hierarchy on the scene view
    bpy.types.Scene.sdf_object_pointer_list = CollectionProperty(type = SDFObjectPointer)
    bpy.types.Scene.sdf_object_pointer_list_index = IntProperty(name = 'Index for sdf_object_pointer_list', default = 0)
    
    # List for sorting objects for each primitive when sdf_object_pointer_list is updated
    bpy.types.Scene.sdf_box_pointer_list = CollectionProperty(type = SDFObjectPointer)
    bpy.types.Scene.sdf_sphere_pointer_list = CollectionProperty(type = SDFObjectPointer)
    bpy.types.Scene.sdf_cylinder_pointer_list = CollectionProperty(type = SDFObjectPointer)
    bpy.types.Scene.sdf_cone_pointer_list = CollectionProperty(type = SDFObjectPointer)
    bpy.types.Scene.sdf_torus_pointer_list = CollectionProperty(type = SDFObjectPointer)
    bpy.types.Scene.sdf_hex_prism_pointer_list = CollectionProperty(type = SDFObjectPointer)
    bpy.types.Scene.sdf_tri_prism_pointer_list = CollectionProperty(type = SDFObjectPointer)
    bpy.types.Scene.sdf_ngon_prism_pointer_list = CollectionProperty(type = SDFObjectPointer)
    bpy.types.Scene.sdf_glsl_pointer_list = CollectionProperty(type = SDFObjectPointer)
    
    print('[mesh_from_sdf] The add-on has been activated.')
    
    bpy.app.handlers.depsgraph_update_post.append(on_depsgraph_update)
    

def unregister():
    del bpy.types.Object.sdf_prop
    del bpy.types.Scene.sdf_object_pointer_list
    del bpy.types.Scene.sdf_object_pointer_list_index
    
    bpy.types.OUTLINER_MT_object.remove(sdf_object_delete_handler)
    bpy.types.VIEW3D_MT_object.remove(sdf_object_delete_handler)
    bpy.types.VIEW3D_MT_object_context_menu.remove(sdf_object_delete_handler)

    marching_cube.unregister()
    raymarching.unregister()
    
    for c in classes:
        bpy.utils.unregister_class(c)
    
    deinit_shader()
        
    print('[mesh_from_sdf] Add-on has been disabled.')
    
    bpy.app.handlers.depsgraph_update_post.remove(on_depsgraph_update)

        
if __name__ == '__main__':
    register()