from PIL import Image, ImageEnhance

# Load the image
input_image_path = "pcb_design_20241109_133923.png"
output_image_path = "pcb.png"
target_scale_factor = 0.2  # Target scale factor

# Open the image
image = Image.open(input_image_path).convert("RGBA")

# Gradual scaling
intermediate_scale = 0.5  # First scale to 50%
image = image.resize((int(image.width * intermediate_scale), int(image.height * intermediate_scale)), Image.LANCZOS)

# Final scaling to target size
final_width = int(image.width * target_scale_factor / intermediate_scale)
final_height = int(image.height * target_scale_factor / intermediate_scale)
resized_image = image.resize((final_width, final_height), Image.LANCZOS)

# Make all white pixels transparent
data = resized_image.getdata()
new_data = []
for item in data:
    if item[:3] == (255, 255, 255):  # Change white pixels to transparent
        new_data.append((255, 255, 255, 0))
    else:
        new_data.append(item)
resized_image.putdata(new_data)

# Optional: Apply sharpening to improve detail after resizing
sharpener = ImageEnhance.Sharpness(resized_image)
resized_image = sharpener.enhance(1.5)  # Adjust sharpness factor as needed

# Save the image
resized_image.save(output_image_path, "PNG")
print(f"Image saved as {output_image_path}")
