from random import Random

from randovania.game_description.game_patches import GamePatches
from randovania.game_description.hint import (
    HintLocationPrecision, HintItemPrecision,
    PrecisionPair
)
from randovania.game_description.resources.pickup_entry import PickupEntry
from randovania.generator.filler.player_state import PlayerState
from randovania.generator.filler.runner import PlayerPool
from randovania.generator.hint_distributor import HintDistributor


class DreadHintDistributor(HintDistributor):
    def precision_pair_weighted_list(self) -> list[PrecisionPair]:
        return [
            PrecisionPair(HintLocationPrecision.WORLD_ONLY, HintItemPrecision.DETAILED, True),
        ]

    def _get_relative_hint_providers(self):
        return []

    async def assign_precision_to_hints(self, patches: GamePatches, rng: Random,
                                        player_pool: PlayerPool, player_state: PlayerState) -> GamePatches:
        return self.add_hints_precision(player_state, patches, rng)

    def interesting_pickup_to_hint(self, pickup: PickupEntry) -> bool:
        return super().interesting_pickup_to_hint(pickup) and pickup.name not in {"Hyper Beam", "Metroid Suit"}