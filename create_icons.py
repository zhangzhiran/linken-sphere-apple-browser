#!/usr/bin/env python3
"""
Create cross-platform icons for Linken Sphere Apple Browser
Generates both Windows (.ico) and macOS (.icns) icons
"""

import os
import sys
from pathlib import Path

def create_simple_icon_svg():
    """Create a simple SVG icon"""
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="256" height="256" viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg">
  <!-- Background circle -->
  <circle cx="128" cy="128" r="120" fill="#1e1e1e" stroke="#0d7377" stroke-width="8"/>
  
  <!-- Apple-like shape -->
  <path d="M128 40 C 100 40, 80 60, 80 88 C 80 116, 100 136, 128 136 C 156 136, 176 116, 176 88 C 176 60, 156 40, 128 40 Z" fill="#ffffff"/>
  
  <!-- Leaf -->
  <path d="M140 45 C 145 40, 155 42, 158 48 C 160 52, 155 55, 150 53 C 145 51, 142 48, 140 45 Z" fill="#28a745"/>
  
  <!-- Link/Chain symbol -->
  <circle cx="100" cy="180" r="20" fill="none" stroke="#0d7377" stroke-width="6"/>
  <circle cx="156" cy="180" r="20" fill="none" stroke="#0d7377" stroke-width="6"/>
  <line x1="120" y1="180" x2="136" y2="180" stroke="#0d7377" stroke-width="6"/>
  
  <!-- Browser window -->
  <rect x="60" y="120" width="136" height="80" rx="8" fill="none" stroke="#ffffff" stroke-width="3"/>
  <line x1="60" y1="135" x2="196" y2="135" stroke="#ffffff" stroke-width="2"/>
  <circle cx="75" cy="127" r="3" fill="#ff5f56"/>
  <circle cx="90" cy="127" r="3" fill="#ffbd2e"/>
  <circle cx="105" cy="127" r="3" fill="#27ca3f"/>
