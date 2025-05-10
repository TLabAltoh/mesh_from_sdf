import moderngl

# Class for generating and updating shaders based on SDF Object Property list
class ShaderFactory(object):
    # Generate distance function for shaders based on SDF Object Property list
    @classmethod
    def generate_distance_function(cls, alist):
        f_dist = '''
            SDFObjectProp sdfObjectProp; uint sdfObjectPropIdx = 0;
            SDFBoxProp sdfBoxProp; uint sdfBoxPropIdx = 0;
            SDfSphereProp sdfSphereProp; uint sdfSpherePropIdx = 0;
            SDFCylinderProp sdfCylinderProp; uint sdfCylinderPropIdx = 0;
            SDFTorusProp sdfTorusProp; uint sdfTorusPropIdx = 0;
            SDFConeProp sdfConeProp; uint sdfConePropIdx = 0;
            SDFPrismProp sdfHexPrismProp; uint sdfHexPrismPropIdx = 0;
            SDFPrismProp sdfTriPrismProp; uint sdfTriPrismPropIdx = 0;
            SDFNgonPrismProp sdfNgonPrismProp; uint sdfNgonPrismPropIdx = 0;
            
            vec3 position, samplpos;
            float scale, dist, k0, k1;
            mat4 rotation;
        '''
        
        f_no_blend_merge = (('Union', 'minDist = opUnion(dist, minDist);'),
                            ('Diffrence', 'minDist = opDiffrence(dist, minDist);'),
                            ('Intersection', 'minDist = opIntersection(dist, minDist);'))
                            
        f_smooth_merge = (('Union', 'minDist = opSmoothUnion(dist, minDist, k0);'),
                          ('Diffrence', 'minDist = opSmoothDiffrence(dist, minDist, k0);'),
                          ('Intersection', 'minDist = opSmoothIntersection(dist, minDist, k0);'))
        
        f_champfer_merge = (('Union', 'minDist = opChampferUnion(dist, minDist, k0);'),
                            ('Diffrence', 'minDist = opChampferDiffrence(dist, minDist, k0);'),
                            ('Intersection', 'minDist = opChampferIntersection(dist, minDist, k0);'))
        
        f_steps_merge = (('Union', 'minDist = opStairsUnion(dist, minDist, k0, k1);'),
                         ('Diffrence', 'minDist = opStairsDiffrence(dist, minDist, k0, k1);'),
                         ('Intersection', 'minDist = opStairsIntersection(dist, minDist, k0, k1);'))
        
        f_round_merge = (('Union', 'minDist = opRoundUnion(dist, minDist, k0);'),
                         ('Diffrence', 'minDist = opRoundDiffrence(dist, minDist, k0);'),
                         ('Intersection', 'minDist = opRoundIntersection(dist, minDist, k0);'))
        
        f_blend = (('No Blending', f_no_blend_merge),
                   ('Smooth', f_smooth_merge),
                   ('Champfer', f_champfer_merge),
                   ('Steps', f_steps_merge),
                   ('Round', f_round_merge))

        is_this_first_elem = True
                
        for i, pointer in enumerate(alist):

            f_dist = f_dist + '''
            sdfObjectProp = sdfObjectProps[sdfObjectPropIdx++];
            '''
            
            sdf_object = pointer.object.sdf_object
            primitive_type = sdf_object.primitive_type
            boolean_type = sdf_object.boolean_type
            blend_type = sdf_object.blend_type
            indent = sdf_object.indent
            
            f_merge = f_blend[blend_type][boolean_type]
            
            if indent == 1 or i == 0:
                f_dist = f_dist + '''{
                '''
                
            
            
            if primitive_type == 'Empty':
                continue
            
            f_dist = f_dist + '''
                {
                    position = sdfObjectProp.ps.xyz;
                    samplpos = p - position;
                    rotation = sdfObjectProp.r;
                    scale = sdfObjectProp.ps.w;
                    samplpos = mulVec(rotation, samplpos).xyz;
                    samplpos /= scale;
                    
                    k0 = sdfObjectProp.bl.x;
                    k1 = sdfObjectProp.bl.y;
                '''
            
            if primitive_type == 'Box':
                f_dist = f_dist + '''
                    sdfBoxProp = sdfBoxProps[sdfBoxPropIdx++];
                    dist = sdBox(samplpos, sdfBoxProp.b.xyz, 0);
                '''
            elif primitive_type == 'Sphere':
                f_dist = f_dist + '''
                    sdfSphereProp = sdfSphereProps[sdfSpherePropIdx++];
                    dist = sdSphere(samplpos, sdfSphereProp.r);
                '''
            elif primitive_type == 'Cylinder':
                f_dist = f_dist + '''
                    sdfCylinderProp = sdfCylinderProps[sdfCylinderPropIdx++];
                    dist = sdCylinder(samplpos, sdfCylinderProp.h, sdfCylinderProp.r);
                '''
            elif primitive_type == 'Cone':
                f_dist = f_dist + '''
                    sdfConeProp = sdfConeProps[sdfConePropIdx++];
                    dist = sdCappedCone(samplpos, sdfConeProp.h, sdfConeProp.r0, sdfConeProp.r1);
                '''
            elif primitive_type == 'Torus':
                f_dist = f_dist + '''
                    sdfTorusProp = sdfTorusProps[sdfTorusPropIdx++];
                    dist = sdTorus(samplpos, sdfTorusProp.r0, sdfTorusProp.r1);
                '''
            elif primitive_type == 'Hexagonal Prism':
                f_dist = f_dist + '''
                    sdfHexPrismProp = sdfHexPrismProps[sdfHexPrismPropIdx++];
                    dist = sdHexPrism(samplpos, sdfHexPrismProp.h);
                '''
            elif primitive_type == 'Triangular Prism':
                f_dist = f_dist + '''
                    sdfTriPrismProp = sdfTriPrismProps[sdfTriPrismPropIdx++];
                    dist = sdTriPrism(samplpos, sdfTriPrismProp.h, sdfTriPrismProp.r);
                '''
            elif primitive_type == 'Ngon Prism':
                f_dist = f_dist + '''
                    sdfNgonPrismProp = sdfNgonPrismProps[sdfNgonPrismPropIdx++];
                    dist = sdNgonPrism(samplpos, sdfNgonPrismProp.h, sdfNgonPrismProp.r, sdfNgonPrismProp.n);
                '''
            elif primitive_type == 'GLSL':
                pass
                
            f_dist = f_dist + f_merge + '''
            }
            '''