import bpy
import bmesh
from mesh_from_sdf.shader_buffer_factory import *
from mesh_from_sdf.util.pointer_list import *
from bpy.types import PropertyGroup
from bpy.props import PointerProperty, FloatProperty, IntProperty, StringProperty

global ctx

class SDFObjectPointer(PropertyGroup):
    object: PointerProperty(type=bpy.types.Object)


class SDFPrimitivePointer(SDFObjectPointer):
    
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
    

class SDFBoxPointer(SDFPrimitivePointer):
    
    # Callback processing when updating properties.
    def on_prop_update(self, context):
        global ctx
        this = self.object.sdf_prop

        # Update mesh for primitive interactions
        prev_mode = self.__class__.update_primitive_mesh_begin(context)
        self.__class__.update_box_mesh(context.scene.sdf_object_pointer_list[this.index])
        self.__class__.update_primitive_mesh_end(prev_mode)
        
        # Updateing Storage Buffre Objects
        ShaderBufferFactory.update_box_buffer(ctx, context, this.index, this.sub_index)
    
    bound: bpy.props.FloatVectorProperty(
        name='Bound',
        description='Lengths of the three sides of a cube',
        size=3,
        min=0.0,
        default=(1.0,1.0,1.0),
        update=on_prop_update)
        
    round: bpy.props.FloatVectorProperty(
        name='Corner Round',
        description='Radius of 4 corners viewed from z-plane',
        size=4,
        min=0.0,
        default=(0,0,0,0),
        update=on_prop_update)
        
    @classmethod
    def update_box_mesh(cls, pointer):
        object = pointer.object
        sdf_prop = object.sdf_prop
        self = bpy.context.scene.sdf_box_pointer_list[sdf_prop.sub_index]
        
        bound = self.bound
        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='CURSOR', location=object.location, rotation=object.rotation_euler, scale=object.scale)

        mesh = object.data
        bm = bmesh.from_edit_mesh(mesh)
        for i, vert in enumerate(bm.verts):
            vert.co[0] = vert.co[0] * bound[0]
            vert.co[1] = vert.co[1] * bound[1]
            vert.co[2] = vert.co[2] * bound[2]
        bmesh.update_edit_mesh(mesh)
        
        
class SDFSpherePointer(SDFPrimitivePointer):
    
    # Callback processing when updating properties.
    def on_prop_update(self, context):
        global ctx
        this = self.object.sdf_prop

        # Update mesh for primitive interactions
        prev_mode = self.__class__.update_primitive_mesh_begin(context)
        self.__class__.update_sphere_mesh(context.scene.sdf_object_pointer_list[this.index])
        self.__class__.update_primitive_mesh_end(prev_mode)
        
        # Updateing Storage Buffre Objects
        ShaderBufferFactory.update_sphere_buffer(ctx, context, this.index, this.sub_index)
    
    radius: bpy.props.FloatProperty(
        name='Radius',
        description='Radius of sphere',
        min=0.0,
        default=1.0,
        update=on_prop_update)
        
    @classmethod
    def update_sphere_mesh(cls, pointer):
        object = pointer.object
        sdf_prop = object.sdf_prop
        self = bpy.context.scene.sdf_sphere_pointer_list[sdf_prop.sub_index]
        
        radius = self.radius
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='CURSOR', location=object.location, rotation=object.rotation_euler, scale=object.scale)


