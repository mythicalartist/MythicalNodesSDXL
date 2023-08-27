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
from nodes import KSampler

class MythicalPipe:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                     "model": ("MODEL",),
                     "clip": ("CLIP",),
                     "vae": ("VAE",),
                     "positive": ("CONDITIONING",),
                     "negative": ("CONDITIONING",),
                     },
                }

    RETURN_TYPES = ("MYTHICAL_PIPE", )
    RETURN_NAMES = ("mythical_pipe", )
    FUNCTION = "pipe_it"

    CATEGORY = "Mythical/Pipe"

    def pipe_it(self, model, clip, vae, positive, negative):
        pipe = (model, clip, vae, positive, negative)
        return (pipe, )

class MythicalSampler:
    @classmethod
    def INPUT_TYPES(s):
                return {
                    "required":
                    {
                     "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                     "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                     "cfg": ("FLOAT", {"default": 7.0, "min": 0.0, "max": 100.0}),
                     "sampler_name": (comfy.samplers.KSampler.SAMPLERS,),
                     "scheduler": (comfy.samplers.KSampler.SCHEDULERS,),
                     "latent_image": ("LATENT",),
                     "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                        "mythical_pipe": ("MYTHICAL_PIPE",),

                    },
                }
    
    CATEGORY = "Mythical/Sampling"

    RETURN_TYPES = ("MODEL", "CONDITIONING", "CONDITIONING", "LATENT", "VAE", "IMAGE", )
    RETURN_NAMES = ("MODEL", "CONDITIONING+", "CONDITIONING-", "LATENT", "VAE", "IMAGE", )
    OUTPUT_NODE = True
    FUNCTION = "sample"

    def sample(self, mythical_pipe, seed, steps, cfg, sampler_name, scheduler, 
               latent_image, denoise=1.0, prompt=None, add_noise=None, start_at_step=None, end_at_step=None,
               return_with_leftover_noise=None):
        
        model, _, vae, positive, negative = mythical_pipe
        samples = KSampler().sample(model, seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, denoise=denoise)
        latent = samples[0]["samples"]
        decoded_image = vae.decode(latent).cpu()
        return model, positive, negative, {"samples": latent}, vae, decoded_image,


class MythicalSDXLPromptEncoder:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "base_clip": ("CLIP", ),
                    "refiner_clip": ("CLIP", ),
                    "pos_g": ("STRING", {"multiline": True, "default": "POS_G"}),
                    "neg_g": ("STRING", {"multiline": True, "default": "NEG_G"}),
                    "width": ("INT", {"default": 4096, "min": 0, "max": nodes.MAX_RESOLUTION, "step": 8}),
                    "height": ("INT", {"default": 4096, "min": 0, "max": nodes.MAX_RESOLUTION, "step": 8}),
                },
                }

    RETURN_TYPES = ("CONDITIONING", "CONDITIONING", "CONDITIONING", "CONDITIONING", )
    RETURN_NAMES = ("base_positive", "base_negative", "refiner_positive", "refiner_negative", )
    FUNCTION = "encode"

    POS_ASCORE = 6.0
    NEG_ASCORE = 2.5

    CATEGORY = "Mythical/ClipEncoding"

    def encode(self, base_clip, refiner_clip, pos_g, neg_g, width, height):

        """
        This method encodes the given prompts using the base and refiner CLIP models.

        Parameters:
        base_clip (CLIP): The base CLIP model used for encoding.
        refiner_clip (CLIP): The refiner CLIP model used for encoding.
        pos_g (str): The positive prompt for the base model.
        neg_g (str): The negative prompt for the base model.
        width (int): The width of the output image.
        height (int): The height of the output image.

        Returns:
        tuple: A tuple containing the encoded prompts.
        """

        empty = base_clip.tokenize("")

        # positive base prompt
        tokens1 = base_clip.tokenize(pos_g)
        tokens1["l"] = base_clip.tokenize(pos_g)["l"]

        if len(tokens1["l"]) != len(tokens1["g"]):
            while len(tokens1["l"]) < len(tokens1["g"]):
                tokens1["l"] += empty["l"]
            while len(tokens1["l"]) > len(tokens1["g"]):
                tokens1["g"] += empty["g"]

        cond1, pooled1 = base_clip.encode_from_tokens(tokens1, return_pooled=True)
        res1 = [[cond1, {"pooled_output": pooled1, "width": width, "height": height, "crop_w": 0, "crop_h": 0, "target_width": width, "target_height": height}]]

        # negative base prompt
        tokens2 = base_clip.tokenize(neg_g)
        tokens2["l"] = base_clip.tokenize(neg_g)["l"]

        if len(tokens2["l"]) != len(tokens2["g"]):
            while len(tokens2["l"]) < len(tokens2["g"]):
                tokens2["l"] += empty["l"]
            while len(tokens2["l"]) > len(tokens2["g"]):
                tokens2["g"] += empty["g"]

        cond2, pooled2 = base_clip.encode_from_tokens(tokens2, return_pooled=True)
        res2 = [[cond2, {"pooled_output": pooled2, "width": width, "height": height, "crop_w": 0, "crop_h": 0, "target_width": width, "target_height": height}]]


        # positive refiner prompt
        tokens3 = refiner_clip.tokenize(pos_g)
        cond3, pooled3 = refiner_clip.encode_from_tokens(tokens3, return_pooled=True)
        res3 = [[cond3, {"pooled_output": pooled3, "aesthetic_score": MythicalSDXLPromptEncoder.POS_ASCORE, "width": width, "height": height}]]

        # negative refiner prompt
        tokens4 = refiner_clip.tokenize(neg_g)
        cond4, pooled4 = refiner_clip.encode_from_tokens(tokens4, return_pooled=True)
        res4 = [[cond4, {"pooled_output": pooled4, "aesthetic_score": MythicalSDXLPromptEncoder.NEG_ASCORE, "width": width, "height": height}]]

        return (res1, res2, res3, res4, )

