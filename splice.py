import os
import cv2
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

def detect_image_splicing(forged_path, original_path):
    # Debug: Print the received image paths
    print("Forged Image Path:", forged_path)
    print("Original Image Path:", original_path)

    # Load the forged and original images
    forged_image = cv2.imread(forged_path)
    original_image = cv2.imread(original_path)

    # Check if the images were loaded successfully
    if forged_image is None or original_image is None:
        raise ValueError("Failed to load one or both of the images.")

    # Ensure both images have the same dimensions
    if forged_image.shape != original_image.shape:
        raise ValueError("The forged and original images must have the same dimensions.")

    # Convert the images to grayscale
    forged_gray = cv2.cvtColor(forged_image, cv2.COLOR_BGR2GRAY)
    original_gray = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)

    # Calculate the absolute difference between the images
    difference = cv2.absdiff(forged_gray, original_gray)

    # Threshold the difference image to obtain binary mask of spliced regions
    _, binary_mask = cv2.threshold(difference, 25, 255, cv2.THRESH_BINARY)

    # Invert the binary mask to get the spliced regions in white and the unspliced in black
    inverted_mask = cv2.bitwise_not(binary_mask)

    # Convert the binary mask to 3-channel (BGR) format
    spliced_regions_mask = cv2.merge([inverted_mask, inverted_mask, inverted_mask])

    # Mask the original image to make the spliced part white and unspliced part black
    output_image = cv2.bitwise_and(original_image, spliced_regions_mask)

    # Convert the images to PIL format
    forged_img_pil = Image.fromarray(cv2.cvtColor(forged_image, cv2.COLOR_BGR2RGB))
    original_img_pil = Image.fromarray(cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB))
    output_img_pil = Image.fromarray(cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB))

    # Resize images to display in the GUI
    image_size = (300, 300)
    forged_img_pil = forged_img_pil.resize(image_size, Image.ANTIALIAS)
    original_img_pil = original_img_pil.resize(image_size, Image.ANTIALIAS)
    output_img_pil = output_img_pil.resize(image_size, Image.ANTIALIAS)

    # Convert the images to PhotoImage for displaying in the GUI
    forged_img_tk = ImageTk.PhotoImage(forged_img_pil)
    original_img_tk = ImageTk.PhotoImage(original_img_pil)
    output_img_tk = ImageTk.PhotoImage(output_img_pil)

    # Update the labels to show the images in the GUI
    forged_label.config(image=forged_img_tk)
    forged_label.image = forged_img_tk

    original_label.config(image=original_img_tk)
    original_label.image = original_img_tk

    output_label.config(image=output_img_tk)
    output_label.image = output_img_tk

    # Mask the forged image to keep only the spliced part in black and the rest in white
    spliced_only_mask = cv2.bitwise_and(forged_image, spliced_regions_mask)

    # Convert the spliced-only mask to grayscale
    spliced_only_gray = cv2.cvtColor(spliced_only_mask, cv2.COLOR_BGR2GRAY)

    # Threshold the spliced-only mask to obtain binary mask of spliced regions
    _, spliced_binary_mask = cv2.threshold(spliced_only_gray, 1, 255, cv2.THRESH_BINARY)

    # Invert the spliced binary mask to get the spliced regions in black and the rest in white
    spliced_regions_output = cv2.bitwise_not(spliced_binary_mask)

    # Convert the spliced regions output to 3-channel (BGR) format
    spliced_regions_output = cv2.merge([spliced_regions_output, spliced_regions_output, spliced_regions_output])

    # Resize the spliced regions output to display in the GUI
    spliced_output_pil = Image.fromarray(cv2.cvtColor(spliced_regions_output, cv2.COLOR_BGR2RGB))
    spliced_output_pil = spliced_output_pil.resize(image_size, Image.ANTIALIAS)

    # Convert the spliced regions output to PhotoImage for displaying in the GUI
    spliced_output_tk = ImageTk.PhotoImage(spliced_output_pil)

    # Update the label to show the spliced regions output image in the GUI
    spliced_output_label.config(image=spliced_output_tk)
    spliced_output_label.image = spliced_output_tk

    # Save the spliced regions output image to a file
    spliced_output_pil.save("spliced_regions_output.jpg")

def select_forged_image():
    path = filedialog.askopenfilename(title="Select Forged Image", filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
    if path:
        forged_image_path.set(path)
        update_output_image()

def select_original_image():
    path = filedialog.askopenfilename(title="Select Original Image", filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
    if path:
        original_image_path.set(path)
        update_output_image()

def update_output_image():
    forged_path = forged_image_path.get()
    original_path = original_image_path.get()

    try:
        detect_image_splicing(forged_path, original_path)

    except Exception as e:
        result_label.config(text=f"")

# Create the main application window
root = tk.Tk()
root.title("Image Forgery Detection")

# Variables to store image paths
forged_image_path = tk.StringVar()
original_image_path = tk.StringVar()

# GUI components
forged_button = tk.Button(root, text="Select Forged Image", command=select_forged_image)
forged_button.pack()

original_button = tk.Button(root, text="Select Original Image", command=select_original_image)
original_button.pack()

input_frame = tk.Frame(root)
input_frame.pack()

forged_label = tk.Label(input_frame, text="Forged Image")
forged_label.pack(side=tk.LEFT)

original_label = tk.Label(input_frame, text="Original Image")
original_label.pack(side=tk.RIGHT)

output_frame = tk.Frame(root)
output_frame.pack()

output_label = tk.Label(output_frame, text="Output Image")
output_label.pack()

# Add a new label to show the spliced regions output in the GUI
spliced_output_label = tk.Label(output_frame, text="Spliced Regions Output Image")
spliced_output_label.pack()

result_label = tk.Label(root, text="Image forgery detection and specification completed successfully.")
result_label.pack()

# Start the main event loop
root.mainloop()
