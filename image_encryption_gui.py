import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

selected_image = None


def select_image():
    global selected_image

    file_path = filedialog.askopenfilename(
        filetypes=[
            ("Image Files", "*.png *.jpg *.jpeg *.bmp"),
            ("All Files", "*.*")
        ]
    )

    if file_path:
        selected_image = file_path
        image_label.config(text=file_path.split("/")[-1])
        show_image(file_path)


def show_image(file_path):
    image = Image.open(file_path)
    image.thumbnail((400, 300))

    photo = ImageTk.PhotoImage(image)
    preview_label.config(image=photo)
    preview_label.image = photo


def encrypt_image():
    if not selected_image:
        messagebox.showwarning("Warning", "Please select an image first.")
        return

    try:
        key = int(key_entry.get())

        if key < 0 or key > 255:
            messagebox.showerror("Error", "Key must be between 0 and 255.")
            return

        image = Image.open(selected_image).convert("RGB")
        pixels = image.load()

        for y in range(image.height):
            for x in range(image.width):
                r, g, b = pixels[x, y]

                pixels[x, y] = (
                    r ^ key,
                    g ^ key,
                    b ^ key
                )

        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png")]
        )

        if save_path:
            image.save(save_path)
            messagebox.showinfo(
                "Success",
                "Image encrypted successfully!"
            )

    except ValueError:
        messagebox.showerror("Error", "Enter a valid numeric key.")


def decrypt_image():
    if not selected_image:
        messagebox.showwarning("Warning", "Please select an image first.")
        return

    try:
        key = int(key_entry.get())

        if key < 0 or key > 255:
            messagebox.showerror("Error", "Key must be between 0 and 255.")
            return

        image = Image.open(selected_image).convert("RGB")
        pixels = image.load()

        for y in range(image.height):
            for x in range(image.width):
                r, g, b = pixels[x, y]

                pixels[x, y] = (
                    r ^ key,
                    g ^ key,
                    b ^ key
                )

        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png")]
        )

        if save_path:
            image.save(save_path)
            messagebox.showinfo(
                "Success",
                "Image decrypted successfully!"
            )

    except ValueError:
        messagebox.showerror("Error", "Enter a valid numeric key.")


def clear_all():
    global selected_image

    selected_image = None
    image_label.config(text="No image selected")
    preview_label.config(image="")
    preview_label.image = None
    key_entry.delete(0, tk.END)


root = tk.Tk()
root.title("Image Encryption Tool")
root.geometry("650x650")
root.resizable(False, False)

title = tk.Label(
    root,
    text="Image Encryption Tool",
    font=("Arial", 24, "bold")
)
title.pack(pady=20)

select_button = tk.Button(
    root,
    text="Select Image",
    width=20,
    command=select_image
)
select_button.pack(pady=10)

image_label = tk.Label(
    root,
    text="No image selected",
    font=("Arial", 10)
)
image_label.pack()

preview_label = tk.Label(root)
preview_label.pack(pady=20)

tk.Label(
    root,
    text="Encryption Key (0-255)",
    font=("Arial", 12, "bold")
).pack()

key_entry = tk.Entry(
    root,
    width=15,
    font=("Arial", 12)
)
key_entry.pack(pady=10)

button_frame = tk.Frame(root)
button_frame.pack(pady=15)

tk.Button(
    button_frame,
    text="Encrypt",
    width=12,
    command=encrypt_image
).grid(row=0, column=0, padx=5)

tk.Button(
    button_frame,
    text="Decrypt",
    width=12,
    command=decrypt_image
).grid(row=0, column=1, padx=5)

tk.Button(
    button_frame,
    text="Clear",
    width=12,
    command=clear_all
).grid(row=0, column=2, padx=5)

root.mainloop()