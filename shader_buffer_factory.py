import moderngl
import numpy as np

# Class for generating and updating Compute Buffer to be bound to shaders
class ShaderBufferFactory(object):
    
    # List to get blend properties of shaders...seems like using dictionary is faster than if else?
    __get_blend_props = {'No Blending': lambda sdf_object: (0, 0),
                         'Smooth' : lambda sdf_object: (sdf_object.blend_smooth, 0),
                         'Champfer' : lambda sdf_object: (sdf_object.blend_champfer_size, 0),
                         'Steps' : lambda sdf_object: (sdf_object.blend_champfer_size, sdf_object.blend_step),
                         'Round' : lambda sdf_object: (sdf_object.blend_radius, 0)}
    
    # Buffer used for SDFObjectProperty
    object_common_buffer = None
    
    # Free all buffers
    @classmethod
    def release_all(cls):
        cls.release_object_common_buffer()

    # Get object_common_buffer regardless of whether the value is None or not
    @classmethod
    def get_object_common_buffer(cls):
        return cls.object_common_buffer
    
    # Generate buffer for SDFObjectProperty
    @classmethod
    def generate_object_common_buffer(cls, ctx, context):
        
        dsize = 10 # position (3), scale (1), quaternion (4), blend (2)
        alist = context.scene.sdf_object_pointer_list
        narray = np.empty(len(alist) * dsize, dtype=np.float32)
        
        for i, pointer in enumerate(alist):
            object = pointer.object
            sdf_object = object.sdf_object
            
            mat = object.matrix_world
            p = mat.to_translation()
            r = mat.to_quaternion()
            s = mat.to_scale()
            bl_0, bl_1 = cls.__get_blend_props[sdf_object.blend_type](sdf_object)
            
            offset = i * dsize
            narray[offset + 0] = p[0]
            narray[offset + 1] = p[1]
            narray[offset + 2] = p[2]
            narray[offset + 3] = s[0]
            narray[offset + 4] = r[0]
            narray[offset + 5] = r[1]
            narray[offset + 6] = r[2]
            narray[offset + 7] = r[3]
            narray[offset + 8] = bl_0
            narray[offset + 9] = bl_1

        # Generate a buffer to bind to the shader using np.array as source
        cls.object_common_buffer = ctx.buffer(narray)
        print('[generate_object_common_buffer] object_common:', narray)
        return cls.object_common_buffer
    
    # Reflects the specified element of the SDFObjectProperty list in the buffer
    @classmethod
    def update_object_common_buffer(cls, ctx, context, i):
        
        # If buffer is set to None for some reason, a new buffer is created here.
        if cls.object_common_buffer == None:
            return cls.generate_object_common_buffer(ctx, context)
        
        dsize = 8 # position (3), scale (1), quaternion (4)
        alist = context.scene.sdf_object_pointer_list
        narray = np.empty(len(alist) * dsize, dtype=np.float32)
        
        pointer = alist[i]
        object = pointer.object
        sdf_object = object.sdf_object
        
        mat = object.matrix_world
        p = mat.to_translation()
        r = mat.to_quaternion()
        s = mat.to_scale()
        bl_0, bl_1 = cls.__get_blend_props[sdf_object.blend_type](sdf_object)
        
        narray[0] = p[0]
        narray[1] = p[1]
        narray[2] = p[2]
        narray[3] = s[0]
        narray[4] = r[0]
        narray[5] = r[1]
        narray[6] = r[2]
        narray[7] = r[3]
        narray[8] = bl_0
        narray[9] = bl_1
        
        buf = cls.object_common_buffer
        buf.write(narray.tobytes())
        
        print('[update_object_common_buffer] index:', i, 'narray:', narray)
        return cls.object_common_buffer
    
    # Release buffer used for SDFObjectProperty
    @classmethod
    def release_object_common_buffer(cls):
        if cls.object_common_buffer != None:
            cls.object_common_buffer.release()
        cls.object_comon_buffer = None

    @classmethod
    def generate_box_buffer(cls, context):
        pass
    
    @classmethod
    def generate_sphere_buffer(cls, context):
        pass
    
    @classmethod
    def gemerate_cylinder_buffer(cls, context):
        pass
    
    @classmethod
    def gemerate_cone_buffer(cls, context):
        pass
    
    @classmethod
    def gemerate_torus_buffer(cls, context):
        pass
    
    @classmethod
    def gemerate_hex_prism_buffer(cls, context):
        pass
    
    @classmethod
    def gemerate_tri_prism_buffer(cls, context):
        pass
    
    @classmethod
    def gemerate_ngon_prism_buffer(cls, context):
        pass
    
    @classmethod
    def gemerate_glsl_buffer(cls, context):
        pass
        
    
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