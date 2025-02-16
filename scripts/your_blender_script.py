import bpy

# Set color management
scene = bpy.context.scene
scene.view_settings.view_transform = 'Standard'
scene.display_settings.display_device = 'sRGB'

# ... rest of your Blender script ... 