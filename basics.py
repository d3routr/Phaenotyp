import bpy
import bmesh
from phaenotyp import geometry
from queue import Queue

def print_data(text):
    """
    Used to print data for debugging.
    :param text: Needs a text as string (Do not pass as list).
    """
    print("Phaenotyp |", text)

def create_data():
    data = bpy.context.scene.get("<Phaenotyp>")
    if not data:
        data = bpy.context.scene["<Phaenotyp>"] = {
            "structure":{},
            "supports":{},
            "members":{},
            "frames":{},
            "loads_v":{},
            "loads_e":{},
            "loads_f":{},
            "process":{},
            "done":{},
            "ga_environment":{},
            "ga_individuals":{},
            "texts":{}
        }

        data["structure"] = None
        data["supports"] = {}
        data["members"] = {}
        data["frames"] = {}
        data["loads_v"] = {}
        data["loads_e"] = {}
        data["loads_f"] = {}

        data["process"]["scipy_available"] = False
        data["done"] = {}

        data["ga_environment"] = {}
        data["ga_individuals"] = {}

        data["texts"] = []

# this function is sorting the keys of the dict
# (to avoid iterating like 0,10,2,3 ...)
def sorted_keys(dict):
    keys_int = list(map(int, dict))
    sorted_int_keys = sorted(keys_int)
    return sorted_int_keys

# to avoid division by zero if a force is 0
def avoid_div_zero(a,b):
    if b == 0:
        return 0
    else:
        return a/b

# function to return the smallest_minus or biggest_plus in a list
def return_max_diff_to_zero(list):
    list_copy = list.copy()
    list_copy.sort()

    smallest_minus = list_copy[0]
    biggest_plus = list_copy[len(list_copy)-1]

    if abs(smallest_minus) > abs(biggest_plus):
        return smallest_minus
    else:
        return biggest_plus

# functions to handle objects
def delete_obj_if_existing(name):
    obj = bpy.data.objects.get(name)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)

def delete_mesh_if_existing(name):
    mesh = bpy.data.meshes.get(name)
    if mesh:
        bpy.data.meshes.remove(mesh, do_unlink=True)

def delete_col_if_existing(name):
    col = bpy.data.collections.get(name)
    if col:
        bpy.data.collections.remove(col, do_unlink=True)

def delete_obj_if_name_contains(text):
    for obj in bpy.data.objects:
        if text in obj.name_full:
            bpy.data.objects.remove(obj, do_unlink=True)

# change view to show vertex-colors
def view_vertex_colors():
    # issue with vertex-color in blender 3.5
    '''
    # change viewport to material
    # based on approach from Hotox:
    # https://devtalk.blender.org/t/how-to-change-view3dshading-type-in-2-8/3462
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'SOLID'
                    space.shading.light = 'FLAT'
                    space.shading.color_type = 'VERTEX'
    '''
    bpy.context.space_data.shading.type = 'MATERIAL'

# change view to show vertex-colors
def revert_vertex_colors():
    '''
    # change viewport to material
    # based on approach from Hotox:
    # https://devtalk.blender.org/t/how-to-change-view3dshading-type-in-2-8/3462
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'SOLID'
                    space.shading.light = 'STUDIO'
                    space.shading.color_type = 'MATERIAL'
    '''
    bpy.context.space_data.shading.type = 'SOLID'

# based on answer from ChameleonScales
# https://blender.stackexchange.com/questions/169844/multi-line-text-box-with-popup-menu
def popup(title = "Phaenotyp", lines=""):
    def draw(self, context):
        for line in lines:
            self.layout.label(text=line)
    bpy.context.window_manager.popup_menu(draw, title = title)

def popup_operator(title = "Phaenotyp", lines="", operator=None, text=""):
    def draw(self, context):
        for line in lines:
            self.layout.label(text=line)
        self.layout.separator()
        self.layout.operator(operator, text=text)
    bpy.context.window_manager.popup_menu(draw, title = title)

def force_distribution_info(self, context):
    # inform user when using force_distribution
    if bpy.context.scene.phaenotyp.calculation_type == "force_distribution":
        # triangulation
        if geometry.triangulation() == False:
            text = ["The selection needs to be triangulated for force distribution.",
                "Should Phaenotyp try to triangulate the selection?"]
            popup_operator(lines=text, operator="wm.fix_structure", text="Triangulate")
            geometry.to_be_fixed = "triangulate"

        else:
            text = [
                "Force distribution is a solver for advance users.",
                "Please make sure, that your structure meets this conditions:",
                "- the mesh is triangulated",
                "- the structure is stable (not flat)",
                "- exactly three vertices are defined as support",
                "- the supports are not connected with egdes",
                "- at least one load is defined"
                ]
            popup(lines = text)


