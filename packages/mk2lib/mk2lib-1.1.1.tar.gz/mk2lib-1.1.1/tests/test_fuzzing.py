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
Machi Koro 2 auto-play game fuzzer test.
"""
import queue
import random

import pytest

from mk2lib.const import GameState, INACTIVITY_TIMEOUT
from mk2lib.events import StateSwitch, CanBuild, ErrorEvent
from mk2lib.game import MachiKoroGame


def rand_bool():
    """
    Generate random bool.
    """
    return bool(random.getrandbits(1))


@pytest.fixture
def game_random():
    """
    Fixture that sets up 2 player game.
    """
    game = MachiKoroGame(1)
    for i in range(2, random.randint(2, 5)):
        game.join(i)
    return game


def exchange_establishments(game, negative=False) -> None:
    """
    Exchange establishments logic.

    :param game: Machi Koro 2 game instance.
    :param negative: Boolean, whether to check negative cases.
    :return: None.
    """
    if rand_bool():
        if negative:
            player = random.choice(game.players)
            if len(player.establishments) == 0:
                return
            opponent = random.choice(game.players)
            if rand_bool():
                card_given = random.choice(player.establishments).name
            else:
                if player.landmarks and rand_bool():
                    card_given = random.choice(player.landmarks).name
                else:
                    card_given = "invalid"
            if rand_bool():
                if len(opponent.establishments) > 0:
                    card_taken = random.choice(opponent.establishments).name
                else:
                    if opponent.landmarks and rand_bool():
                        card_taken = random.choice(opponent.landmarks).name
                    else:
                        card_taken = "invalid"
            else:
                card_taken = "invalid"
        else:
            player = game._get_current_player()
            while True:
                opponent = random.choice(game.players)
                if opponent != player and len(opponent.establishments) > 0:
                    break
            card_given = random.choice(player.establishments).name
            card_taken = random.choice(opponent.establishments).name
        game.exchange_establishments(player, opponent, card_given, card_taken)
    else:
        game.dont_exchange_establishments()


@pytest.mark.parametrize("execution_number,", range(1000))
def test_random_game(game_random, execution_number):
    """
    Run a random game with self-playing dummy agents.
    """
    negative = bool(execution_number % 2)
    g = game_random
    if negative and len(g.players) == 1:  # Try to start 1p game.
        g.start(1, rand_bool(), rand_bool())
        assert g.state.is_in_lobby
    g.join(len(g.players) + 1)
    if (
        negative and rand_bool()
    ):  # Attempt to join sixth player or already joined player
        if len(g.players) == 5:
            g.join(6)
        else:
            g.join(1)
    assert g.state.is_in_lobby
    assert not g.state.is_game_active
    if negative and rand_bool():  # Start as non-owner
        g.start(2, rand_bool(), rand_bool())
        assert g.state.is_in_lobby
    if negative and rand_bool():  # Start as non-player:
        g.start(10, rand_bool(), rand_bool())
        assert g.state.is_in_lobby
    if negative and rand_bool():
        assert not g.is_owner_or_timeout(2)
        g.last_op = g.last_op - INACTIVITY_TIMEOUT
        assert g.is_owner_or_timeout(2)
    g.start(1, rand_bool(), rand_bool())
    assert not g.state.is_in_lobby
    assert g.state.is_game_active
    while not g.state.is_game_ended:
        e = g.events.get_nowait()
        if negative and g.events.empty() and not random.randint(0, 10):
            save = g.serialize()
            g = g.deserialize(save)
        if negative and not random.randint(0, 10):
            match random.randint(0, 10):
                case 0:
                    g.join(5)
                case 1:
                    g.start(1)
                case 2:
                    g.build_card(-1, "unknown")
                case 3:
                    g.roll_dice(player=-1)
                case 4:
                    if g.state != GameState.ON_ROLL:
                        g.roll_dice()
                case 5:
                    g.exchange_establishments(-1, 1, "unknown", "unknown")
                case 6:
                    g.exchange_establishments(1, -1, "unknown", "unknown")
                case 7:
                    g.dont_exchange_establishments(-1)
                case 8:
                    g.give_establishment(-1, "unknown")
                case 9:
                    if g.state != GameState.ON_ESTABLISHMENT_EXCHANGE:
                        g.exchange_establishments(1, 2, "unknown", "unknown")
                case 10:
                    if g.state != GameState.ON_ESTABLISHMENT_EXCHANGE:
                        g.dont_exchange_establishments(1)
        if isinstance(e, StateSwitch):
            if e.new_state == GameState.ON_ROLL:
                g.roll_dice(dual=rand_bool())
            elif e.new_state == GameState.ON_ESTABLISHMENT_GIVE:
                while True:
                    if negative:
                        player = random.choice(g.players)
                        if len(player.establishments) == 0:
                            continue
                        if rand_bool():
                            card_given = "invalid"
                        else:
                            card_given = random.choice(player.establishments).name
                    else:
                        player = g._get_current_player()
                        card_given = random.choice(player.establishments).name
                    if g.give_establishment(player, card_given):
                        break
            elif e.new_state == GameState.ON_ESTABLISHMENT_EXCHANGE:
                player = g._get_current_player()
                while player.exchange_establishments:
                    exchange_establishments(g, negative)
        elif isinstance(e, CanBuild):
            if rand_bool():
                while True:
                    if negative and rand_bool():
                        if g.build_card(None, "invalid"):
                            break
                    else:
                        g.build_card(None, random.choice(e.build_options).name)
                        break
            else:
                g.build_card(e.player, None)
        elif isinstance(e, ErrorEvent) and not negative:
            raise RuntimeError(f"ErrorEvent is raised in non-negative scenario: {e}")
    while True:
        try:
            e = g.events.get_nowait()
        except queue.Empty:
            break
