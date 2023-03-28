import bpy
import bmesh
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

# change view to show vertex-colors
def revert_vertex_colors():
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

# based on answer from ChameleonScales
# https://blender.stackexchange.com/questions/169844/multi-line-text-box-with-popup-menu
def popup(title = "Phaenotyp", lines=""):
    def draw(self, context):
        for line in lines:
            self.layout.label(text=line)
    bpy.context.window_manager.popup_menu(draw, title = title)

def force_distribution_info(self, context):
    # inform user when using force_distribution
    if bpy.context.scene.phaenotyp.calculation_type == "force_distribution":
        text = [
            "Force distribution is a solver for advance users.",
            "Please make sure, that your structure meets this conditions:",
            "- geometry is a mesh",
            "- the mesh is triangulated",
            "- the structure is stable (not flat)",
            "- the structure is one part only",
            "- exactly three vertices are defined as support",
            "- the supports are not connected with egdes",
            "- at least one load is defined"
            ]
        popup(lines = text)
