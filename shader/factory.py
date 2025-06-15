import bpy
import moderngl

# Class for generating and updating shaders based on SDF Object Property list
class ShaderFactory(object):

    # Concatenate distance function snippets that match the primitive_type of the SDFObject    
    __distance_function_by_primitive_type = {'Box':'''
                sdfBoxProp = sdfBoxProps[sdfBoxPropIdx++];
                dist = sdBox(samplpos, sdfBoxProp.br.xyz, sdfBoxProp.cr);
                dist = opRound(dist, sdfBoxProp.br.w);
            ''',
            'Sphere':'''
                sdfSphereProp = sdfSphereProps[sdfSpherePropIdx++];
                dist = sdSphere(samplpos, sdfSphereProp.r);
            ''',
            'Cylinder':'''
                sdfCylinderProp = sdfCylinderProps[sdfCylinderPropIdx++];
                dist = sdCylinder(samplpos, sdfCylinderProp.h, sdfCylinderProp.ra);
                dist = opRound(dist, sdfCylinderProp.rd);
            ''',
            'Cone':'''
                sdfConeProp = sdfConeProps[sdfConePropIdx++];
                dist = sdCappedCone(samplpos, sdfConeProp.h, sdfConeProp.r0, sdfConeProp.r1);
                dist = opRound(dist, sdfConeProp.rd);
            ''',
            'Torus':'''
                sdfTorusProp = sdfTorusProps[sdfTorusPropIdx++];
                dist = sdCappedTorus(samplpos, sdfTorusProp.sc, sdfTorusProp.r0, sdfTorusProp.r1);
            ''',
            'Pyramid':'''
                sdfPyramidProp = sdfPyramidProps[sdfPyramidPropIdx++];
                dist = sdPyramid(samplpos, sdfPyramidProp.hw, sdfPyramidProp.hd, sdfPyramidProp.hh);
                dist = opRound(dist, sdfPyramidProp.rd);
            ''',
            'Truncated Pyramid':'''
                sdfTruncatedPyramidProp = sdfTruncatedPyramidProps[sdfTruncatedPyramidPropIdx++];
                dist = sdTruncatedPyramid(samplpos, sdfTruncatedPyramidProp.hw0, sdfTruncatedPyramidProp.hd0, sdfTruncatedPyramidProp.hw1, sdfTruncatedPyramidProp.hd1, sdfTruncatedPyramidProp.hh);
                dist = opRound(dist, sdfTruncatedPyramidProp.rd);
            ''',
            'Hexagonal Prism':'''
                sdfHexPrismProp = sdfHexPrismProps[sdfHexPrismPropIdx++];
                dist = sdHexPrism(samplpos, sdfHexPrismProp.h, sdfHexPrismProp.ra);
                dist = opRound(dist, sdfHexPrismProp.rd);
            ''',
            'Triangular Prism':'''
                sdfTriPrismProp = sdfTriPrismProps[sdfTriPrismPropIdx++];
                dist = sdTriPrism(samplpos, sdfTriPrismProp.h, sdfTriPrismProp.ra);
                dist = opRound(dist, sdfTriPrismProp.rd);
            ''',
            'Ngon Prism':'''
                sdfNgonPrismProp = sdfNgonPrismProps[sdfNgonPrismPropIdx++];
                dist = sdNgonPrism(samplpos, sdfNgonPrismProp.h, sdfNgonPrismProp.ra, sdfNgonPrismProp.n);
                dist = opRound(dist, sdfNgonPrismProp.rd);
            '''}

    @classmethod
    def __get_distance_function_by_primitive_type(cls, primitive_type, sub_idx):
        
        if primitive_type == 'GLSL':
            return '''
                {
                    sdfGLSLProp = sdfGLSLProps[sdfGLSLPropIdx++];
                    dist = 1e+10;
                    ''' + bpy.context.scene.sdf_glsl_pointer_list[sub_idx].shader_string + '''
                    dist = opRound(dist, sdfGLSLProp.br.w);
                }
            '''
        
        return cls.__distance_function_by_primitive_type[primitive_type]

    
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
            SDFPyramidProp sdfPyramidProp; uint sdfPyramidPropIdx = 0;
            SDFTruncatedPyramidProp sdfTruncatedPyramidProp; uint sdfTruncatedPyramidPropIdx = 0;
            SDFPrismProp sdfHexPrismProp; uint sdfHexPrismPropIdx = 0;
            SDFPrismProp sdfTriPrismProp; uint sdfTriPrismPropIdx = 0;
            SDFNgonPrismProp sdfNgonPrismProp; uint sdfNgonPrismPropIdx = 0;
            SDFGLSLProp sdfGLSLProp; uint sdfGLSLPropIdx = 0;
            
            vec3 position, samplpos;
            mat4 rotation;
            float scale, dist, minDist0, minDist1, k0, k1;
        '''
        
        f_common = '''
                sdfObjectProp = sdfObjectProps[sdfObjectPropIdx++];
                position = sdfObjectProp.ps.xyz;
                samplpos = p - position;
                rotation = qua2mat(sdfObjectProp.qu);
                scale = sdfObjectProp.ps.w;
                samplpos = mulVec(rotation, samplpos).xyz;
                samplpos /= scale;
                
                k0 = sdfObjectProp.bl.x;
                k1 = sdfObjectProp.bl.y;'''
        
        f_no_blend_merge_1 = {'Union' : 'minDist1 = opUnion(dist, minDist1);',
                              'Difference' : 'minDist1 = opDifference(dist, minDist1);',
                              'Intersection' : 'minDist1 = opIntersection(dist, minDist1);'}
                            
        f_smooth_merge_1 = {'Union' : 'minDist1 = opSmoothUnion(dist, minDist1, k0);',
                            'Difference' : 'minDist1 = opSmoothDifference(dist, minDist1, k0);',
                            'Intersection' : 'minDist1 = opSmoothIntersection(dist, minDist1, k0);'}
        
        f_champfer_merge_1 = {'Union' : 'minDist1 = opChampferUnion(dist, minDist1, k0);',
                              'Difference' : 'minDist1 = opChampferDifference(minDist1, dist, k0);',
                              'Intersection' : 'minDist1 = 0.5 * opChampferIntersection(minDist1, dist, k0);'}
        
        f_steps_merge_1 = {'Union' : 'minDist1 = opStairsUnion(dist, minDist1, k0, k1);',
                           'Difference' : 'minDist1 = opStairsDifference(minDist1, dist, k0, k1);',
                           'Intersection' : 'minDist1 = opStairsIntersection(dist, minDist1, k0, k1);'}
        
        f_round_merge_1 = {'Union' : 'minDist1 = opRoundUnion(dist, minDist1, k0);',
                           'Difference' : 'minDist1 = opRoundDifference(minDist1, dist, k0);',
                           'Intersection' : 'minDist1 = 0.5 * opRoundIntersection(dist, minDist1, k0);'}

        f_blend_1 = {'No Blending': f_no_blend_merge_1,
                     'Smooth' : f_smooth_merge_1,
                     'Champfer' : f_champfer_merge_1,
                     'Steps' : f_steps_merge_1,
                     'Round' : f_round_merge_1}

        f_no_blend_merge_0 = {'Union' : 'minDist0 = opUnion(minDist1, minDist0);',
                              'Difference' : 'minDist0 = opDifference(minDist1, minDist0);',
                              'Intersection' : 'minDist0 = opIntersection(minDist1, minDist0);'}
                            
        f_smooth_merge_0 = {'Union' : 'minDist0 = opSmoothUnion(minDist1, minDist0, k0);',
                            'Difference' : 'minDist0 = opSmoothDifference(minDist1, minDist0, k0);',
                            'Intersection' : 'minDist0 = opSmoothIntersection(minDist1, minDist0, k0);'}
        
        f_champfer_merge_0 = {'Union' : 'minDist0 = opChampferUnion(minDist1, minDist0, k0);',
                              'Difference' : 'minDist0 = opChampferDifference(minDist0, minDist1, k0);',
                              'Intersection' : 'minDist0 = 0.5 * opChampferIntersection(minDist0, minDist1, k0);'}
        
        f_steps_merge_0 = {'Union' : 'minDist0 = opStairsUnion(minDist1, minDist0, k0, k1);',
                           'Difference' : 'minDist0 = opStairsDifference(minDist0, minDist1, k0, k1);',
                           'Intersection' : 'minDist0 = opStairsIntersection(minDist1, minDist0, k0, k1);'}
        
        f_round_merge_0 = {'Union' : 'minDist0 = opRoundUnion(minDist1, minDist0, k0);',
                           'Difference' : 'minDist0 = opRoundDifference(minDist0, minDist1, k0);',
                           'Intersection' : 'minDist0 = 0.5 * opRoundIntersection(minDist1, minDist0, k0);'}
        
        f_blend_0 = {'No Blending' : f_no_blend_merge_0,
                     'Smooth' : f_smooth_merge_0,
                     'Champfer' : f_champfer_merge_0,
                     'Steps' : f_steps_merge_0,
                     'Round' : f_round_merge_0}

        # Generate a distance function that always returns MAX_DIST if there is no SDF object in the list
        if len(alist) == 0:
            f_dist = f_common + 'minDist0 = MAX_DIST'
            return f_dist

        # When the first dist is obtained, minDist1 is still undetermined, so assign the dist directly to minDist1
        pointer = alist[0]
        sdf_prop = pointer.object.sdf_prop
        primitive_type = sdf_prop.primitive_type
        boolean_type = sdf_prop.boolean_type
        blend_type = sdf_prop.blend_type
        nest = sdf_prop.nest
        sub_idx = sdf_prop.sub_index
        
        f_merge_0 = ''
        f_merge_1 = ''
        
        f_dist = f_dist + '''
            {
        ''' + f_common +  cls.__get_distance_function_by_primitive_type(primitive_type, sub_idx) + '''
                dist *= scale;
                
                minDist1 = dist;'''

        idx_offset = 0

        # When the first SDF object group operation is completed, minDist0 is not yet determined, so minDist1 is directly assigned.
        for idx in range(1, len(alist)):
            pointer = alist[idx]
            sdf_prop = pointer.object.sdf_prop
            primitive_type = sdf_prop.primitive_type
            boolean_type = sdf_prop.boolean_type
            blend_type = sdf_prop.blend_type
            nest = sdf_prop.nest
            sub_idx = sdf_prop.sub_index
            
            break_loop = False
            if nest == False:
                idx_offset = idx
                break_loop = True
                
                f_dist = f_dist + '''
                minDist0 = minDist1;
            }
            {
                ''' + f_common + '''
                    ''' + cls.__get_distance_function_by_primitive_type(primitive_type, sub_idx) + '''
                dist *= scale;
                
                minDist1 = dist;'''
                
                f_merge_0 = f_blend_0[blend_type][boolean_type]
            else:            
                f_merge_1 = f_blend_1[blend_type][boolean_type]
                # To align the indentation of the generated shaders, a tab-only string is inserted between them.
                f_dist = f_dist + f_common + '''
                    ''' + cls.__get_distance_function_by_primitive_type(primitive_type, sub_idx) + '''
                dist *= scale;
                
                ''' + f_merge_1
                
            if break_loop:
                break
                
        # Concatenate the distance numbers to the end while rotating the loop
        for idx in range(idx_offset + 1, len(alist)):
            pointer = alist[idx]
            sdf_prop = pointer.object.sdf_prop
            primitive_type = sdf_prop.primitive_type
            boolean_type = sdf_prop.boolean_type
            blend_type = sdf_prop.blend_type
            nest = sdf_prop.nest
            sub_idx = sdf_prop.sub_index

            if nest == False:
                f_dist = f_dist + '''
                ''' + f_merge_0 + '''
            }
            {
                '''

                f_dist = f_dist + f_common + '''
                    ''' + cls.__get_distance_function_by_primitive_type(primitive_type, sub_idx) + '''
                dist *= scale;
                
                minDist1 = dist;'''
                
                f_merge_0 = f_blend_0[blend_type][boolean_type]
            else:
                f_merge_1 = f_blend_1[blend_type][boolean_type]
                f_dist = f_dist + f_common + '''
                    ''' + cls.__get_distance_function_by_primitive_type(primitive_type, sub_idx) + '''
                dist *= scale;
                
                ''' + f_merge_1
        
        if len(alist) == 1:
            f_merge_0 = 'minDist0 = minDist1;'
        
        # Remember to close the trailing scope
        f_dist = f_dist + '''
                ''' + f_merge_0 + '''
            }'''
        return f_dist