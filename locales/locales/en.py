class Messages:
    server_description = (
        "https://discord.gg/UntitledCharts\nThe official UntitledCharts custom server!"
    )

    def item_not_found(item: str, name: str) -> str:
        return f'{item} item "{name}" not found.'

    def item_type_not_found(item: str) -> str:
        return f'Item "{item}" not found.'

    def items_not_found(item: str) -> str:
        return f"Could not find any {item}."

    def items_not_found_search(item: str) -> str:
        return f"Could not find any {item} matching your search."