class SDFCylinderPointer(SDFPrimitivePointer):
    
    # Callback processing when updating properties.
    def on_prop_update(self, context):
        global ctx
        this = self.object.sdf_prop
        
        # Update mesh for primitive interactions
        prev_mode = self.__class__.update_primitive_mesh_begin(context)
        self.__class__.update_cylinder_mesh(context.scene.sdf_object_pointer_list[this.index])
        self.__class__.update_primitive_mesh_end(prev_mode)
        
        # Updateing Storage Buffre Objects
        ShaderBufferFactory.update_cylinder_buffer(ctx, context, this.index, this.sub_index)
    
    height: bpy.props.FloatProperty(
        name='Height',
        description='',
        min=0.0,
        default=2.0,
        update=on_prop_update)
        
    radius: bpy.props.FloatProperty(
        name='Radius',
        description='',
        min=0.0,
        default=1.0,
        update=on_prop_update)
        
    @classmethod
    def update_cylinder_mesh(cls, pointer):
        object = pointer.object
        sdf_prop = object.sdf_prop
        self = bpy.context.scene.sdf_cylinder_pointer_list[sdf_prop.sub_index]

        height = self.height
        radius = self.radius
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=height, enter_editmode=False, align='CURSOR', location=object.location, rotation=object.rotation_euler, scale=object.scale)
        
        
class SDFConePointer(SDFPrimitivePointer):
    
    # Callback processing when updating properties.
    def on_prop_update(self, context):
        global ctx
        this = self.object.sdf_prop

        # Update mesh for primitive interactions
        prev_mode = self.__class__.update_primitive_mesh_begin(context)
        self.__class__.update_cone_mesh(context.scene.sdf_object_pointer_list[this.index])
        self.__class__.update_primitive_mesh_end(prev_mode)
        
        # Updateing Storage Buffre Objects
        ShaderBufferFactory.update_cone_buffer(ctx, context, this.index, this.sub_index)
    
    height: bpy.props.FloatProperty(
        name='Height',
        description='',
        min=0.0,
        default=2.0,
        update=on_prop_update)
    
    radius: bpy.props.FloatVectorProperty(
        name='Radius',
        description='',
        size=2,
        min=0.0,
        default=(0.75,0.25),
        update=on_prop_update)
        
    @classmethod
    def update_cone_mesh(cls, pointer):
        object = pointer.object
        sdf_prop = object.sdf_prop
        self = bpy.context.scene.sdf_cone_pointer_list[sdf_prop.sub_index]
        
        height = self.height
        radius = self.radius
        bpy.ops.mesh.primitive_cone_add(radius1=radius[0], radius2=radius[1], depth=height, enter_editmode=False, align='CURSOR', location=object.location, rotation=object.rotation_euler, scale=object.scale)
        
        
class SDFTorusPointer(SDFPrimitivePointer):
    
    # Callback processing when updating properties.
    def on_prop_update(self, context):
        global ctx
        this = self.object.sdf_prop

        # Update mesh for primitive interactions
        prev_mode = self.__class__.update_primitive_mesh_begin(context)
        self.__class__.update_torus_mesh(context.scene.sdf_object_pointer_list[this.index])
        self.__class__.update_primitive_mesh_end(prev_mode)
        
        # Updateing Storage Buffre Objects
        ShaderBufferFactory.update_torus_buffer(ctx, context, self.index, self.sub_index)
    
    radius: bpy.props.FloatVectorProperty(
        name='Radius',
        description='',
        size=2,
        min=0.0,
        default=(0.75,0.25),
        update=on_prop_update)
        
    fill: bpy.props.FloatProperty(
        name='Fill',
        description='',
        min=0.0,
        default=1.0,
        update=on_prop_update)
        
    @classmethod
    def update_torus_mesh(cls, pointer):
        object = pointer.object
        sdf_prop = object.sdf_prop
        self = bpy.context.scene.sdf_torus_pointer_list[sdf_prop.sub_index]
        
        prv_scale = (object.scale[0], object.scale[1], object.scale[2])
        object.scale = (1,1,1)
        radius = self.radius
        bpy.ops.mesh.primitive_torus_add(major_radius=radius[0], minor_radius=radius[1], abso_major_rad=1.25, abso_minor_rad=0.75, align='CURSOR', location=object.location, rotation=object.rotation_euler)
        object.scale = prv_scale
        
        
