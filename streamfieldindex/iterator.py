from wagtail import blocks


def flatten_block(block, path=None):
    if path is None:
        path = []

    yield (block, path)

    if isinstance(block.block, blocks.StructBlock):
        for sub_block_type, sub_block in block.value.bound_blocks.items():
            yield from flatten_block(sub_block, path=path + [sub_block_type])
    if isinstance(block.block, blocks.StreamBlock):
        for i, sub_block in enumerate(block.value):
            yield from flatten_block(sub_block, path=path + [str(i), sub_block.block.name])
    if isinstance(block.block, blocks.ListBlock):
        for i, item in enumerate(block.value):
            sub_block = block.block.child_block
            bound_block = blocks.BoundBlock(sub_block, item)
            yield from flatten_block(bound_block, path=path + [str(i)])


def flatten_streamfield(streamvalue):
    """Generator function which yields (block, path) where `block` is a bound block and `path` is a list of
    stream block names and integers defining where the block is positioned in the streamvalue.
    """

    for i, block in enumerate(streamvalue):
        yield from flatten_block(block, path=[str(i), block.block.name])
