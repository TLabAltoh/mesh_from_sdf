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


class MarchingCube(object):

    basic_shader = '''

        #version 430
    
        #define LOCAL_X 8
        #define LOCAL_Y 8
        #define LOCAL_Z 8
        #define BOX_DIM_X 128
        #define BOX_DIM_Y 128
        #define BOX_DIM_Z 128
    
        ''' + common.include_struct_ + '''

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

        layout(local_size_x=LOCAL_X,local_size_y=LOCAL_Y,local_size_z=LOCAL_Z) in;
        layout(binding=11) buffer inout_0 { uint count; };
        layout(binding=12) writeonly buffer out_0 { Triangle triangles[]; };
        layout(binding=13) readonly buffer in_1 { uint edge[]; };
        layout(binding=14) readonly buffer in_2 { int triangulation[][16]; };
        layout(binding=15) readonly buffer in_3 { uint cornerIndexAFromEdge[]; };
        layout(binding=16) readonly buffer in_4 { uint cornerIndexBFromEdge[]; };
        uniform vec2 isoRange;
        uniform vec3 boxSize;
        uniform vec3 boxOffset;
        uniform float isoLevel;
        const ivec3 localSize = ivec3(LOCAL_X,LOCAL_Y,LOCAL_Z);
        const ivec3 boxDim = ivec3(BOX_DIM_X,BOX_DIM_Y,BOX_DIM_Z);
        ''' + common.include_frag_ + '''
        float getDist(vec3 p) {
            return sdBox(p, vec3(1,1,1), vec4(0.2,0.2,0,0));
            //return sdTorus(p, 1.0, 0.25);
        }
        float saturate(float x, float min, float max) {
            if (max<=min) return min;
            return (clamp(x,min,max)-min)/(max-min);
        }
        float saturate(float x, vec2 range) {
            return saturate(x,range.x,range.y);
        }
        vec3 interpolateVerts(vec4 v1, vec4 v2) {
            if (v2.w-v1.w==0) return (v2.xyz+v1.xyz)*0.5;
            float t = (isoLevel-v1.w)/(v2.w-v1.w);
            return v1.xyz+t*(v2.xyz-v1.xyz);
        }
        int indexFromCoord(int x, int y, int z) {
            return z*LOCAL_Z*LOCAL_Y+y*LOCAL_X+x;
        }
        vec3f vecn2vecnf(vec3 a) {
            return vec3f(a.x,a.y,a.z);
        }
        void main() {
            const ivec3 group_xyz = ivec3(gl_WorkGroupID);
            const ivec3 thread_xyz = ivec3(gl_LocalInvocationID);
            const ivec3 box_xyz = group_xyz*localSize+thread_xyz;
            
            const vec3 tmp0 = 0.5*vec3(boxDim);
            const vec3 tmp2 = 1.0/tmp0*boxSize;
            const vec3 tmp1 = box_xyz-tmp0*(vec3(1,1,1)+boxOffset);
            const vec3 cubeCornersOffset[8] = {
                (tmp1+vec3(0,0,0))*tmp2,
                (tmp1+vec3(1,0,0))*tmp2,
                (tmp1+vec3(1,0,1))*tmp2,
                (tmp1+vec3(0,0,1))*tmp2,
                (tmp1+vec3(0,1,0))*tmp2,
                (tmp1+vec3(1,1,0))*tmp2,
                (tmp1+vec3(1,1,1))*tmp2,
                (tmp1+vec3(0,1,1))*tmp2
            };
            const vec4 cubeCorners[8] = {
                vec4(cubeCornersOffset[0], saturate(getDist(cubeCornersOffset[0]), isoRange)),
                vec4(cubeCornersOffset[1], saturate(getDist(cubeCornersOffset[1]), isoRange)),
                vec4(cubeCornersOffset[2], saturate(getDist(cubeCornersOffset[2]), isoRange)),
                vec4(cubeCornersOffset[3], saturate(getDist(cubeCornersOffset[3]), isoRange)),
                vec4(cubeCornersOffset[4], saturate(getDist(cubeCornersOffset[4]), isoRange)),
                vec4(cubeCornersOffset[5], saturate(getDist(cubeCornersOffset[5]), isoRange)),
                vec4(cubeCornersOffset[6], saturate(getDist(cubeCornersOffset[6]), isoRange)),
                vec4(cubeCornersOffset[7], saturate(getDist(cubeCornersOffset[7]), isoRange))
            };
            
            int cubeIndex = 0;
            if (cubeCorners[0].w < isoLevel) cubeIndex |= 1;
            if (cubeCorners[1].w < isoLevel) cubeIndex |= 2;
            if (cubeCorners[2].w < isoLevel) cubeIndex |= 4;
            if (cubeCorners[3].w < isoLevel) cubeIndex |= 8;
            if (cubeCorners[4].w < isoLevel) cubeIndex |= 16;
            if (cubeCorners[5].w < isoLevel) cubeIndex |= 32;
            if (cubeCorners[6].w < isoLevel) cubeIndex |= 64;
            if (cubeCorners[7].w < isoLevel) cubeIndex |= 128;
            
            for (uint i = 0; triangulation[cubeIndex][i] != -1; i +=3) {
                uint a0 = cornerIndexAFromEdge[triangulation[cubeIndex][i+0]];
                uint b0 = cornerIndexBFromEdge[triangulation[cubeIndex][i+0]];

                uint a1 = cornerIndexAFromEdge[triangulation[cubeIndex][i+1]];
                uint b1 = cornerIndexBFromEdge[triangulation[cubeIndex][i+1]];

                uint a2 = cornerIndexAFromEdge[triangulation[cubeIndex][i+2]];
                uint b2 = cornerIndexBFromEdge[triangulation[cubeIndex][i+2]];
                
                uint index = atomicAdd(count,1);
                triangles[index].c = vecn2vecnf(interpolateVerts(cubeCorners[a0], cubeCorners[b0]));
                triangles[index].b = vecn2vecnf(interpolateVerts(cubeCorners[a1], cubeCorners[b1]));
                triangles[index].a = vecn2vecnf(interpolateVerts(cubeCorners[a2], cubeCorners[b2]));
            }
        } 
    '''

    ctx = None
    LOCAL_X,LOCAL_Y,LOCAL_Z = 8,8,8
    BOX_DIM_X,BOX_DIM_Y,BOX_DIM_Z = 128,128,128
    BOX_SIZE_X,BOX_SIZE_Y,BOX_SIZE_Z = 0.5,0.5,0.5
    voxel_count=BOX_DIM_X*BOX_DIM_Y*BOX_DIM_Z
    max_triangle_count=voxel_count*5

    @classmethod
    def set_context(cls, ctx):
        cls.ctx = ctx

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
        
        xran = int(xran / chunk_size) * chunk_size + 2 * chunk_size * (xran % chunk_size != 0)
        yran = int(yran / chunk_size) * chunk_size + 2 * chunk_size * (yran % chunk_size != 0)
        zran = int(zran / chunk_size) * chunk_size + 2 * chunk_size * (zran % chunk_size != 0)

        xlen = xran / chunk_size
        ylen = yran / chunk_size
        zlen = zran / chunk_size

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
        
        return corners, (xlen, ylen, zlen)

    @classmethod
    def generate(cls):
        view_layer = bpy.context.view_layer
        mesh = bpy.data.meshes.new("marching-cube")
        new_object = bpy.data.objects.new("Marching Cube", mesh)
        view_layer.active_layer_collection.collection.objects.link(new_object)
        new_object.select_set(True)
        view_layer.objects.active = new_object

        print('[Mesh Generation] start ...')

        print('\n', cls.basic_shader, '\n')
        
        chunk_size = bpy.context.scene.marching_cube_chunk_size
        corners, chunk_count = cls.get_smallest_bounding_box(chunk_size)
        
        print('\n', 'chunk_count:', chunk_count, '\n')
        
        for corner in corners:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, enter_editmode=False, align='CURSOR', location=corner)
            
        return

        cls.BOX_SIZE_X = chunk_size
        cls.BOX_SIZE_Y = chunk_size
        cls.BOX_SIZE_X = chunk_size

        compute_shader = cls.ctx.compute_shader(cls.basic_shader)
        compute_shader["isoRange"].value = np.array([-0.1,0.1])
        compute_shader["isoLevel"].value = 0.5
        compute_shader["boxSize"].value = np.array([cls.BOX_SIZE_X,cls.BOX_SIZE_Y,cls.BOX_SIZE_Z])
        in_buf = cls.ctx.buffer(marching_tables.edges)
        in_buf.bind_to_storage_buffer(13)
        in_buf = cls.ctx.buffer(marching_tables.triangulation)
        in_buf.bind_to_storage_buffer(14)
        in_buf = cls.ctx.buffer(marching_tables.corner_index_a_from_edge)
        in_buf.bind_to_storage_buffer(15)
        in_buf = cls.ctx.buffer(marching_tables.corner_index_b_from_edge)
        in_buf.bind_to_storage_buffer(16)

        total_count = 0
        total_verts = None

        for x in range(chunk_count[0]):
            for y in range(chunk_count[1]):
                for z in range(chunk_count[2]):
                    count_buf = cls.ctx.buffer(data=b'\x00\x00\x00\x00')
                    count_buf.bind_to_storage_buffer(11)
                    tri_siz = 3*3+1
                    out_buf = np.empty((cls.max_triangle_count,tri_siz),dtype=np.float32).tobytes()
                    out_buf = cls.ctx.buffer(out_buf) # 128 --> 400MB, 256 --> 3019 MB (map error !)
                    out_buf.bind_to_storage_buffer(12)
                    compute_shader["boxOffset"].value = np.array([x,y,z])
                    compute_shader.run(group_x=cls.BOX_DIM_X//cls.LOCAL_X,group_y=cls.BOX_DIM_Y//cls.LOCAL_Y,group_z=cls.BOX_DIM_Z//cls.LOCAL_Z)

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
        MarchingCube.generate()
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