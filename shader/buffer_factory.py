import moderngl
import math
import struct
import numpy as np

# Class for generating and updating Storage Buffer Objects to be bound to shaders
class ShaderBufferFactory(object):
    
    # List to get blend properties of shaders...seems like using dictionary is faster than if else?
    __get_blend_props = {'No Blending': lambda sdf_prop: (0, 0),
                         'Smooth' : lambda sdf_prop: (sdf_prop.blend_smooth, 0),
                         'Champfer' : lambda sdf_prop: (sdf_prop.blend_champfer_size, 0),
                         'Steps' : lambda sdf_prop: (sdf_prop.blend_champfer_size, sdf_prop.blend_step),
                         'Round' : lambda sdf_prop: (sdf_prop.blend_radius, 0)}
    
    # Buffer used for SDFObjectProperty
    object_common_buffer = None
    box_buffer = None
    sphere_buffer = None
    cylinder_buffer = None
    torus_buffer = None
    cone_buffer = None
    pyramid_buffer = None
    truncated_pyramid_buffer = None
    hex_prism_buffer = None
    tri_prism_buffer = None
    ngon_prism_buffer = None
    glsl_buffer = None
    active_buffers = {}
    
    @classmethod
    def bind_to_storage_buffer(cls):
        for k, v in cls.active_buffers.items():
            v.bind_to_storage_buffer(k)
    
    # Free all buffers
    @classmethod
    def release_all(cls):
        cls.release_object_common_buffer()
        cls.release_box_buffer()
        cls.release_sphere_buffer()
        cls.release_cylinder_buffer()
        cls.release_torus_buffer()
        cls.release_cone_buffer()
        cls.release_pyramid_buffer()
        cls.release_truncated_pyramid_buffer()
        cls.release_hex_prism_buffer()
        cls.release_tri_prism_buffer()
        cls.release_ngon_prism_buffer()
        cls.release_glsl_buffer()

    # Build all buffers
    @classmethod
    def generate_all(cls, ctx, context):
        cls.generate_object_common_buffer(ctx, context)        
        cls.generate_box_buffer(ctx, context)
        cls.generate_sphere_buffer(ctx, context)
        cls.generate_cylinder_buffer(ctx, context)
        cls.generate_torus_buffer(ctx, context)
        cls.generate_cone_buffer(ctx, context)
        cls.generate_pyramid_buffer(ctx, context)
        cls.generate_truncated_pyramid_buffer(ctx, context)
        cls.generate_hex_prism_buffer(ctx, context)
        cls.generate_tri_prism_buffer(ctx, context)
        cls.generate_ngon_prism_buffer(ctx, context)
        cls.generate_glsl_buffer(ctx, context)

    # ----------------------------------------------------------
    # Storage Buffer Objects of Common Propertys
    #

    # Get object_common_buffer regardless of whether the value is None or not
    @classmethod
    def get_object_common_buffer(cls):
        return cls.object_common_buffer
    
    # Generate buffer for SDFObjectProperty
    @classmethod
    def _generate_object_common_buffer(cls, ctx, context):
        
        # If the buffer has already been allocated, release it
        cls.release_object_common_buffer()
        
        dsize = 12 # position (3), scale (1), quaternion (4), blend (4)
        alist = context.scene.sdf_object_pointer_list
        narray = np.empty(len(alist) * dsize, dtype='float32')
        
        for i, pointer in enumerate(alist):
            object = pointer.object
            sdf_prop = object.sdf_prop
            
            mat = object.matrix_world
            p = mat.to_translation()
            r = mat.to_quaternion()
            s = mat.to_scale()
            po = sdf_prop.position_offset
            bl_0, bl_1 = cls.__get_blend_props[sdf_prop.blend_type](sdf_prop)
            
            offset = i * dsize
            narray[offset + 0] = p[0] + (po[0] * s[0])
            narray[offset + 1] = p[1] + (po[1] * s[0])
            narray[offset + 2] = p[2] + (po[2] * s[0])
            narray[offset + 3] = s[0]
            narray[offset + 4] = r[0]
            narray[offset + 5] = r[1]
            narray[offset + 6] = r[2]
            narray[offset + 7] = r[3]
            narray[offset + 8] = bl_0
            narray[offset + 9] = bl_1
            # narray[offset + 10] = 0
            # narray[offset + 11] = 0

        # Generate a buffer to bind to the shader using np.array as source
        buf = ctx.buffer(narray.tobytes())
        cls.object_common_buffer = buf
        cls.active_buffers[0] = cls.object_common_buffer
        # buf.bind_to_storage_buffer(0)
        
        print('\n', '[generate_object_common_buffer] object_common:', narray, '\n')
        
        return cls.object_common_buffer
    
    # Generate buffer for SDFObjectProperty
    @classmethod
    def generate_object_common_buffer(cls, ctx, context):
        # If the element of the list is 0, the buffer is not used and shall be released.
        if len(context.scene.sdf_object_pointer_list) > 0:
            cls._generate_object_common_buffer(ctx, context)
        else:
            return cls.release_object_common_buffer()
    
    # Reflects the specified element of the SDFObjectProperty list in the buffer
    @classmethod
    def _update_object_common_buffer(cls, ctx, context, i):
        
        dsize = 12 # position (3), scale (1), quaternion (4), blend (4)
        alist = context.scene.sdf_object_pointer_list
        narray = np.empty(dsize, dtype='float32')
        
        pointer = alist[i]
        object = pointer.object
        sdf_prop = object.sdf_prop
        
        mat = object.matrix_world
        p = mat.to_translation()
        r = mat.to_quaternion()
        s = mat.to_scale()
        po = sdf_prop.position_offset
        bl_0, bl_1 = cls.__get_blend_props[sdf_prop.blend_type](sdf_prop)
        
        narray[0] = p[0] + (po[0] * s[0])
        narray[1] = p[1] + (po[1] * s[0])
        narray[2] = p[2] + (po[2] * s[0])
        narray[3] = s[0]
        narray[4] = r[0]
        narray[5] = r[1]
        narray[6] = r[2]
        narray[7] = r[3]
        narray[8] = bl_0
        narray[9] = bl_1
        # narray[10] = 0
        # narray[11] = 0
        
        buf = cls.object_common_buffer
        buf.write(narray.tobytes(), i * dsize * 4)
        
        print('\n', '[update_object_common_buffer] index:', i, 'narray:', narray, '\n')
        
        return cls.object_common_buffer

    # Reflects the specified element of the SDFObjectProperty list in the buffer
    @classmethod
    def update_object_common_buffer(cls, ctx, context, i):

        # If the element of the list is 0, the buffer is not used and shall be released.
        if len(context.scene.sdf_object_pointer_list) == 0:
            return cls.release_object_common_buffer()
        
        # If buffer is set to None for some reason, a new buffer is created here.
        if cls.object_common_buffer == None:
            return cls._generate_object_common_buffer(ctx, context)
        
        return cls._update_object_common_buffer(ctx, context, i)
    
    # Release buffer used for SDFObjectProperty
    @classmethod
    def release_object_common_buffer(cls):
        if cls.object_common_buffer != None:
            del cls.active_buffers[0]
            cls.object_common_buffer.release()
        cls.object_comon_buffer = None

    # ----------------------------------------------------------
    # Storage Buffer Objects of Box Primitive
    #

    @classmethod
    def get_box_buffer(cls):
        return cls.box_buffer
    
    @classmethod
    def _generate_box_buffer(cls, ctx, context):
        
        # If the buffer has already been allocated, release it
        cls.release_box_buffer()
        
        dsize = 8 # bound (3), round (1), corner round (4)
        alist = context.scene.sdf_box_pointer_list
        narray = np.empty(len(alist) * dsize, dtype='float32')
        
        for i, pointer in enumerate(alist):
            object = pointer.object
            sdf_prop = object.sdf_prop
            
            bound = [
                pointer.bound[0],
                pointer.bound[1],
                pointer.bound[2]
            ]
            round = min(bound) * pointer.round
            bound[0] = bound[0] - round
            bound[1] = bound[1] - round
            bound[2] = bound[2] - round
            
            mnhalf = min(bound[0], bound[1])
            cround = (
                pointer.corner_round[0] * mnhalf,
                pointer.corner_round[1] * mnhalf,
                pointer.corner_round[2] * mnhalf,
                pointer.corner_round[3] * mnhalf
            )
            
            offset = i * dsize
            narray[offset + 0] = bound[0]
            narray[offset + 1] = bound[1]
            narray[offset + 2] = bound[2]
            narray[offset + 3] = round
            narray[offset + 4] = cround[0]
            narray[offset + 5] = cround[1]
            narray[offset + 6] = cround[2]
            narray[offset + 7] = cround[3]

        # Generate a buffer to bind to the shader using np.array as source
        buf = ctx.buffer(narray.tobytes())
        cls.box_buffer = buf
        cls.active_buffers[1] = cls.box_buffer
        # buf.bind_to_storage_buffer(1)
        
        print('\n', '[generate_box_buffer] narray:', narray, 'buf:', buf.read(), '\n')
        
        return cls.box_buffer
    
    @classmethod
    def generate_box_buffer(cls, ctx, context):
        if len(context.scene.sdf_box_pointer_list) > 0:
            return cls._generate_box_buffer(ctx, context)
        else:
            return cls.release_box_buffer()
    
    @classmethod
    def _update_box_buffer(cls, ctx, context, i, sub_i):
                
        dsize = 8 # bound (3), round (1), corner round (4)
        alist = context.scene.sdf_box_pointer_list
        narray = np.empty(dsize, dtype='float32')
        
        pointer = alist[sub_i]
        object = pointer.object
        sdf_prop = object.sdf_prop
        
        bound = [
            pointer.bound[0],
            pointer.bound[1],
            pointer.bound[2]
        ]
        round = min(bound) * pointer.round
        
        print('\n', '[round amount]', round, '\n')
        
        bound[0] = bound[0] - round
        bound[1] = bound[1] - round
        bound[2] = bound[2] - round
        
        mnhalf = min(bound[0], bound[2])
        cround = (
            pointer.corner_round[0] * mnhalf,
            pointer.corner_round[1] * mnhalf,
            pointer.corner_round[2] * mnhalf,
            pointer.corner_round[3] * mnhalf
        )
        
        narray[0] = bound[0]
        narray[1] = bound[1]
        narray[2] = bound[2]
        narray[3] = round
        narray[4] = cround[0]
        narray[5] = cround[1]
        narray[6] = cround[2]
        narray[7] = cround[3]
        
        buf = cls.box_buffer
        buf.write(narray.tobytes(), sub_i * dsize * 4)
        
        print('\n', '[generate_box_buffer] index:', i, 'narray:', narray, 'buf:', buf.read(), '\n')
        
        return cls.box_buffer
    
    @classmethod
    def update_box_buffer(cls, ctx, context, i, sub_i):

        # If the element of the list is 0, the buffer is not used and shall be released.
        if len(context.scene.sdf_box_pointer_list) == 0:
            return cls.release_box_buffer()
        
        # If buffer is set to None for some reason, a new buffer is created here.
        if cls.box_buffer == None:
            return cls._generate_box_buffer(ctx, context)
        
        return cls._update_box_buffer(ctx, context, i, sub_i)
    
    @classmethod
    def release_box_buffer(cls):
        if cls.box_buffer != None:
            del cls.active_buffers[1]
            cls.box_buffer.release()
        cls.box_buffer = None

    # ----------------------------------------------------------
    # Storage Buffer Objects of Sphere Primitive
    #

    @classmethod
    def get_sphere_buffer(cls):
        return cls.sphere_buffer
    
    @classmethod
    def _generate_sphere_buffer(cls, ctx, context):
        
        # If the buffer has already been allocated, release it
        cls.release_sphere_buffer()
        
        dsize = 1 # radius (1)
        alist = context.scene.sdf_sphere_pointer_list
        narray = np.empty(len(alist) * dsize, dtype=np.float32)
        
        for i, pointer in enumerate(alist):
            object = pointer.object
            sdf_prop = object.sdf_prop
            
            radius = pointer.radius
            
            offset = i * dsize
            narray[offset + 0] = radius

        # Generate a buffer to bind to the shader using np.array as source
        buf = ctx.buffer(narray.tobytes())
        cls.sphere_buffer = buf
        cls.active_buffers[2] = cls.sphere_buffer
        # buf.bind_to_storage_buffer(2)
        
        print('\n', '[generate_sphere_buffer] narray:', narray, 'buf:', buf.read(), '\n')
        
        return cls.sphere_buffer

    @classmethod
    def generate_sphere_buffer(cls, ctx, context):
        if len(context.scene.sdf_sphere_pointer_list) > 0:
            cls._generate_sphere_buffer(ctx, context)
        else:
            cls.release_sphere_buffer()

    @classmethod
    def _update_sphere_buffer(cls, ctx, context, i, sub_i):
        
        dsize = 1 # radius (1)
        alist = context.scene.sdf_sphere_pointer_list
        narray = np.empty(dsize, dtype=np.float32)
        
        pointer = alist[sub_i]
        object = pointer.object
        sdf_prop = object.sdf_prop
        
        radius = pointer.radius
        
        narray[0] = radius
        
        buf = cls.sphere_buffer
        buf.write(narray.tobytes(), sub_i * dsize * 4)
        
        print('\n', '[generate_sphere_buffer] index:', i, 'narray:', narray, 'buf:', buf.read(), '\n')
        
        return cls.sphere_buffer

    @classmethod
    def update_sphere_buffer(cls, ctx, context, i, sub_i):

        # If the element of the list is 0, the buffer is not used and shall be released.
        if len(context.scene.sdf_sphere_pointer_list) == 0:
            return cls.release_sphere_buffer()
        
        # If buffer is set to None for some reason, a new buffer is created here.
        if cls.sphere_buffer == None:
            return cls._generate_sphere_buffer(ctx, context)
        
        return cls._update_sphere_buffer(ctx, context, i, sub_i)
    
    @classmethod
    def release_sphere_buffer(cls):
        if cls.sphere_buffer != None:
            del cls.active_buffers[2]
            cls.sphere_buffer.release()
        cls.sphere_buffer = None
    
    # ----------------------------------------------------------
    # Storage Buffer Objects of Cylinder Primitive
    #
    
    @classmethod
    def get_cylinder_buffer(cls):
        return cls.cylinder_buffer
    
    @classmethod
    def _generate_cylinder_buffer(cls, ctx, context):
        
        # If the buffer has already been allocated, release it
        cls.release_cylinder_buffer()
        
        dsize = 4 # height (1), radius (1), round (1), dummy (1)
        alist = context.scene.sdf_cylinder_pointer_list
        narray = np.empty(len(alist) * dsize, dtype=np.float32)
        
        for i, pointer in enumerate(alist):
            object = pointer.object
            sdf_prop = object.sdf_prop
            
            height = pointer.height * 0.5
            radius = pointer.radius
            round = min(radius, height) * pointer.round
            
            offset = i * dsize
            narray[offset + 0] = height - round
            narray[offset + 1] = radius - round
            narray[offset + 2] = round
            # narray[offset + 3] = 0 # dummy

        # Generate a buffer to bind to the shader using np.array as source
        buf = ctx.buffer(narray.tobytes())
        cls.cylinder_buffer = buf
        cls.active_buffers[3] = cls.cylinder_buffer
        # buf.bind_to_storage_buffer(3)
        
        print('\n', '[generate_cylinder_buffer] narray:', narray, 'buf:', buf.read(), '\n')
        
        return cls.cylinder_buffer

    @classmethod
    def generate_cylinder_buffer(cls, ctx, context):
        if len(context.scene.sdf_cylinder_pointer_list) > 0:
            cls._generate_cylinder_buffer(ctx, context)
        else:
            cls.release_cylinder_buffer()

    @classmethod
    def _update_cylinder_buffer(cls, ctx, context, i, sub_i):
        
        dsize = 4 # height (1), radius (1), round (1), dummy (1)
        alist = context.scene.sdf_cylinder_pointer_list
        narray = np.empty(dsize, dtype=np.float32)
        
        pointer = alist[sub_i]
        object = pointer.object
        sdf_prop = object.sdf_prop
        
        height = pointer.height * 0.5
        radius = pointer.radius
        round = min(radius, height) * pointer.round
        
        narray[0] = height - round
        narray[1] = radius - round
        narray[2] = round
        # narray[3] = 0 # dummy
        
        buf = cls.cylinder_buffer
        buf.write(narray.tobytes(), sub_i * dsize * 4)
        
        print('\n', '[generate_cylinder_buffer] narray:', narray, 'buf:', buf.read(), '\n')
        
        return cls.cylinder_buffer

    @classmethod
    def update_cylinder_buffer(cls, ctx, context, i, sub_i):

        # If the element of the list is 0, the buffer is not used and shall be released.
        if len(context.scene.sdf_cylinder_pointer_list) == 0:
            return cls.release_cylinder_buffer()
        
        # If buffer is set to None for some reason, a new buffer is created here.
        if cls.cylinder_buffer == None:
            return cls._generate_cylinder_buffer(ctx, context)
        
        return cls._update_cylinder_buffer(ctx, context, i, sub_i)
    
    @classmethod
    def release_cylinder_buffer(cls):
        if cls.cylinder_buffer != None:
            del cls.active_buffers[3]
            cls.cylinder_buffer.release()
        cls.cylinder_buffer = None

    # ----------------------------------------------------------
    # Storage Buffer Objects of Torus Primitive
    #
    
    @classmethod
    def get_torus_buffer(cls):
        return cls.torus_buffer
    
    @classmethod
    def _generate_torus_buffer(cls, ctx, context):
        
        # If the buffer has already been allocated, release it
        cls.release_torus_buffer()
        
        dsize = 4 # radius0 (1), radius1 (1), fill (sin(theta), cos(theta))
        alist = context.scene.sdf_torus_pointer_list
        narray = np.empty(len(alist) * dsize, dtype=np.float32)
        
        for i, pointer in enumerate(alist):
            object = pointer.object
            sdf_prop = object.sdf_prop
            
            radius = pointer.radius
            fill = pointer.fill * math.pi
            
            offset = i * dsize
            narray[offset + 0] = radius[0]
            narray[offset + 1] = radius[1]
            narray[offset + 2] = math.sin(fill)
            narray[offset + 3] = math.cos(fill)

        # Generate a buffer to bind to the shader using np.array as source
        buf = ctx.buffer(narray.tobytes())
        cls.torus_buffer = buf
        cls.active_buffers[4] = cls.torus_buffer
        # buf.bind_to_storage_buffer(4)
        
        print('\n', '[generate_torus_buffer] narray:', narray, 'buf:', buf.read(), '\n')
        
        return cls.torus_buffer

    @classmethod
    def generate_torus_buffer(cls, ctx, context):
        if len(context.scene.sdf_torus_pointer_list) > 0:
            cls._generate_torus_buffer(ctx, context)
        else:
            cls.release_torus_buffer()

    @classmethod
    def _update_torus_buffer(cls, ctx, context, i, sub_i):
        
        dsize = 4 # radius0 (1), radius1 (1), fill (sin(theta), cos(theta))
        alist = context.scene.sdf_torus_pointer_list
        narray = np.empty(dsize, dtype=np.float32)
        
        pointer = alist[sub_i]
        object = pointer.object
        sdf_prop = object.sdf_prop
        
        radius = pointer.radius
        fill = pointer.fill * math.pi
        
        narray[0] = radius[0]
        narray[1] = radius[1]
        narray[2] = math.sin(fill)
        narray[3] = math.cos(fill)
        
        buf = cls.torus_buffer
        buf.write(narray.tobytes(), sub_i * dsize * 4)
        
        print('\n', '[generate_torus_buffer] narray:', narray, 'buf:', buf.read(), '\n')
        
        return cls.torus_buffer

    @classmethod
    def update_torus_buffer(cls, ctx, context, i, sub_i):

        # If the element of the list is 0, the buffer is not used and shall be released.
        if len(context.scene.sdf_torus_pointer_list) == 0:
            return cls.release_torus_buffer()
        
        # If buffer is set to None for some reason, a new buffer is created here.
        if cls.torus_buffer == None:
            return cls._generate_torus_buffer(ctx, context)
        
        return cls._update_torus_buffer(ctx, context, i, sub_i)
    
    @classmethod
    def release_torus_buffer(cls):
        if cls.torus_buffer != None:
            del cls.active_buffers[4]
            cls.torus_buffer.release()
        cls.torus_buffer = None
    
    # ----------------------------------------------------------
    # Storage Buffer Objects of Cone Primitive
    #
    
    @classmethod
    def get_cone_buffer(cls):
        return cls.cone_buffer
    
    @classmethod
    def _generate_cone_buffer(cls, ctx, context):
        
        # If the buffer has already been allocated, release it
        cls.release_cone_buffer()
        
        dsize = 4 # height (1), radius0 (1), radius1 (1), round (1)
        alist = context.scene.sdf_cone_pointer_list
        narray = np.empty(len(alist) * dsize, dtype=np.float32)
        
        for i, pointer in enumerate(alist):
            object = pointer.object
            sdf_prop = object.sdf_prop
            
            radius = pointer.radius
            height = pointer.height * 0.5
            round = min(radius[0], radius[1], height) * pointer.round
            
            offset = i * dsize
            narray[offset + 0] = height - round
            narray[offset + 1] = radius[0] - round
            narray[offset + 2] = radius[1] - round
            narray[offset + 3] = round

        # Generate a buffer to bind to the shader using np.array as source
        buf = ctx.buffer(narray.tobytes())
        cls.cone_buffer = buf
        cls.active_buffers[5] = cls.cone_buffer
        # buf.bind_to_storage_buffer(5)
        
        print('\n', '[generate_cone_buffer] narray:', narray, 'buf:', buf.read(), '\n')
        
        return cls.cone_buffer

    @classmethod
    def generate_cone_buffer(cls, ctx, context):
        if len(context.scene.sdf_cone_pointer_list) > 0:
            cls._generate_cone_buffer(ctx, context)
        else:
            cls.release_cone_buffer()

    @classmethod
    def _update_cone_buffer(cls, ctx, context, i, sub_i):
        
        dsize = 4 # height (1), radius0 (1), radius1 (1), round (1)
        alist = context.scene.sdf_cone_pointer_list
        narray = np.empty(dsize, dtype=np.float32)
        
        pointer = alist[sub_i]
        object = pointer.object
        sdf_prop = object.sdf_prop
        
        radius = pointer.radius
        height = pointer.height * 0.5
        round = min(radius[0], radius[1], height) * pointer.round
        
        narray[0] = height - round
        narray[1] = radius[0] - round
        narray[2] = radius[1] - round
        narray[3] = round
        
        buf = cls.cone_buffer
        buf.write(narray.tobytes(), sub_i * dsize * 4)
        
        print('\n', '[generate_cone_buffer] narray:', narray, 'buf:', buf.read(), '\n')
        
        return cls.cone_buffer

    @classmethod
    def update_cone_buffer(cls, ctx, context, i, sub_i):

        # If the element of the list is 0, the buffer is not used and shall be released.
        if len(context.scene.sdf_cone_pointer_list) == 0:
            return cls.release_cone_buffer()
        
        # If buffer is set to None for some reason, a new buffer is created here.
        if cls.cone_buffer == None:
            return cls._generate_cone_buffer(ctx, context)
        
        return cls._update_cone_buffer(ctx, context, i, sub_i)
    
    @classmethod
    def release_cone_buffer(cls):
        if cls.cone_buffer != None:
            del cls.active_buffers[5]
            cls.cone_buffer.release()
        cls.cone_buffer = None
    
    
    # ----------------------------------------------------------
    # Storage Buffer Objects of Pyramid
    #
    
    @classmethod
    def get_pyramid_buffer(cls):
        return cls.pyramid_buffer
    
    @classmethod
    def _generate_pyramid_buffer(cls, ctx, context):
        
        # If the buffer has already been allocated, release it
        cls.release_pyramid_buffer()
        
        dsize = 4 # half width (1), half depth (1), half height (1), round (1)
        alist = context.scene.sdf_pyramid_pointer_list
        narray = np.empty(len(alist) * dsize, dtype=np.float32)
        
        for i, pointer in enumerate(alist):
            object = pointer.object
            sdf_prop = object.sdf_prop
        
            hwidth = pointer.width * 0.5
            hdepth = pointer.depth * 0.5
            hheight = pointer.height * 0.5
            
            height = pointer.height
            
            theta_w0 = math.atan(height / hwidth)
            theta_w1 = theta_w0 * 0.5
            theta_d0 = math.atan(height / hdepth)
            theta_d1 = theta_d0 * 0.5
            
            padding_width_lim_min = hwidth * math.tan(theta_w1)
            padding_depth_lim_min = hdepth * math.tan(theta_d1)
            
            round = min(padding_width_lim_min, padding_depth_lim_min, hheight) * pointer.round
            offst = round / math.cos(max(theta_w0, theta_d0))
            
            padding_width = round / math.tan(theta_w1)
            padding_depth = round / math.tan(theta_d1)
            
            offset = i * dsize
            narray[offset + 0] = hwidth - padding_width
            narray[offset + 1] = hdepth - padding_depth
            narray[offset + 2] = hheight - (round + offst) * 0.5
            narray[offset + 3] = round
            
            sdf_prop.position_offset[2] = -(offst-round) * 0.5
            

        # Generate a buffer to bind to the shader using np.array as source
        buf = ctx.buffer(narray.tobytes())
        cls.pyramid_buffer = buf
        cls.active_buffers[6] = cls.pyramid_buffer
        # buf.bind_to_storage_buffer(6)
        
        print('\n', '[generate_pyramid_buffer] narray:', narray, 'buf:', buf.read(), '\n')
        
        return cls.pyramid_buffer

    @classmethod
    def generate_pyramid_buffer(cls, ctx, context):
        if len(context.scene.sdf_pyramid_pointer_list) > 0:
            cls._generate_pyramid_buffer(ctx, context)
        else:
            cls.release_pyramid_buffer()

    @classmethod
    def _update_pyramid_buffer(cls, ctx, context, i, sub_i):
        
        dsize = 4 # half width (1), half depth (1), half height (1), round (1)
        alist = context.scene.sdf_pyramid_pointer_list
        narray = np.empty(dsize, dtype=np.float32)
        
        pointer = alist[sub_i]
        object = pointer.object
        sdf_prop = object.sdf_prop
        
        hwidth = pointer.width * 0.5
        hdepth = pointer.depth * 0.5
        hheight = pointer.height * 0.5
                
        height = pointer.height
        
        theta_w0 = math.atan(height / hwidth)
        theta_w1 = theta_w0 * 0.5
        theta_d0 = math.atan(height / hdepth)
        theta_d1 = theta_d0 * 0.5
        
        padding_width_lim_min = hwidth * math.tan(theta_w1)
        padding_depth_lim_min = hdepth * math.tan(theta_d1)
        
        round = min(padding_width_lim_min, padding_depth_lim_min, hheight) * pointer.round
        offst = round / math.cos(max(theta_w0, theta_d0))
        
        padding_width = round / math.tan(theta_w1)
        padding_depth = round / math.tan(theta_d1)
        
        narray[0] = hwidth - padding_width
        narray[1] = hdepth - padding_depth
        narray[2] = hheight - (round + offst) * 0.5
        narray[3] = round

        sdf_prop.position_offset[2] = -(offst-round) * 0.5
        
        buf = cls.pyramid_buffer
        buf.write(narray.tobytes(), sub_i * dsize * 4)
        
        print('\n', '[generate_pyramid_buffer] narray:', narray, 'buf:', buf.read(), '\n')
        
        return cls.pyramid_buffer

    @classmethod
    def update_pyramid_buffer(cls, ctx, context, i, sub_i):

        # If the element of the list is 0, the buffer is not used and shall be released.
        if len(context.scene.sdf_pyramid_pointer_list) == 0:
            return cls.release_pyramid_buffer()
        
        # If buffer is set to None for some reason, a new buffer is created here.
        if cls.pyramid_buffer == None:
            return cls._generate_pyramid_buffer(ctx, context)
        
        return cls._update_pyramid_buffer(ctx, context, i, sub_i)
    
    @classmethod
    def release_pyramid_buffer(cls):
        if cls.pyramid_buffer != None:
            del cls.active_buffers[6]
            cls.pyramid_buffer.release()
        cls.pyramid_buffer = None

    # ----------------------------------------------------------
    # Storage Buffer Objects of Pyramid
    #
    
    @classmethod
    def get_truncated_pyramid_buffer(cls):
        return cls.truncated_pyramid_buffer
    
    @classmethod
    def _generate_truncated_pyramid_buffer(cls, ctx, context):
        
        # If the buffer has already been allocated, release it
        cls.release_truncated_pyramid_buffer()
        
        dsize = 6 # half width 0 (1), half depth 0 (1), half width 1 (1), half depth 1 (1), half height (1), round (1)
        alist = context.scene.sdf_truncated_pyramid_pointer_list
        narray = np.empty(len(alist) * dsize, dtype=np.float32)
        
        for i, pointer in enumerate(alist):
            object = pointer.object
            sdf_prop = object.sdf_prop
            
            hwidth_0 = pointer.width_0 * 0.5
            hdepth_0 = pointer.depth_0 * 0.5
            hwidth_1 = pointer.width_1 * 0.5
            hdepth_1 = pointer.depth_1 * 0.5
            hheight = pointer.height * 0.5
            
            height = pointer.height
            round = hheight * pointer.round
            
            hwidth_idx_max, hwidth_idx_min = 0, 2
            hdepth_idx_max, hdepth_idx_min = 1, 3
            
            if hwidth_0 > hwidth_1:
                hwidth_max, hwidth_min = hwidth_0, hwidth_1
                hwidth_idx_max, hwidth_idx_min = 0, 2
            else:
                hwidth_max, hwidth_min = hwidth_1, hwidth_0
                hwidth_idx_max, hwidth_idx_min = 2, 0
                
            if hdepth_0 > hdepth_1:
                hdepth_max, hdepth_min = hdepth_0, hdepth_1
                hdepth_idx_max, hdepth_idx_min = 1, 3
            else:
                hdepth_max, hdepth_min = hdepth_1, hdepth_0
                hdepth_idx_max, hdepth_idx_min = 3, 1
                
            theta_w0 = math.atan(height / (hwidth_max - hwidth_min)) if hwidth_max > hwidth_min else math.pi * 0.5
            theta_w1 = theta_w0 * 0.5
            
            theta_d0 = math.atan(height / (hdepth_max - hdepth_min)) if hdepth_max > hdepth_min else math.pi * 0.5
            theta_d1 = theta_d0 * 0.5
            
            padding_width_lim_min = hwidth_min * math.sin(theta_w0)
            padding_depth_lim_min = hdepth_min * math.sin(theta_d0)
            
            round = min(round, padding_width_lim_min, padding_depth_lim_min)
            ratio = round / height
            
            padding_width_max = round / math.tan(theta_w1)
            padding_width_min = round / math.sin(theta_w0) - ratio * (hwidth_max - hwidth_min)
            
            padding_depth_max = round / math.tan(theta_d1)
            padding_depth_min = round / math.sin(theta_d0) - ratio * (hdepth_max - hdepth_min)
            
            offset = i * dsize
            narray[offset + hwidth_idx_max] = hwidth_max - padding_width_max
            narray[offset + hwidth_idx_min] = hwidth_min - padding_width_min
            narray[offset + hdepth_idx_max] = hdepth_max - padding_depth_max
            narray[offset + hdepth_idx_min] = hdepth_min - padding_depth_min
            narray[offset + 4] = hheight - round
            narray[offset + 5] = round

        # Generate a buffer to bind to the shader using np.array as source
        buf = ctx.buffer(narray.tobytes())
        cls.truncated_pyramid_buffer = buf
        cls.active_buffers[7] = cls.truncated_pyramid_buffer
        # buf.bind_to_storage_buffer(7)
        
        print('\n', '[generate_truncated_pyramid_buffer] narray:', narray, 'buf:', buf.read(), '\n')
        
        return cls.truncated_pyramid_buffer

    @classmethod
    def generate_truncated_pyramid_buffer(cls, ctx, context):
        if len(context.scene.sdf_truncated_pyramid_pointer_list) > 0:
            cls._generate_truncated_pyramid_buffer(ctx, context)
        else:
            cls.release_truncated_pyramid_buffer()

    @classmethod
    def _update_truncated_pyramid_buffer(cls, ctx, context, i, sub_i):
        
        dsize = 6 # half width 0 (1), half depth 0 (1), half width 1 (1), half depth 1 (1), half height (1), round (1)
        alist = context.scene.sdf_truncated_pyramid_pointer_list
        narray = np.empty(dsize, dtype=np.float32)
        
        pointer = alist[sub_i]
        object = pointer.object
        sdf_prop = object.sdf_prop
        
        object = pointer.object
        sdf_prop = object.sdf_prop
        
        hwidth_0 = pointer.width_0 * 0.5
        hdepth_0 = pointer.depth_0 * 0.5
        hwidth_1 = pointer.width_1 * 0.5
        hdepth_1 = pointer.depth_1 * 0.5
        hheight = pointer.height * 0.5
        
        height = pointer.height
        round = hheight * pointer.round
        
        hwidth_idx_max, hwidth_idx_min = 0, 2
        hdepth_idx_max, hdepth_idx_min = 1, 3
        
        if hwidth_0 > hwidth_1:
            hwidth_max, hwidth_min = hwidth_0, hwidth_1
            hwidth_idx_max, hwidth_idx_min = 0, 2
        else:
            hwidth_max, hwidth_min = hwidth_1, hwidth_0
            hwidth_idx_max, hwidth_idx_min = 2, 0
            
        if hdepth_0 > hdepth_1:
            hdepth_max, hdepth_min = hdepth_0, hdepth_1
            hdepth_idx_max, hdepth_idx_min = 1, 3
        else:
            hdepth_max, hdepth_min = hdepth_1, hdepth_0
            hdepth_idx_max, hdepth_idx_min = 3, 1
            
        theta_w0 = math.atan(height / (hwidth_max - hwidth_min))
        theta_w1 = theta_w0 * 0.5
        
        theta_d0 = math.atan(height / (hdepth_max - hdepth_min))
        theta_d1 = theta_d0 * 0.5
        
        padding_width_lim_min = hwidth_min * math.sin(theta_w0)
        padding_depth_lim_min = hdepth_min * math.sin(theta_d0)
        
        round = min(round, padding_width_lim_min, padding_depth_lim_min)
        ratio = round / height
        
        padding_width_max = round / math.tan(theta_w1)
        padding_width_min = round / math.sin(theta_w0) - ratio * (hwidth_max - hwidth_min)
        
        padding_depth_max = round / math.tan(theta_d1)
        padding_depth_min = round / math.sin(theta_d0) - ratio * (hdepth_max - hdepth_min)
        
        narray[hwidth_idx_max] = hwidth_max - padding_width_max
        narray[hwidth_idx_min] = hwidth_min - padding_width_min
        narray[hdepth_idx_max] = hdepth_max - padding_depth_max
        narray[hdepth_idx_min] = hdepth_min - padding_depth_min
        narray[4] = hheight - round
        narray[5] = round
        
        buf = cls.truncated_pyramid_buffer
        buf.write(narray.tobytes(), sub_i * dsize * 4)
        
        print('\n', '[generate_truncated_pyramid_buffer] narray:', narray, 'buf:', buf.read(), '\n')
        
        return cls.truncated_pyramid_buffer

    @classmethod
    def update_truncated_pyramid_buffer(cls, ctx, context, i, sub_i):

        # If the element of the list is 0, the buffer is not used and shall be released.
        if len(context.scene.sdf_truncated_pyramid_pointer_list) == 0:
            return cls.release_truncated_pyramid_buffer()
        
        # If buffer is set to None for some reason, a new buffer is created here.
        if cls.truncated_pyramid_buffer == None:
            return cls._generate_truncated_pyramid_buffer(ctx, context)
        
        return cls._update_truncated_pyramid_buffer(ctx, context, i, sub_i)
    
    @classmethod
    def release_truncated_pyramid_buffer(cls):
        if cls.truncated_pyramid_buffer != None:
            del cls.active_buffers[7]
            cls.truncated_pyramid_buffer.release()
        cls.truncated_pyramid_buffer = None

    # ----------------------------------------------------------
    # Storage Buffer Objects of Hex Prism Primitive
    #
    
    @classmethod
    def get_hex_prism_buffer(cls):
        return cls.hex_prism_buffer
    
    @classmethod
    def _generate_hex_prism_buffer(cls, ctx, context):
        
        # If the buffer has already been allocated, release it
        cls.release_hex_prism_buffer()
        
        dsize = 4 # height (1), radius (1), round (1), dummy (1)
        alist = context.scene.sdf_hex_prism_pointer_list
        narray = np.empty(len(alist) * dsize, dtype=np.float32)
        
        for i, pointer in enumerate(alist):
            object = pointer.object
            sdf_prop = object.sdf_prop
            
            height = pointer.height * 0.5
            radius = pointer.radius * math.sqrt(3) / 2
            round = min(radius, height) * pointer.round
            
            offset = i * dsize
            narray[offset + 0] = height - round
            narray[offset + 1] = radius - round
            narray[offset + 2] = round
            # narray[offset + 3] = 0 # dummy

        # Generate a buffer to bind to the shader using np.array as source
        buf = ctx.buffer(narray.tobytes())
        cls.hex_prism_buffer = buf
        cls.active_buffers[8] = cls.hex_prism_buffer
        # buf.bind_to_storage_buffer(8)
        
        print('\n', '[generate_hex_prism_buffer] narray:', narray, 'buf:', buf.read(), '\n')
        
        return cls.hex_prism_buffer

    @classmethod
    def generate_hex_prism_buffer(cls, ctx, context):
        if len(context.scene.sdf_hex_prism_pointer_list) > 0:
            cls._generate_hex_prism_buffer(ctx, context)
        else:
            cls.release_hex_prism_buffer()

    @classmethod
    def _update_hex_prism_buffer(cls, ctx, context, i, sub_i):
        
        dsize = 4 # height (1), radius (1), round (1), dummy (1)
        alist = context.scene.sdf_hex_prism_pointer_list
        narray = np.empty(dsize, dtype=np.float32)
        
        pointer = alist[sub_i]
        object = pointer.object
        sdf_prop = object.sdf_prop
        
        height = pointer.height * 0.5
        radius = pointer.radius * math.sqrt(3) / 2
        round = min(radius, height) * pointer.round
        
        narray[0] = height - round
        narray[1] = radius - round
        narray[2] = round
        # narray[3] = 0 # dummy
        
        buf = cls.hex_prism_buffer
        buf.write(narray.tobytes(), sub_i * dsize * 4)
        
        print('\n', '[generate_hex_prism_buffer] narray:', narray, 'buf:', buf.read(), '\n')
        
        return cls.hex_prism_buffer

    @classmethod
    def update_hex_prism_buffer(cls, ctx, context, i, sub_i):

        # If the element of the list is 0, the buffer is not used and shall be released.
        if len(context.scene.sdf_hex_prism_pointer_list) == 0:
            return cls.release_hex_prism_buffer()
        
        # If buffer is set to None for some reason, a new buffer is created here.
        if cls.hex_prism_buffer == None:
            return cls._generate_hex_prism_buffer(ctx, context)
        
        return cls._update_hex_prism_buffer(ctx, context, i, sub_i)
    
    @classmethod
    def release_hex_prism_buffer(cls):
        if cls.hex_prism_buffer != None:
            del cls.active_buffers[8]
            cls.hex_prism_buffer.release()
        cls.hex_prism_buffer = None

    
    # ----------------------------------------------------------
    # Storage Buffer Objects of Tri Prism Primitive
    #
    
    @classmethod
    def get_tri_prism_buffer(cls):
        return cls.tri_prism_buffer
    
    @classmethod
    def _generate_tri_prism_buffer(cls, ctx, context):
        
        # If the buffer has already been allocated, release it
        cls.release_tri_prism_buffer()
        
        dsize = 4 # height (1), radius (1), round (1), dummy (1)
        alist = context.scene.sdf_tri_prism_pointer_list
        narray = np.empty(len(alist) * dsize, dtype=np.float32)
        
        for i, pointer in enumerate(alist):
            object = pointer.object
            sdf_prop = object.sdf_prop
            
            height = pointer.height * 0.5
            radius = pointer.radius
            round = min(radius, height) * pointer.round
            
            offset = i * dsize
            narray[offset + 0] = height - round
            narray[offset + 1] = radius - round
            narray[offset + 2] = round
            # narray[offset + 3] = 0 # dummy

        # Generate a buffer to bind to the shader using np.array as source
        buf = ctx.buffer(narray.tobytes())
        cls.tri_prism_buffer = buf
        cls.active_buffers[9] = cls.tri_prism_buffer
        # buf.bind_to_storage_buffer(9)
        
        print('\n', '[generate_tri_prism_buffer] narray:', narray, 'buf:', buf.read(), '\n')
        
        return cls.tri_prism_buffer

    @classmethod
    def generate_tri_prism_buffer(cls, ctx, context):
        if len(context.scene.sdf_tri_prism_pointer_list) > 0:
            cls._generate_tri_prism_buffer(ctx, context)
        else:
            cls.release_tri_prism_buffer()

    @classmethod
    def _update_tri_prism_buffer(cls, ctx, context, i, sub_i):
        
        dsize = 4 # height (1), radius (1), round (1), dummy (1)
        alist = context.scene.sdf_tri_prism_pointer_list
        narray = np.empty(dsize, dtype=np.float32)
        
        pointer = alist[sub_i]
        object = pointer.object
        sdf_prop = object.sdf_prop
        
        height = pointer.height * 0.5
        radius = pointer.radius
        round = min(radius, height) * pointer.round
        
        narray[0] = height - round
        narray[1] = radius - round
        narray[2] = round
        # narray[3] = 0 # dummy
        
        buf = cls.tri_prism_buffer
        buf.write(narray.tobytes(), sub_i * dsize * 4)
        
        print('\n', '[generate_tri_prism_buffer] narray:', narray, 'buf:', buf.read(), '\n')
        
        return cls.tri_prism_buffer

    @classmethod
    def update_tri_prism_buffer(cls, ctx, context, i, sub_i):

        # If the element of the list is 0, the buffer is not used and shall be released.
        if len(context.scene.sdf_tri_prism_pointer_list) == 0:
            return cls.release_tri_prism_buffer()
        
        # If buffer is set to None for some reason, a new buffer is created here.
        if cls.tri_prism_buffer == None:
            return cls._generate_tri_prism_buffer(ctx, context)
        
        return cls._update_tri_prism_buffer(ctx, context, i, sub_i)
    
    @classmethod
    def release_tri_prism_buffer(cls):
        if cls.tri_prism_buffer != None:
            del cls.active_buffers[9]
            cls.tri_prism_buffer.release()
        cls.tri_prism_buffer = None
    
    # ----------------------------------------------------------
    # Storage Buffer Objects of Ngon Prism Primitive
    #
    
    @classmethod
    def get_ngon_prism_buffer(cls):
        return cls.ngon_prism_buffer
    
    @classmethod
    def _generate_ngon_prism_buffer(cls, ctx, context):
        
        # If the buffer has already been allocated, release it
        cls.release_ngon_prism_buffer()
        
        dsize = 4 # height (1), radius (1), round (1), nsides (1)
        alist = context.scene.sdf_ngon_prism_pointer_list
        narray = np.empty(len(alist) * dsize, dtype=np.float32)
        
        for i, pointer in enumerate(alist):
            object = pointer.object
            sdf_prop = object.sdf_prop
            
            height = pointer.height * 0.5
            radius = pointer.radius
            round = min(radius, height) * pointer.round
            nsides = pointer.nsides
            
            offset = i * dsize
            narray[offset + 0] = height - round
            narray[offset + 1] = radius - round
            narray[offset + 2] = round
            narray[offset + 3] = nsides

        # Generate a buffer to bind to the shader using np.array as source
        buf = ctx.buffer(narray.tobytes())
        cls.ngon_prism_buffer = buf
        cls.active_buffers[10] = cls.ngon_prism_buffer
        # buf.bind_to_storage_buffer(10)
        
        print('\n', '[generate_ngon_prism_buffer] narray:', narray, 'buf:', buf.read(), '\n')
        
        return cls.ngon_prism_buffer

    @classmethod
    def generate_ngon_prism_buffer(cls, ctx, context):
        if len(context.scene.sdf_ngon_prism_pointer_list) > 0:
            cls._generate_ngon_prism_buffer(ctx, context)
        else:
            cls.release_ngon_prism_buffer()

    @classmethod
    def _update_ngon_prism_buffer(cls, ctx, context, i, sub_i):
        
        dsize = 4 # height (1), radius (1), round (1), nsides (1)
        alist = context.scene.sdf_ngon_prism_pointer_list
        narray = np.empty(dsize, dtype=np.float32)
        
        pointer = alist[sub_i]
        object = pointer.object
        sdf_prop = object.sdf_prop
        
        height = pointer.height * 0.5
        radius = pointer.radius
        round = min(radius, height) * pointer.round
        nsides = pointer.nsides
        
        narray[0] = height - round
        narray[1] = radius - round
        narray[2] = round
        narray[3] = nsides
        
        buf = cls.ngon_prism_buffer
        buf.write(narray.tobytes(), sub_i * dsize * 4)
        
        print('\n','[generate_ngon_prism_buffer] narray:', narray, 'buf:', buf.read(),'\n')
        
        return cls.ngon_prism_buffer

    @classmethod
    def update_ngon_prism_buffer(cls, ctx, context, i, sub_i):

        # If the element of the list is 0, the buffer is not used and shall be released.
        if len(context.scene.sdf_ngon_prism_pointer_list) == 0:
            return cls.release_ngon_prism_buffer()
        
        # If buffer is set to None for some reason, a new buffer is created here.
        if cls.ngon_prism_buffer == None:
            return cls._generate_ngon_prism_buffer(ctx, context)
        
        return cls._update_ngon_prism_buffer(ctx, context, i, sub_i)
    
    @classmethod
    def release_ngon_prism_buffer(cls):
        if cls.ngon_prism_buffer != None:
            del cls.active_buffers[10]
            cls.ngon_prism_buffer.release()
        cls.ngon_prism_buffer = None
    
    # ----------------------------------------------------------
    # Storage Buffer Objects of GLSL Primitive
    #
    
    @classmethod
    def get_glsl_buffer(cls):
        return cls.glsl_buffer
    
    @classmethod
    def generate_glsl_buffer(cls, ctx, context):
        pass

    @classmethod
    def update_glsl_buffer(cls, ctx, context, i, sub_i):
        pass
    
    @classmethod
    def release_glsl_buffer(cls):
        pass

    pass