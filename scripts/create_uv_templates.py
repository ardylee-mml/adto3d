import bpy
import os

def create_uv_templates():
    template_dir = os.path.join(os.getcwd(), 'templates')
    os.makedirs(template_dir, exist_ok=True)
    
    # Shirt template
    bpy.ops.mesh.primitive_cube_add()
    shirt = bpy.context.active_object
    shirt.name = "ShirtTemplate"
    shirt.scale = (0.585/2, 0.559/2, 0.585/2)
    
    # Smart UV unwrap
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Export shirt template
    bpy.ops.export_scene.fbx(
        filepath=os.path.join(template_dir, 'shirt_template.fbx'),
        use_selection=True
    )
    
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Hat template
    bpy.ops.mesh.primitive_cylinder_add()
    hat = bpy.context.active_object
    hat.name = "HatTemplate"
    hat.scale = (0.25, 0.25, 0.1)
    
    # Add attachment point
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    attachment = bpy.context.active_object
    attachment.name = "HatAttachment"
    attachment.parent = hat
    
    # Export hat template
    bpy.ops.export_scene.fbx(
        filepath=os.path.join(template_dir, 'hat_template.fbx'),
        use_selection=True
    )
    
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Shoe template
    bpy.ops.mesh.primitive_cube_add()
    shoe = bpy.context.active_object
    shoe.name = "ShoeTemplate"
    shoe.scale = (0.1, 0.15, 0.05)
    
    # Add foot attachments
    for side in ['Left', 'Right']:
        bpy.ops.object.empty_add(type='PLAIN_AXES')
        attachment = bpy.context.active_object
        attachment.name = f"{side}FootAttachment"
        attachment.parent = shoe
        attachment.location = (0.1 if side == 'Right' else -0.1, 0, 0)
    
    # Export shoe template
    bpy.ops.export_scene.fbx(
        filepath=os.path.join(template_dir, 'shoe_template.fbx'),
        use_selection=True
    )

if __name__ == "__main__":
    create_uv_templates() 