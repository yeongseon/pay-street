# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false
"""Score topics by estimated engagement potential."""

from ...models.content import ContentTopic

# Weight factors for scoring
EXPERIENCE_WEIGHTS = {
    1: 0.7,
    2: 0.8,
    3: 1.0,
    4: 1.0,
    5: 1.1,
    6: 1.1,
    7: 1.0,
    8: 0.9,
    9: 0.8,
    10: 0.7,
}
HIGH_INTEREST_JOBS = {
    "Backend Developer",
    "Frontend Developer",
    "ML Engineer",
    "Data Engineer",
    "DevOps",
    "백엔드 개발자",
    "프론트엔드 개발자",
}
HIGH_INTEREST_REGIONS = {"Seoul", "Pangyo", "서울", "판교"}


def score_topic(topic: ContentTopic) -> float:
    """Compute an engagement score for a topic (0.0 - 10.0)."""
    score = 5.0

    # Job title interest bonus
    if topic.job_title in HIGH_INTEREST_JOBS:
        score += 1.5

    # Experience sweet spot (3-6 years most engaging)
    exp_weight = EXPERIENCE_WEIGHTS.get(topic.experience_years, 0.6)
    score *= exp_weight

    # Region bonus
    if topic.region in HIGH_INTEREST_REGIONS:
        score += 0.5

    # Company size -- large companies more interesting
    if topic.company_size == "large":
        score += 0.3
    elif topic.company_size == "startup":
        score += 0.2

    return round(min(10.0, max(0.0, score)), 2)


def score_and_update(topic: ContentTopic) -> ContentTopic:
    """Score a topic in-place and return it."""
    topic.score = score_topic(topic)
    return topic
