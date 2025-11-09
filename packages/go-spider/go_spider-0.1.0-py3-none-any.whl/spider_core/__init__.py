"""
Spider implementations: basic, stealth, and goal-oriented variants.
"""
from spider_core.spiders.basic_spider import BasicSpider
from spider_core.spiders.stealth.stealth_spider import StealthSpider
try:
    from spider_core.spiders.goal_spider import GoalOrientedSpider
except ImportError:
    GoalOrientedSpider = None

__all__ = ["BasicSpider", "StealthSpider", "GoalOrientedSpider"]
