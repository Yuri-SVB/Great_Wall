from datetime import datetime, timezone
from typing import Any, Optional

# from fsrs import FSRS, Card, Rating, State


class MemoCard:
    """A card that contains knowledge and implements spaced repetition algorithm."""

    def __init__(self, knowledge) -> None:
        self._knowledge = knowledge
        self._algorithm = FSRS()
        self._card = Card()
        self._log = None

    def rate_card(self, rating: str):
        """Review the card knowledge now and rate it.

        Args:
            rating (str): The rate of the card knowledge. It can take rate values
                'again', 'hard', 'good' and 'easy'.
        """
        now = datetime.now(timezone.utc)
        rates = {
            "again": Rating.Again,
            "hard": Rating.Hard,
            "good": Rating.Good,
            "easy": Rating.Easy,
        }

        scheduling_cards = self._algorithm.repeat(self._card, now)
        self._card = scheduling_cards[rates[rating]].card
        self._log = scheduling_cards[rates[rating]].review_log

    @property
    def knowledge(self) -> Any:
        return self._knowledge

    @property
    def due(self) -> Optional[datetime]:
        return self._card.due

    @property
    def state(self) -> Optional[int]:
        if self._log:
            return self._log.state
        else:
            return State.New

    def __str__(self) -> str:
        return (
            "Memorization Card for Knowledge: {}; with state: {} and due at: {}.".format(
                self.knowledge, self.state, self.due
            )
        )

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(knowledge={self.knowledge})"
