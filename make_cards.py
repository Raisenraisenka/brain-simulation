from PIL import Image, ImageDraw, ImageFont

W, H = 800, 800

try:
    font_large = ImageFont.truetype("/system/fonts/Roboto-Regular.ttf", 60)
    font_medium = ImageFont.truetype("/system/fonts/Roboto-Regular.ttf", 40)
    font_small = ImageFont.truetype("/system/fonts/Roboto-Regular.ttf", 25)
except:
    font_large = ImageFont.load_default()
    font_medium = ImageFont.load_default()
    font_small = ImageFont.load_default()

# 1. INTRO ŞƏKLİ (İngiliscə)
intro = Image.new('RGB', (W, H), color='#0a0a1a')
draw = ImageDraw.Draw(intro)
draw.text((W/2, H/2 - 80), "Brain Neural Network", fill="white", font=font_large, anchor="mm")
draw.text((W/2, H/2 + 20), "Izhikevich 2003 Model", fill="#00ccff", font=font_medium, anchor="mm")
draw.text((W/2, H/2 + 100), "3D Visualization", fill="#ff3366", font=font_small, anchor="mm")
intro.save("intro.png")
print("✅ intro.png (English) yaradıldı")

# 2. OUTRO ŞƏKLİ (İngiliscə)
outro = Image.new('RGB', (W, H), color='#0a0a1a')
draw = ImageDraw.Draw(outro)
draw.text((W/2, H/2 - 60), "Code & Details", fill="white", font=font_medium, anchor="mm")
draw.text((W/2, H/2 + 20), "github.com/Raisenraisenka", fill="#ff3366", font=font_small, anchor="mm")
draw.text((W/2, H/2 + 60), "brain-simulation", fill="#ff3366", font=font_small, anchor="mm")
draw.text((W/2, H/2 + 150), "Python + Matplotlib", fill="#00ccff", font=font_small, anchor="mm")
outro.save("outro.png")
print("✅ outro.png (English) yaradıldı")