class SDFPrismPointer(SDFPrimitivePointer):
    
    # List of SDFProperty.update_{nsides}_mesh and ShaderBufferFactory.update_{nsides_prism}_buffer, keyed by prism_type
    # example: update = update_prism_mesh_and_buffer_by_prism_type[primitive_type]
    #          update(ctx, context, self.index, self.sub_index) # execute
    update_prism_mesh_and_buffer_by_prism_type = {'Hexagonal Prism': lambda ctx, context, index, sub_index: (
                                                SDFPrismPointer.update_hex_prism_mesh(context.scene.sdf_object_pointer_list[index]),
                                                ShaderBufferFactory.update_hex_prism_buffer(ctx, context, index, sub_index)),
                                                  'Triangular Prism': lambda ctx, context, index, sub_index: (
                                                SDFPrismPointer.update_tri_prism_mesh(context.scene.sdf_object_pointer_list[index]),
                                                ShaderBufferFactory.update_tri_prism_buffer(ctx, context, index, sub_index)),
                                                  'Ngon Prism': lambda ctx, context, index, sub_index: (
                                                SDFPrismPointer.update_ngon_prism_mesh(context.scene.sdf_object_pointer_list[index]),
                                                ShaderBufferFactory.update_ngon_prism_buffer(ctx, context, index, sub_index))}
        
    def on_prop_update(self, context):
        global ctx
        this = self.object.sdf_prop
        
        # Updateing Prism Mesh and Storage Buffre Objects
        # Determine how many angles you are with an if statement.    
        prev_mode = self.__class__.update_primitive_mesh_begin(context)
        update_prism_mesh_and_buffer_by_prism_type[this.primitive_type](ctx, context, this.index, this.sub_index)
        self.__class__.update_primitive_mesh_end(prev_mode)
    
    def on_ngon_prism_prop_update(self, context):
        global ctx
        this = self.object.sdf_prop
        
        # Update mesh for primitive interactions
        prev_mode = self.__class__.update_primitive_mesh_begin(context)
        self.__class__.update_ngon_prism_mesh(context.scene.sdf_object_pointer_list[this.index])
        self.__class__.update_primitive_mesh_end(prev_mode)

        # Updateing Storage Buffre Objects        
        ShaderBufferFactory.update_ngon_prism_buffer(ctx, context, this.index, this.sub_index)
    
    radius: bpy.props.FloatProperty(
        name='Radius',
        description='',
        min=0.0,
        default=1.0,
        update=on_prop_update)
        
    height: bpy.props.FloatProperty(
        name='Height',
        description='',
        min=0.0,
        default=3.0,
        update=on_prop_update)
        
    nsides: bpy.props.IntProperty(
        name='N',
        description='',
        min=3,
        default=6,
        update=on_ngon_prism_prop_update)
        
    @classmethod
    def update_hex_prism_mesh(cls, pointer):
        object = pointer.object
        sdf_prop = object.sdf_prop
        self = bpy.context.scene.sdf_hex_prism_pointer_list[sdf_prop.sub_index]
        
        height = self.height
        radius = self.radius
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=radius, depth=height, enter_editmode=False, align='CURSOR', location=object.location, rotation=object.rotation_euler, scale=object.scale)
        
    @classmethod
    def update_tri_prism_mesh(cls, pointer):
        object = pointer.object
        sdf_prop = object.sdf_prop
        self = bpy.context.scene.sdf_tri_prism_pointer_list[sdf_prop.sub_index]
        
        height = self.height
        radius = self.radius
        bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=radius, depth=height, enter_editmode=False, align='CURSOR', location=object.location, rotation=object.rotation_euler, scale=object.scale)
        
    @classmethod
    def update_ngon_prism_mesh(cls, pointer):
        object = pointer.object
        sdf_prop = object.sdf_prop
        self = bpy.context.scene.sdf_ngon_prism_pointer_list[sdf_prop.sub_index]
        
        nsides = self.nsides
        height = self.height
        radius = self.radius
        bpy.ops.mesh.primitive_cylinder_add(vertices=nsides, radius=radius, depth=height, enter_editmode=False, align='CURSOR', location=object.location, rotation=object.rotation_euler, scale=object.scale)


class SDFGLSLPointer(SDFPrimitivePointer):
    
    # Callback processing when updating properties.
    def on_prop_update(self, context):
        pass
    
    bound: bpy.props.FloatVectorProperty(
        name='Bound',
        description='',
        size=3,
        min=0.0,
        default=(1.0,1.0,1.0),
        update=on_prop_update)
    
    shader_path: StringProperty(
        name='Shader PATH',
        description='',
        default='C:\\',
        update=on_prop_update)
        
    @classmethod
    def update_glsl_mesh(cls, pointer):
        pass
    
    
def set_context(context):
    global ctx
    ctx = context