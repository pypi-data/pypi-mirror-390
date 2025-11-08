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
Machi Koro 2 game testcases.
"""

import pytest

from mk2lib.events import (
    GameEnded,
    NotInGame,
    OnlyOwnerOperation,
    NoGameInProgress,
    FinalScores,
    StateSwitch,
    GameCreated,
    PlayerJoined,
    PlayerLeft,
    TurnSkipped,
    TurnBegins,
    CanBuild,
    OwnerChanged,
)
from mk2lib.game import MachiKoroGame
from mk2lib.const import INACTIVITY_TIMEOUT


@pytest.fixture
def game():
    """
    Fixture that sets up 5 player game.
    """
    game = MachiKoroGame(1)
    game.join(2)
    game.join(3)
    game.join(4)
    game.join(5)
    while not game.events.empty():
        game.events.get_nowait()
    return game


def test_kick(game: MachiKoroGame):
    """
    Test that kick works.
    """
    # Not existing kicker/kickee.
    assert not game.is_owner_self_or_timeout(6, 6)  # Fail-path.
    assert isinstance(game.events.get_nowait(), NotInGame)
    assert not game.kick(6, 2)
    assert isinstance(game.events.get_nowait(), NotInGame)
    assert not game.kick(2, 6)
    assert isinstance(game.events.get_nowait(), NotInGame)
    save = game.serialize()
    assert not game.kick(2, 3)  # Not owner
    assert isinstance(game.events.get_nowait(), OnlyOwnerOperation)
    game.last_op -= INACTIVITY_TIMEOUT
    assert not game.kick(2, 3)  # Even after timeout cannot kick arbitrary.
    assert isinstance(game.events.get_nowait(), OnlyOwnerOperation)
    assert game.kick(2, 1)  # But can kick owner.
    assert isinstance(game.events.get_nowait(), PlayerLeft)
    assert isinstance(game.events.get_nowait(), GameEnded)
    assert isinstance(game.events.get_nowait(), StateSwitch)
    assert game.state == game.state.CANCELLED
    assert not game.kick(2, 2)  # Can't kick from cancelled game.
    assert isinstance(game.events.get_nowait(), NoGameInProgress)
    game = MachiKoroGame.deserialize(save)
    for i in range(2, 6):
        assert game.kick(1, i)  # Owner kicks all
        assert isinstance(game.events.get_nowait(), PlayerLeft)
    assert not game.state.is_game_ended  # Game won't cancel with < 2 players in lobby.
    game = MachiKoroGame.deserialize(save)
    game.start(1, True, False)

    # In-game leave checks.
    while not game.events.empty():
        game.events.get_nowait()
    assert game.current_player == 0
    for _ in range(2):
        assert game.build_card(None, None)  # Skip build to advance player counter.
    while not game.events.empty():
        game.events.get_nowait()

    assert game.kick(1, 5)  # Kick player with high index.
    assert isinstance(game.events.get_nowait(), PlayerLeft)
    assert game.current_player == 2  # Current index won't change.
    assert game.events.empty()  # No skip turn events.
    assert game.owner_id == 1  # Owner didn't change.
    assert not game.kick(2, 3)  # Not owner still can't kick.
    assert isinstance(game.events.get_nowait(), OnlyOwnerOperation)
    game.last_op -= INACTIVITY_TIMEOUT
    assert not game.kick(3, 2)  # Timeout doesn't allow to kick non-current.
    assert isinstance(game.events.get_nowait(), OnlyOwnerOperation)
    assert not game.kick(3, 1)  # Owner included.
    assert isinstance(game.events.get_nowait(), OnlyOwnerOperation)
    assert game.kick(2, 3)  # Current player can be kicked by anyone.
    assert isinstance(game.events.get_nowait(), PlayerLeft)
    assert isinstance(game.events.get_nowait(), TurnSkipped)
    assert isinstance(game.events.get_nowait(), StateSwitch)
    assert isinstance(game.events.get_nowait(), TurnBegins)
    assert isinstance(game.events.get_nowait(), StateSwitch)
    assert isinstance(game.events.get_nowait(), CanBuild)
    assert game.current_player == 2  # Current index won't change.
    assert game.owner_id == 1  # Owner didn't change.
    assert game.kick(1, 2)  # Kick player before current.
    assert isinstance(game.events.get_nowait(), PlayerLeft)
    assert game.current_player == 1  # Index must have been decremented.
    assert game.players[1].player_id == 4  # Still player 4 is current.
    assert game.kick(1, 1)  # Owner leaves, .
    assert isinstance(game.events.get_nowait(), PlayerLeft)
    assert isinstance(game.events.get_nowait(), OwnerChanged)
    assert game.current_player == 0
    assert game.owner_id == 4
    assert isinstance(game.events.get_nowait(), GameEnded)
    assert isinstance(game.events.get_nowait(), FinalScores)
    assert game.state == game.state.CANCELLED


def test_leave(game: MachiKoroGame):
    """
    Test that player can leave the game.
    """
    assert game.leave(2)
    assert isinstance(game.events.get_nowait(), PlayerLeft)
    assert game.leave(1)
    assert isinstance(game.events.get_nowait(), PlayerLeft)
    event = game.events.get_nowait()
    assert isinstance(event, GameEnded)
    assert event.owner_left


def test_cancel(game: MachiKoroGame):
    """
    Check that we can cancel the game.
    """
    save = game.serialize()
    assert not game.cancel(6)  # Not existing player.
    assert isinstance(game.events.get_nowait(), NotInGame)
    assert not game.cancel(2)  # Non-owner.
    assert isinstance(game.events.get_nowait(), OnlyOwnerOperation)
    assert game.cancel(1)  # Owner cancels.
    assert isinstance(game.events.get_nowait(), GameEnded)
    assert isinstance(game.events.get_nowait(), StateSwitch)
    assert not game.cancel(1)  # Cancel already cancelled game.
    assert isinstance(game.events.get_nowait(), NoGameInProgress)
    assert game.state == game.state.CANCELLED
    game = MachiKoroGame.deserialize(save)
    game.last_op -= INACTIVITY_TIMEOUT
    assert game.cancel(2)  # Non-owner after timeout.
    assert isinstance(game.events.get_nowait(), GameEnded)
    game = MachiKoroGame.deserialize(save)
    game.start(1)
    while not game.events.empty():
        game.events.get_nowait()
    assert game.cancel(1)  # Owner cancels in game.
    assert isinstance(game.events.get_nowait(), GameEnded)
    assert game.state == game.state.CANCELLED
    assert isinstance(game.events.get_nowait(), FinalScores)
    assert isinstance(game.events.get_nowait(), StateSwitch)

def test_not_initialized(game: MachiKoroGame):
    """
    Things that should never happen, but still have checks.
    """
    with pytest.raises(ValueError):
        game._activate_landmarks(game.players[0])
    with pytest.raises(ValueError):
        game._enter_build_phase(game.players[0])
    with pytest.raises(ValueError):
        game.build_card(None, "unknown")
