#!/usr/bin/env python3
"""
Simple icon creator using only Pillow
Creates both Windows (.ico) and basic PNG icons
"""

import os
import sys

def install_pillow():
    """Install Pillow if not available"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        return True
    except ImportError:
        print("🔧 Installing Pillow...")
        try:
            import subprocess
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'Pillow'], check=True)
            print("✅ Pillow installed successfully")
            return True
        except:
            print("❌ Failed to install Pillow")
            return False

def create_icon_image(size):
    """Create a single icon image of specified size"""
    from PIL import Image, ImageDraw, ImageFont
    
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Colors
    bg_color = (30, 30, 30, 255)      # Dark background
    accent_color = (13, 115, 119, 255) # Teal accent
    white_color = (255, 255, 255, 255) # White
    apple_color = (40, 167, 69, 255)   # Green for apple
    
    # Draw background circle
    margin = max(2, size // 16)
    circle_size = size - 2 * margin
    draw.ellipse([margin, margin, margin + circle_size, margin + circle_size], 
                fill=bg_color, outline=accent_color, width=max(1, size//32))
    
    # Draw apple-like shape in upper part
    apple_size = size // 3
    apple_x = size // 2 - apple_size // 2
    apple_y = size // 4
    
    # Apple body (circle)
    draw.ellipse([apple_x, apple_y, apple_x + apple_size, apple_y + apple_size], 
                fill=white_color)
    
    # Apple leaf (small ellipse)
    leaf_size = apple_size // 4
    leaf_x = apple_x + apple_size - leaf_size // 2
    leaf_y = apple_y - leaf_size // 2
    draw.ellipse([leaf_x, leaf_y, leaf_x + leaf_size, leaf_y + leaf_size], 
                fill=apple_color)
    
    # Draw link/chain symbol in lower part
    link_y = size // 2 + size // 6
    link_size = size // 8
    link1_x = size // 2 - link_size - size // 16
    link2_x = size // 2 + size // 16
    
    # Two circles connected
    draw.ellipse([link1_x, link_y, link1_x + link_size, link_y + link_size], 
                outline=accent_color, width=max(1, size//64))
    draw.ellipse([link2_x, link_y, link2_x + link_size, link_y + link_size], 
                outline=accent_color, width=max(1, size//64))
    
    # Connection line
    line_y = link_y + link_size // 2
    draw.line([link1_x + link_size, line_y, link2_x, line_y], 
             fill=accent_color, width=max(1, size//64))
    
    # Draw browser window outline
    if size >= 32:  # Only for larger sizes
        window_margin = size // 6
        window_width = size - 2 * window_margin
        window_height = size // 3
        window_y = size - window_margin - window_height
        
        # Window frame
        draw.rectangle([window_margin, window_y, window_margin + window_width, window_y + window_height], 
                      outline=white_color, width=max(1, size//64))
        
        # Title bar
        title_bar_height = max(2, window_height // 6)
        draw.line([window_margin, window_y + title_bar_height, 
                  window_margin + window_width, window_y + title_bar_height], 
                 fill=white_color, width=max(1, size//64))
        
        # Traffic lights (if size is large enough)
        if size >= 64:
            dot_size = max(1, size // 64)
            dot_y = window_y + title_bar_height // 2
            dot_spacing = title_bar_height
            
            # Red, yellow, green dots
            colors = [(255, 95, 86, 255), (255, 189, 46, 255), (39, 202, 63, 255)]
            for i, color in enumerate(colors):
                dot_x = window_margin + dot_spacing + i * dot_spacing
                draw.ellipse([dot_x, dot_y, dot_x + dot_size, dot_y + dot_size], fill=color)
    
    return img

def create_all_icons():
    """Create all required icon sizes"""
    if not install_pillow():
        return False
    
    print("🎨 Creating icons...")
    
    # Standard icon sizes
    sizes = [16, 32, 48, 64, 128, 256, 512]
    images = []
    
    for size in sizes:
        try:
            img = create_icon_image(size)
            img.save(f'app_icon_{size}.png')
            images.append(img)
            print(f"✅ Created app_icon_{size}.png")
        except Exception as e:
            print(f"❌ Failed to create {size}px icon: {e}")
    
    # Create Windows ICO file
    try:
        if images:
            # Use sizes that work well for ICO
            ico_images = [img for img in images if img.size[0] <= 256]
            if ico_images:
                ico_images[0].save('app_icon.ico', format='ICO', 
                                 sizes=[(img.width, img.height) for img in ico_images])
                print("✅ Created app_icon.ico (Windows)")
            else:
                print("❌ No suitable images for ICO creation")
        else:
            print("❌ No images available for ICO creation")
    except Exception as e:
        print(f"❌ ICO creation failed: {e}")
    
    # Create a high-quality PNG for macOS (can be converted to ICNS later)
    try:
        if images:
            # Save the largest image as the main icon
            largest_img = max(images, key=lambda x: x.size[0])
            largest_img.save('app_icon.png')
            print("✅ Created app_icon.png (main icon)")
    except Exception as e:
        print(f"❌ Main PNG creation failed: {e}")
    
    # Clean up individual size files
    try:
        for size in sizes:
            png_file = f'app_icon_{size}.png'
            if os.path.exists(png_file):
                os.remove(png_file)
        print("🗑️ Cleaned up intermediate files")
    except:
        pass
    
    return True

def create_simple_fallback_icon():
    """Create a very simple fallback icon if Pillow fails"""
    # Create a simple text-based icon file
    icon_data = '''
    Simple Icon Placeholder
    
    This is a placeholder for the application icon.
    The actual icon should be created using proper image tools.
    
    For Windows: app_icon.ico
    For macOS: app_icon.icns
    For general use: app_icon.png
    '''
    
    with open('icon_placeholder.txt', 'w') as f:
        f.write(icon_data)
    
    print("📝 Created icon placeholder file")

def main():
    """Main function"""
    print("🎨 Simple Icon Creator for Linken Sphere Apple Browser")
    print("=" * 60)
    
    try:
        if create_all_icons():
            print("\n🎉 Icon creation completed!")
            print("📁 Created files:")
            
            if os.path.exists('app_icon.ico'):
                size = os.path.getsize('app_icon.ico')
                print(f"  - app_icon.ico ({size} bytes) - Windows icon")
            
            if os.path.exists('app_icon.png'):
                size = os.path.getsize('app_icon.png')
                print(f"  - app_icon.png ({size} bytes) - Main icon")
            
            print("\n💡 Usage:")
            print("  - Windows: Use app_icon.ico in your application")
            print("  - macOS: Convert app_icon.png to .icns using:")
            print("    sips -s format icns app_icon.png --out app_icon.icns")
            print("  - Linux: Use app_icon.png")
            
        else:
            print("❌ Icon creation failed, creating fallback...")
            create_simple_fallback_icon()
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        create_simple_fallback_icon()

if __name__ == "__main__":
    main()
