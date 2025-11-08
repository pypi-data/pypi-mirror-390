#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# mk2lib - Machi Koro 2 Game Engine
# Copyright (C) 2025  Vitaly Ostrosablin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Event dataclasses - purely informational objects for game flow tracking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .player import Player
    from .const import GameState
    from .mk2deck import Card, Establishment, Landmark
    from .dice import Dice


class Event:
    """
    Base class for all Events.
    """


@dataclass(frozen=True)
class GameCreated(Event):
    """
    New game is created.
    """

    owner: Player


@dataclass(frozen=True)
class GameStarted(Event):
    """
    New game is created.
    """

    owner: Player
    turn_order: list[Player]
    use_promo: bool
    randomize_players: bool


@dataclass(frozen=True)
class PlayerJoined(Event):
    """
    Player has joined game.
    """

    player: Player


@dataclass(frozen=True)
class PlayerLeft(Event):
    """
    Player has left game.
    """

    player: Player
    initiator: Player
    during_game: bool = False


@dataclass(frozen=True)
class DiceRolled(Event):
    """
    Player rolls dice.
    """

    player: Player
    dice: Dice


@dataclass(frozen=True)
class StateSwitch(Event):
    """
    Game state changes from A to B.
    """

    prev_state: GameState
    new_state: GameState


@dataclass(frozen=True)
class MoneyTaken(Event):
    """
    Player A takes money from player B (possibly not in full amount, if any).
    """

    reason: Card
    from_user: Player
    to_user: Player
    owed: int
    taken: int


@dataclass(frozen=True)
class MoneyEarned(Event):
    """
    Player gets money from bank.
    """

    reason: Card
    user: Player
    earned: int


@dataclass(frozen=True)
class MoneyDivided(Event):
    """
    Money was evenly distributed among the players (possibly rounding up from bank).
    """

    reason: Card
    players: int
    total_coins: int
    from_bank: int
    coins: int


@dataclass(frozen=True)
class GetOneCoinBecauseHadNoMoney(Event):
    """
    At the start of build phase, player received 1 coin, because he had none.
    """

    user: Player


@dataclass(frozen=True)
class TurnBegins(Event):
    """
    Next turn begins.
    """

    extra: bool
    turn_number: int
    round_number: int
    initial: int
    player: Player


@dataclass(frozen=True)
class TurnSkipped(Event):
    """
    Player skips turn.
    """

    player: Player


@dataclass(frozen=True)
class DealtCardsToMarket(Event):
    """
    New cards were dealt to market.
    """

    cards: list[Card] = field(default_factory=list)
    initial: bool = False


@dataclass(frozen=True)
class CardBuilt(Event):
    """
    Player has built a new card.
    """

    buyer: Player
    card: Card
    price_paid: int


@dataclass(frozen=True)
class SkipBuild(Event):
    """
    Player skips the build phase.
    """

    player: Player
    cannot_buy: bool = False


@dataclass(frozen=True)
class CanBuild(Event):
    """
    Player can build something in build phase.
    """

    player: Player
    build_options: list[Card]


@dataclass(frozen=True)
class GetExtraTurn(Event):
    """
    Player gets an extra turn.
    """

    player: Player
    no_effect: bool


@dataclass(frozen=True)
class NewLandmarkEffectActivated(Event):
    """
    New landmark effect activates.
    """

    landmark: Landmark
    builder_only: bool = False


@dataclass(frozen=True)
class MustGiveEstablishment(Event):
    """
    Player must give some establishment to previous player.
    """

    from_user: Player
    to_user: Player


@dataclass(frozen=True)
class CanExchangeEstablishments(Event):
    """
    Player can exchange establishments with another player.
    """

    player: Player


@dataclass(frozen=True)
class SkipExchangeEstablishments(Event):
    """
    Player has decided not to exchange establishments.
    """

    player: Player


@dataclass(frozen=True)
class CannotExchangeWithSelf(Event):
    """
    Player has attempted to exchange establishments with self.
    """

    player: Player


@dataclass(frozen=True)
class EstablishmentGiven(Event):
    """
    Establishment was given to player.
    """

    from_user: Player
    to_user: Player
    establishment: Establishment


@dataclass(frozen=True)
class EstablishmentExchanged(Event):
    """
    Players have exchanged establishments.
    """

    from_user: Player
    to_user: Player
    establishment_given: Establishment
    establishment_taken: Establishment


@dataclass(frozen=True)
class OwnerChanged(Event):
    """
    Old owner left a game in progress.
    """

    oldowner: Player
    newowner: Player


@dataclass(frozen=True)
class GameEnded(Event):
    """
    Game finished.
    """

    player: Player
    finished: bool = False
    launch_pad: bool = False
    cancelled: bool = False
    owner_left: bool = False
    not_enough_players: bool = False


@dataclass(frozen=True)
class FinalScores(Event):
    """
    Scores at the time of game end.
    """

    scores: dict[int, list[Player]]
    finished: bool = True


class ErrorEvent(Event):
    """
    Base class for error events.
    """


@dataclass(frozen=True)
class WrongState(ErrorEvent):
    """
    Emitted when action is attempted in wrong state.
    """

    expected_state: GameState
    current_state: GameState


@dataclass(frozen=True)
class NotYourTurn(ErrorEvent):
    """
    Emitted when action is attempted during another player's turn.
    """

    expected_player: Player
    moved_player: Player


@dataclass(frozen=True)
class NotInGame(ErrorEvent):
    """
    Emitted when action is attempted by player who's not in current game.
    """

    player_id: int


@dataclass(frozen=True)
class GameInProgress(ErrorEvent):
    """
    Emitted when action is attempting to join a game in progress.
    """

    player_id: int


@dataclass(frozen=True)
class NoGameInProgress(ErrorEvent):
    """
    Emitted when action is attempted on already finished game.
    """

    player: Player


@dataclass(frozen=True)
class CardUnavailable(ErrorEvent):
    """
    Emitted on attempt to build a card that's not currently available.

    If card is technically available on market, but rules don't allow purchasing
    it - prohibited would be set to True.
    """

    buyer: Player
    card_name: str
    prohibited: bool = False


@dataclass(frozen=True)
class NotEnoughMoney(ErrorEvent):
    """
    Emitted on attempt to build a card with insufficient coins.
    """

    buyer: Player
    card_name: str
    card_price: int


@dataclass(frozen=True)
class PlayerHasNoSuchCard(ErrorEvent):
    """
    Emitted on attempt to give/take a card that's not in player's possession.
    """

    player: Player
    card_name: str
    current: bool


@dataclass(frozen=True)
class AlreadyInGame(ErrorEvent):
    """
    Emitted when player who's already in room tries to join again.
    """

    player: Player


@dataclass(frozen=True)
class RoomIsFull(ErrorEvent):
    """
    Emitted when attempting to join a game with 5 joined players.
    """

    player_id: int


@dataclass(frozen=True)
class NotEnoughPlayers(ErrorEvent):
    """
    Emitted when attempting to start a game with less than 2 players.
    """

    player: Player


@dataclass(frozen=True)
class OnlyOwnerOperation(ErrorEvent):
    """
    Emitted when attempted to do an owner-only operation.

    Also returns inactivity timeout state.
    """

    owner: Player
    user: Player
    inactivity_remains: float
