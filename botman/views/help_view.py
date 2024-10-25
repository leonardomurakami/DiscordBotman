import hikari
import miru

from typing import List


class HelpView(miru.View):
    def __init__(self, embeds: List[hikari.Embed], labels: List[str], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.embeds = embeds
        self.labels = labels
        self.current_page = 0

    @miru.text_select(
        placeholder="Select a page...",
        options=[],
        row=0
    )
    async def select_page(self, ctx: miru.ViewContext, select: miru.TextSelect) -> None:
        # Update current page based on selection
        selected_index = self.labels.index(select.values[0])
        self.current_page = selected_index
        await self.update_message(ctx)

    async def update_message(self, ctx: miru.ViewContext) -> None:
        await ctx.edit_response(
            embed=self.embeds[self.current_page],
            components=self.build()
        )

    def __init__(self, embeds: List[hikari.Embed], labels: List[str], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.embeds = embeds
        self.labels = labels
        self.current_page = 0
        
        # Set the options for the select menu
        self.select_page.options = [
            miru.SelectOption(
                label=label,
                value=label,  # Using label as value for simplicity
                description=f"Go to {label} page"
            )
            for label in labels
        ]
