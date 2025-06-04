import bpy
import bmesh
import gpu
import moderngl
import math
import numpy as np
from bpy_extras import view3d_utils
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from mathutils.geometry import intersect_line_plane
from mesh_from_sdf.shader import common
from mesh_from_sdf.shader.buffer_factory import ShaderBufferFactory


class Raymarching(bpy.types.Operator):
    
    # The function generates a mesh that covers the area (frustum) seen by the camera in the scene view. 
    # The result of ray-marching is displayed on the mesh generated here. This function is used to 
    # perform full-screen ray marching on the scene view.
    @classmethod
    def get_frustom_plane_from_view3d(cls,region,region3d,near):
        plane = []
        if region3d.is_perspective:
            pn = Vector((0,0,1)) @ region3d.view_rotation.to_matrix().inverted()
            ro = region3d.view_matrix.inverted().translation
            for coord in ([0,0],[0,region.height],[region.width,region.height],[region.width,0]):
                rd = view3d_utils.region_2d_to_vector_3d(
                        region,
                        region3d,
                        coord)
                cp = intersect_line_plane(ro,ro+rd,ro-pn*near,pn)
                plane.append(cp)
            return plane
        else:
            for coord in ([0,0],[0,region.height],[region.width,region.height],[region.width,0]):
                cp = view3d_utils.region_2d_to_origin_3d(
                        region,
                        region3d,
                        coord,
                        clamp=1/near) # TODO: The behaviour of clamp() needs to be properly understood.
                plane.append(cp)
            return plane

    # Update shader configuration (mesh vertices, camera position, view matrix)
    config = {}
    @classmethod
    def update_config(cls):
        screen = bpy.context.window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        region3d = bpy.context.space_data.region_3d
                        cls.config["vertices"] = cls.get_frustom_plane_from_view3d(region,region3d,0.1)
                        cls.config["u_PerspectiveMatrix"] = region3d.perspective_matrix
                        cls.config["u_ViewMatrix"] = region3d.view_matrix
                        cls.config["u_CameraRotationMatrix"] = region3d.view_rotation.to_matrix().to_4x4()
                        cls.config["u_IsPers"] = region3d.is_perspective
                        if region3d.is_perspective:
                            cls.config["u_CameraPosition"] = region3d.view_matrix.inverted().translation
                        else:
                            cls.config["u_CameraPosition"] = view3d_utils.region_2d_to_origin_3d(
                                region,
                                region3d,
                                [region.width / 2, region.height / 2],
                                clamp=10.0
                            )

    # Force scene view redraw
    @classmethod
    def tag_redraw_all_3dviews(cls):
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            region.tag_redraw()

    dist_ = '''
        const vec3 positions[OBJECT_COUNT] = { 
            vec3(0.5,0.5,0.5), 
            vec3(0.2,0.5,0.0),
            vec3(0.1,0.3,0.1),
            vec3(0.3,0.2,0.6),
            vec3(0.4,0.1,0.8),
            vec3(0.1,0.6,0.1)
        };
        const vec3 axiss[OBJECT_COUNT] = { 
            vec3(1.0, 0.0, 0.0),
            vec3(1.0, 0.0, 0.0),
            vec3(0.0, 1.0, 0.0),
            vec3(0.0, 0.0, 1.0),
            vec3(0.0, 1.0, 0.0),
            vec3(1.0, 0.0, 0.0)
        };
        const float thetas[OBJECT_COUNT] = {
            3.14 * 0.5,
            3.14 * 0.2,
            3.14 * 0.0,
            3.14 * 0.15,
            3.14 * 0.25,
            3.14 * 0.33
        };
        const float scales[OBJECT_COUNT] = { 
            0.50,
            0.70,
            1.00,
            1.30,
            1.00,
            1.15
        };
        const int primitives[OBJECT_COUNT] = {
            BOX,
            CAPPED_CONE,
            SPHERE,
            TORUS,
            NGON_PRISM,
            TRI_PRISM
        };
        
        vec3 position, samplpos, axis;
        float theta, scale, dist, k;
        mat4 rotation;
        float minDist0 = MAX_DIST;
        
        {
            {
                position = positions[0];
                samplpos = p - position;
                axis = axiss[0];
                theta = thetas[0];
                rotation = rotmat(axis, theta);
                scale = scales[0];
                samplpos = mulVec(rotation, samplpos).xyz;
                samplpos /= scale;
                
                switch (primitives[0]) {
                    case BOX:
                        dist = sdBox(samplpos, vec3(1,1,1), vec4(0.2,0.2,0,0));
                        dist = opRound(dist, 0.1);
                        break;
                    case SPHERE:
                        dist = sdSphere(samplpos, 0.75);
                        break;
                    case TORUS:
                        float theta = 0.75 * 3.14;
                        dist = sdCappedTorus(samplpos, vec2(sin(theta),cos(theta)), 1.0, 0.25 );
                        break;
                    case CAPPED_CONE:
                        dist = sdCappedCone(samplpos, 1.0, 0.1, 0.75);
                        break;
                    case TRI_PRISM:
                        dist = sdTriPrism(samplpos, 0.5, 0.8);
                        break;
                    case NGON_PRISM:
                        dist = sdNgonPrism(samplpos, 0.5, 8, 0.75);
                        break;
                }
                dist *= scale;
                minDist0 = dist;
            }
            
            {
                for (int i = 1; i < OBJECT_COUNT; i++) {
                    position = positions[i];
                    samplpos = p - position;
                    axis = axiss[i];
                    theta = thetas[i];
                    rotation = rotmat(axis, theta);
                    scale = scales[i];
                    samplpos = mulVec(rotation, samplpos).xyz;
                    samplpos /= scale;
                    
                    switch (primitives[i]) {
                        case BOX:
                            dist = sdBox(samplpos, vec3(1,1,1), vec4(0.2,0.2,0,0));
                            dist = opRound(dist, 0.1);
                            break;
                        case SPHERE:
                            dist = sdSphere(samplpos, 0.75);
                            break;
                        case TORUS:
                            float theta = 0.75 * 3.14;
                            dist = sdCappedTorus(samplpos, vec2(sin(theta),cos(theta)), 1.0, 0.25 );
                            break;
                        case CAPPED_CONE:
                            dist = sdCappedCone(samplpos, 1.0, 0.1, 0.75);
                            break;
                        case TRI_PRISM:
                            dist = sdTriPrism(samplpos, 0.8, 0.5);
                            break;
                        case NGON_PRISM:
                            dist = sdNgonPrism(samplpos, 0.8, 0.5, 8);
                            break;
                    }
                    dist *= scale;
                    
                    k = 0.05;
                    minDist0 = opRoundUnion(dist, minDist0, k);
                    //minDist0 = opUnion(dist, minDist0);
                    //minDist0 = opStairsUnion(dist, minDist0, k, 3);
                    //minDist0 = opSmoothUnion(dist, minDist0, k);
                    //minDist0 = opChampferUnion(dist, minDist0, k);
                }
            }
        }
    '''

    @classmethod
    def get_vert(cls):
        # generate vertex shader
        vert_ = '''
        in vec3 in_pos;
        out vec3 pos;
        out vec3 orthoRayDir;
        out vec3 orthoCameraOffset;

        uniform mat4 u_PerspectiveMatrix;
        uniform mat4 u_ViewMatrix;
        uniform mat4 u_CameraRotationMatrix;

        ''' + common.include_ + '''
        
        void main() {
            pos = in_pos;
            vec4 viewMatrixAppliedPos = mulVec(u_ViewMatrix, pos);
            orthoCameraOffset = mulVec(u_CameraRotationMatrix, vec3(viewMatrixAppliedPos.xy, 0)).xyz;
            orthoRayDir = mulVec(u_CameraRotationMatrix, vec3(0, 0, -1)).xyz;
            gl_Position = mulVec(u_PerspectiveMatrix, in_pos);
        }
        '''
        return vert_

    @classmethod
    def get_frag(cls):
        # generate fragment shader
        frag_ = common.include_ + common.include_struct_ + '''
        
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
        
        in vec3 pos;
        in vec3 orthoRayDir;
        in vec3 orthoCameraOffset;
        out vec4 fragColor;

        uniform mat4 u_PerspectiveMatrix;
        uniform bool u_IsPers;
        uniform vec3 u_CameraPosition;
        
        #define MAX_STEPS 100
        #define MAX_DIST 100
        #define SURF_DIST 1e-3
        #define OBJECT_COUNT 6
        
        #define UNION 0
        #define SUBTRACTION 1
        #define INTERSECTION 2
        
        #define BOX 0
        #define SPHERE 1
        #define TORUS 2
        #define CAPPED_CONE 3
        #define HEX_PRISM 4
        #define TRI_PRISM 5
        #define NGON_PRISM 6
        
        ''' + common.include_frag_ + '''
                
        float getDist(vec3 p) {
        
        ''' + cls.dist_ + '''
        
            return minDist0;
        }
        vec2 raymarch(vec3 ro, vec3 rd) {
            float dO = 0;
            float dS;
            for (int i = 0; i < MAX_STEPS; i++) {
                vec3 p = ro + dO * rd;
                dS = getDist(p);
                dO += dS;
                if (dS < SURF_DIST || dO > MAX_DIST)
                    break;
            }
            return vec2(dO, dS);
        }
        vec4 normalizedColor(vec4 color) {
            return color/255.0;
        }
        vec3 getNormal(vec3 pos)
        {
            vec2 e=vec2(1.0,-1.0)*0.5773;
            const float eps=0.0005;
            return normalize(e.xyy*getDist(pos+e.xyy*eps)+ 
                             e.yyx*getDist(pos+e.yyx*eps)+ 
                             e.yxy*getDist(pos+e.yxy*eps)+ 
                             e.xxx*getDist(pos+e.xxx*eps));
        }
        void main() {
            vec3 ro = u_CameraPosition;
            vec3 rd;        
            if (u_IsPers)
                rd = normalize(pos-ro);
            else {
                ro += orthoCameraOffset;
                rd = orthoRayDir;
            }
            
            vec2 d = raymarch(ro, rd);
            vec4 col = vec4(0, 0, 0, 0);
            
            if (d.x >= MAX_DIST) {
                discard;     
            } else {
                vec3 p = ro + rd * d.x;
                vec3 n = getNormal(p);
                float c = clamp(dot(n,-rd),0,1);
                col = vec4(c,c,c,1)*normalizedColor(vec4(245,113,5,255));
                vec4 clipSpace = mulVec(u_PerspectiveMatrix, p);
                float fragDepth = clipSpace.z / clipSpace.w;
                fragDepth = (fragDepth + 1.0) / 2.0;
                gl_FragDepth = fragDepth;
            }
            
            fragColor = col;
        }
        '''
        return frag_
    
    ctx = None
    pause = False
    shader = None
    recreate_shader_requested = False
    indices = np.array([[0,2,1],[0,3,2]], dtype='int32')

    # If the shader instance does not exist, a new shader instance is created
    @classmethod
    def recreate_shader(cls):
        if cls.shader != None:
            del cls.shader
        print(cls.get_frag())
        cls.shader = gpu.types.GPUShader(cls.get_vert(), cls.get_frag())

    # Update the distance function part of the shader
    @classmethod
    def update_distance_function(cls, dist):
        cls.dist_ = dist
        cls.recreate_shader_requested = True

    # Set the OpenGL context retrieved from ModernGL
    @classmethod
    def set_context(cls, ctx):
        cls.ctx = ctx

    # Execution of drawing process. Register this method with drawing events
    @classmethod
    def draw(cls):
        
        if cls.pause:
            return

        if (cls.shader is None) or cls.recreate_shader_requested:
            cls.recreate_shader()
            cls.recreate_shader_requested = False
        
        cls.shader.bind()
        cls.update_config()
        cls.shader.uniform_bool("u_IsPers", cls.config["u_IsPers"])
        cls.shader.uniform_float("u_PerspectiveMatrix", cls.config["u_PerspectiveMatrix"])
        cls.shader.uniform_float("u_ViewMatrix", cls.config["u_ViewMatrix"])
        cls.shader.uniform_float("u_CameraPosition", cls.config["u_CameraPosition"])
        cls.shader.uniform_float("u_CameraRotationMatrix", cls.config["u_CameraRotationMatrix"])
        
        ShaderBufferFactory.generate_all(cls.ctx, bpy.context)
        
        batch = batch_for_shader(cls.shader, 'TRIS', {"in_pos": cls.config["vertices"]}, indices=cls.indices,)
        gpu.state.blend_set("ALPHA") 
        gpu.state.depth_test_set('LESS_EQUAL')
        gpu.state.depth_mask_set(True)
        batch.draw(cls.shader)
        gpu.state.depth_mask_set(False)
        gpu.state.blend_set("NONE")
        cls.tag_redraw_all_3dviews()


classes = []

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    
    Raymarching.pause = True
    
    for c in classes:
        bpy.utils.unregister_class(c)