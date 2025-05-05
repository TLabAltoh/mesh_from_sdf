import moderngl

def create_context():
    # Note: bgl.glGetString has defined but returns None. How can I detect the OpenGL version in Blender ?
    # print("OpenGL supported version (by Blender):", bgl.glGetString(bgl.GL_VERSION))
    ctx = moderngl.create_context()
    print("[ModernGL Util] GL context version code:", ctx.version_code)
    assert ctx.version_code >= 430
    print("[ModernGL Util] Compute max work group size:", ctx.info['GL_MAX_COMPUTE_WORK_GROUP_SIZE'], end='\n\n')
    
    return ctx