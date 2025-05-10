import moderngl

# Class for generating and updating Compute Buffer to be bound to shaders
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