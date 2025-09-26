#!/usr/bin/env python3
"""
创建Apple图标文件
生成简单的Apple logo图标用于GUI界面
"""

try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

import tkinter as tk

def create_simple_icon():
    """创建简单的Apple图标"""
    if not PIL_AVAILABLE:
        print("PIL/Pillow 未安装，跳过图标创建")
        return False
        
    # 创建64x64的图标
    size = 64
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制简单的苹果形状
    # 苹果主体 (椭圆)
    apple_color = (76, 175, 80, 255)  # 绿色
    draw.ellipse([12, 20, 52, 55], fill=apple_color)
    
    # 苹果叶子
    leaf_color = (56, 142, 60, 255)  # 深绿色
    draw.ellipse([35, 8, 45, 25], fill=leaf_color)
    
    # 苹果缺口
    bite_color = (0, 0, 0, 0)  # 透明
    draw.ellipse([40, 25, 50, 40], fill=bite_color)
    
    # 保存为PNG
    img.save('apple_icon.png')
    print("✅ 已创建 apple_icon.png")
    
    # 如果在Windows上，尝试创建ICO文件
    try:
        img.save('apple_icon.ico', format='ICO', sizes=[(32, 32), (64, 64)])
        print("✅ 已创建 apple_icon.ico")
    except Exception as e:
        print(f"⚠️ 创建ICO文件失败: {e}")
    
    return True

def create_tkinter_icon():
    """使用tkinter创建简单图标"""
    # 创建一个临时窗口来生成图标
    root = tk.Tk()
    root.withdraw()  # 隐藏窗口
    
    # 创建Canvas
    canvas = tk.Canvas(root, width=64, height=64, bg='white')
    
    # 绘制简单的苹果形状
    canvas.create_oval(12, 20, 52, 55, fill='#4CAF50', outline='#388E3C', width=2)
    canvas.create_oval(35, 8, 45, 25, fill='#388E3C', outline='#2E7D32', width=1)
    canvas.create_oval(40, 25, 50, 40, fill='white', outline='white')
    
    # 保存为PostScript文件（可以转换为其他格式）
    try:
        canvas.postscript(file="apple_icon.eps")
        print("✅ 已创建 apple_icon.eps")
    except Exception as e:
        print(f"⚠️ 创建EPS文件失败: {e}")
    
    root.destroy()

def main():
    """主函数"""
    print("🎨 创建Apple图标文件...")
    
    # 尝试使用PIL创建图标
    if create_simple_icon():
        print("✅ 图标创建完成")
    else:
        print("⚠️ PIL不可用，使用tkinter创建简单图标")
        create_tkinter_icon()
        print("💡 建议安装PIL/Pillow以获得更好的图标: pip install Pillow")

if __name__ == "__main__":
    main()
