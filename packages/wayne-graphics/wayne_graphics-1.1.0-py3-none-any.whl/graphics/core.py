import tkinter as tk
from graphics import events

class WayneGraphics:
    def __init__(self, width=400, height=400, title="Wayne Graphics"):
        self.root = tk.Tk()
        self.root.title(title)
        self.canvas = tk.Canvas(self.root, width=width, height=height)
        self.canvas.pack()

    # Mouse Events
    def onMousePress(self, func): events.onMousePress(self.canvas, func)
    def onMouseRelease(self, func): events.onMouseRelease(self.canvas, func)
    def onMouseDrag(self, func): events.onMouseDrag(self.canvas, func)
    def onMouseMove(self, func): events.onMouseMove(self.canvas, func)
    def onMouseEnter(self, func): events.onMouseEnter(self.canvas, func)
    def onMouseLeave(self, func): events.onMouseLeave(self.canvas, func)
    def onRightClick(self, func): events.onRightClick(self.canvas, func)
    def onMiddleClick(self, func): events.onMiddleClick(self.canvas, func)
    def onScroll(self, func): events.onScroll(self.canvas, func)

    # Keyboard Events
    def onKeyPress(self, func): events.onKeyPress(self.root, func)
    def onKeyRelease(self, func): events.onKeyRelease(self.root, func)

    # Animation / Frame Updates
    def onStep(self, func, delay=33): events.onStep(self.root, func, delay)

    # Custom Binding
    def bind(self, event, func): events.bind(self.canvas, event, func)

    # Run the app
    def run(self): self.root.mainloop()
