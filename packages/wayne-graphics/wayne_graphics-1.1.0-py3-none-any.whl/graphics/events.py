def onMousePress(canvas, func):
    canvas.bind("<Button-1>", lambda e: func(e.x, e.y))

def onMouseRelease(canvas, func):
    canvas.bind("<ButtonRelease-1>", lambda e: func(e.x, e.y))

def onMouseDrag(canvas, func):
    canvas.bind("<B1-Motion>", lambda e: func(e.x, e.y))

def onMouseMove(canvas, func):
    canvas.bind("<Motion>", lambda e: func(e.x, e.y))

def onMouseEnter(canvas, func):
    canvas.bind("<Enter>", lambda e: func(e.x, e.y))

def onMouseLeave(canvas, func):
    canvas.bind("<Leave>", lambda e: func(e.x, e.y))

def onRightClick(canvas, func):
    canvas.bind("<Button-3>", lambda e: func(e.x, e.y))

def onMiddleClick(canvas, func):
    canvas.bind("<Button-2>", lambda e: func(e.x, e.y))

def onScroll(canvas, func):
    canvas.bind("<MouseWheel>", lambda e: func(e.delta))

def onKeyPress(root, func):
    root.bind("<KeyPress>", lambda e: func(e.char))

def onKeyRelease(root, func):
    root.bind("<KeyRelease>", lambda e: func(e.char))

def onStep(root, func, delay=33):
    def step():
        func()
        root.after(delay, step)
    root.after(delay, step)

def bind(widget, event, func):
    widget.bind(event, func)
