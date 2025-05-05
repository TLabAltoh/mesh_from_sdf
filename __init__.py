
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
import numpy as np
from mesh_from_sdf import raymarching as ry
# from mesh_from_sdf import marching_cube as mc
from mesh_from_sdf import marching_tables as mt
from bpy.app.handlers import persistent
from bpy.types import Panel, Operator, UIList, PropertyGroup
from bpy.props import PointerProperty, EnumProperty, FloatProperty, IntProperty, StringProperty, BoolProperty, CollectionProperty


class ShaderFactory(object):
    pass


class ShaderBufferFactory(object):
    
    buffers = {}
    
    @classmethod
    def generate_buffer(cls, ctx, key, size, item_size = 1):
        size = size * item_size
        if key in cls.buffers:
            buffer = cls.buffers[key]
            buffer.orphan(size)
        else:
            buffer = ctx.buffer(reserve=size, dynamic=True)
            cls.buffers[key] = buffer
    
    @classmethod
    def update_buffer(cls, key, offset, data):
        if key in cls.buffers:
            buffer = cls.buffers[key]
            buffer.write(data, offset)
            
    @classmethod
    def release_buffer(cls, key):
        if key in cls.buffers:
            buffer = cls.buffers[key]
            buffre.release()
            del cls.buffres[key]
    
    @classmethod
    def release_all(cls):
        for buffer in cls.buffers:
            buffre.release()
        cls.buffers.clear()
        
    
#    count_buf = cls.ctx.buffer(data=b'\x00\x00\x00\x00')
#    count_buf.bind_to_storage_buffer(0)
#    tri_siz = 3*3+1
#    out_buf = np.empty((cls.max_triangle_count,tri_siz),dtype=np.float32).tobytes()
#    out_buf = cls.ctx.buffer(out_buf) # 128 --> 400MB, 256 --> 3019 MB (map error !)
#    out_buf.bind_to_storage_buffer(1)
#    compute_shader["boxOffset"].value = np.array([x,y,z])
#    compute_shader.run(group_x=cls.BOX_DIM_X//cls.LOCAL_X,group_y=cls.BOX_DIM_Y//cls.LOCAL_Y,group_z=cls.BOX_DIM_Z//cls.LOCAL_Z)

#    count = count_buf.read()
#    count = np.frombuffer(count,dtype='uint32')[0]
#    verts = out_buf.read()
#    verts = np.frombuffer(verts,dtype='float32')
#    verts = verts.reshape((int(len(verts)/tri_siz),tri_siz))
#    verts = verts[:count,:tri_siz-1]
#    verts = verts.reshape(int(len(verts)*9/3),3)
#    
#    total_count = total_count+count
#    if total_verts is None:
#        total_verts = verts
#    else:
#        total_verts = np.concatenate((total_verts, verts),axis=0)
#    
#    count_buf.release()
#    out_buf.release()
    pass


