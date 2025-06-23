from mesh_from_sdf.util.algorithm import *

# List of SDF{PrimitiveType}Pointer, keyed by primitive_type
# example: alist = sdf_object_pointer_list_by_primitive_type[primitive_type](context)
global sdf_object_pointer_list_by_primitive_type
sdf_object_pointer_list_by_primitive_type = {'Box': lambda context: context.scene.sdf_box_pointer_list,
                                     'Sphere': lambda context: context.scene.sdf_sphere_pointer_list,
                                     'Cylinder': lambda context: context.scene.sdf_cylinder_pointer_list,
                                     'Torus': lambda context: context.scene.sdf_torus_pointer_list,
                                     'Cone': lambda context: context.scene.sdf_cone_pointer_list,
                                     'Pyramid': lambda context: context.scene.sdf_pyramid_pointer_list,
                                     'Truncated Pyramid': lambda context: context.scene.sdf_truncated_pyramid_pointer_list,
                                     'Hexagonal Prism': lambda context: context.scene.sdf_hex_prism_pointer_list,
                                     'Quadratic Bezier': lambda context: context.scene.sdf_quadratic_bezier_pointer_list,
                                     'Ngon Prism': lambda context: context.scene.sdf_ngon_prism_pointer_list,
                                     'GLSL': lambda context: context.scene.sdf_glsl_pointer_list}


class PointerListUtil(object):
    
    @classmethod
    def recalc_sub_index_without_sort(cls, alist):
        # PointerListUtil.recalc_sub_index_without_sort(alist)
        cls.__refresh_pointer_list(alist)
        
        for i, pointer in enumerate(alist):
            pointer.object.sdf_prop.sub_index = i
    
    @classmethod
    def recalc_sub_index(cls, alist):
        # PointerListUtil.recalc_sub_index(alist)
        cls.__refresh_pointer_list(alist)
             
        Algorithm.quick_sort_by_index(alist)
        
        for i, pointer in enumerate(alist):
            pointer.object.sdf_prop.sub_index = i
    
    @classmethod
    def __refresh_pointer_list(cls, alist):

        len_ = len(alist)
        
        # Items with no referenced object and duplicated SDFObject are removed from the list.        
        cache = []
        i = -1
        while i < len_ - 1:
            i += 1
            pointer = alist[i]
            if pointer.object == None or (pointer.object in cache):
                alist.remove(i)
                i -= 1
                len_ -= 1
                continue
            cache.append(pointer.object)

    # Refresh a specific (single) pointer_list
    @classmethod
    def refresh_pointer_list(cls, context, primitive_type):
        global sdf_object_pointer_list_by_primitive_type
        cls.__refresh_pointer_list(sdf_object_pointer_list_by_primitive_type[primitive_type](context))

    # Refresh specific(s) pointer_list(s)
    @classmethod
    def refresh_pointer_lists(cls, context, primitive_types):
        for primitive_type in primitive_types:
            cls.refresh_pointer_list(context, primitive_type)
            
    # Refresh all pointer_lists
    @classmethod
    def refresh_all_pointer_list(cls, context):
        global sdf_object_pointer_list_by_primitive_type
        for reflesh_pointer_list_handler in sdf_object_pointer_list_by_primitive_type.values():
            reflesh_pointer_list_handler(context)
        cls.__refresh_pointer_list(context.scene.sdf_object_pointer_list)
            
    @classmethod
    def __delete_from_sub_pointer_list(cls, alist, target):
        delete_index = -1
        for i,pointer in enumerate(alist):
            if (pointer.object == None) or (pointer.object == target):
                delete_index = i
                break
        if delete_index > -1:
            alist.remove(delete_index)
            # After deleting an object, update the sub-indexes of the currently existing objects
            for i in range(delete_index, len(alist)):
                alist[i].object.sdf_prop.sub_index = alist[i].object.sdf_prop.sub_index - 1

    @classmethod
    def delete_from_sub_pointer_list(cls, context, target):
        global sdf_object_pointer_list_by_primitive_type
        primitive_type = target.sdf_prop.prev_primitive_type
        cls.__delete_from_sub_pointer_list(sdf_object_pointer_list_by_primitive_type[primitive_type](context), target)