import subprocess
import os
import sys

def generate_templates():
    """
    Generate all required templates for Roblox outfit processing
    """
    try:
        # Create templates directory
        template_dir = os.path.join(os.getcwd(), 'templates')
        os.makedirs(template_dir, exist_ok=True)
        
        # Generate R15 armature template
        print("Generating R15 armature template...")
        subprocess.run([
            'blender', 
            '--background',
            '--python',
            'scripts/create_r15_template.py'
        ], check=True)
        
        # Generate UV templates
        print("Generating UV templates...")
        subprocess.run([
            'blender',
            '--background',
            '--python',
            'scripts/create_uv_templates.py'
        ], check=True)
        
        print("Templates generated successfully!")
        return True
        
    except Exception as e:
        print(f"Error generating templates: {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    generate_templates() 