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
import comfy.samplers


class MythicalInputParamaters:
    RETURN_TYPES = (
        "INT", "INT", 'STRING', 'STRING', comfy.samplers.KSampler.SAMPLERS, comfy.samplers.KSampler.SCHEDULERS,
        "PARAMETERS")
    RETURN_NAMES = (
        "image_width", "image_height", 'text_positive', 'text_negative', "sampler_name", "scheduler", "parameters")
    FUNCTION = "process"

    CATEGORY = "Mythical/UI/Inputs"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_width": ("INT", {"default": 1024, "min": 0, "max": nodes.MAX_RESOLUTION, "step": 8}),
                "image_height": ("INT", {"default": 1024, "min": 0, "max": nodes.MAX_RESOLUTION, "step": 8}),
                "text_positive": ("STRING", {"default": "", "multiline": True}),
                "text_negative": ("STRING", {"default": "", "multiline": True}),
                "sampler_name": (comfy.samplers.KSampler.SAMPLERS,),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS,)}
        }

    def process(self, image_width, image_height, text_positive, text_negative, sampler_name, scheduler):
        parameters = {}
        parameters["image_width"] = image_width
        parameters["image_height"] = image_height
        parameters['text_positive'] = text_positive
        parameters['text_negative'] = text_negative
        parameters["sampler_name"] = sampler_name
        parameters["scheduler"] = scheduler
        return (image_width, image_height, text_positive, text_negative, sampler_name, scheduler, parameters)


class MythicalParameterProcessor:
    RETURN_TYPES = (
    "INT", "INT", 'STRING', 'STRING', comfy.samplers.KSampler.SAMPLERS, comfy.samplers.KSampler.SCHEDULERS,
    "PARAMETERS")
    RETURN_NAMES = (
        "image_width", "image_height", 'text_positive', 'text_negative', "sampler_name", "scheduler", "parameters")
    FUNCTION = "process"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "parameters": ("PARAMETERS",),
            },
        }

    CATEGORY = "Mythical/UI/Inputs"

    def process(self, parameters):
        print(f"Received: {parameters}")
        return (
            parameters["image_width"], parameters["image_height"], parameters['text_positive'],
            parameters['text_negative'], parameters["sampler_name"], parameters["scheduler"],
            parameters
        )


class MythicalSamplerScheduler:
    RETURN_TYPES = (comfy.samplers.KSampler.SAMPLERS, comfy.samplers.KSampler.SCHEDULERS,)
    RETURN_NAMES = ("sampler_name", "scheduler",)
    FUNCTION = "get_names"

    CATEGORY = "Mythical/UI/Inputs"

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"sampler_name": (comfy.samplers.KSampler.SAMPLERS,),
                             "scheduler": (comfy.samplers.KSampler.SCHEDULERS,)}}

    def get_names(self, sampler_name, scheduler):
        return (image_width, image_height, sampler_name, scheduler)


class MythicalWidthHeight:
    RETURN_TYPES = ("INT", "INT",)
    RETURN_NAMES = ("image_width", "image_height",)
    FUNCTION = "mux"

    CATEGORY = "Mythical/UI/Inputs"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image_width": ("INT", {"default": 1024, "min": 0, "max": nodes.MAX_RESOLUTION, "step": 8}),
                "image_height": ("INT", {"default": 1024, "min": 0, "max": nodes.MAX_RESOLUTION, "step": 8}),
            },
        }

    def mux(self, image_width, image_height):
        return (image_width, image_height)


NODE_CLASS_MAPPINGS = {
    "MythicalInputParamaters": MythicalInputParamaters,
    "MythicalParameterProcessor": MythicalParameterProcessor,
    "MythicalWidthHeight": MythicalWidthHeight,
    "MythicalSamplerScheduler": MythicalSamplerScheduler,
}

# Human readable names for the nodes

NODE_DISPLAY_NAME_MAPPINGS = {
    "MythicalInputParamaters": "Input Parameters",
    "MythicalParameterProcessor": "Parameter Processor",
    "MythicalWidthHeight": "Width and height input",
    "MythicalSamplerScheduler": "Sampler scheduler input",

}