</svg>'''
    
    with open('app_icon.svg', 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    print("✅ Created app_icon.svg")

def create_png_from_svg():
    """Convert SVG to PNG using available tools"""
    try:
        # Try using cairosvg (Python library)
        import cairosvg
        
        # Create multiple sizes for better icon quality
        sizes = [16, 32, 48, 64, 128, 256, 512]
        
        for size in sizes:
            cairosvg.svg2png(
                url='app_icon.svg',
                write_to=f'app_icon_{size}.png',
                output_width=size,
                output_height=size
            )
            print(f"✅ Created app_icon_{size}.png")
        
        return True
        
    except ImportError:
        print("⚠️ cairosvg not available, trying alternative methods...")
        
        # Try using Pillow with svg support
        try:
            from PIL import Image
            import subprocess
            
            # Try using Inkscape if available
            try:
                subprocess.run(['inkscape', '--version'], capture_output=True, check=True)
                
                sizes = [16, 32, 48, 64, 128, 256, 512]
                for size in sizes:
                    subprocess.run([
                        'inkscape',
                        '--export-type=png',
                        f'--export-filename=app_icon_{size}.png',
                        f'--export-width={size}',
                        f'--export-height={size}',
                        'app_icon.svg'
                    ], check=True)
                    print(f"✅ Created app_icon_{size}.png using Inkscape")
                
                return True
                
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("⚠️ Inkscape not available")
                
        except ImportError:
            pass
        
        # Fallback: create a simple colored rectangle as PNG
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            sizes = [16, 32, 48, 64, 128, 256, 512]
            
            for size in sizes:
                # Create image
                img = Image.new('RGBA', (size, size), (30, 30, 30, 255))
                draw = ImageDraw.Draw(img)
                
                # Draw background circle
                margin = size // 16
                draw.ellipse([margin, margin, size-margin, size-margin], 
                           fill=(13, 115, 119, 255), outline=(255, 255, 255, 255), width=max(1, size//64))
                
                # Draw simple "LA" text for Linken Apple
                try:
                    font_size = max(8, size // 4)
                    font = ImageFont.load_default()
                    text = "LA"
                    
                    # Get text size
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    # Center text
                    x = (size - text_width) // 2
                    y = (size - text_height) // 2
                    
                    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
                    
                except:
                    # If text fails, draw a simple shape
                    center = size // 2
                    radius = size // 4
                    draw.ellipse([center-radius, center-radius, center+radius, center+radius], 
                               fill=(255, 255, 255, 255))
                
                img.save(f'app_icon_{size}.png')
                print(f"✅ Created app_icon_{size}.png using PIL")
            
            return True
            
        except ImportError:
            print("❌ No image processing libraries available")
            return False

def create_ico_file():
    """Create Windows .ico file"""
    try:
        from PIL import Image
        
        # Load PNG files
        sizes = [16, 32, 48, 64, 128, 256]
        images = []
        
        for size in sizes:
            png_file = f'app_icon_{size}.png'
            if os.path.exists(png_file):
                img = Image.open(png_file)
                images.append(img)
        
        if images:
            # Save as ICO
            images[0].save('app_icon.ico', format='ICO', sizes=[(img.width, img.height) for img in images])
            print("✅ Created app_icon.ico")
            return True
        else:
            print("❌ No PNG files found for ICO creation")
            return False
            
    except ImportError:
        print("❌ PIL not available for ICO creation")
        return False

def create_icns_file():
    """Create macOS .icns file"""
    try:
        import subprocess
        
        # Check if iconutil is available (macOS only)
        try:
            subprocess.run(['iconutil', '--version'], capture_output=True, check=True)
            
            # Create iconset directory
            iconset_dir = 'app_icon.iconset'
            os.makedirs(iconset_dir, exist_ok=True)
            
            # Copy PNG files with correct naming for iconset
            icon_mappings = {
                16: 'icon_16x16.png',
                32: ['icon_16x16@2x.png', 'icon_32x32.png'],
                64: 'icon_32x32@2x.png',
                128: ['icon_64x64@2x.png', 'icon_128x128.png'],
                256: ['icon_128x128@2x.png', 'icon_256x256.png'],
                512: ['icon_256x256@2x.png', 'icon_512x512.png'],
            }
            
            for size, names in icon_mappings.items():
                src_file = f'app_icon_{size}.png'
                if os.path.exists(src_file):
                    if isinstance(names, list):
                        for name in names:
                            import shutil
                            shutil.copy2(src_file, os.path.join(iconset_dir, name))
                    else:
                        import shutil
                        shutil.copy2(src_file, os.path.join(iconset_dir, names))
            
            # Create ICNS file
            subprocess.run(['iconutil', '-c', 'icns', iconset_dir], check=True)
            
            # Clean up iconset directory
            import shutil
            shutil.rmtree(iconset_dir)
            
            print("✅ Created app_icon.icns")
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ iconutil not available (not on macOS)")
            return False
            
    except Exception as e:
        print(f"❌ ICNS creation failed: {e}")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("🔧 Installing icon creation dependencies...")
    
    try:
        import subprocess
        import sys
        
        # Try to install cairosvg and Pillow
        packages = ['Pillow', 'cairosvg']
        
        for package in packages:
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                             capture_output=True, check=True)
                print(f"✅ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"⚠️ Failed to install {package}")
        
    except Exception as e:
        print(f"❌ Dependency installation failed: {e}")

def main():
    """Main function"""
    print("🎨 Creating cross-platform icons for Linken Sphere Apple Browser")
    print("=" * 70)
    
    # Install dependencies
    install_dependencies()
    
    # Create SVG icon
    create_simple_icon_svg()
    
    # Convert to PNG
    if create_png_from_svg():
        print("✅ PNG creation successful")
        
        # Create Windows ICO
        if create_ico_file():
            print("✅ Windows ICO creation successful")
        
        # Create macOS ICNS (only works on macOS)
        if create_icns_file():
            print("✅ macOS ICNS creation successful")
        
        # Clean up intermediate PNG files
        try:
            for size in [16, 32, 48, 64, 128, 256, 512]:
                png_file = f'app_icon_{size}.png'
                if os.path.exists(png_file):
                    os.remove(png_file)
            print("🗑️ Cleaned up intermediate PNG files")
        except:
            pass
        
        print("\n🎉 Icon creation completed!")
        print("📁 Created files:")
        if os.path.exists('app_icon.ico'):
            print("  - app_icon.ico (Windows)")
        if os.path.exists('app_icon.icns'):
            print("  - app_icon.icns (macOS)")
        print("  - app_icon.svg (source)")
        
    else:
        print("❌ PNG creation failed")

if __name__ == "__main__":
    main()
