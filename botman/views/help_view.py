import hikari
import miru

from typing import List


class HelpView(miru.View):
    def __init__(self, embeds: List[hikari.Embed], labels: List[str], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.embeds = embeds
        self.labels = labels
        self.current_page = 0
        
        # Create the select menu
        select = miru.TextSelect(
            placeholder="Select a page...",
            options=[
                miru.SelectOption(
                    label=label,
                    value=label,
                    description=f"Go to {label} page"
                )
                for label in labels
            ],
            row=0
        )
        
        # Add the select menu to the view
        self.add_item(select)

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

    async def select_callback(self, ctx: miru.ViewContext, select: miru.TextSelect) -> None:
        # Update current page based on selection
        selected_index = self.labels.index(select.values[0])
        self.current_page = selected_index
        
        # Update the message with the new embed
        await ctx.edit_response(
            embed=self.embeds[self.current_page],
            components=self.build()
        )
