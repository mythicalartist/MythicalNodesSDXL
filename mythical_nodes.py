"""

Custom nodes for SDXL in ComfyUI

MIT License

Copyright (c) 2023 Mythical_Artist

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""
import nodes

class MythicalWidthHeight:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "image_width": ("INT", {"default": 1024, "min": 0, "max": nodes.MAX_RESOLUTION, "step": 8}),
                    "image_height": ("INT", {"default": 1024, "min": 0, "max": nodes.MAX_RESOLUTION, "step": 8}),
                    },
                }

    RETURN_TYPES = ("INT", "INT", )
    RETURN_NAMES = ("image_width", "image_height",)
    FUNCTION = "mux"

    def mux(self, image_width, image_height):
        return (image_width, image_height)

NODE_CLASS_MAPPINGS = {
    "MythicalWidhtHeightTuple": MythicalWidthHeight,
}


# Human readable names for the nodes

NODE_DISPLAY_NAME_MAPPINGS = {
     "MythicalWidthHeight": "A simple width and height input",
}
