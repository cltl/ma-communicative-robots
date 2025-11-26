# Image-to-text description
'''
Image Descriptor - Wrapper for BLIP/GPT-4V
'''
class ImageDescriptor:
    def __init__(self, method='blip', api_key=None):
        '''
        method: 'blip', 'blip2', or 'gpt4v'
        '''
        self.method = method
        self.api_key = api_key
        # TODO: Initialize models

    def describe(self, image_array, prompt=None):
        '''Generate description from image'''
        # TODO: Implement
        pass