# check modifieres in modify or deform
# modifieres working with Phänotyp:
modifiers = {}
modifiers["ARMATURE"] = True
modifiers["CAST"] = True
modifiers["CLOTH"] = True
modifiers["COLLISION"] = True
modifiers["CURVE"] = True
modifiers["DATA_TRANSFER"] = True
modifiers["DYNAMIC_PAINT"] = True
modifiers["DISPLACE"] = True
modifiers["HOOK"] = True
modifiers["LAPLACIANDEFORM"] = True
modifiers["LATTICE"] = True
modifiers["MESH_CACHE"] = True
modifiers["MESH_DEFORM"] = True
modifiers["MESH_SEQUENCE_CACHE"] = True
modifiers["NORMAL_EDIT"] = True
modifiers["NODES"] = True
modifiers["SHRINKWRAP"] = True
modifiers["SIMPLE_DEFORM"] = True
modifiers["SMOOTH"] = True
modifiers["CORRECTIVE_SMOOTH"] = True
modifiers["LAPLACIANSMOOTH"] = True
modifiers["OCEAN"] = True
modifiers["PARTICLE_INSTANCE"] = True
modifiers["PARTICLE_SYSTEM"] = True
modifiers["SOFT_BODY"] = True
modifiers["SURFACE"] = True
modifiers["SURFACE_DEFORM"] = True
modifiers["WARP"] = True
modifiers["WAVE"] = True
modifiers["WEIGHTED_NORMAL"] = True
modifiers["UV_PROJECT"] = True
modifiers["UV_WARP"] = True
modifiers["VERTEX_WEIGHT_EDIT"] = True
modifiers["VERTEX_WEIGHT_MIX"] = True
modifiers["VERTEX_WEIGHT_PROXIMITY"] = True

# not working:
modifiers["ARRAY"] = False
modifiers["BEVEL"] = False
modifiers["BOOLEAN"] = False
modifiers["BUILD"] = False
modifiers["DECIMATE"] = False
modifiers["EDGE_SPLIT"] = False
modifiers["EXPLODE"] = False
modifiers["FLUID"] = False
modifiers["MASK"] = False
modifiers["MIRROR"] = False
modifiers["MESH_TO_VOLUME"] = False
modifiers["MULTIRES"] = False
modifiers["REMESH"] = False
modifiers["SCREW"] = False
modifiers["SKIN"] = False
modifiers["SOLIDIFY"] = False
modifiers["SUBSURF"] = False
modifiers["TRIANGULATE"] = False
modifiers["VOLUME_TO_MESH"] = False
modifiers["WELD"] = False
modifiers["WIREFRAME"] = False
modifiers["VOLUME_DISPLACE"] = False


def check_modifiers():
    obj = bpy.context.object
    for modifiere in obj.modifiers:
        name = modifiere.type

        if name == "NODES":
            text = ["Geometry Nodes can be used but make sure that no geometry is added",
               "or deleted during execution of Phaenotyp to avoid weird results"]
            popup(lines = text)

        elif name in modifiers:
            working = modifiers[name]
            if working == False:
                text = [
                        "Modifiere with type " + str(name) + " can cause weird results.",
                        "",
                        "You can use this modifiers:",
                        "ARMATURE, CAST, CLOTH, COLLISION, CURVE, DATA_TRANSFER,",
                        "DYNAMIC_PAINT, DISPLACE, HOOK, LAPLACIANDEFORM, LATTICE,",
                        "MESH_CACHE, MESH_DEFORM, MESH_SEQUENCE_CACHE, NORMAL_EDIT,",
                        "NODES, SHRINKWRAP, SIMPLE_DEFORM, SMOOTH, CORRECTIVE_SMOOTH,",
                        "LAPLACIANSMOOTH, OCEAN, PARTICLE_INSTANCE, PARTICLE_SYSTEM,",
                        "SOFT_BODY, SURFACE, SURFACE_DEFORM, WARP, WAVE, WEIGHTED_NORMAL,",
                        "UV_PROJECT, UV_WARP, VERTEX_WEIGHT_EDIT, VERTEX_WEIGHT_MIX,",
                        "VERTEX_WEIGHT_PROXIMITY."
                        ]
                popup(lines = text)
