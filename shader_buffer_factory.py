import moderngl
import numpy as np

# Class for generating and updating Compute Buffer to be bound to shaders
class ShaderBufferFactory(object):
    
    # Holds the buffer object and the buffer size of its elements
    buffers = {}
    
    # Generate a ComputeBuffer with any key
    @classmethod
    def generate_buffer(cls, ctx, key, size, item_size = 1):
        size = size * item_size
        if key in cls.buffers:
            buffer = cls.buffers[key][0]
            buffer.orphan(size)
        else:
            buffer = ctx.buffer(reserve=size, dynamic=True)
            cls.buffers[key] = (buffer, item_size)
    
    # Update buffer at specified index
    @classmethod
    def update_buffer(cls, key, data, index, offset = 0):
        if key in cls.buffers:
            touple = cls.buffers[key]
            buffer = touple[0]
            imsize = touple[1]
            buffer.write(data, index * imsize + offset)
            
    # Releases the buffer associated with the specified key
    @classmethod
    def release_buffer(cls, key):
        if key in cls.buffers:
            buffer = cls.buffers[key][0]
            buffre.release()
            del cls.buffres[key]
    
    # Free all buffers
    @classmethod
    def release_all(cls):
        for touple in cls.buffers:
            touple[0].release()
        cls.buffers.clear()
    
    # Pack elements of SDFObjectProperty into a touple
    @classmethod
    def pack_sdf_object_common_property(cls, object):
        mat = object.matrix_world
        p = mat.to_translation()
        r = mat.to_quaternion()
        s = mat.to_scale()
        return p[0], p[1], p[2], s[0], r[0], r[1], r[2], r[3]
    
    @classmethod
    def generate_object_common_buffer(cls, context):
        alist = context.scene.sdf_object_pointer_list
        blist = [cls.pack_sdf_object_common_property(p.object) for p in alist]
        print('blist:', blist)
        pass

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