class MythicalInputParamaters:
    RETURN_TYPES = (
        "INT",  # image_width
        "INT",  # image_height
        'STRING',  # text_positive
        'STRING',  # text_negative
        comfy.samplers.KSampler.SAMPLERS,
        comfy.samplers.KSampler.SCHEDULERS,
        'INT',
        'INT',
        "FLOAT",
        "FLOAT",
        "INT",
        "PARAMETERS"
    )
    RETURN_NAMES = (
        "image_width", "image_height", 'text_positive', 'text_negative', "sampler_name", "scheduler", "steps",
        "refiner_start_step", "base_cfg", "refiner_cfg", "noise_seed",
        "parameters"
    )
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
                "sampler_name": (comfy.samplers.KSampler.SAMPLERS, {"default": "dpmpp_sde_gpu"}),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS, {"default": "karras"}),
                "steps": ("INT", {"default": 40}),
                "refiner_start_step": ("INT", {"default": 25}),
                "base_cfg": ("FLOAT", {"default": 7.0, "min": 0.0, "max": 30.0, "step": 0.5}),
                "refiner_cfg": ("FLOAT", {"default": 4.0, "min": 0.0, "max": 30.0, "step": 0.5}),
                "noise_seed": ("INT", {"default": 0}),
            }
        }

    def process(self, image_width, image_height, text_positive, text_negative, sampler_name, scheduler, steps,
                refiner_start_step, base_cfg, refiner_cfg, noise_seed):
        parameters = {}
        parameters["image_width"] = image_width
        parameters["image_height"] = image_height
        parameters['text_positive'] = text_positive
        parameters['text_negative'] = text_negative
        parameters["sampler_name"] = sampler_name
        parameters["scheduler"] = scheduler
        parameters["steps"] = steps
        parameters["refiner_start_step"] = refiner_start_step
        parameters["base_cfg"] = base_cfg
        parameters["refiner_cfg"] = refiner_cfg
        parameters["noise_seed"] = noise_seed

        return (
            image_width, image_height, text_positive, text_negative, sampler_name, scheduler, steps, refiner_start_step,
            base_cfg, refiner_cfg, noise_seed,
            parameters)


class MythicalParameterProcessor:
    RETURN_TYPES = (
        "INT", "INT", 'STRING', 'STRING', comfy.samplers.KSampler.SAMPLERS, comfy.samplers.KSampler.SCHEDULERS, 'INT',
        'INT', "FLOAT", "FLOAT", "INT",
        "PARAMETERS")
    RETURN_NAMES = (
        "image_width", "image_height", 'text_positive', 'text_negative', "sampler_name", "scheduler", "steps",
        "refiner_start_step", "base_cfg", "refiner_cfg", "noise_seed",
        "parameters")
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
            parameters['text_negative'], parameters["sampler_name"], parameters["scheduler"], parameters["steps"],
            parameters["refiner_start_step"], parameters["base_cfg"], parameters["refiner_cfg"], parameters["noise_seed"],
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
        return (sampler_name, scheduler)


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
    "MythicalPipe": MythicalPipe,
    "MythicalSampler": MythicalSampler,
    "MythicalSDXLPromptEncoder": MythicalSDXLPromptEncoder,
    "MythicalInputParamaters": MythicalInputParamaters,
    "MythicalParameterProcessor": MythicalParameterProcessor,
    "MythicalWidthHeight": MythicalWidthHeight,
    "MythicalSamplerScheduler": MythicalSamplerScheduler,
}

# Human readable names for the nodes

NODE_DISPLAY_NAME_MAPPINGS = {
    "MythicalPipe": "Mythical Pipe",
    "MythicalSampler": "All in one Sampler",
    "MythicalSDXLPromptEncoder": "Simplified Prompt Encoder",
    "MythicalInputParamaters": "Input Parameters",
    "MythicalParameterProcessor": "Parameter Processor",
    "MythicalWidthHeight": "Width and height input",
    "MythicalSamplerScheduler": "Sampler scheduler input",

}
