import time
import bpy
import bmesh
import gpu
import moderngl
import math
import numpy as np
from bpy.props import FloatProperty
from bpy_extras import view3d_utils
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from mesh_from_sdf import marching_tables
from mesh_from_sdf.shader import common
from mesh_from_sdf.shader.factory import *
from mesh_from_sdf.shader.buffer_factory import *


class MarchingCube(object):

    THREAD_DIMENSION_X,THREAD_DIMENSION_Y,THREAD_DIMENSION_Z = 8,8,8
    CHUNK_DIMENSION_X,CHUNK_DIMENSION_Y,CHUNK_DIMENSION_Z = 128,128,128
    voxel_count=CHUNK_DIMENSION_X*CHUNK_DIMENSION_Y*CHUNK_DIMENSION_Z
    max_triangle_count=voxel_count*5
    
    ctx = None

    @classmethod
    def generate_glsl(cls, dist):
        return '''
        #version 430
    
        #define THREAD_DIMENSION_X 8
        #define THREAD_DIMENSION_Y 8
        #define THREAD_DIMENSION_Z 8
        #define CHUNK_DIMENSION_X 128
        #define CHUNK_DIMENSION_Y 128
        #define CHUNK_DIMENSION_Z 128
    
        ''' + common.include_ + common.include_struct_ + '''
        
        struct vec3f { 
            float x;
            float y;
            float z;
        };
        struct Triangle {
            vec3f c;
            vec3f b;
            vec3f a;
            float d;
        };

        layout(local_size_x=THREAD_DIMENSION_X,local_size_y=THREAD_DIMENSION_Y,local_size_z=THREAD_DIMENSION_Z) in;
        
        layout(binding=0) readonly buffer in_prop_object { SDFObjectProp sdfObjectProps[]; };
        layout(binding=1) readonly buffer in_prop_box { SDFBoxProp sdfBoxProps[]; };
        layout(binding=2) readonly buffer in_prop_sphere { SDfSphereProp sdfSphereProps[]; };
        layout(binding=3) readonly buffer in_prop_cylinder { SDFCylinderProp sdfCylinderProps[]; };
        layout(binding=4) readonly buffer in_prop_torus { SDFTorusProp sdfTorusProps[]; };
        layout(binding=5) readonly buffer in_prop_cone { SDFConeProp sdfConeProps[]; };
        layout(binding=6) readonly buffer in_prop_pyramid { SDFPyramidProp sdfPyramidProps[]; };
        layout(binding=7) readonly buffer in_prop_truncated_pyramid { SDFTruncatedPyramidProp sdfTruncatedPyramidProps[]; };
        layout(binding=8) readonly buffer in_prop_hex_prism { SDFPrismProp sdfHexPrismProps[]; };
        layout(binding=9) readonly buffer in_prop_tri_prism { SDFPrismProp sdfTriPrismProps[]; };
        layout(binding=10) readonly buffer in_prop_ngon_prism { SDFNgonPrismProp sdfNgonPrismProps[]; };
        
        layout(binding=11) buffer inout_0 { uint count; };
        layout(binding=12) writeonly buffer out_0 { Triangle triangles[]; };
        layout(binding=13) readonly buffer in_1 { uint edge[]; };
        layout(binding=14) readonly buffer in_2 { int triangulation[][16]; };
        
        uniform vec2 isoRange;
        uniform vec3 chunkSize;
        uniform vec3 forward;
        uniform vec3 right;
        uniform vec3 up;
        uniform vec3 base;
        uniform vec3 chunkOffset;
        uniform float isoLevel;
        
        const ivec3 THREAD_DIMENSION = ivec3(THREAD_DIMENSION_X,THREAD_DIMENSION_Y,THREAD_DIMENSION_Z);
        const ivec3 CHUNK_DIMENSION = ivec3(CHUNK_DIMENSION_X,CHUNK_DIMENSION_Y,CHUNK_DIMENSION_Z);
        const int CORNER_INDEX_A_FROM_EDGE[12] = { 0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3 };
        const int CORNER_INDEX_B_FROM_EDGE[12] = { 1, 2, 3, 0, 5, 6, 7, 4, 4, 5, 6, 7 };
        
        ''' + common.include_frag_ + '''
                
        float getDist(vec3 p) {
        
        ''' + dist + '''
        
            return minDist0;
        }
        float saturate(float x, float min, float max) {
            if (max<=min) return min;
            return (clamp(x,min,max)-min)/(max-min);
        }
        float saturate(float x, vec2 range) {
            return saturate(x,range.x,range.y);
        }
        vec3 interpolateVerts(vec4 v1, vec4 v2) {
            float t = (isoLevel-v1.w)/(v2.w-v1.w);
            return which((v2.xyz+v1.xyz)*0.5,v1.xyz+t*(v2.xyz-v1.xyz),v2.w-v1.w==0);
        }
        int indexFromCoord(int x, int y, int z) {
            return z*THREAD_DIMENSION_Z*THREAD_DIMENSION_Y+y*THREAD_DIMENSION_X+x;
        }
        vec3f vecn2vecnf(vec3 a) {
            return vec3f(a.x,a.y,a.z);
        }
        vec3 baseTransformation(vec3 v) {
            return v.x * right + v.y * up + v.z * forward;
        }
        void main() {
            const ivec3 GROUP_XYZ = ivec3(gl_WorkGroupID);
            const ivec3 THREAD_XYZ = ivec3(gl_LocalInvocationID);
            const ivec3 CHUNK_XYZ = GROUP_XYZ*THREAD_DIMENSION+THREAD_XYZ;
            
            const vec3 TMP_0 = vec3(CHUNK_DIMENSION);
            const vec3 TMP_2 = chunkSize/TMP_0;
            const vec3 TMP_1 = CHUNK_XYZ+chunkOffset*TMP_0;
            const vec3 CUBE_CORNERS_OFFSET[8] = {
                baseTransformation((TMP_1+vec3(0,0,0))*TMP_2)+base,
                baseTransformation((TMP_1+vec3(1,0,0))*TMP_2)+base,
                baseTransformation((TMP_1+vec3(1,0,1))*TMP_2)+base,
                baseTransformation((TMP_1+vec3(0,0,1))*TMP_2)+base,
                baseTransformation((TMP_1+vec3(0,1,0))*TMP_2)+base,
                baseTransformation((TMP_1+vec3(1,1,0))*TMP_2)+base,
                baseTransformation((TMP_1+vec3(1,1,1))*TMP_2)+base,
                baseTransformation((TMP_1+vec3(0,1,1))*TMP_2)+base
            };
            const vec4 CUBE_CORNERS[8] = {
                vec4(CUBE_CORNERS_OFFSET[0], saturate(getDist(CUBE_CORNERS_OFFSET[0]), isoRange)),
                vec4(CUBE_CORNERS_OFFSET[1], saturate(getDist(CUBE_CORNERS_OFFSET[1]), isoRange)),
                vec4(CUBE_CORNERS_OFFSET[2], saturate(getDist(CUBE_CORNERS_OFFSET[2]), isoRange)),
                vec4(CUBE_CORNERS_OFFSET[3], saturate(getDist(CUBE_CORNERS_OFFSET[3]), isoRange)),
                vec4(CUBE_CORNERS_OFFSET[4], saturate(getDist(CUBE_CORNERS_OFFSET[4]), isoRange)),
                vec4(CUBE_CORNERS_OFFSET[5], saturate(getDist(CUBE_CORNERS_OFFSET[5]), isoRange)),
                vec4(CUBE_CORNERS_OFFSET[6], saturate(getDist(CUBE_CORNERS_OFFSET[6]), isoRange)),
                vec4(CUBE_CORNERS_OFFSET[7], saturate(getDist(CUBE_CORNERS_OFFSET[7]), isoRange))
            };
            
            int cubeIndex = 0;
            cubeIndex |= 1 * int(CUBE_CORNERS[0].w < isoLevel);
            cubeIndex |= 2 * int(CUBE_CORNERS[1].w < isoLevel);
            cubeIndex |= 4 * int(CUBE_CORNERS[2].w < isoLevel);
            cubeIndex |= 8 * int(CUBE_CORNERS[3].w < isoLevel);
            cubeIndex |= 16 * int(CUBE_CORNERS[4].w < isoLevel);
            cubeIndex |= 32 * int(CUBE_CORNERS[5].w < isoLevel);
            cubeIndex |= 64 * int(CUBE_CORNERS[6].w < isoLevel);
            cubeIndex |= 128 * int(CUBE_CORNERS[7].w < isoLevel);

            for (uint i = 0; triangulation[cubeIndex][i] != -1; i +=3) {
                uint a0 = CORNER_INDEX_A_FROM_EDGE[triangulation[cubeIndex][i+0]];
                uint b0 = CORNER_INDEX_B_FROM_EDGE[triangulation[cubeIndex][i+0]];

                uint a1 = CORNER_INDEX_A_FROM_EDGE[triangulation[cubeIndex][i+1]];
                uint b1 = CORNER_INDEX_B_FROM_EDGE[triangulation[cubeIndex][i+1]];

                uint a2 = CORNER_INDEX_A_FROM_EDGE[triangulation[cubeIndex][i+2]];
                uint b2 = CORNER_INDEX_B_FROM_EDGE[triangulation[cubeIndex][i+2]];
                
                uint index = atomicAdd(count,1);
                triangles[index].c = vecn2vecnf(interpolateVerts(CUBE_CORNERS[a0], CUBE_CORNERS[b0]));
                triangles[index].b = vecn2vecnf(interpolateVerts(CUBE_CORNERS[a1], CUBE_CORNERS[b1]));
                triangles[index].a = vecn2vecnf(interpolateVerts(CUBE_CORNERS[a2], CUBE_CORNERS[b2]));
            }
        } 
        '''

    @classmethod
    def set_context(cls, ctx):
        cls.ctx = ctx

    @classmethod
    def _np_normalized(cls, x):
        x_l2_norm = sum(x**2)**0.5
        x_l2_normalized = x / x_l2_norm
        return x_l2_normalized

    @classmethod
    def get_smallest_bounding_box(cls, chunk_size):
        verts = []
        for pointer in bpy.context.scene.sdf_object_pointer_list:
            object = pointer.object
            verts += [object.matrix_world @ v.co for v in object.data.vertices]

        points = np.asarray(verts)

        means = np.mean(points, axis=1)
        cov = np.cov(points, y = None,rowvar = 0,bias = 1)
        v, vect = np.linalg.eig(cov)
        tvect = np.transpose(vect)
        points_r = np.dot(points, np.linalg.inv(tvect))
        co_min = np.min(points_r, axis=0)
        co_max = np.max(points_r, axis=0)

        xmin, xmax = co_min[0], co_max[0]
        ymin, ymax = co_min[1], co_max[1]
        zmin, zmax = co_min[2], co_max[2]

        xran = xmax - xmin
        yran = ymax - ymin
        zran = zmax - zmin

        xlen = 1
        ylen = 1
        zlen = 1

        if xran > chunk_size:
            xran = int(xran / chunk_size) * chunk_size + chunk_size
            xlen = int(xran / chunk_size)
            
        if yran > chunk_size:
            yran = int(yran / chunk_size) * chunk_size + chunk_size
            ylen = int(yran / chunk_size)
            
        if zran > chunk_size:
            zran = int(zran / chunk_size) * chunk_size + chunk_size
            zlen = int(zran / chunk_size)

        xmin = (xmax + xmin) * 0.5 - xran * 0.5
        ymin = (ymax + ymin) * 0.5 - yran * 0.5
        zmin = (zmax + zmin) * 0.5 - zran * 0.5
        
        xmax = xmin + xran
        ymax = ymin + yran
        zmax = zmin + zran

        xdif = xran * 0.5
        ydif = yran * 0.5
        zdif = zran * 0.5

        cx = xmin + xdif
        cy = ymin + ydif
        cz = zmin + zdif

        corners = np.array([
            [cx - xdif, cy - ydif, cz - zdif],
            [cx - xdif, cy + ydif, cz - zdif],
            [cx - xdif, cy + ydif, cz + zdif],
            [cx - xdif, cy - ydif, cz + zdif],
            [cx + xdif, cy + ydif, cz + zdif],
            [cx + xdif, cy + ydif, cz - zdif],
            [cx + xdif, cy - ydif, cz + zdif],
            [cx + xdif, cy - ydif, cz - zdif],
        ])

        corners = np.dot(corners, tvect)
        
        forward = cls._np_normalized(corners[4] - corners[5])
        right = cls._np_normalized(corners[7] - corners[0])
        up = cls._np_normalized(corners[2] - corners[3])
        
        return corners, (xlen, ylen, zlen), forward, right, up

    @classmethod
    def generate(cls, operator):
        
        print('[Mesh Generation] start ...')

        dist = ShaderFactory.generate_distance_function(bpy.context.scene.sdf_object_pointer_list)
        glsl = cls.generate_glsl(dist)

        print('\n', glsl, '\n')

        try:
            compute_shader = cls.ctx.compute_shader(glsl)
        except Exception as e:
            operator.report({'ERROR'}, '[Mesh Generation] Error occurred when compiling shaders')
            operator.report({'ERROR'}, e)
            return
        
        view_layer = bpy.context.view_layer
        mesh = bpy.data.meshes.new("marching-cube")
        new_object = bpy.data.objects.new("Marching Cube", mesh)
        view_layer.active_layer_collection.collection.objects.link(new_object)
        new_object.select_set(True)
        view_layer.objects.active = new_object
        
        chunk_size = bpy.context.scene.marching_cube_chunk_size
        corners, chunk_count, forward, right, up = cls.get_smallest_bounding_box(chunk_size)
        
        print('\n', 'chunk_count:', chunk_count, '\n')
        
