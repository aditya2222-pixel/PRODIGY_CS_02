import hashlib
import random
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk


class ImageEncryptorApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Image Encryption Tool - Pixel Manipulation")
        self.root.geometry("900x600")

        # State Variables
        self.original_img = None
        self.encrypted_img = None
        self.decrypted_img = None

        # GUI Layout Construction
        self._build_ui()

    def _build_ui(self):
        # Key Entry Frame
        key_frame = tk.Frame(self.root, pady=10)
        key_frame.pack(fill=tk.X, padx=20)

        tk.Label(
            key_frame, text="Secret Password/Key:", font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=5)
        self.key_entry = tk.Entry(key_frame, show="*", width=30)
        self.key_entry.pack(side=tk.LEFT, padx=5)

        # Main Image Displays (3 Panels)
        preview_frame = tk.Frame(self.root)
        preview_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

        self.panel_orig = self._create_preview_panel(
            preview_frame, "1. Original Image"
        )
        self.panel_enc = self._create_preview_panel(
            preview_frame, "2. Encrypted Preview"
        )
        self.panel_dec = self._create_preview_panel(
            preview_frame, "3. Decrypted Preview"
        )

        # Control Buttons
        btn_frame = tk.Frame(self.root, pady=15)
        btn_frame.pack(fill=tk.X)

        tk.Button(
            btn_frame,
            text="Load Image",
            command=self.load_image,
            bg="#2196F3",
            fg="white",
            width=12,
        ).pack(side=tk.LEFT, padx=8)
        tk.Button(
            btn_frame,
            text="Encrypt",
            command=self.encrypt_image,
            bg="#4CAF50",
            fg="white",
            width=10,
        ).pack(side=tk.LEFT, padx=8)
        tk.Button(
            btn_frame,
            text="Decrypt",
            command=self.decrypt_image,
            bg="#FF9800",
            fg="white",
            width=10,
        ).pack(side=tk.LEFT, padx=8)
        tk.Button(
            btn_frame,
            text="Save Encrypted",
            command=self.save_encrypted,
            width=14,
        ).pack(side=tk.LEFT, padx=8)
        tk.Button(
            btn_frame,
            text="Save Decrypted",
            command=self.save_decrypted,
            width=14,
        ).pack(side=tk.LEFT, padx=8)
        tk.Button(
            btn_frame,
            text="Clear",
            command=self.clear_all,
            bg="#f44336",
            fg="white",
            width=10,
        ).pack(side=tk.LEFT, padx=8)

    def _create_preview_panel(self, parent, title):
        frame = tk.LabelFrame(parent, text=title, font=("Arial", 9, "bold"))
        frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)

        lbl = tk.Label(frame, text="No Image Loaded", bg="#e0e0e0")
        lbl.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        return lbl

    # Core Encryption & Key Processing Engine
    def _derive_seed_and_keys(self, password, length):
        """Generates deterministic pseudo-random seeds and XOR streams from key."""
        hashed = hashlib.sha256(password.encode("utf-8")).digest()
        seed = int.from_bytes(hashed, "big")

        # Generate PRNG stream for XOR operations
        prng = random.Random(seed)
        xor_stream = bytearray(prng.getrandbits(8) for _ in range(length))
        return seed, xor_stream

    def _generate_shuffle_permutation(self, length, seed):
        """Creates reversible index mapping using key-seeded Fisher-Yates shuffle."""
        indices = list(range(length))
        prng = random.Random(seed)
        for i in range(length - 1, 0, -1):
            j = prng.randint(0, i)
            indices[i], indices[j] = indices[j], indices[i]
        return indices

    def load_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")]
        )
        if not path:
            return
        try:
            self.original_img = Image.open(path).convert("RGB")
            self.encrypted_img = None
            self.decrypted_img = None

            self._update_display(self.panel_orig, self.original_img)
            self._reset_panel(self.panel_enc, "Encrypted Preview")
            self._reset_panel(self.panel_dec, "Decrypted Preview")
        except Exception as e:
            messagebox.showerror(
                "Error", f"Failed to load image:\n{str(e)}"
            )  # Error Handling

    def encrypt_image(self):
        if not self.original_img:
            messagebox.showwarning(
                "Warning", "Please load an original image first!"
            )  # Error Handling
            return
        key = self.key_entry.get()
        if not key:
            messagebox.showwarning(
                "Warning", "Please enter a secret password key!"
            )  # Error Handling
            return

        width, height = self.original_img.size
        raw_bytes = bytearray(self.original_img.tobytes())
        total_bytes = len(raw_bytes)

        seed, xor_stream = self._derive_seed_and_keys(key, total_bytes)

        # Step 1: Pixel/Byte Level XOR Transformation
        xored_bytes = bytearray(
            b ^ x for b, x in zip(raw_bytes, xor_stream)
        )

        # Step 2: Pixel Shuffling (Groups of 3 bytes for RGB)
        num_pixels = width * height
        pixel_indices = self._generate_shuffle_permutation(num_pixels, seed)

        shuffled_bytes = bytearray(total_bytes)
        for orig_idx, new_idx in enumerate(pixel_indices):
            shuffled_bytes[new_idx * 3 : (new_idx + 1) * 3] = xored_bytes[
                orig_idx * 3 : (orig_idx + 1) * 3
            ]

        self.encrypted_img = Image.frombytes(
            "RGB", (width, height), bytes(shuffled_bytes)
        )
        self._update_display(self.panel_enc, self.encrypted_img)

    def decrypt_image(self):
        if not self.encrypted_img:
            messagebox.showwarning(
                "Warning", "No encrypted image present to decrypt!"
            )  # Error Handling
            return
        key = self.key_entry.get()
        if not key:
            messagebox.showwarning(
                "Warning", "Please enter the decryption password key!"
            )  # Error Handling
            return

        width, height = self.encrypted_img.size
        shuffled_bytes = bytearray(self.encrypted_img.tobytes())
        total_bytes = len(shuffled_bytes)

        seed, xor_stream = self._derive_seed_and_keys(key, total_bytes)

        # Step 1: Un-shuffle Pixels (Reverse Permutation)
        num_pixels = width * height
        pixel_indices = self._generate_shuffle_permutation(num_pixels, seed)

        unshuffled_bytes = bytearray(total_bytes)
        for orig_idx, new_idx in enumerate(pixel_indices):
            unshuffled_bytes[orig_idx * 3 : (orig_idx + 1) * 3] = (
                shuffled_bytes[new_idx * 3 : (new_idx + 1) * 3]
            )

        # Step 2: Reverse XOR Operation
        decrypted_bytes = bytearray(
            b ^ x for b, x in zip(unshuffled_bytes, xor_stream)
        )

        self.decrypted_img = Image.frombytes(
            "RGB", (width, height), bytes(decrypted_bytes)
        )
        self._update_display(self.panel_dec, self.decrypted_img)

    def save_encrypted(self):
        if not self.encrypted_img:
            messagebox.showwarning("Warning", "No encrypted image to save!")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png", filetypes=[("PNG Image", "*.png")]
        )
        if path:
            # Lossless saving mandatory to preserve encrypted byte integrity
            self.encrypted_img.save(path, format="PNG")
            messagebox.showinfo("Success", "Encrypted image saved successfully!")

    def save_decrypted(self):
        if not self.decrypted_img:
            messagebox.showwarning("Warning", "No decrypted image to save!")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG Image", "*.png"),
                ("JPEG Image", "*.jpg"),
            ],
        )
        if path:
            self.decrypted_img.save(path)
            messagebox.showinfo("Success", "Decrypted image saved successfully!")

    def clear_all(self):
        self.original_img = None
        self.encrypted_img = None
        self.decrypted_img = None
        self.key_entry.delete(0, tk.END)

        self._reset_panel(self.panel_orig, "1. Original Image")
        self._reset_panel(self.panel_enc, "2. Encrypted Preview")
        self._reset_panel(self.panel_dec, "3. Decrypted Preview")

    def _update_display(self, label_widget, img):
        # Resize image dynamically for fixed UI layout preview
        resizing_img = img.copy()
        resizing_img.thumbnail((260, 380))
        tk_img = ImageTk.PhotoImage(resizing_img)

        label_widget.configure(image=tk_img, text="")
        label_widget.image = tk_img

    def _reset_panel(self, label_widget, text):
        label_widget.configure(image="", text="No Image Loaded")
        label_widget.image = None


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEncryptorApp(root)
    root.mainloop()