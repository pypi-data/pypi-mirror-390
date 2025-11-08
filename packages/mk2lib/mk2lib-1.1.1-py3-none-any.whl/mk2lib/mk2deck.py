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
Market implementation and card decks definitions.
"""

from __future__ import annotations

from dataclasses import replace
from random import shuffle
from typing import TYPE_CHECKING, cast

from mk2lib.cards import Card, Establishment, Landmark
from mk2lib.const import ActivationOrder, LandmarkKind, Kind, Effect
from mk2lib.effects import (
    EarnFromBank,
    EarnFromActivePlayer,
    EarnFromBankCombo,
    ExchangeEstablishments,
    TakeHalfIfElevenOrMore,
    TakeFromAllOpponents,
    PersistentEffect,
    ExtraTurn,
    TakeCoinForEachEstablishment,
    BuiltLoanOffice,
    TakeCoinsForEachLandmark,
    EvenlyDistributeCoins,
    TakeFiveCoinsIfTwoLandmarks,
    InstaWin,
)
from mk2lib.events import CardUnavailable, NotEnoughMoney, DealtCardsToMarket, CardBuilt

if TYPE_CHECKING:
    from mk2lib.game import MachiKoroGame
    from mk2lib.player import Player


class Market:
    """
    Implementation of 5-5-5 market of Machi Koro 2.
    """

    def __init__(self, game: MachiKoroGame, use_promo: bool = True):
        """
        Create a new Market object, clone and shuffle decks and make an initial deal.
        """
        self.est_low = cast(list[Establishment], Market._make_card_deck(DECK_1_6))
        self.est_high = cast(list[Establishment], Market._make_card_deck(DECK_7_12))
        self.landmarks = cast(list[Landmark], Market._make_card_deck(DECK_LANDMARKS))
        if not use_promo:
            self.landmarks = list(filter(lambda c: not c.is_promo, self.landmarks))
        self.dealt_low: dict[str, Establishment] = {}
        self.dealt_high: dict[str, Establishment] = {}
        self.dealt_landmarks: dict[str, Landmark] = {}
        self.game = game
        initial_deal = self.deal_to_market()
        self.game.emit_event(DealtCardsToMarket(initial_deal, initial=True))

    @staticmethod
    def _make_card_deck(cards: list[Establishment] | list[Landmark]) -> list[Card]:
        """
        Clone and shuffle card deck.

        :param cards: Source card deck.
        :return: Cloned and shuffled card deck with un-stacked cards.
        """
        deck = []
        for card in cards:
            for _ in range(card.quantity):
                deck.append(replace(card, quantity=1))
        shuffle(deck)
        return cast(list[Card], deck)

    def deal_to_market(self) -> list[Card]:
        """
        Deal cards, until there's 5 of each type.

        Duplicate cards are stacked.

        :return: List of cards that were dealt to market.
        """
        dealt = []
        for deck, _market in (
            (self.est_low, self.dealt_low),
            (self.est_high, self.dealt_high),
            (self.landmarks, self.dealt_landmarks),
        ):
            market = cast(dict[str, Card], _market)
            while deck and len(market) < 5:
                card = deck.pop()
                dealt.append(card)
                if card.name in market:
                    market[card.name].quantity += 1
                else:
                    market[card.name] = card
        return cast(list[Card], dealt)

    def can_build(self, player: Player) -> list[Card]:
        """
        Check is player can build something.

        Checks that market has any cards up for building and that player
        can afford at least any one card.

        :param player: Player, whose build phase it is.
        """
        affordable_cards = []
        for market in (self.dealt_low, self.dealt_high, self.dealt_landmarks):
            for card in market.values():
                if player.can_afford(card.get_real_price(self.game, player)):
                    affordable_cards.append(card)
        return cast(list[Card], affordable_cards)

    def build_card(self, player: Player, card_name: str) -> Card | None:
        """
        Build the specified card.

        Checks whether card is dealt to market, plus if player can afford and is
        allowed to build it by rules.

        If yes - gives card to player and emits CardBuilt event. If for any reason
        building is illegal - either CardUnavailable or NotEnoughMoney event is
        emitted.

        :param player: Player who builds the card.
        :param card_name: Name of the card that player wants to build.
        :return: Card instance, if built successfully. None otherwise.
        """
        for market in (self.dealt_low, self.dealt_high, self.dealt_landmarks):
            if card_name in market:
                card = replace(market[card_name], quantity=1)
                real_price = card.get_real_price(self.game, player)
                if player.can_afford(real_price) and real_price is not None:
                    player.spend_coins(real_price)
                    if market[card_name].quantity > 1:
                        market[card_name].quantity -= 1
                    else:
                        market.pop(card_name)
                    player.add_card(card)
                    self.game.emit_event(
                        CardBuilt(
                            buyer=player,
                            card=card,
                            price_paid=real_price,
                        )
                    )
                    dealt = self.deal_to_market()
                    if dealt:
                        self.game.emit_event(DealtCardsToMarket(dealt))
                    return card
                if real_price is None:
                    self.game.emit_event(
                        CardUnavailable(
                            buyer=player,
                            card_name=card_name,
                            prohibited=True,
                        )
                    )
                else:
                    self.game.emit_event(
                        NotEnoughMoney(
                            buyer=player,
                            card_name=card_name,
                            card_price=real_price,
                        )
                    )
                return None
        self.game.emit_event(CardUnavailable(buyer=player, card_name=card_name))
        return None

    def serialize(self) -> dict:
        """
        Prepare JSON serializable version of this Market instance.

        Preserves card state and order.

        :return: JSON-friendly dict that has enough state to reconstruct Market object.
        """
        return {
            "est_low": [card.name for card in self.est_low],
            "est_high": [card.name for card in self.est_high],
            "landmarks": [card.name for card in self.landmarks],
            "dealt_low": {name: card.quantity for name, card in self.dealt_low.items()},
            "dealt_high": {
                name: card.quantity for name, card in self.dealt_high.items()
            },
            "dealt_landmarks": {
                name: card.quantity for name, card in self.dealt_landmarks.items()
            },
        }

    @classmethod
    def deserialize(cls, game: MachiKoroGame, data: dict) -> Market:
        """
        Reconstruct Market from saved dict, produced by .serialize()

        :return: Loaded Market from saved data.
        """
        market = cls.__new__(cls)  # bypass __init__, we restore manually
        market.game = game

        # reconstruct decks in order
        def rebuild_deck(names):
            return [replace(ALL_CARDS[name], quantity=1) for name in names]

        market.est_low = rebuild_deck(data["est_low"])
        market.est_high = rebuild_deck(data["est_high"])
        market.landmarks = rebuild_deck(data["landmarks"])

        # reconstruct dealt dicts (quantities matter!)
        def rebuild_dealt(d):
            return {
                name: replace(ALL_CARDS[name], quantity=qty) for name, qty in d.items()
            }

        market.dealt_low = rebuild_dealt(data["dealt_low"])
        market.dealt_high = rebuild_dealt(data["dealt_high"])
        market.dealt_landmarks = rebuild_dealt(data["dealt_landmarks"])

        return market


# Deck definitions follows


DECK_1_6 = [
    Establishment(
        name="wheat_field",
        effect=EarnFromBank(1),
        order=ActivationOrder.ANY_TURN,
        quantity=5,
        activation_numbers=[1, 2],
        cost=1,
        category=Kind.AGRICULTURE,
    ),
    Establishment(
        name="sushi_bar",
        effect=EarnFromActivePlayer(3),
        order=ActivationOrder.OTHER_TURN,
        quantity=5,
        activation_numbers=[1],
        cost=2,
        category=Kind.FOOD,
    ),
    Establishment(
        name="business_center",
        effect=ExchangeEstablishments(),
        order=ActivationOrder.OWN_TURN_MAJOR,
        quantity=3,
        activation_numbers=[6],
        cost=3,
        category=Kind.MAJOR,
    ),
    Establishment(
        name="flower_shop",
        effect=EarnFromBankCombo(Kind.FLOWER, 3),
        order=ActivationOrder.OWN_TURN,
        quantity=3,
        activation_numbers=[6],
        cost=1,
        category=Kind.COMBO,
    ),
    Establishment(
        name="cafe",
        effect=EarnFromActivePlayer(2),
        order=ActivationOrder.OTHER_TURN,
        quantity=5,
        activation_numbers=[3],
        cost=1,
        category=Kind.FOOD,
    ),
    Establishment(
        name="bakery",
        effect=EarnFromBank(2),
        order=ActivationOrder.OWN_TURN,
        quantity=5,
        activation_numbers=[2, 3],
        cost=1,
        category=Kind.SHOP,
    ),
    Establishment(
        name="flower_garden",
        effect=EarnFromBank(2),
        order=ActivationOrder.ANY_TURN,
        quantity=5,
        activation_numbers=[4],
        cost=2,
        category=Kind.FLOWER,
    ),
    Establishment(
        name="vineyard",
        effect=EarnFromBank(2),
        order=ActivationOrder.ANY_TURN,
        quantity=5,
        activation_numbers=[2],
        cost=1,
        category=Kind.FRUIT,
    ),
    Establishment(
        name="forest",
        effect=EarnFromBank(2),
        order=ActivationOrder.ANY_TURN,
        quantity=5,
        activation_numbers=[5],
        cost=3,
        category=Kind.GEAR,
    ),
    Establishment(
        name="convenience_store",
        effect=EarnFromBank(3),
        order=ActivationOrder.OWN_TURN,
        quantity=5,
        activation_numbers=[4],
        cost=1,
        category=Kind.SHOP,
    ),
]

DECK_7_12 = [
    Establishment(
        name="corn_field",
        effect=EarnFromBank(3),
        order=ActivationOrder.ANY_TURN,
        quantity=5,
        activation_numbers=[7],
        cost=2,
        category=Kind.AGRICULTURE,
    ),
    Establishment(
        name="food_warehouse",
        effect=EarnFromBankCombo(Kind.FOOD, 2),
        order=ActivationOrder.OWN_TURN,
        quantity=3,
        activation_numbers=[10, 11],
        cost=2,
        category=Kind.COMBO,
    ),
    Establishment(
        name="family_restaurant",
        effect=EarnFromActivePlayer(2),
        order=ActivationOrder.OTHER_TURN,
        quantity=5,
        activation_numbers=[9, 10],
        cost=2,
        category=Kind.FOOD,
    ),
    Establishment(
        name="shopping_district",
        effect=TakeHalfIfElevenOrMore(),
        order=ActivationOrder.OWN_TURN_MAJOR,
        quantity=3,
        activation_numbers=[8, 9],
        cost=3,
        category=Kind.MAJOR,
    ),
    Establishment(
        name="hamburger_stand",
        effect=EarnFromActivePlayer(2),
        order=ActivationOrder.OTHER_TURN,
        quantity=5,
        activation_numbers=[8],
        cost=1,
        category=Kind.FOOD,
    ),
    Establishment(
        name="furniture_factory",
        effect=EarnFromBankCombo(Kind.GEAR, 4),
        order=ActivationOrder.OWN_TURN,
        quantity=3,
        activation_numbers=[8],
        cost=4,
        category=Kind.COMBO,
    ),
    Establishment(
        name="stadium",
        effect=TakeFromAllOpponents(3),
        order=ActivationOrder.OWN_TURN_MAJOR,
        quantity=3,
        activation_numbers=[7],
        cost=3,
        category=Kind.MAJOR,
    ),
    Establishment(
        name="winery",
        effect=EarnFromBankCombo(Kind.FRUIT, 3),
        order=ActivationOrder.OWN_TURN,
        quantity=3,
        activation_numbers=[9],
        cost=3,
        category=Kind.COMBO,
    ),
    Establishment(
        name="apple_orchard",
        effect=EarnFromBank(3),
        order=ActivationOrder.ANY_TURN,
        quantity=5,
        activation_numbers=[10],
        cost=1,
        category=Kind.FRUIT,
    ),
    Establishment(
        name="mine",
        effect=EarnFromBank(6),
        order=ActivationOrder.ANY_TURN,
        quantity=5,
        activation_numbers=[11, 12],
        cost=4,
        category=Kind.GEAR,
    ),
]

DECK_LANDMARKS = [
    Landmark(
        name="publisher",
        effect=TakeCoinForEachEstablishment(Kind.SHOP),
        quantity=1,
        cost=[10, 14, 22],
        is_promo=False,
        kind=LandmarkKind.OWN_TURN_ONCE,
    ),
    Landmark(
        name="airport",
        effect=PersistentEffect(Effect.SKIP_BUILD_FOR_5_COINS),
        quantity=1,
        cost=[12, 16, 22],
        is_promo=False,
        kind=LandmarkKind.ANY_TURN_INFINITE,
    ),
    Landmark(
        name="museum",
        effect=TakeCoinsForEachLandmark(3),
        quantity=1,
        cost=[12, 16, 22],
        is_promo=False,
        kind=LandmarkKind.OWN_TURN_ONCE,
    ),
    Landmark(
        name="exhibit_hall",
        effect=TakeHalfIfElevenOrMore(),
        quantity=1,
        cost=[12, 16, 22],
        is_promo=False,
        kind=LandmarkKind.OWN_TURN_ONCE,
    ),
    Landmark(
        name="temple",
        effect=PersistentEffect(Effect.TAKE_2_COINS_ON_DOUBLE),
        quantity=1,
        cost=[12, 16, 22],
        is_promo=False,
        kind=LandmarkKind.ANY_TURN_INFINITE,
    ),
    Landmark(
        name="tv_station",
        effect=TakeCoinForEachEstablishment(Kind.FOOD),
        quantity=1,
        cost=[12, 16, 22],
        is_promo=False,
        kind=LandmarkKind.OWN_TURN_ONCE,
    ),
    Landmark(
        name="loan_office",
        effect=BuiltLoanOffice(),
        quantity=1,
        cost=[10, None, None],
        is_promo=False,
        kind=LandmarkKind.OWN_TURN_INFINITE,
    ),
    Landmark(
        name="park",
        effect=EvenlyDistributeCoins(),
        quantity=1,
        cost=[12, 16, 22],
        is_promo=False,
        kind=LandmarkKind.OWN_TURN_ONCE,
    ),
    Landmark(
        name="tech_startup",
        effect=PersistentEffect(Effect.GET_8_COINS_ON_12_ROLL),
        quantity=1,
        cost=[10, 14, 22],
        is_promo=False,
        kind=LandmarkKind.ANY_TURN_INFINITE,
    ),
    Landmark(
        name="french_restaurant",
        effect=TakeFromAllOpponents(2),
        quantity=1,
        cost=[10, 14, 22],
        is_promo=False,
        kind=LandmarkKind.OWN_TURN_ONCE,
    ),
    Landmark(
        name="shopping_mall",
        effect=PersistentEffect(Effect.BOOST_ONE_COIN_SHOP),
        quantity=1,
        cost=[10, 14, 22],
        is_promo=False,
        kind=LandmarkKind.ANY_TURN_INFINITE,
    ),
    Landmark(
        name="launch_pad",
        effect=InstaWin(),
        quantity=1,
        cost=[45, 38, 25],
        is_promo=False,
        kind=LandmarkKind.OWN_TURN_INSTAWIN,
    ),
    Landmark(
        name="soda_bottling_plant",
        effect=PersistentEffect(Effect.BOOST_ONE_COIN_FOOD),
        quantity=1,
        cost=[12, 16, 22],
        is_promo=False,
        kind=LandmarkKind.ANY_TURN_INFINITE,
    ),
    Landmark(
        name="charterhouse",
        effect=PersistentEffect(Effect.NO_EARN_COMPENSATION_TWO_DICE),
        quantity=1,
        cost=[12, 16, 22],
        is_promo=False,
        kind=LandmarkKind.ANY_TURN_INFINITE,
    ),
    Landmark(
        name="radio_tower",
        effect=ExtraTurn(),
        quantity=1,
        cost=[12, 16, 22],
        is_promo=False,
        kind=LandmarkKind.OWN_TURN_ONCE,
    ),
    Landmark(
        name="amusement_park",
        effect=PersistentEffect(Effect.EXTRA_TURN_ON_DOUBLE),
        quantity=1,
        cost=[12, 16, 22],
        is_promo=False,
        kind=LandmarkKind.ANY_TURN_INFINITE,
    ),
    Landmark(
        name="private_club",
        effect=TakeFiveCoinsIfTwoLandmarks(),
        quantity=1,
        cost=[12, 16, 22],
        is_promo=True,
        kind=LandmarkKind.OWN_TURN_ONCE,
    ),
    Landmark(
        name="forge",
        effect=PersistentEffect(Effect.BOOST_ONE_COIN_GEAR),
        quantity=1,
        cost=[12, 16, 22],
        is_promo=False,
        kind=LandmarkKind.ANY_TURN_INFINITE,
    ),
    Landmark(
        name="city_hall",
        effect=PersistentEffect(Effect.NO_EARN_COMPENSATION_ONE_DICE),
        quantity=1,
        cost=[10, 14, 22],
        is_promo=True,
        kind=LandmarkKind.ANY_TURN_INFINITE,
    ),
    Landmark(
        name="renovation_company",
        effect=PersistentEffect(Effect.GET_COIN_FOR_EACH_FOOD_IF_ROLLED_6),
        quantity=1,
        cost=[10, 14, 22],
        is_promo=True,
        kind=LandmarkKind.ANY_TURN_INFINITE,
    ),
    Landmark(
        name="farmers_market",
        effect=PersistentEffect(Effect.BOOST_ONE_COIN_AGRICULTURE),
        quantity=1,
        cost=[10, 14, 22],
        is_promo=False,
        kind=LandmarkKind.ANY_TURN_INFINITE,
    ),
    Landmark(
        name="moving_company",
        effect=PersistentEffect(Effect.GIVE_ESTABLISHMENT_ON_DOUBLE),
        quantity=1,
        cost=[10, 14, 22],
        is_promo=False,
        kind=LandmarkKind.ANY_TURN_INFINITE,
    ),
    Landmark(
        name="observatory",
        effect=PersistentEffect(Effect.LAUNCH_PAD_DISCOUNT),
        quantity=1,
        cost=[10, 14, 22],
        is_promo=False,
        kind=LandmarkKind.ANY_TURN_INFINITE,
    ),
]

# Helper lookup table of all possible cards
ALL_CARDS = {}
for _deck in (DECK_1_6, DECK_7_12, DECK_LANDMARKS):
    for _card in _deck:
        ALL_CARDS[_card.name] = _card
