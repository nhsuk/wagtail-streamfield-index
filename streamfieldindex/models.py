from django.db import models
from django.urls import reverse
from wagtail.blocks import ListBlock, StreamBlock, StructBlock


class BlockTypes:
    OTHER = 0
    STRUCT = 1
    STREAM = 2
    LIST = 3


class IndexEntry(models.Model):

    BLOCK_TYPE_CHOICES = [(BlockTypes.OTHER, "Other"), (BlockTypes.STRUCT, "Struct"), (BlockTypes.STREAM, "Stream")]

    block_name = models.CharField(max_length=255)
    block_type = models.IntegerField(choices=BLOCK_TYPE_CHOICES)
    block_value = models.TextField(blank=True)
    block_path = models.TextField()
    field_name = models.CharField(max_length=255)

    page = models.ForeignKey("wagtailcore.Page", on_delete=models.CASCADE)

    def get_edit_url(self):
        return reverse("wagtailadmin_pages:edit", args=[self.page.id])

    def get_bound_block(self):
        field_value = getattr(self.page.specific, self.field_name)
        path = self.block_path.split("/")

        def get_sub_block(bound_block, path_list):
            if len(path_list) == 0:
                return bound_block

            path_item = path_list.pop(0)  # Pop the first element
            if isinstance(bound_block.block, ListBlock):
                index = int(path_item)
                next_block = bound_block.block.child_block.bind(bound_block.value[index])
                return get_sub_block(next_block, path_list)
            elif isinstance(bound_block.block, StructBlock):
                next_block = bound_block.value.bound_blocks[path_item]
                return get_sub_block(next_block, path_list)
            elif isinstance(bound_block.block, StreamBlock):
                index = int(path_item)
                path_list.pop(0)  # We can throw away the next path as it is just the block_type which we don't need
                next_block = bound_block.value[index]
                return get_sub_block(next_block, path_list)
            else:
                raise ValueError(f"We don't know how to iterate over block type {type(bound_block.block)}")

        first_index = path.pop(0)  # The first index must always be a number, since it is a streamfield
        path.pop(0)  # We can throw away the next path as it is just the block_type which we don't need
        block = field_value[int(first_index)]
        return get_sub_block(block, path)

    def __str__(self):
        return f"Streamfield index: {self.page.title} {self.field_name} {self.block_path}"  # noqa E231

    class Meta:
        verbose_name_plural = "Index Entries"
