from sc2 import maps
from sc2.player import Bot, Computer
from sc2.main import run_game
from sc2.data import Race, Difficulty
from sc2.bot_ai import BotAI
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.buff_id import BuffId
from sc2.unit import Unit

class ZergoBot(BotAI):

    macroing = True
    defensive_queens = []
    injecting_queens = []
    hatches = []

    async def on_step(self, iteration: int):
        if iteration == 0:
            self.hatches.append(self.townhalls.first)

        if self.townhalls.amount >= 3:
            self.macroing = False

        await self.control_army()
        await self.inject()
        await self.distribute_workers()
        await self.produce_overlords()
        await self.produce_units()
        await self.techup()
    
    async def control_army(self):
        for queen in self.defensive_queens:
            if queen.is_idle:
                queen.attack(self.game_info.map_center)
    
    async def inject(self):
        for i in range(len(self.hatches)):
            hatch = self.hatches[i]
            if not hatch.has_buff(BuffId.QUEENSPAWNLARVATIMER):
                if i < len(self.injecting_queens):
                    queen = self.injecting_queens[i]
                    if queen.energy >= 25:
                        queen(AbilityId.EFFECT_INJECTLARVA, hatch)

    async def techup(self):
        # build spawning pool
        if self.filter_by_unit(UnitTypeId.SPAWNINGPOOL, self.structures).amount == 0:
            if self.can_afford(UnitTypeId.SPAWNINGPOOL):
                to_center = self.start_location.towards(self.game_info.map_center, distance=5)
                await self.build(UnitTypeId.SPAWNINGPOOL, to_center, placement_step=1)
        # zergling speed
        elif not self.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED) and self.can_afford(UpgradeId.ZERGLINGMOVEMENTSPEED):
            self.filter_by_unit(UnitTypeId.SPAWNINGPOOL, self.structures).random.research(UpgradeId.ZERGLINGMOVEMENTSPEED)

    async def produce_units(self):
        if self.macroing:
            # get first gas
            if self.supply_workers >= 16 and self.gas_buildings.amount == 0 and not self.already_pending(UnitTypeId.EXTRACTOR):
                gas_location = self.vespene_geyser.closest_to(self.townhalls.random)
                await self.build(UnitTypeId.EXTRACTOR, gas_location)

            # expand
            if self.already_pending(UnitTypeId.HATCHERY) == 0 and self.supply_workers >= self.townhalls.amount * 16 and self.can_afford(UnitTypeId.HATCHERY):
                await self.expand_now()
            
            # drones
            while self.can_afford(UnitTypeId.DRONE) and self.larva:
                self.larva.random(AbilityId.LARVATRAIN_DRONE, subtract_cost=True, subtract_supply=True)

        else:
            while self.can_afford(UnitTypeId.ZERGLING) and self.larva:
                self.larva.random(AbilityId.LARVATRAIN_ZERGLING, subtract_cost=True, subtract_supply=True)

        # queens
        queens_needed = (8 - len(self.defensive_queens)) + (self.townhalls.amount - len(self.injecting_queens))
        if queens_needed - self.already_pending(UnitTypeId.QUEEN) > 0:
            for townhall in self.townhalls:
                if townhall.is_idle and self.can_afford(UnitTypeId.QUEEN):
                    townhall.train(UnitTypeId.QUEEN)
                    break

    async def produce_overlords(self):
        while (self.supply_left + (self.already_pending(UnitTypeId.OVERLORD) * 8)) <= (self.townhalls.amount * 4) and self.can_afford(UnitTypeId.OVERLORD) and self.larva:
            self.larva.random(AbilityId.LARVATRAIN_OVERLORD, subtract_cost=True)

    def filter_by_unit(self, id, array):
        return array.filter(lambda item: item.type_id == id)
    
    async def on_unit_created(self, unit: Unit):
        # distribute queens
        if unit.type_id == UnitTypeId.QUEEN:
            if len(self.injecting_queens) < self.townhalls.amount:
                self.injecting_queens.append(unit)
            elif len(self.defensive_queens) < 8:
                self.defensive_queens.append(unit)
    
    async def on_building_construction_complete(self, unit: Unit):
        if unit.type_id == UnitTypeId.HATCHERY:
            self.hatches.append(unit)

run_game(maps.get("AcropolisLE"), [
    Bot(Race.Zerg, ZergoBot()),
    Computer(Race.Protoss, Difficulty.Medium)
], realtime=False)