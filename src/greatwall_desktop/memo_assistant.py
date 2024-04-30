from fsrs import Card, FSRS, Rating, State
from datetime import datetime


memo_algorithm = FSRS()
card = Card()

now = datetime.utcnow()
scheduling_cards = memo_algorithm.repeat(card, now)

print(card)
print(scheduling_cards)

card = scheduling_cards[Rating.Again].card
review_log = scheduling_cards[Rating.Good].review_log
print(review_log.state)
print(card.due)


class MeomCard():

    def __init__(self) -> None:
        memo_algorithm = FSRS()
        card = Card()


