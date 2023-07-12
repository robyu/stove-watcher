from PIL import Image, ImageDraw, ImageTk
from tkinter import Tk, Label
import sys

def markbb(image_file):
    root = Tk()
    root.title("Image")
    
    # Open the image using Pillow
    image = Image.open(image_file)
    
    # Create a drawing object
    draw = ImageDraw.Draw(image)
    
    # Create a label to display the image
    image_label = Label(root)
    image_label.pack()
    
    # Convert the image to PhotoImage format
    image_tk = ImageTk.PhotoImage(image)

    # Display the image
    image_label.configure(image=image_tk)
    image_label.image = image_tk


    start_x = 0
    start_y = 0
    
    def handle_keypress(event):
        print("got keypress")
        if event.char.lower() == 'q':
            sys.exit(0)
    
    def handle_mousepress(event):
        nonlocal start_x, start_y
        (start_x, start_y) = event.x, event.y
        print(f"{start_x}, {start_y}")
    
    def handle_mousedrag(event):
        nonlocal start_x, start_y
        end_x, end_y = event.x, event.y
        print(f"{end_x}, {end_y}")
        draw.rectangle((start_x, start_y, end_x, end_y), outline="green", width=2)
        image_label.configure(image=image_tk)
        root.update_idletasks()
    
    root.bind("<KeyPress>", handle_keypress)
    root.bind("<ButtonPress-1>", handle_mousepress)
    root.bind("<B1-Motion>", handle_mousedrag)
    root.mainloop()


markbb('out-resized/apple-2023-05-14-19-18-2.jpg')
