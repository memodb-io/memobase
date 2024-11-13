def tag_strings_in_order_xml(
    strings: list[str], tag_name: str = "doc", index_offset: int = 0
):
    return "\n".join(
        f"<{tag_name} data_index={i+index_offset}>\n{s}\n</{tag_name}>"
        for i, s in enumerate(strings)
    )
