import bpy

# To avoid name conflicts with other materials, a hash value should be assigned.
def get_name_of_transparent_mat():
    return '[mesh_from_sdf] transparent (7493ea8aeafebfc85dbeb62756d8784c)'

# Create and regist a transparent material to hide the mesh and display only the SDF rendering results.
# https://blender.stackexchange.com/a/190027/230565
def confirm_to_transparent_mat_registed():
    mat_name = get_name_of_transparent_mat()
    mat = None

    # Create a new material if it has not been registered yet, or overwrite it if it has already been registered.
    if mat_name in bpy.data.materials:
        mat = bpy.data.materials[mat_name]
    else:
        mat = bpy.data.materials.new(mat_name)
        
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    for node in nodes:
        nodes.remove(node)
    links = mat.node_tree.links
    
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_output.location = 400,0
    node_pbsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_pbsdf.location = 0,0
    node_pbsdf.inputs['Base Color'].default_value = (1, 1, 1, 1)
    node_pbsdf.inputs['Alpha'].default_value = 0
    node_pbsdf.inputs['Roughness'].default_value = 0
    
    link = links.new(node_pbsdf.outputs['BSDF'], node_output.inputs['Surface'])