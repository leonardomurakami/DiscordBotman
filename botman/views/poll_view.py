import hikari
import miru

from typing import List, Dict


class PollView(miru.View):
    def __init__(self, question: str, choices: List[str], timeout: int = 600):
        super().__init__(timeout=timeout)
        self.question = question
        self.choices = choices
        self.votes: Dict[str, List[int]] = {choice: [] for choice in choices}
        
    def build_embed(self) -> hikari.Embed:
        total_votes = sum(len(voters) for voters in self.votes.values())
        
        embed = hikari.Embed(
            title="📊 " + self.question,
            color=hikari.Color(0x9b59b6)
        )
        
        for idx, choice in enumerate(self.choices):
            vote_count = len(self.votes[choice])
            percentage = (vote_count / total_votes * 100) if total_votes > 0 else 0
            
            # Create a visual bar using filled and empty blocks
            blocks = 20  # Total number of blocks for 100%
            filled_blocks = int((percentage / 100) * blocks)
            bar = "█" * filled_blocks + "░" * (blocks - filled_blocks)
            
            embed.add_field(
                name=f"Option {idx + 1}: {choice}",
                value=f"```\n{bar} {percentage:.1f}% ({vote_count} votes)\n```",
                inline=False
            )
            
        embed.set_footer(text=f"Total votes: {total_votes}")
        return embed
    
    async def handle_vote(self, ctx: miru.ViewContext, choice_idx: int) -> None:
        choice = self.choices[choice_idx]
        user_id = ctx.user.id
        
        # Remove user's previous votes
        for voters in self.votes.values():
            if user_id in voters:
                voters.remove(user_id)
        
        # Add new vote
        self.votes[choice].append(user_id)
        
        # Update the embed
        await ctx.message.edit(embed=self.build_embed())
        await ctx.respond(
            f"You voted for: {choice}",
            flags=hikari.MessageFlag.EPHEMERAL
        )

class PollButton(miru.Button):
    def __init__(self, idx: int, choice: str):
        super().__init__(
            label=f"Option {idx + 1}",
            custom_id=f"poll_{idx}",
            style=hikari.ButtonStyle.PRIMARY
        )
        self.choice_idx = idx
        
    async def callback(self, ctx: miru.ViewContext) -> None:
        await self.view.handle_vote(ctx, self.choice_idx)