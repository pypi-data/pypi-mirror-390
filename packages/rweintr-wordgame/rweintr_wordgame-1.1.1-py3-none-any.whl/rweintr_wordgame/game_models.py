# game_models.py
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Player(Base):
    __tablename__ = "players"

    player_id: Mapped[int] = mapped_column(primary_key=True)
    alias: Mapped[str]
    start_dt: Mapped[str]

    games: Mapped[list["Game"]] = relationship(back_populates="player",
        cascade="all, delete-orphan")

    def __repr__(self):
        return (
            f"Player(player_id={self.player_id!r}, "
            f"alias={self.alias!r}, "
            f"start date={self.start_dt!r})"
	)

class Game(Base):
    __tablename__ = "games"

    game_id: Mapped[int] = mapped_column(primary_key=True)
    score: Mapped[int]
    play_dt: Mapped[str]
    player_id: Mapped[int] = mapped_column(ForeignKey("players.player_id"),
        nullable=False)

    player: Mapped["Player"] = relationship(back_populates="games")

    def __repr__(self):
        return (
            f"Game(game_id={self.game_id!r}, "
            f"score={self.score!r}, "
            f"date played={self.play_dt!r}, "
            f"player_id={self.player_id!r})"
	)