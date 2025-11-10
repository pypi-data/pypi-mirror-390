def drawRect(canvas, x, y, width, height, color="black"):
    return canvas.create_rectangle(x, y, x + width, y + height, fill=color)

def drawCircle(canvas, x, y, radius, color="black"):
    return canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color)

def drawText(canvas, x, y, text, font=("Arial", 12), color="black"):
    return canvas.create_text(x, y, text=text, font=font, fill=color)

def drawOval(canvas, x, y, width, height, color="black"):
    return canvas.create_oval(x, y, x + width, y + height, fill=color)

def drawLine(canvas, x1, y1, x2, y2, color="black", width=2):
    return canvas.create_line(x1, y1, x2, y2, fill=color, width=width)

def drawPolygon(canvas, points, color="black"):
    return canvas.create_polygon(points, fill=color)

def drawArc(canvas, x, y, width, height, start=0, extent=90, color="black"):
    return canvas.create_arc(x, y, x + width, y + height, start=start, extent=extent, fill=color)

def drawImage(canvas, x, y, image_path):
    from tkinter import PhotoImage
    img = PhotoImage(file=image_path)
    return canvas.create_image(x, y, image=img, anchor="nw")