class SDFObjectProperty(PropertyGroup):

    primitive_types = (('Box', 'Box', ''),
            ('Sphere', 'Sphere', ''),
            ('Cylinder','Cylinder',''),
            ('Cone','Cone',''),
            ('Torus','Torus',''),
            ('Hexagonal Prism', 'Hexagonal Prism', ''),
            ('Triangular Prism', 'Triangular Prism', ''),
            ('NGon Prism','NGon Prism',''),
            ('GLSL','GLSL',''),
            ('Empty','Empty',''),)
             
    boolean_types = (('Union', 'Union', ''),
            ('Difference', 'Difference', ''),
            ('Intersection', 'Intersection', ''),)
            
    blend_types = (('No Blending', 'No Blending', ''),
            ('Smooth', 'Smooth', ''),
            ('Champfer', 'Champfer', ''),
            ('Steps', 'Steps', ''),
            ('Round', 'Round', ''),)

    @classmethod
    def contains_in_list(cls, list, object):
        for p in list:
            if p.object == object:
                return True
        return False

    def property_event_on_object_prop_updated(self, context):
        pass

    def property_event_on_box_prop_updated(self, context):
        pass
    
    def property_event_on_sphere_prop_updated(self, context):
        pass
    
    def property_event_on_cylinder_prop_updated(self, context):
        pass
    
    def property_event_on_cone_prop_updated(self, context):
        pass
    
    def property_event_on_torus_prop_updated(self, context):
        pass
    
    def property_event_on_prism_prop_updated(self, context):
        pass
    
    def property_event_on_glsl_prop_updated(self, context):
        pass

    def property_event_on_primitive_type_changed(self, context):
        # Undo works for this operation
        prev_primitive_type = self.prev_primitive_type
        primitive_type = self.primitive_type
        if primitive_type != prev_primitive_type:
            object = context.object
            mesh = object.data
            if mesh:
                prev_mode = context.object.mode
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.delete(type='FACE')

                # Delete objects to be updated from the list in advance.
                SDFOBJECT_UTILITY.delete_from_sub_list(context, object)

                prv_pointer = None
                new_pointer = None
                for p in context.scene.sdf_object_pointer_list:
                    if p.object == object:
                        prv_pointer = p
                
                # Create a new property object and add it to the list of applicable primitive types
                # CollectionProperty does not have an alternative to the append function; the add function must be used.
                # Sorts the list of SDF Objects according to the order of the hierarchy.
                blist = None
                if (primitive_type == 'Box') and (SDFObjectProperty.contains_in_list(context.scene.sdf_box_pointer_list, prv_pointer.object) == False):
                    bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='CURSOR', location=object.location, rotation=object.rotation_euler, scale=object.scale)
                    blist = context.scene.sdf_box_pointer_list
                elif (primitive_type == 'Sphere') and (SDFObjectProperty.contains_in_list(context.scene.sdf_sphere_pointer_list, prv_pointer.object) == False):
                    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, enter_editmode=False, align='CURSOR', location=object.location, rotation=object.rotation_euler, scale=object.scale)
                    blist = context.scene.sdf_sphere_pointer_list
                elif (primitive_type == 'Cylinder') and (SDFObjectProperty.contains_in_list(context.scene.sdf_cylinder_pointer_list, prv_pointer.object) == False):
                    bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2, enter_editmode=False, align='CURSOR', location=object.location, rotation=object.rotation_euler, scale=object.scale)
                    blist = context.scene.sdf_cylinder_pointer_list
                elif (primitive_type == 'Cone') and (SDFObjectProperty.contains_in_list(context.scene.sdf_cone_pointer_list, prv_pointer.object) == False):
                    bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=0, depth=2, enter_editmode=False, align='CURSOR', location=object.location, rotation=object.rotation_euler, scale=object.scale)
                    blist = context.scene.sdf_cone_pointer_list
                elif (primitive_type == 'Torus') and (SDFObjectProperty.contains_in_list(context.scene.sdf_torus_pointer_list, prv_pointer.object) == False):
                    # Torus has no argument to scale with primitive_add. Scaling is applied manually.
                    prv_scale = (object.scale[0], object.scale[1], object.scale[2])
                    object.scale = (1,1,1)
                    bpy.ops.mesh.primitive_torus_add(major_radius=1, minor_radius=0.25, abso_major_rad=1.25, abso_minor_rad=0.75, align='CURSOR', location=object.location, rotation=object.rotation_euler)
                    object.scale = prv_scale
                    blist = context.scene.sdf_torus_pointer_list
                elif (primitive_type == 'Hexagonal Prism') and (SDFObjectProperty.contains_in_list(context.scene.sdf_hex_prism_pointer_list, prv_pointer.object) == False):
                    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=1, depth=2, enter_editmode=False, align='CURSOR', location=object.location, rotation=object.rotation_euler, scale=object.scale)
                    blist = context.scene.sdf_hex_prism_pointer_list
                elif (primitive_type == 'Triangular Prism') and (SDFObjectProperty.contains_in_list(context.scene.sdf_tri_prism_pointer_list, prv_pointer.object) == False):
                    bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=1, depth=2, enter_editmode=False, align='CURSOR', location=object.location, rotation=object.rotation_euler, scale=object.scale)
                    blist = context.scene.sdf_tri_prism_pointer_list
                elif (primitive_type == 'NGon Prism') and (SDFObjectProperty.contains_in_list(context.scene.sdf_ngon_prism_pointer_list, prv_pointer.object) == False):
                    bpy.ops.mesh.primitive_cylinder_add(vertices=prv_pointer.object.sdf_object.prop_prism.nsides, radius=1, depth=2, enter_editmode=False, align='CURSOR', location=object.location, rotation=object.rotation_euler, scale=object.scale)
                    blist = context.scene.sdf_ngon_prism_pointer_list
                elif (primitive_type == 'GLSL') and (SDFObjectProperty.contains_in_list(context.scene.sdf_glsl_pointer_list, prv_pointer.object) == False):
                    bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='CURSOR', location=object.location, rotation=object.rotation_euler, scale=object.scale)
                    blist = context.scene.sdf_glsl_pointer_list
                elif (primitive_type == 'Empty') and (SDFObjectProperty.contains_in_list(context.scene.sdf_empty_pointer_list, prv_pointer.object) == False):
                    blist = context.scene.sdf_empty_pointer_list

                if blist != None:
                    new_pointer = blist.add()
                    new_pointer.object = prv_pointer.object
                    SDFOBJECT_UTILITY.recalc_sub_index(blist)
                    ShaderBufferFactory.generate_buffer(ry.Raymarching.get_context(), primitive_type, len(blist))
                 
                object.sdf_object.prev_primitive_type = object.sdf_object.primitive_type
                bpy.ops.object.mode_set(mode=prev_mode)
        
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
        update=property_event_on_object_prop_updated)
                 
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

    blend_radius: FloatProperty(
        name='Radius',
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
           
    rounding: FloatProperty(
       name='Rounding',
       description='',
       min=0.0,
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
    prop_box_bounding: bpy.props.FloatVectorProperty(
        name='Bounding',
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
        default=1.0,
        update=property_event_on_cylinder_prop_updated)
        
    prop_cylinder_radius: bpy.props.FloatProperty(
        name='Radius',
        description='',
        min=0.0,
        default=1.0,
        update=property_event_on_cylinder_prop_updated)
    
    # torus
    prop_torus_radiuss: bpy.props.FloatVectorProperty(
        name='Radiuss',
        description='',
        size=2,
        min=0.0,
        default=(1.00,0.25),
        update=property_event_on_torus_prop_updated)
    
    # prism
    prop_prism_radius: bpy.props.FloatProperty(
        name='Radius',
        description='',
        min=0.0,
        default=0.5,
        update=property_event_on_prism_prop_updated)
        
    prop_prism_height: bpy.props.FloatProperty(
        name='Height',
        description='',
        min=0.0,
        default=1.0,
        update=property_event_on_prism_prop_updated)
        
    prop_prism_nsides: bpy.props.IntProperty(
        name='N',
        description='',
        min=3,
        default=6,
        update=property_event_on_prism_prop_updated)
    
    # cone
    prop_cone_radiuss: bpy.props.FloatVectorProperty(
        name='Radiuss',
        description='',
        size=2,
        min=0.0,
        default=(0.25,0.75),
        update=property_event_on_cone_prop_updated)
        
    prop_cone_height: bpy.props.FloatProperty(
        name='Height',
        description='',
        min=0.0,
        default=1.0,
        update=property_event_on_cone_prop_updated)
    
    # glsl
    prop_glsl_bounding: bpy.props.FloatVectorProperty(
        name='Bounding',
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
           
           
class SDFObjectPointerProperty(PropertyGroup):       
    object: PointerProperty(type=bpy.types.Object)


class SDF2MESH_UL_List(UIList):
    bl_idname = 'SDF2MESH_UL_List'
    layout_type = 'DEFAULT'
    
    def draw_filter(self, context, layout):
        # Disable the filter because there is currently no string property in 
        # SDFObjectProperty that could be used to sort items.
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
                props = item.object.sdf_object
                layout = layout.row()
                if index > 0 and props.nest:
                    layout.separator()
                layout.label(text=str(item.object.name))
                layout.label(text=str(props.primitive_type))
                layout.label(text=str(props.boolean_type))
                layout.label(text=str(props.blend_type))
                layout.label(text=str(props.index))
                layout.label(text=str(props.sub_index))
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
        # Fix index properties.
        alist = context.scene.sdf_object_pointer_list
        for i, pointer in enumerate(alist):
            alist[i].object.sdf_object.index = i
        
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
        SDFOBJECT_UTILITY.recalc_sub_index(context.scene.sdf_empty_pointer_list)
        
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
        pointer = context.scene.sdf_object_pointer_list.add()
        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='CURSOR', location=(0,0,0), rotation=(0,0,0), scale=(1,1,1))
        pointer.name = context.active_object.name
        pointer.object = context.active_object
        pointer.object.sdf_object.enabled = True
        pointer.object.sdf_object.index = len(context.scene.sdf_object_pointer_list) - 1
        
        # Add Box primitive by default
        pointer.object.sdf_object.prev_primitive_type = 'Box'
        pointer.object.sdf_object.primitive_type = 'Box'
        box_pointer = context.scene.sdf_box_pointer_list.add()
        box_pointer.object = pointer.object
        pointer.object.sdf_object.sub_index = len(context.scene.sdf_box_pointer_list) - 1

        # Generate compute buffer
        ShaderBufferFactory.generate_buffer(ry.Raymarching.get_context(), 'Box', len(context.scene.sdf_box_pointer_list))
        
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
        alist = context.scene.sdf_object_pointer_list
        index = context.scene.sdf_object_pointer_list_index
        deleted_index = index
        if deleted_index > -1:
            object = context.scene.sdf_object_pointer_list[deleted_index].object
            primitive_type = object.sdf_object.primitive_type
            if object != None:
                # Delete mesh
                if object.data:
                    bpy.data.meshes.remove(object.data,do_unlink=True)
                    
            alist.remove(deleted_index)
            SDFOBJECT_UTILITY.refresh_list(context, primitive_type)
            
            # Decrements the index by 1 from the item whose index is larger than the deleted item
            for i in range(deleted_index,len(alist)):
                alist[i].object.sdf_object.index -= 1
            
            if len(alist) > context.scene.sdf_object_pointer_list_index:
                pass
            else:
                context.scene.sdf_object_pointer_list_index = -1
                
            # Update the order of CollectionProperty(type=SDFObjectRefPointerProperty).
            blist = None
            if primitive_type == 'Box':
                blist = context.scene.sdf_box_pointer_list
            elif primitive_type == 'Sphere':
                blist = context.scene.sdf_sphere_pointer_list
            elif primitive_type == 'Cylinder':
                blist = context.scene.sdf_cylinder_pointer_list
            elif primitive_type == 'Cone':
                blist = context.scene.sdf_cone_pointer_list
            elif primitive_type == 'Torus':
                blist = context.scene.sdf_torus_pointer_list
            elif primitive_type == 'Hexagonal Prism':
                blist = context.scene.sdf_hex_prism_pointer_list
            elif primitive_type == 'Triangular Prism':
                blist = context.scene.sdf_tri_prism_pointer_list
            elif primitive_type == 'NGon Prism':
                blist = context.scene.sdf_ngon_prism_pointer_list
            elif primitive_type == 'GLSL':
                blist = context.scene.sdf_glsl_prism_pointer_list
            elif primitive_type == 'Empty':
                blist = context.scene.sdf_empty_prism_pointer_list
                
            SDFOBJECT_UTILITY.recalc_sub_index_without_sort(blist)
            ShaderBufferFactory.generate_buffer(ry.Raymarching.get_context(), primitive_type, len(blist))
                
            bpy.ops.ed.undo_push(message='mesh_from_sdf.hierarchy_remove')
        return {'FINISHED'}


class SDF2MESH_OT_List_Reorder(Operator):
    
    # TODO: Updating Index Properties
    # STATE: Not tested yet
    
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
        alist = context.scene.sdf_object_pointer_list
        index = context.scene.sdf_object_pointer_list_index

        neighbor = index + (-1 if self.direction == 'UP' else 1)
        alist[neighbor].object.sdf_object.index = index # Exchange index property values with each other
        alist[index].object.sdf_object.index = neighbor
        alist.move(neighbor, index)
        self.move_index()
        
        # Update the order of CollectionProperty(type=SDFObjectRefPointerProperty).
        item0 = alist[neighbor].object.sdf_object
        item1 = alist[index].object.sdf_object
        if item0.primitive_type == item1.primitive_type:
            blist = None
            
            primitive_type = alist[neighbor].object.sdf_object.primitive_type
            if primitive_type == 'Box':
                blist = context.scene.sdf_box_pointer_list
            elif primitive_type == 'Sphere':
                blist = context.scene.sdf_sphere_pointer_list
            elif primitive_type == 'Cylinder':
                blist = context.scene.sdf_cylinder_pointer_list
            elif primitive_type == 'Cone':
                blist = context.scene.sdf_cone_pointer_list
            elif primitive_type == 'Torus':
                blist = context.scene.sdf_torus_pointer_list
            elif primitive_type == 'Hexagonal Prism':
                blist = context.scene.sdf_hex_prism_pointer_list
            elif primitive_type == 'Triangular Prism':
                blist = context.scene.sdf_tri_prism_pointer_list
            elif primitive_type == 'NGon Prism':
                blist = context.scene.sdf_ngon_prism_pointer_list
            elif primitive_type == 'GLSL':
                blist = context.scene.sdf_glsl_prism_pointer_list
            elif primitive_type == 'Empty':
                blist = context.scene.sdf_empty_prism_pointer_list
            
            blist.move(item0.sub_index, item1.sub_index)
            tmp = int(item0.sub_index)
            item0.sub_index = int(item1.sub_index)
            item1.sub_index = tmp
        
        bpy.ops.ed.undo_push(message='mesh_from_sdf.hierarchy_reorder')
        return {'FINISHED'}
    
    
class SDF2MESH_OT_Select_On_The_List(Operator):
    bl_idname = 'mesh_from_sdf.select_on_the_hierarchy'
    bl_label = 'Select on the hierarchy'
    bl_description = 'Select the objects displayed in Object Properties, also on the tallbox hierarchy.'
    
    def execute(self, context):
        context.scene.sdf_object_pointer_list_index = context.object.sdf_object.index
        
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
                col_r_1.enabled = (context.scene.sdf_object_pointer_list_index > 0) and (context.scene.sdf_object_pointer_list_index < len(context.scene.sdf_object_pointer_list) - 1)
                col_r_1.operator('mesh_from_sdf.hierarchy_reorder', text='', icon='TRIA_DOWN').direction = 'DOWN'
                    
                if SDF2MESH_PT_Panel.is_pointer_list_index_validity(scene):
                    col_l.separator()
                    row_l = col_l.row()
                    pointer = scene.sdf_object_pointer_list[scene.sdf_object_pointer_list_index]
                    if (pointer.object != None) and (scene.sdf_object_pointer_list_index > 0):
                        prop = pointer.object.sdf_object
                        row_l.prop(prop, "nest")
                    row_l.operator('mesh_from_sdf.select_on_the_properties', text='Select on the properties')
            
            col_r.separator()
            col_r = col_r.column()
            col_r.operator('mesh_from_sdf.hierarchy_reload', text='', icon='FILE_REFRESH')


class SDFOBJECT_PT_Panel(Panel):
    bl_label = 'SDF Object'
    bl_idname = 'SDFOBJECT_PT_Panel'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_description = 'When the object is an SDF Object, each property for defining the shape is displayed.'

    def draw(self, context):
        object = context.active_object
        row = self.layout.row()
        row.alignment = 'CENTER'
        if object.sdf_object.enabled:
            col = row.column(align=True)
            row = self.layout.row()
            item = object.sdf_object
            col = self.layout.column()
            col.prop(item, 'primitive_type')
            
            if item.primitive_type == 'Box':
                col.prop(item, 'prop_box_bounding')
            elif item.primitive_type == 'Sphere':
                col.prop(item, 'prop_sphere_radius')
            elif item.primitive_type == 'Cylinder':
                col.prop(item, 'prop_cylinder_height')
                col.prop(item, 'prop_cylinder_radius')
            elif item.primitive_type == 'Torus':
                col.prop(item, 'prop_torus_radiuss')
            elif (item.primitive_type == 'Hexagonal Prism') or (item.primitive_type == 'Triangular Prism') or (item.primitive_type == 'NGon Prism'):
                col.prop(item, 'prop_prism_radius')
                col.prop(item, 'prop_prism_height')
                if (item.primitive_type == 'NGon Prism'):
                    col.prop(item, 'prop_prism_nsides')
            elif item.primitive_type == 'Cone':
                col.prop(item, 'prop_cone_height')
                col.prop(item, 'prop_cone_radiuss')
            elif item.primitive_type == 'GLSL':
                col.prop(item, 'prop_glsl_shader_path')
                col.prop(item, 'prop_glsl_bounding')
            elif item.primitive_type == 'Empty':
                pass
            
            col.prop(item, 'boolean_type')
            col.prop(item, 'blend_type')
            
            if item.blend_type == 'Smooth':
                col.prop(item, 'blend_smooth')
            elif item.blend_type == 'Champfer':
                col.prop(item, 'blend_champfer_size')
            elif item.blend_type == 'Steps':
                col.prop(item, 'blend_step')
                col.prop(item, 'blend_champfer_size')
            elif item.blend_type == 'Round':
                col.prop(item, 'blend_radius')
            
            col.prop(item, 'rounding')
            col.separator()
            col.operator('mesh_from_sdf.select_on_the_hierarchy', text='Select on the hierarchy')
        else:
            col = row.column(align=True)
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
            if object.sdf_object.enabled:
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
                
                # Update the CollectionProperty(type=SDFObjectRefPointerProperty) that references the deleted SDFObject.
                refresh_required_primitive_types.append(str(object.sdf_object.prev_primitive_type))
                
                deleted_index = object.sdf_object.index
                alist.remove(deleted_index)

                bpy.data.meshes.remove(object.data,do_unlink=True) # Delete mesh
                
                # Decrement the index because the object was deleted
                if (deleted_index > -1) and (len(alist) > 0) and (len(alist) > deleted_index):
                    next_neighbors_index = len(alist) - 1 if (i > len(delete_target_objects) - 2) else delete_target_objects[i + 1].object.sdf_object.index
                    # Update index properties to include the following targets to be excluded.
                    for j in range(deleted_index, next_neighbors_index + 1):
                        alist[j].object.sdf_object.index = alist[j].object.sdf_object.index - decrement
                        
                    decrement = decrement + 1
                
        refresh_required_primitive_types = set(refresh_required_primitive_types) # Remove duplicates
        SDFOBJECT_UTILITY.refresh_lists(context, refresh_required_primitive_types)
                
        if indexed_object_deleted == False:
            context.scene.sdf_object_pointer_list_index = -1
        else:
            context.scene.sdf_object_pointer_list_index = indexed_object.object.sdf_object.index
            
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
            while alist[i].object.sdf_object.index < alist[p].object.sdf_object.index:
                i = i + 1
            while alist[j].object.sdf_object.index > alist[p].object.sdf_object.index:
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
        cls.__refresh_list(alist)
        
        i = -1
        for pointer in alist:
            i = i + 1
            alist[i].object.sdf_object.sub_index = i
    
    @classmethod
    def recalc_sub_index(cls, alist):
        # SDFOBJECT_UTILITY.recalc_sub_index(alist)
        cls.__refresh_list(alist)
             
        Algorithms.quick_sort_by_index(alist)
        
        i = -1
        for pointer in alist:
            i = i + 1
            alist[i].object.sdf_object.sub_index = i
    
    @classmethod
    def __refresh_list(cls, alist):
        # Items with no referenced object and duplicated pointer are removed from the list.
        cache = []
        i = -1
        for pointer in alist:
            i = i + 1
            if alist[i].object == None or alist[i].object in cache:
                alist.remove(i)
                i = i - 1
                continue
            cache.append(alist[i].object)

    @classmethod
    def refresh_list(cls, context, primitive_type):
        if primitive_type == 'Box':
            cls.__refresh_list(context.scene.sdf_box_pointer_list)
        elif primitive_type == 'Sphere':
            cls.__refresh_list(context.scene.sdf_sphere_pointer_list)
        elif primitive_type == 'Cylinder':
            cls.__refresh_list(context.scene.sdf_cylinder_pointer_list)
        elif primitive_type == 'Cone':
            cls.__refresh_list(context.scene.sdf_cone_pointer_list)
        elif primitive_type == 'Torus':
            cls.__refresh_list(context.scene.sdf_torus_pointer_list)
        elif primitive_type == 'Hexagonal Prism':
            cls.__refresh_list(context.scene.sdf_hex_prism_pointer_list, target)
        elif primitive_type == 'Triangular Prism':
            cls.__refresh_list(context.scene.sdf_tri_prism_pointer_list, target)
        elif primitive_type == 'NGon Prism':
            cls.__refresh_list(context.scene.sdf_ngon_prism_pointer_list, target)
        elif primitive_type == 'GLSL':
            cls.__refresh_list(context.scene.sdf_glsl_pointer_list)
        elif primitive_type == 'Empty':
            cls.__refresh_list(context.scene.sdf_empty_pointer_list)
            
    @classmethod
    def refresh_lists(cls, context, primitive_types):
        for primitive_type in primitive_types:
            cls.refresh_list(context, primitive_type)
            
    @classmethod
    def __delete_from_sub_list(cls, alist, target):
        delete_index = -1
        for i,pointer in enumerate(alist):
            if (pointer.object == None) or (pointer.object == target):
                delete_index = i
                break
        if delete_index > -1:
            alist.remove(delete_index)
        for i in range(delete_index, len(alist)):
            alist[i].object.sdf_object.sub_index = alist[i].object.sdf_object.sub_index - 1

    @classmethod
    def delete_from_sub_list(cls, context, target):
        primitive_type = target.sdf_object.prev_primitive_type
        if primitive_type == 'Box':
            cls.__delete_from_sub_list(context.scene.sdf_box_pointer_list, target)
        elif primitive_type == 'Sphere':
            cls.__delete_from_sub_list(context.scene.sdf_sphere_pointer_list, target)
        elif primitive_type == 'Cylinder':
            cls.__delete_from_sub_list(context.scene.sdf_cylinder_pointer_list, target)
        elif primitive_type == 'Cone':
            cls.__delete_from_sub_list(context.scene.sdf_cone_pointer_list, target)
        elif primitive_type == 'Torus':
            cls.__delete_from_sub_list(context.scene.sdf_torus_pointer_list, target)
        elif primitive_type == 'Hexagonal Prism':
            cls.__delete_from_sub_list(context.scene.sdf_hex_prism_pointer_list, target)
        elif primitive_type == 'Triangular Prism':
            cls.__delete_from_sub_list(context.scene.sdf_tri_prism_pointer_list, target)
        elif primitive_type == 'NGon Prism':
            cls.__delete_from_sub_list(context.scene.sdf_ngon_prism_pointer_list, target)
        elif primitive_type == 'GLSL':
            cls.__delete_from_sub_list(context.scene.sdf_glsl_pointer_list, target)
        elif primitive_type == 'Empty':
            cls.__delete_from_sub_list(context.scene.sdf_empty_pointer_list, target)


def sdf_object_delete_func(self, context):
    self.layout.operator(OBJECT_OT_Delete_SDF.bl_idname, text='Delete (SDF Object)')


classes = [
    SDFObjectProperty,
    SDFObjectPointerProperty,
    
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


def init_shader_buffer():
    pass


def deinit_shader_buffer():
    ShaderBufferFactory.release_all()


def register():
    for c in classes:
        bpy.utils.register_class(c)

    init_shader_buffer()
    ry.register()
    # mc.register()

    bpy.types.OUTLINER_MT_object.append(sdf_object_delete_func)
    bpy.types.VIEW3D_MT_object.append(sdf_object_delete_func)
    bpy.types.VIEW3D_MT_object_context_menu.append(sdf_object_delete_func)
    
    # Add the sdf property to the bpy.types.object
    bpy.types.Object.sdf_object = PointerProperty(type = SDFObjectProperty)
    
    # Display this list in the UI hierarchy on the scene view
    bpy.types.Scene.sdf_object_pointer_list = CollectionProperty(type = SDFObjectPointerProperty)
    bpy.types.Scene.sdf_object_pointer_list_index = IntProperty(name = 'Index for sdf_object_pointer_list', default = 0)
    
    # List for sorting objects for each primitive when sdf_object_pointer_list is updated
    bpy.types.Scene.sdf_box_pointer_list = CollectionProperty(type = SDFObjectPointerProperty)
    bpy.types.Scene.sdf_sphere_pointer_list = CollectionProperty(type = SDFObjectPointerProperty)
    bpy.types.Scene.sdf_cylinder_pointer_list = CollectionProperty(type = SDFObjectPointerProperty)
    bpy.types.Scene.sdf_cone_pointer_list = CollectionProperty(type = SDFObjectPointerProperty)
    bpy.types.Scene.sdf_torus_pointer_list = CollectionProperty(type = SDFObjectPointerProperty)
    bpy.types.Scene.sdf_hex_prism_pointer_list = CollectionProperty(type = SDFObjectPointerProperty)
    bpy.types.Scene.sdf_tri_prism_pointer_list = CollectionProperty(type = SDFObjectPointerProperty)
    bpy.types.Scene.sdf_ngon_prism_pointer_list = CollectionProperty(type = SDFObjectPointerProperty)
    bpy.types.Scene.sdf_glsl_pointer_list = CollectionProperty(type = SDFObjectPointerProperty)
    bpy.types.Scene.sdf_empty_pointer_list = CollectionProperty(type = SDFObjectPointerProperty)


def unregister():
    del bpy.types.Object.sdf_object
    del bpy.types.Scene.sdf_object_pointer_list
    del bpy.types.Scene.sdf_object_pointer_list_index
    
    bpy.types.OUTLINER_MT_object.remove(sdf_object_delete_func)
    bpy.types.VIEW3D_MT_object.remove(sdf_object_delete_func)
    bpy.types.VIEW3D_MT_object_context_menu.remove(sdf_object_delete_func)

    # mc.unregister()
    ry.unregister()
    deinit_shader_buffer()
    
    for c in classes:
        bpy.utils.unregister_class(c)

        
if __name__ == '__main__':
    register()
