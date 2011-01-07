## Adapters to and from different data structures

class MomentumDataAdapter(object):

        def encode(self, *args, **kwargs):
            raise NotImplementedError('Encoding functionality cannot be used on an abstract MomentumDataAdapter.')

        def decode(self, *args, **kwargs):
            raise NotImplementedError('Decoding functionality cannot be used on an abstract MomentumDataAdapter.')