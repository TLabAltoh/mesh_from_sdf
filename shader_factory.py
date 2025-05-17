import moderngl

# Class for generating and updating shaders based on SDF Object Property list
class ShaderFactory(object):

    # Concatenate distance function snippets that match the primitive_type of the SDFObject    
    __distance_function_by_primitive_type = {'Box':'''
                sdfBoxProp = sdfBoxProps[sdfBoxPropIdx++];
                dist = sdBox(samplpos, sdfBoxProp.br.xyz, sdfBoxProp.br.w);
            ''',
            'Sphere':'''
                sdfSphereProp = sdfSphereProps[sdfSpherePropIdx++];
                dist = sdSphere(samplpos, sdfSphereProp.r);
            ''',
            'Cylinder':'''
                sdfCylinderProp = sdfCylinderProps[sdfCylinderPropIdx++];
                dist = sdCylinder(samplpos, sdfCylinderProp.h, sdfCylinderProp.ra);
                dist = rounding(dist, sdfCylinderProp.rd);
            ''',
            'Cone':'''
                sdfConeProp = sdfConeProps[sdfConePropIdx++];
                dist = sdCappedCone(samplpos, sdfConeProp.h, sdfConeProp.r0, sdfConeProp.r1);
                dist = rounding(dist, sdfConeProp.rd);
            ''',
            'Torus':'''
                sdfTorusProp = sdfTorusProps[sdfTorusPropIdx++];
                dist = sdTorus(samplpos, sdfTorusProp.r0, sdfTorusProp.r1);
                dist = rounding(dist, sdfTorusProp.rd);
            ''',
            'Hexagonal Prism':'''
                sdfHexPrismProp = sdfHexPrismProps[sdfHexPrismPropIdx++];
                dist = sdHexPrism(samplpos, sdfHexPrismProp.h);
                dist = rounding(dist, sdfHexPrismProp.rd);
            ''',
            'Triangular Prism':'''
                sdfTriPrismProp = sdfTriPrismProps[sdfTriPrismPropIdx++];
                dist = sdTriPrism(samplpos, sdfTriPrismProp.h, sdfTriPrismProp.ra);
                dist = rounding(dist, sdfTriPrismProp.rd);
            ''',
            'Ngon Prism':'''
                sdfNgonPrismProp = sdfNgonPrismProps[sdfNgonPrismPropIdx++];
                dist = sdNgonPrism(samplpos, sdfNgonPrismProp.h, sdfNgonPrismProp.ra, sdfNgonPrismProp.n);
                dist = rounding(dist, sdfNgonPrismProp.rd);
            ''',
            'GLSL':'{dist = 1000000000}'}

    
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
                              'Diffrence' : 'minDist1 = opDiffrence(dist, minDist1);',
                              'Intersection' : 'minDist1 = opIntersection(dist, minDist1);'}
                            
        f_smooth_merge_1 = {'Union' : 'minDist1 = opSmoothUnion(dist, minDist1, k0);',
                            'Diffrence' : 'minDist1 = opSmoothDiffrence(dist, minDist1, k0);',
                            'Intersection' : 'minDist1 = opSmoothIntersection(dist, minDist1, k0);'}
        
        f_champfer_merge_1 = {'Union' : 'minDist1 = opChampferUnion(dist, minDist1, k0);',
                              'Diffrence' : 'minDist1 = opChampferDiffrence(dist, minDist1, k0);',
                              'Intersection' : 'minDist1 = opChampferIntersection(dist, minDist1, k0);'}
        
        f_steps_merge_1 = {'Union' : 'minDist1 = opStairsUnion(dist, minDist1, k0, k1);',
                           'Diffrence' : 'minDist1 = opStairsDiffrence(dist, minDist1, k0, k1);',
                           'Intersection' : 'minDist1 = opStairsIntersection(dist, minDist1, k0, k1);'}
        
        f_round_merge_1 = {'Union' : 'minDist1 = opRoundUnion(dist, minDist1, k0);',
                           'Diffrence' : 'minDist1 = opRoundDiffrence(dist, minDist1, k0);',
                           'Intersection' : 'minDist1 = opRoundIntersection(dist, minDist1, k0);'}

        f_blend_1 = {'No Blending': f_no_blend_merge_1,
                     'Smooth' : f_smooth_merge_1,
                     'Champfer' : f_champfer_merge_1,
                     'Steps' : f_steps_merge_1,
                     'Round' : f_round_merge_1}

        f_no_blend_merge_0 = {'Union' : 'minDist0 = opUnion(minDist1, minDist0);',
                              'Diffrence' : 'minDist0 = opDiffrence(minDist1, minDist0);',
                              'Intersection' : 'minDist0 = opIntersection(minDist1, minDist0);'}
                            
        f_smooth_merge_0 = {'Union' : 'minDist0 = opSmoothUnion(minDist1, minDist0, k0);',
                            'Diffrence' : 'minDist0 = opSmoothDiffrence(minDist1, minDist0, k0);',
                            'Intersection' : 'minDist0 = opSmoothIntersection(minDist1, minDist0, k0);'}
        
        f_champfer_merge_0 = {'Union' : 'minDist0 = opChampferUnion(minDist1, minDist0, k0);',
                              'Diffrence' : 'minDist0 = opChampferDiffrence(minDist1, minDist0, k0);',
                              'Intersection' : 'minDist0 = opChampferIntersection(minDist1, minDist0, k0);'}
        
        f_steps_merge_0 = {'Union' : 'minDist0 = opStairsUnion(minDist1, minDist0, k0, k1);',
                           'Diffrence' : 'minDist0 = opStairsDiffrence(minDist1, minDist0, k0, k1);',
                           'Intersection' : 'minDist0 = opStairsIntersection(minDist1, minDist0, k0, k1);'}
        
        f_round_merge_0 = {'Union' : 'minDist0 = opRoundUnion(minDist1, minDist0, k0);',
                           'Diffrence' : 'minDist0 = opRoundDiffrence(minDist1, minDist0, k0);',
                           'Intersection' : 'minDist0 = opRoundIntersection(minDist1, minDist0, k0);'}
        
        f_blend_0 = {'No Blending' : f_no_blend_merge_0,
                     'Smooth' : f_smooth_merge_0,
                     'Champfer' : f_champfer_merge_0,
                     'Steps' : f_steps_merge_0,
                     'Round' : f_round_merge_0}

        # When the first dist is obtained, minDist1 is still undetermined, so assign the dist directly to minDist1
        pointer = alist[0]
        sdf_object = pointer.object.sdf_object
        primitive_type = sdf_object.primitive_type
        boolean_type = sdf_object.boolean_type
        blend_type = sdf_object.blend_type
        nest = sdf_object.nest
        
        f_merge_0 = ''
        f_merge_1 = ''
        
        f_dist = f_dist + '''
            {
        ''' + f_common +  cls.__distance_function_by_primitive_type[primitive_type] + '''
                minDist1 = dist;'''

        idx_offset = 0

        # When the first SDF object group operation is completed, minDist0 is not yet determined, so minDist1 is directly assigned.
        for idx in range(1, len(alist)):
            pointer = alist[idx]
            sdf_object = pointer.object.sdf_object
            primitive_type = sdf_object.primitive_type
            boolean_type = sdf_object.boolean_type
            blend_type = sdf_object.blend_type
            nest = sdf_object.nest
            
            break_loop = False
            if nest == False:
                idx_offset = idx
                break_loop = True
                
                f_dist = f_dist + '''
                minDist0 = minDist1;
            }
            {
                ''' + f_common + '''
                    ''' + cls.__distance_function_by_primitive_type[primitive_type] + '''
                minDist1 = dist;'''
                
                f_merge_0 = f_blend_0[blend_type][boolean_type]
            else:            
                f_merge_1 = f_blend_1[blend_type][boolean_type]
                # To align the indentation of the generated shaders, a tab-only string is inserted between them.
                f_dist = f_dist + f_common + '''
                    ''' + cls.__distance_function_by_primitive_type[primitive_type] + '''
                ''' + f_merge_1
                
            if break_loop:
                break
                
        # Concatenate the distance numbers to the end while rotating the loop
        for idx in range(idx_offset + 1, len(alist)):
            pointer = alist[idx]
            sdf_object = pointer.object.sdf_object
            primitive_type = sdf_object.primitive_type
            boolean_type = sdf_object.boolean_type
            blend_type = sdf_object.blend_type
            nest = sdf_object.nest

            if nest == False:
                f_dist = f_dist + '''
                ''' + f_merge_0 + '''
            }
            {
                '''

                f_dist = f_dist + f_common + '''
                    ''' + cls.__distance_function_by_primitive_type[primitive_type] + '''
                minDist1 = dist;'''
                
                f_merge_0 = f_blend_0[blend_type][boolean_type]
            else:
                f_merge_1 = f_blend_1[blend_type][boolean_type]
                f_dist = f_dist + f_common + '''
                    ''' + cls.__distance_function_by_primitive_type[primitive_type] + '''
                ''' + f_merge_1
        
        # Remember to close the trailing scope
        f_dist = f_dist + '''
                ''' + f_merge_0 + '''
            }'''
        return f_dist