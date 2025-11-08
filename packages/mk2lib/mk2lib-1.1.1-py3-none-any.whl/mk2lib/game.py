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
Main Machi Koro 2 game class.
"""
from __future__ import annotations

import random
from dataclasses import replace
from queue import SimpleQueue
from time import time
from typing import Iterator, cast

from mk2lib.const import (
    INACTIVITY_TIMEOUT,
    ActivationOrder,
    Effect,
    BOOST_ONE_COIN_EFFECTS,
    GameState,
)
from .cards import Card, Establishment, Landmark
from .dice import Dice
from .effects import TakeFromAllOpponents, ExtraTurn
from .events import (
    DiceRolled,
    NotYourTurn,
    StateSwitch,
    WrongState,
    Event,
    TurnBegins,
    SkipBuild,
    CanBuild,
    MoneyEarned,
    MustGiveEstablishment,
    GetOneCoinBecauseHadNoMoney,
    GameCreated,
    AlreadyInGame,
    RoomIsFull,
    PlayerJoined,
    OnlyOwnerOperation,
    GameStarted,
    PlayerHasNoSuchCard,
    SkipExchangeEstablishments,
    EstablishmentExchanged,
    EstablishmentGiven,
    CannotExchangeWithSelf,
    NotInGame,
    NotEnoughPlayers,
    GameInProgress,
    GameEnded,
    NoGameInProgress,
    FinalScores,
    PlayerLeft,
    TurnSkipped,
    OwnerChanged,
)
from .mk2deck import Market, ALL_CARDS
from .player import Player, PlayerType


class MachiKoroGame:
    """
    Machi Koro 2 Game implementation.
    """

    def __init__(self, owner: int):
        """
        Create a new game.

        :param owner: ID of player who created game.
        """
        self.players: list[Player] = [Player(player_id=owner)]
        self.player_map: dict[int, Player] = {owner: self.players[0]}
        self.current_player: int = 0
        self.state: GameState = GameState.NOT_STARTED
        self.market: None | Market = None
        self.owner_id: int = owner
        self.turn: int = 0
        self.round: int = 1
        self.use_promo: bool = True
        self.randomize_players: bool = True
        self.dice: Dice | None = None
        self.last_op: float = time()
        self.events: SimpleQueue[Event] = SimpleQueue()  # Primary event bus
        self.active_effects: dict[Effect, Landmark] = {}
        self.emit_event(GameCreated(owner=self.players[0]))  # Game is ready.

    # Event bus management

    def emit_event(self, event: Event) -> None:
        """
        Put a new event into event queue.

        :param event: Event that's being emitted.
        :return None:
        """
        self.events.put(event)

    # Card effect helpers

    def is_player_eligible_for_loan_office(self, player: Player) -> bool:
        """
        Check if player can buy loan office. He must be only one without landmarks.

        :param player: Player, for whom condition is checked.
        :return: Whether player is only one without landmarks & can build loan office.
        """
        for plr in self.players:
            if plr is player and plr.landmarks:
                # Player already has landmarks - cannot buy loan office.
                # Should not really happen, because if player has landmarks - build
                # wouldn't list Loan Office, as it has undefined 2nd and 3rd landmark
                # price.
                return False  # pragma: no cover
            if plr is not player and not plr.landmarks:
                # Another player doesn't have landmarks - cannot buy loan office.
                return False
        return True

    def get_gain_modifier(self, card: Card) -> int:
        """
        Check for active landmark effects that increase card's yield.

        :param card: Card that we're checking.
        :return: Yield delta that must be added to card's income value.
        """
        if isinstance(card, Establishment):
            if (effect := BOOST_ONE_COIN_EFFECTS.get(card.category)) is not None:
                return 1 if effect in self.active_effects else 0
        return 0

    # State machine management

    def _switch_state(self, new_state: GameState) -> None:
        """
        Switch game to a new state and emit event.

        :param new_state: New state that we're entering.
        :return: None.
        """
        if new_state == self.state:
            return
        self.emit_event(StateSwitch(self.state, new_state))
        self.state = new_state
        self.last_op = time()

    def is_owner_or_timeout(self, player: PlayerType) -> bool:
        """
        Check if player is owner or inactivity timeout has hit.

        :param player: Player, who attempts action.
        :return: Boolean, indicating whether privileged action is allowed.
        """
        if player := self._get_player_object(player):
            if player.player_id == self.owner_id:
                return True
            now_time = time()
            if (now_time - self.last_op) >= INACTIVITY_TIMEOUT:
                return True
            self.emit_event(
                OnlyOwnerOperation(
                    owner=self._get_owner(),
                    user=player,
                    inactivity_remains=INACTIVITY_TIMEOUT - (now_time - self.last_op),
                )
            )
        return False

    def is_owner_self_or_timeout(self, player: PlayerType, target: PlayerType) -> bool:
        """
        Check if player is owner, targets himself or inactivity timeout has hit.

        This check is particularly useful for kick, which can be invoked not only by
        admin, but also by player himself (to leave the game).

        :param player: Player who invokes action.
        :param target: Player, targeted by action.
        :return: Boolean, indicating whether privileged action is allowed.
        """
        if player := self._get_player_object(player):
            if target := self._get_player_object(target):
                if player is target:
                    return True
                return self.is_owner_or_timeout(player)
        return False

    def _expect_state(self, target_state: GameState) -> bool:
        """
        Action expects that game is in specified state.

        If not, an error event would be generated.

        :param target_state: Current expected game state.
        :return: Whether game is now in expected state.
        """
        if self.state != target_state:
            self.emit_event(WrongState(target_state, self.state))
            return False
        return True

    def _expect_current_player(self, player: Player) -> bool:
        """
        Action expects that it's invoked by current player only.

        :param player: Player who attempts action.
        :return: Whether player is current player.
        """
        if self._get_current_player() != player:
            self.emit_event(NotYourTurn(self._get_current_player(), player))
            return False
        return True

    def _expect_state_and_player(self, player: Player, target_state: GameState) -> bool:
        """
        Action expects that it's invoked strictly in certain state by current player.

        :param player: Player who attempts action.
        :param target_state: Current expected game state.
        :return: Whether game state is right and it's player's turn now.
        """
        if not self._expect_current_player(player):
            return False
        if not self._expect_state(target_state):
            return False
        return True

    # Player object management and traversal

    def _get_current_player(self) -> Player:
        """
        Get current player's object.

        :return: Current player object.
        """
        return self.players[self.current_player]

    def _get_owner(self) -> Player:
        """
        Get game owner's player object.

        :return: Game owner's player object.
        """
        return self.player_map[self.owner_id]

    def _get_player_object(self, player: PlayerType) -> Player | None:
        """
        Get player's object.

        If None is passed - current player is returned.
        If player ID is passed - matching player object is taken.
        Player object would be just returned intact.

        :param player: None, player ID or player object.
        :return: Player object.
        """
        if player is None:
            return self._get_current_player()
        if isinstance(player, int):
            obj = self.player_map.get(player)
            if obj is None:
                self.emit_event(NotInGame(player))
            return obj
        return player

    def _remove_player(self, initiator: Player, target: Player) -> None:
        """
        Remove player from game on behalf of initiator.

        Removal logic in the lobby:
        -If owner leaves the lobby - game is cancelled.
        -If owner kicks someone - they leave lobby. Owner can kick anyone at any time.
        -Players can leave lobby anytime. Normally, players can only target themselves.
        -If inactivity timeout is hit - players gain ability to kick the owner.

        Removal logic in the game:
        -If owner is kicked or voluntarily leaves - current player becomes a new owner.
        -Owner can still kick anyone at any time. Kicked player immediately leaves game.
        -Players can leave game anytime. Normally, players can only target themselves.
        -If current player is kicked - their turn is skipped & next player begins turn.
        -If inactivity timeout is hit - players gain ability to kick current player.
        -If player count drops below 2 - game is cancelled and final scores emitted.

        :param initiator: Player who initiated the removal.
        :param target: Player, who is targeted by kick.
        :return: None.
        """
        # Emit player leave event.
        self.emit_event(
            PlayerLeft(
                player=target,
                initiator=initiator,
                during_game=self.state.is_game_active,
            )
        )

        if self.state.is_game_active:  # Leave during game - complex logic.
            current = self._get_current_player()
            target_index = self.players.index(target)
            if target == current:  # Skip kicked player's turn.
                self.emit_event(TurnSkipped(target))
                self._switch_turn()
                current = self._get_current_player()
            if self.current_player > target_index:  # Adjust player index.
                self.current_player -= 1
            if target.player_id == self.owner_id:  # Transfer ownership.
                self.owner_id = current.player_id
                self.emit_event(OwnerChanged(oldowner=target, newowner=current))
            if (len(self.players) - 1) < 2:  # Check if there's enough players remain.
                self.emit_event(
                    GameEnded(
                        player=initiator,
                        cancelled=True,
                        not_enough_players=True,
                    )
                )
                self.emit_event(FinalScores(self.get_scores(), finished=False))
                self._switch_state(GameState.CANCELLED)

        # Actually remove kicked player. At this point we no longer need their obj.
        # However, if owner leaves lobby - player object is not actually removed.
        if not (self.state.is_in_lobby and target.player_id == self.owner_id):
            self.players.remove(target)
            self.player_map.pop(target.player_id)

        # If game is in lobby and owner has left - cancel the game.
        if self.state.is_in_lobby and target.player_id == self.owner_id:
            self.emit_event(
                GameEnded(player=initiator, cancelled=True, owner_left=True)
            )
            self._switch_state(GameState.CANCELLED)

    def _traverse_backward_red(self) -> Iterator[Player]:
        """
        Go through players one by one in backwards order, excluding current player.

        This is order you have to pay for opponents' red cards.

        :return: Previous player.
        """
        current = (self.current_player - 1) % len(self.players)
        while current != self.current_player:
            yield self.players[current]
            current = (current - 1) % len(self.players)

    def traverse_forward_players(self, skipcurrent=False) -> Iterator[Player]:
        """
        Go through players one by one, starting with current or next player.

        :param skipcurrent: Don't include current player in iteration.
        :return: Next player.
        """
        for offset in range(len(self.players) - (1 if skipcurrent else 0)):
            idx = (self.current_player + offset + (1 if skipcurrent else 0)) % len(
                self.players
            )
            yield self.players[idx]

    # Internal logic

    def _on_twelve_roll(self, player: Player) -> None:
        """
        Landmark effect, triggered on rolling 12.

        Only Tech Startup uses this to give 8 coins.

        :param player: Player, whose turn it is now.
        :return: None.
        """
        if (card := self.active_effects.get(Effect.GET_8_COINS_ON_12_ROLL)) is not None:
            self.emit_event(
                MoneyEarned(
                    reason=card,
                    user=player,
                    earned=player.earn_coins(8),
                )
            )

    def _on_six_roll(self, player: Player) -> None:
        """
        Landmark effect, triggered on rolling 6.

        Only Renovation Company uses this to give money for Food establishments.

        :param player: Player, whose turn it is now.
        :return: None.
        """
        card = self.active_effects.get(Effect.GET_COIN_FOR_EACH_FOOD_IF_ROLLED_6)
        if card is not None:
            count = 0
            for establishment in player.establishments:
                if establishment.category == "food":
                    count += 1
            if count:
                self.emit_event(
                    MoneyEarned(
                        reason=card,
                        user=player,
                        earned=player.earn_coins(count),
                    )
                )

    def _on_skip_build(self, player: Player):
        """
        Landmark effect, triggered by skipping build phase.

        Airport uses this to give 5 coins if you didn't build anything on your turn.

        :param player: Player, whose turn it is now.
        :return: None.
        """
        if Effect.SKIP_BUILD_FOR_5_COINS in self.active_effects:
            self.emit_event(
                MoneyEarned(
                    reason=self.active_effects[Effect.SKIP_BUILD_FOR_5_COINS],
                    user=player,
                    earned=player.earn_coins(5),
                )
            )

    def _compensation_no_earn(self, player: Player) -> None:
        """
        Handle landmark effects that pay compensation for earning no coins on roll.

        :param player: Player, whose turn it is now.
        :return: None.
        """
        if self.dice is not None and self.dice.dual:
            card = self.active_effects.get(Effect.NO_EARN_COMPENSATION_TWO_DICE)
            payout = 3
        else:
            card = self.active_effects.get(Effect.NO_EARN_COMPENSATION_ONE_DICE)
            payout = 2
        if card is not None:
            self.emit_event(
                MoneyEarned(
                    reason=card,
                    user=player,
                    earned=player.earn_coins(payout),
                )
            )

    def _give_establishment(self, player: Player) -> bool:
        """
        Handle Moving Company effect that forces you to give an establishment.

        Activated on rolling a double.

        :param player: Player, whose turn it is now.
        :return: Boolean, indicating whether player has to give establishments.
        """
        if Effect.GIVE_ESTABLISHMENT_ON_DOUBLE in self.active_effects:
            if len(player.establishments) > 0:
                player.give_establishment = True
                self._switch_state(GameState.ON_ESTABLISHMENT_GIVE)
                self.emit_event(
                    MustGiveEstablishment(
                        from_user=player,
                        to_user=next(self._traverse_backward_red()),
                    )
                )
                return True
        return False

    def _activate_landmarks(self, player: Player) -> bool:
        """
        Activate orange landmark effects.

        Some complex landmarks are moved into separate functions (see above).
        Ordering matters, don't shuffle handlers around.

        :param player: Player, whose turn it is now.
        :return: Whether landmark effect interrupts normal turn flow.
        """
        if self.dice is None:
            raise ValueError("Activation of landmarks without rolling dice")

        if self.dice.sum == 12:
            self._on_twelve_roll(player)
        if self.dice.sum == 6:
            self._on_six_roll(player)
        if self.dice.double:
            if (
                card := self.active_effects.get(Effect.TAKE_2_COINS_ON_DOUBLE)
            ) is not None:
                TakeFromAllOpponents(2).trigger(self, card, player, player)
        if not player.earned_coins_this_turn:
            self._compensation_no_earn(player)
        if self.dice.double:
            if (
                card := self.active_effects.get(Effect.EXTRA_TURN_ON_DOUBLE)
            ) is not None:
                ExtraTurn().trigger(self, card, player, player)
            if self._give_establishment(player):
                return True
        return False

    def _enter_build_phase(self, player: Player) -> None:
        """
        Initiate build phase.

        This would give a coin if player is broke. Building phase would be skipped if
        player cannot afford anything.

        :param player: Player, whose turn it is now.
        :return: None.
        """
        if self.market is None:
            raise ValueError("Entered build phase with not initialized market")

        if not player.initial_build_turns and player.coins == 0:
            player.earn_coins(1)
            self.emit_event(GetOneCoinBecauseHadNoMoney(player))
        buildable = self.market.can_build(player)
        if buildable:
            self._switch_state(GameState.ON_BUILD)
            self.emit_event(CanBuild(player, build_options=buildable))
            return
        self.emit_event(SkipBuild(player, cannot_buy=True))
        self._on_skip_build(player)
        self._switch_turn()

    def _activate_establishments(self, roll: int) -> None:
        """
        Activate establishment cards for current roll and card color.

        :param roll: Dice sum rolled.
        :return: None.
        """
        current = self._get_current_player()
        for player in self._traverse_backward_red():
            for establishment in player.get_activated_establishments(
                roll, ActivationOrder.OTHER_TURN
            ):
                establishment.effect.trigger(self, establishment, player, current)

        for player in self.traverse_forward_players():
            for establishment in player.get_activated_establishments(
                roll, ActivationOrder.ANY_TURN
            ):
                establishment.effect.trigger(self, establishment, player, current)

            if player != current:
                continue

            for establishment in player.get_activated_establishments(
                roll, ActivationOrder.OWN_TURN
            ):
                establishment.effect.trigger(self, establishment, player, current)

        for establishment in current.get_activated_establishments(
            roll, ActivationOrder.OWN_TURN_MAJOR
        ):
            establishment.effect.trigger(self, establishment, current, current)

    def _switch_turn(self, no_advance=False) -> None:
        """
        Switch turn and give control to next player.

        This does a lot of internal state tracking and preparations for next turn,
        selects next player. This method should be called whenever player ends the turn,
        even if he has extra turn.

        :param no_advance: Don't advance turn state. Used only for first turn.
        :return: None.
        """
        if not no_advance:
            self._switch_state(GameState.TURN_FINISHED)
        self.turn += 1
        current_player = self._get_current_player()
        extra_turn = current_player.extra_turn
        if extra_turn:
            current_player.end_turn()
        elif not no_advance:
            current_player.end_turn()
            self.current_player = (self.current_player + 1) % len(self.players)
            if self.current_player == 0:
                self.round += 1
            current_player = self._get_current_player()
        current_player.new_turn()
        initial_build_turns = 0
        if current_player.initial_build_turns:
            initial_build_turns = 3 - current_player.initial_build_turns + 1
        self.emit_event(
            TurnBegins(
                extra=extra_turn,
                turn_number=self.turn,
                round_number=self.round,
                initial=initial_build_turns,
                player=current_player,
            )
        )
        if initial_build_turns:
            self._enter_build_phase(current_player)
        else:
            self._switch_state(GameState.ON_ROLL)
        self.dice = None

    def _check_is_game_won(self, player: Player) -> bool:
        """
        Check if game is won and change into Finished state if so.

        :param player: Player, whose turn it is now.
        :return: Whether game is won and was switched into Finished state.
        """
        if player.is_winner():
            self.emit_event(
                GameEnded(
                    player=player,
                    finished=True,
                    launch_pad=player.have_launch_pad,
                )
            )
            self.emit_event(FinalScores(self.get_scores(), finished=True))
            self._switch_state(GameState.FINISHED)
            return True
        return False

    # External API

    def give_establishment(self, player: PlayerType, card_given: str) -> bool:
        """
        Give establishment per Moving Company effect.

        :param player: Player object, integer ID or None (implies current).
        :param card_given: Which card you want to give previous player.
        :return: Boolean, indicating whether move is legal & was successfully performed.
        """
        if not (player := self._get_player_object(player)):
            return False

        if self._expect_state_and_player(player, GameState.ON_ESTABLISHMENT_GIVE):
            if not player.has_card(card_given, only_establishments=True):
                self.emit_event(
                    PlayerHasNoSuchCard(
                        player=player, card_name=card_given, current=True
                    )
                )
                return False
            opponent = next(self._traverse_backward_red())
            given_card = cast(Establishment, player.pop_card(card_given))
            opponent.add_card(given_card)
            self.emit_event(
                EstablishmentGiven(
                    from_user=player,
                    to_user=opponent,
                    establishment=given_card,
                )
            )
            player.give_establishment = False
            self._enter_build_phase(player)
            return True

        return False

    def dont_exchange_establishments(self, player: PlayerType = None) -> bool:
        """
        Skip establishment exchange.

        Note, that this move will forfeit all remaining exchanges, if you have more than
        one Business Center establishments.

        :param player: Player object, integer ID or None (implies current).
        :return: Boolean, indicating whether move is legal & was successfully performed.
        """
        if not (player := self._get_player_object(player)):
            return False

        if self._expect_state_and_player(player, GameState.ON_ESTABLISHMENT_EXCHANGE):
            self.emit_event(SkipExchangeEstablishments(player=player))
            player.exchange_establishments = 0  # Remaining exchanges are forfeited, too
            if self._activate_landmarks(player):
                return True
            self._enter_build_phase(player)
            return True

        return False

    def exchange_establishments(
        self,
        player: PlayerType,
        opponent: PlayerType,
        card_given: str,
        card_taken: str,
    ) -> bool:
        """
        Exchange establishments with another player via Business Center effect.

        :param player: Player object, integer ID or None (implies current).
        :param opponent: Player descriptor of opponent, with whom you want to exchange.
        :param card_given: Establishment card that's given to opponent.
        :param card_taken: Establishment card that's taken from opponent.
        :return: Boolean, indicating whether move is legal & was successfully performed.
        """
        if not (player := self._get_player_object(player)):
            return False
        if not (opponent := self._get_player_object(opponent)):
            return False
        if player is opponent:
            self.emit_event(CannotExchangeWithSelf(player=player))
            return False

        if self._expect_state_and_player(player, GameState.ON_ESTABLISHMENT_EXCHANGE):

            if not player.has_card(card_given, only_establishments=True):
                self.emit_event(
                    PlayerHasNoSuchCard(
                        player=player, card_name=card_given, current=True
                    )
                )
                return False
            if not opponent.has_card(card_taken, only_establishments=True):
                self.emit_event(
                    PlayerHasNoSuchCard(
                        player=opponent, card_name=card_taken, current=False
                    )
                )
                return False

            given_card = cast(Establishment, player.pop_card(card_given))
            taken_card = cast(Establishment, opponent.pop_card(card_taken))
            player.add_card(taken_card)
            opponent.add_card(given_card)
            self.emit_event(
                EstablishmentExchanged(
                    from_user=player,
                    to_user=opponent,
                    establishment_given=given_card,
                    establishment_taken=taken_card,
                )
            )
            self.last_op = time()
            player.exchange_establishments -= 1
            if player.exchange_establishments < 1:
                if self._activate_landmarks(player):
                    return True
                self._enter_build_phase(player)
            return True

        return False

    def roll_dice(
            self,
            player: PlayerType = None,
            dual: bool = False,
            dice: Dice | None = None,
    ) -> bool:
        """
        Roll dice and activate establishments.

        Covers turn phase 1 and mostly 2 (but can be interrupted by establishment or
        landmark effect that requires player action).

        :param player: Player object, integer ID or None (implies current).
        :param dual: Whether to roll two dice.
        :param dice: Use externally created Dice (possibly from other random source).
        :return: Boolean, indicating whether move is legal & was successfully performed.
        """
        if not (player := self._get_player_object(player)):
            return False

        if self._expect_state_and_player(player, GameState.ON_ROLL):
            self.dice = Dice.roll(dual) if dice is None else dice
            self.emit_event(DiceRolled(player, self.dice))
            self._activate_establishments(self.dice.sum)
            if player.exchange_establishments:
                if any(
                    (
                        p.establishments
                        for p in self.traverse_forward_players(skipcurrent=True)
                    )
                ):
                    self._switch_state(GameState.ON_ESTABLISHMENT_EXCHANGE)
                    return True
            if self._activate_landmarks(player):
                return True
            self._enter_build_phase(player)
            return True

        return False

    def build_card(self, player: PlayerType, card_name: str | None) -> bool:
        """
        Build an establishment or landmark (or skip build phase).

        Since winning game requires to build landmarks, only during the build phase game
        can gracefully end, so winning is also handled there.

        :param player: Player object, integer ID or None (implies current).
        :param card_name: Name of card that player wants to build.
        :return: Boolean, indicating whether move is legal & was successfully performed.
        """
        if self.market is None:
            raise ValueError("Entered build phase with not initialized market")

        if not (player := self._get_player_object(player)):
            return False

        if self._expect_state_and_player(player, GameState.ON_BUILD):
            if card_name is None:
                self.emit_event(SkipBuild(player=player, cannot_buy=False))
                self._on_skip_build(player)
                self._switch_turn()
                return True
            card = self.market.build_card(player, card_name)
            if card is not None:
                if isinstance(card, Landmark):
                    card.effect.trigger(self, card, player, player)
                if not self._check_is_game_won(player):
                    self._switch_turn()
                return True

        return False

    def start(
        self, player: PlayerType, use_promo: bool = True, randomize_players: bool = True
    ) -> bool:
        """
        Start game when lobby is ready.

        Only game's owner (player, who created game) can start it, unless inactivity
        timeout has been hit.

        :param player: Player object, integer ID or None (implies current).
        :param use_promo: Use Promo Landmark addon with three new cards.
        :param randomize_players: Shuffle players (rather than keeping join order).
        :return: Boolean, indicating, whether the game was successfully started.
        """
        if not (player := self._get_player_object(player)):
            return False
        if not self.is_owner_or_timeout(player):
            return False

        if self._expect_state(GameState.NOT_STARTED):
            if len(self.players) < 2:
                self.emit_event(NotEnoughPlayers(player=player))
                return False
            self.use_promo = use_promo
            self.randomize_players = randomize_players
            if randomize_players:
                random.shuffle(self.players)
            self.emit_event(
                GameStarted(
                    owner=self._get_owner(),
                    turn_order=self.players,
                    use_promo=use_promo,
                    randomize_players=randomize_players,
                )
            )
            self.market = Market(self, use_promo=use_promo)
            self._switch_turn(no_advance=True)
            return True

        return False

    def join(self, player_id: int) -> bool:
        """
        Join this game.

        Game can be only joined while it's in not started state.
        If player is already in game - error event is raised and nothing happens.
        If there's already 5 players in a lobby - joining will fail.

        :param player_id: Unique ID of player who joins the game.
        :return: Boolean, indicating whether player has successfully joined game.
        """
        if self._expect_state(GameState.NOT_STARTED):
            if len(self.players) >= 5:
                self.emit_event(RoomIsFull(player_id=player_id))
                return False
            if player_id in self.player_map:
                self.emit_event(AlreadyInGame(self.player_map[player_id]))
                return False
            player_obj = Player(player_id)
            self.players.append(player_obj)
            self.player_map[player_id] = player_obj
            self.emit_event(PlayerJoined(player=player_obj))
            return True
        self.emit_event(GameInProgress(player_id=player_id))

        return False

    def leave(self, player: PlayerType) -> bool:
        """
        Leave the game, this is essentially a self-kick.

        :param player: Player, who wants to leave game.
        :return: Whether player has left the game.
        """
        return self.kick(player, player)

    def kick(self, player: PlayerType, target: PlayerType) -> bool:
        """
        Kick the player from game.

        Normally kicking could only be done by owner, or if player targets self
        (leaves voluntarily).

        Kick logic in the lobby:
        -If owner leaves the lobby - game is cancelled.
        -If owner kicks someone - they leave lobby. Owner can kick anyone at any time.
        -Players can leave lobby anytime. Normally, players can only target themselves.
        -If inactivity timeout is hit - players gain ability to kick the owner.

        Kick logic in the game:
        -If owner is kicked or voluntarily leaves - current player becomes a new owner.
        -Owner can still kick anyone at any time. Kicked player immediately leaves game.
        -Players can leave game anytime. Normally, players can only target themselves.
        -If current player is kicked - their turn is skipped & next player begins turn.
        -If inactivity timeout is hit - players gain ability to kick current player.
        -If player count drops below 2 - game is cancelled and final scores emitted.

        :param player: Player, who invokes the kick.
        :param target: Player, who is targeted by kick.
        :return: Whether kick was successful.
        """
        if not (player := self._get_player_object(player)):
            return False
        if not (target := self._get_player_object(target)):
            return False

        if not self.is_owner_self_or_timeout(player, target):
            return False

        owner = self._get_owner()

        if self.state.is_game_ended:  # No kicking if game ended.
            self.emit_event(NoGameInProgress(player))
            return False

        if player is not owner and target is not player:
            # If player is in lobby and timeout has hit - he can kick owner.
            if self.state.is_in_lobby:
                if target is not owner:
                    self.emit_event(
                        OnlyOwnerOperation(
                            owner=owner,
                            user=player,
                            inactivity_remains=0,
                        )
                    )
                    return False
            # If player is in game and timeout has hit - he can kick current player.
            elif self.state.is_game_active:
                if target is not self._get_current_player():
                    self.emit_event(
                        OnlyOwnerOperation(
                            owner=owner,
                            user=player,
                            inactivity_remains=0,
                        )
                    )
                    return False

        self._remove_player(initiator=player, target=target)
        return True

    def cancel(self, player: PlayerType) -> bool:
        """
        Cancel a lobby or active game.

        If game is in progress, final scores event would be also emitted.

        :return: Boolean, indicating whether game was actually cancelled.
        """
        if not (player := self._get_player_object(player)):
            return False
        if not self.is_owner_or_timeout(player):
            return False
        if self.state.is_game_ended:
            self.emit_event(NoGameInProgress(player))
            return False

        self.emit_event(GameEnded(player=player, cancelled=True))
        if not self.state.is_in_lobby:
            self.emit_event(FinalScores(self.get_scores(), finished=False))
        self._switch_state(GameState.CANCELLED)
        return True

    def get_scores(self) -> dict[int, list[Player]]:
        """
        Get player rankings (ties are possible).

        :return: Dict of places with lists of players as values.
        """
        sorted_players = sorted(
            self.players,
            key=lambda x: (x.is_winner(), len(x.landmarks), x.coins),
            reverse=True,
        )

        places: dict[int, list[Player]] = {}
        place = 0
        prev_key = None
        for player in sorted_players:
            key = (player.is_winner(), len(player.landmarks), player.coins)
            if prev_key != key:
                prev_key = key
                place += 1
                places[place] = []
            places[place].append(player)

        return places

    def serialize(self) -> dict:
        """
        Serialize game into a save dict.

        Warning: Serialization doesn't preserve event bus state! All outstanding events
        would be lost upon save-load cycle. Since moves are atomic, you're expected to
        consume all events upon committing move, and call serialize() with empty queue.

        :return: JSON-friendly savegame.
        """
        return {
            "players": [p.serialize() for p in self.players],
            # Player map is reconstructed procedurally
            "current_player": self.current_player,
            "state": int(self.state),
            "market": None if self.market is None else self.market.serialize(),
            "owner_id": self.owner_id,
            "turn": self.turn,
            "round": self.round,
            "use_promo": self.use_promo,
            "randomize_players": self.randomize_players,
            "dice": None if self.dice is None else self.dice.serialize(),
            "last_op": self.last_op,
            # Event bus state is not captured
            "active_effects": {str(k): v.name for k, v in self.active_effects.items()},
        }

    @classmethod
    def deserialize(cls, data: dict) -> MachiKoroGame:
        """
        Load game from save dict.

        :param data: Dict with game save.
        :return: Loaded game.
        """
        game = cls.__new__(cls)  # bypass __init__, we restore manually

        game.players = [Player.deserialize(p) for p in data["players"]]
        game.player_map = {}
        for player in game.players:
            game.player_map[player.player_id] = player
        game.current_player = data["current_player"]
        game.state = GameState(data["state"])
        game.market = None
        if data["market"] is not None:
            game.market = Market.deserialize(game, data["market"])
        game.owner_id = data["owner_id"]
        game.turn = data["turn"]
        game.round = data["round"]
        game.use_promo = data["use_promo"]
        game.randomize_players = data["randomize_players"]
        game.dice = None
        if data["dice"] is not None:
            game.dice = Dice.deserialize(data["dice"])
        game.last_op = data["last_op"]
        game.events = SimpleQueue()
        game.active_effects = {}
        for effect, card in data["active_effects"].items():
            card_obj = cast(Landmark, replace(ALL_CARDS[card], quantity=1))
            game.active_effects[Effect(effect)] = card_obj
        return game
