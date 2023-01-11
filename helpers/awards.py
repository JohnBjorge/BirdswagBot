import logging


logger = logging.getLogger(__name__)


# todo: see query notes for this stuff, I think it makes sense to make an award table
#  essentially a scoreboard for all awards, just need to filter on year/week or year/quarter or year
#  need to be careful about how week_of_year rolls over years/quarters and how that could impact counts
async def award_weekly(self):
    # todo: put embed here
    #  weekly shoutouts on Sunday (Query #1)
    #         list all users that have more than half of days over the last week with some activity
    #             consider ordering them by sum(difficulty) for a twinge of competitiveness
    await self.bot.get_channel(1045906913080115225).send("This is a weekly goal trigger")


async def award_quarterly(self):
    # todo: put embed here
    #  weekly badge - consistency (need name for award), if 4+ days activity every week in given quarter
    await self.bot.get_channel(1045906913080115225).send("This is a quarterly goal trigger")


async def award_yearly(self):
    # todo: put embed here
    #  yearly badge - consistency (need name for award), if all 4 quarters in given year "consistent"
    await self.bot.get_channel(1045906913080115225).send("This is a yearly goal trigger")