#        for corner in corners:
#            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, enter_editmode=False, align='CURSOR', location=corner)
#            
#        return

        compute_shader["isoRange"].value = np.array([-0.1,0.1])
        compute_shader["isoLevel"].value = 0.5
        compute_shader["forward"].value = forward
        compute_shader["right"].value = right
        compute_shader["up"].value = up
        compute_shader["base"].value = corners[0]
        compute_shader["chunkSize"].value = np.array([chunk_size,chunk_size,chunk_size])
        
        in_buf = cls.ctx.buffer(marching_tables.edges)
        in_buf.bind_to_storage_buffer(13)
        in_buf = cls.ctx.buffer(marching_tables.triangulation)
        in_buf.bind_to_storage_buffer(14)

        ShaderBufferFactory.bind_to_storage_buffer()

        total_count = 0
        total_verts = None

        for x in range(chunk_count[0]):
            for y in range(chunk_count[1]):
                for z in range(chunk_count[2]):
                    
                    start = time.perf_counter()
                    
                    count_buf = cls.ctx.buffer(data=b'\x00\x00\x00\x00')
                    count_buf.bind_to_storage_buffer(11)
                    tri_siz = 3*3+1
                    out_buf = np.empty((cls.max_triangle_count,tri_siz),dtype=np.float32).tobytes()
                    out_buf = cls.ctx.buffer(out_buf) # 128 --> 400MB, 256 --> 3019 MB (map error !)
                    out_buf.bind_to_storage_buffer(12)
                    compute_shader["chunkOffset"].value = np.array([x,y,z])
                    compute_shader.run(group_x=cls.CHUNK_DIMENSION_X//cls.THREAD_DIMENSION_X,group_y=cls.CHUNK_DIMENSION_Y//cls.THREAD_DIMENSION_Y,group_z=cls.CHUNK_DIMENSION_Z//cls.THREAD_DIMENSION_Z)

                    count = count_buf.read()
                    count = np.frombuffer(count,dtype='uint32')[0]
                    verts = out_buf.read()
                    verts = np.frombuffer(verts,dtype='float32')
                    verts = verts.reshape((int(len(verts)/tri_siz),tri_siz))
                    verts = verts[:count,:tri_siz-1]
                    verts = verts.reshape(int(len(verts)*9/3),3)
                    
                    total_count = total_count+count
                    if total_verts is None:
                        total_verts = verts
                    else:
                        total_verts = np.concatenate((total_verts, verts),axis=0)
                    
                    count_buf.release()
                    out_buf.release()
                    
                    end = time.perf_counter()
                    
                    print(x,y,z,end=':')
                    print('{:.2f}'.format((end-start)))


        in_buf.release()
        compute_shader.release()

        edges = []
        faces = np.arange(3*total_count).reshape(total_count,3)
        mesh.from_pydata(total_verts, edges, faces)

        print('[Mesh Generation] finish.')


class SDF2MESH_OT_Generate(bpy.types.Operator):

    bl_idname = "mesh_from_sdf.ot_generate"
    bl_label = "Generate mesh from sdf"
    bl_description = "Generate a mesh from the SDF"

    def invoke(self, context, event):
        MarchingCube.generate(self)
        return {'FINISHED'}


class SDF2MESH_PT_Generate(bpy.types.Panel):

    bl_label = "Start mesh generation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SDF2Mesh"
    bl_context = "objectmode"

    def draw(self, context):
        sc = context.scene
        op_cls = SDF2MESH_OT_Generate

        layout = self.layout
        layout.prop(context.scene, 'marching_cube_chunk_size')
        layout.operator(op_cls.bl_idname, text="Generate", icon="PLAY")


classes = [
    SDF2MESH_OT_Generate,
    SDF2MESH_PT_Generate,
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    
    bpy.types.Scene.marching_cube_chunk_size = FloatProperty(name = 'Chunk Size', default = 2.5)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)