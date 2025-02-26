import bpy
import os

def create_r15_template():
    # Clear scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # Create armature
    bpy.ops.object.armature_add()
    armature = bpy.context.active_object
    armature.name = "R15_Armature"
    
    # Enter edit mode to add bones
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Dictionary of bone definitions (name, head, tail)
    bones = {
        "Root": ((0, 0, 0), (0, 0, 0.1)),
        "LowerTorso": ((0, 0, 0.1), (0, 0, 0.3)),
        "UpperTorso": ((0, 0, 0.3), (0, 0, 0.5)),
        "Head": ((0, 0, 0.5), (0, 0, 0.7)),
        "LeftUpperArm": ((-0.2, 0, 0.5), (-0.4, 0, 0.5)),
        "LeftLowerArm": ((-0.4, 0, 0.5), (-0.6, 0, 0.5)),
        "LeftHand": ((-0.6, 0, 0.5), (-0.7, 0, 0.5)),
        "RightUpperArm": ((0.2, 0, 0.5), (0.4, 0, 0.5)),
        "RightLowerArm": ((0.4, 0, 0.5), (0.6, 0, 0.5)),
        "RightHand": ((0.6, 0, 0.5), (0.7, 0, 0.5)),
        "LeftUpperLeg": ((-0.1, 0, 0.1), (-0.1, 0, -0.1)),
        "LeftLowerLeg": ((-0.1, 0, -0.1), (-0.1, 0, -0.3)),
        "LeftFoot": ((-0.1, 0, -0.3), (-0.1, 0.1, -0.3)),
        "RightUpperLeg": ((0.1, 0, 0.1), (0.1, 0, -0.1)),
        "RightLowerLeg": ((0.1, 0, -0.1), (0.1, 0, -0.3)),
        "RightFoot": ((0.1, 0, -0.3), (0.1, 0.1, -0.3))
    }
    
    # Create bones
    for name, (head, tail) in bones.items():
        bone = armature.data.edit_bones.new(name)
        bone.head = head
        bone.tail = tail
    
    # Set bone hierarchy
    eb = armature.data.edit_bones
    eb["UpperTorso"].parent = eb["LowerTorso"]
    eb["LowerTorso"].parent = eb["Root"]
    eb["Head"].parent = eb["UpperTorso"]
    
    eb["LeftUpperArm"].parent = eb["UpperTorso"]
    eb["LeftLowerArm"].parent = eb["LeftUpperArm"]
    eb["LeftHand"].parent = eb["LeftLowerArm"]
    
    eb["RightUpperArm"].parent = eb["UpperTorso"]
    eb["RightLowerArm"].parent = eb["RightUpperArm"]
    eb["RightHand"].parent = eb["RightLowerArm"]
    
    eb["LeftUpperLeg"].parent = eb["LowerTorso"]
    eb["LeftLowerLeg"].parent = eb["LeftUpperLeg"]
    eb["LeftFoot"].parent = eb["LeftLowerLeg"]
    
    eb["RightUpperLeg"].parent = eb["LowerTorso"]
    eb["RightLowerLeg"].parent = eb["RightUpperLeg"]
    eb["RightFoot"].parent = eb["RightLowerLeg"]
    
    # Exit edit mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Create a cage mesh for mesh deform
    bpy.ops.mesh.primitive_cube_add(size=2)
    cage = bpy.context.active_object
    cage.name = "R15_Cage"
    cage.scale = (0.4, 0.2, 0.8)
    
    # Export the template
    template_dir = os.path.join(os.getcwd(), 'templates')
    os.makedirs(template_dir, exist_ok=True)
    
    bpy.ops.export_scene.fbx(
        filepath=os.path.join(template_dir, 'r15_armature.fbx'),
        use_selection=False,
        use_mesh_modifiers=True,
        add_leaf_bones=False,
        bake_anim=False
    )

if __name__ == "__main__":
    create_r15_template() 