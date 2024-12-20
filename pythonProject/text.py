from manim import *


class Text(Scene):
    def construct(self):
        background = NumberPlane()
        self.play(Create(background))
        x_range = [-10, 10]
        t = ValueTracker(0)

        def func(x):
            return # USER_FUNCTION_PLACEHOLDER

        self.wait()
        graph = background.plot(func, x_range=x_range)
        self.play(FadeIn(graph))
        self.wait(3)