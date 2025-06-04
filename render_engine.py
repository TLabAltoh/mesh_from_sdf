import bpy
import gpu
from mathutils import * 
from mesh_from_sdf.raymarching import *


class MeshFromSDFRenderEngine(bpy.types.RenderEngine):
    
    bl_idname = "mesh_from_sdf"
    bl_label = "Mesh from SDF"
    bl_use_preview = True

    def __init__(self):
        self.scene_data = None

    def __del__(self):
        del self.scene_data

    # For viewport renders, this method gets called once at the start and
    # whenever the scene or 3D viewport changes. This method is where data
    # should be read from Blender in the same thread. Typically a render
    # thread will be started to do the work while keeping Blender responsive.
    def view_update(self, context, depsgraph):
        
        region = context.region
        view3d = context.space_data
        scene = depsgraph.scene

        if not self.scene_data:
            # First time initialization
            self.scene_data = {}
            first_time = True

            for datablock in depsgraph.ids:
                pass
        else:
            first_time = False

            for update in depsgraph.updates:
                pass

            if depsgraph.id_type_updated('MATERIAL'):
                pass

        if first_time or depsgraph.id_type_updated('OBJECT'):
            for instance in depsgraph.object_instances:
                ob = instance.object

    # For viewport renders, this method is called whenever Blender redraws
    # the 3D viewport. The renderer is expected to quickly draw the render
    # with OpenGL, and not perform other expensive work.
    # Blender will draw overlays for selection and editing on top of the
    # rendered image automatically.
    def view_draw(self, context, depsgraph):

        view3d = context.space_data
        r3d = view3d.region_3d

        # gpu.matrix.load_matrix(r3d.perspective_matrix)
        # gpu.matrix.load_projection_matrix(Matrix.Identity(4))
        
        Raymarching.draw()


# RenderEngines also need to tell UI Panels that they are compatible with.
# We recommend to enable all panels marked as BLENDER_RENDER, and then
# exclude any panels that are replaced by custom panels registered by the
# render engine, or that are not supported.
def get_panels():
    exclude_panels = {
        'VIEWLAYER_PT_filter',
        'VIEWLAYER_PT_layer_passes',
    }

    panels = []
    for panel in bpy.types.Panel.__subclasses__():
        if hasattr(panel, 'COMPAT_ENGINES') and 'BLENDER_RENDER' in panel.COMPAT_ENGINES:
            if panel.__name__ not in exclude_panels:
                panels.append(panel)

    return panels


def register():
    bpy.utils.register_class(MeshFromSDFRenderEngine)

    for panel in get_panels():
        panel.COMPAT_ENGINES.add('mesh_from_sdf')


def unregister():
    bpy.utils.unregister_class(MeshFromSDFRenderEngine)

    for panel in get_panels():
        if 'mesh_from_sdf' in panel.COMPAT_ENGINES:
            panel.COMPAT_ENGINES.remove('mesh_from_sdf')