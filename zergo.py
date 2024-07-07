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
from sc2.units import Units
import numpy as np
from antony import IncrediBot

class ZergoBot(BotAI):

    macroing = True
    defensive_queens = []
    injecting_queens = []
    hatches = []
    scout = None

    async def on_step(self, iteration: int):
        if iteration == 0:
            self.hatches.append(self.townhalls.first)
            self.scout = self.units.of_type(UnitTypeId.OVERLORD).first.tag
            self.units.by_tag(self.scout).move(self.enemy_start_locations[0])

        enemy_advantage = self.count_supply(self.enemy_units.exclude_type(UnitTypeId.PROBE)) - self.supply_army
        if enemy_advantage > 4:
            #await self.chat_send("danger " + str(diff))
            self.macroing = False
        elif self.supply_workers >= 4*22 and self.townhalls.amount >= 4:
            #await self.chat_send("based")
            self.macroing = False
        else:
            #await self.chat_send("no danger " + str(diff))
            self.macroing = True

        await self.control_army()
        await self.inject()
        await self.distribute_workers()
        await self.produce_overlords()
        await self.produce_units()
        await self.techup()
    
    async def control_army(self):
        army_units = self.units.exclude_type(UnitTypeId.DRONE).exclude_type(UnitTypeId.OVERLORD).exclude_type(UnitTypeId.LARVA).exclude_type(UnitTypeId.QUEEN)

        if self.units.find_by_tag(self.scout):
            visible_enemies = self.enemy_units.visible.further_than(self.units.by_tag(self.scout).sight_range+2, self.units.by_tag(self.scout))
        else:
            visible_enemies = self.enemy_units.visible

        if visible_enemies.amount == 0:
            for u in army_units:
                if u.is_idle:
                    u.attack(self.hatches[-1].position)
        else:
            for u in army_units:
                #if u.is_idle:
                    u.attack(visible_enemies.closest_to(u).position)
        
        for v in visible_enemies:
            if not self.has_creep(v):
                visible_enemies.remove(v)
        
        if visible_enemies.amount > 0:
            for q in self.defensive_queens:
                if q.is_idle:
                    q.attack(visible_enemies.closest_to(q))

        if self.supply_army + self.supply_workers >= 195:
            for u in army_units:
                if u.is_idle:
                    u.attack(self.enemy_start_locations[0])


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
        if self.townhalls.amount >= 2 and self.structures.of_type(UnitTypeId.SPAWNINGPOOL).amount == 0 and self.already_pending(UnitTypeId.SPAWNINGPOOL) <= 0:
            if self.can_afford(UnitTypeId.SPAWNINGPOOL):
                to_center = self.start_location.towards(self.game_info.map_center, distance=5)
                await self.build(UnitTypeId.SPAWNINGPOOL, to_center, placement_step=1)
        # zergling speed
        elif not self.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED) and self.can_afford(UpgradeId.ZERGLINGMOVEMENTSPEED):
            self.research(UpgradeId.ZERGLINGMOVEMENTSPEED)
            #self.structures.of_type(UnitTypeId.SPAWNINGPOOL).random.research(UpgradeId.ZERGLINGMOVEMENTSPEED)
        
        # build evolution chamber
        if (self.structures.of_type(UnitTypeId.EVOLUTIONCHAMBER).amount + self.already_pending(UnitTypeId.EVOLUTIONCHAMBER)) < 2:
            if self.macroing or (self.supply_workers >= 3*20 and self.townhalls.ready.amount >= 3):
                if self.townhalls.ready.amount >= 2 and self.supply_workers >= (2*15):
                    if self.can_afford(UnitTypeId.EVOLUTIONCHAMBER):
                        await self.chat_send("three")
                        to_center = self.start_location.towards(self.game_info.map_center, distance=5)
                        await self.build(UnitTypeId.EVOLUTIONCHAMBER, to_center, placement_step=1)
        # upgrades
        elif self.macroing:
            if not self.already_pending_upgrade(UpgradeId.ZERGMELEEWEAPONSLEVEL1):
                if self.can_afford(UpgradeId.ZERGMELEEWEAPONSLEVEL1):
                    self.research(UpgradeId.ZERGMELEEWEAPONSLEVEL1)
            elif not self.already_pending_upgrade(UpgradeId.ZERGMELEEWEAPONSLEVEL2):
                if self.can_afford(UpgradeId.ZERGMELEEWEAPONSLEVEL2):
                    self.research(UpgradeId.ZERGMELEEWEAPONSLEVEL2)
            elif not self.already_pending_upgrade(UpgradeId.ZERGMELEEWEAPONSLEVEL3):
                if self.can_afford(UpgradeId.ZERGMELEEWEAPONSLEVEL3):
                    self.research(UpgradeId.ZERGMELEEWEAPONSLEVEL3)
            
            if not self.already_pending_upgrade(UpgradeId.ZERGGROUNDARMORSLEVEL1):
                if self.can_afford(UpgradeId.ZERGGROUNDARMORSLEVEL1):
                    self.research(UpgradeId.ZERGGROUNDARMORSLEVEL1)
            elif not self.already_pending_upgrade(UpgradeId.ZERGGROUNDARMORSLEVEL2):
                if self.can_afford(UpgradeId.ZERGGROUNDARMORSLEVEL2):
                    self.research(UpgradeId.ZERGGROUNDARMORSLEVEL2)
            elif not self.already_pending_upgrade(UpgradeId.ZERGGROUNDARMORSLEVEL3):
                if self.can_afford(UpgradeId.ZERGGROUNDARMORSLEVEL3):
                    self.research(UpgradeId.ZERGGROUNDARMORSLEVEL3)

        # lair
        if self.structures.of_type(UnitTypeId.LAIR).amount < 1:
            if self.can_afford(AbilityId.UPGRADETOLAIR_LAIR):
                self.townhalls.first(AbilityId.UPGRADETOLAIR_LAIR)

        # infestation pit
        if self.structures.of_type(UnitTypeId.INFESTATIONPIT).amount < 1 and self.already_pending(UnitTypeId.INFESTATIONPIT) <= 0:
            if self.can_afford(UnitTypeId.INFESTATIONPIT):
                to_center = self.start_location.towards(self.game_info.map_center, distance=5)
                await self.build(UnitTypeId.INFESTATIONPIT, to_center, placement_step=1)
        
        # hive
        if self.structures.of_type(UnitTypeId.HIVE).amount < 1 and self.structures.ready.of_type(UnitTypeId.LAIR).amount >= 1:
            if self.can_afford(AbilityId.UPGRADETOHIVE_HIVE):
                self.structures.ready.of_type(UnitTypeId.LAIR).first(AbilityId.UPGRADETOHIVE_HIVE)
        
        # ultralisk cavern
        if self.structures.of_type(UnitTypeId.ULTRALISKCAVERN).amount < 1 and self.already_pending(UnitTypeId.ULTRALISKCAVERN) <= 0:
            if self.can_afford(UnitTypeId.ULTRALISKCAVERN):
                to_center = self.start_location.towards(self.game_info.map_center, distance=5)
                await self.build(UnitTypeId.ULTRALISKCAVERN, to_center, placement_step=1)
        else:
            # chitinous plating
            if not self.already_pending_upgrade(UpgradeId.CHITINOUSPLATING) and self.can_afford(UpgradeId.CHITINOUSPLATING):
                self.research(UpgradeId.CHITINOUSPLATING)
            # anabolic synthesis
            if not self.already_pending_upgrade(UpgradeId.ANABOLICSYNTHESIS) and self.can_afford(UpgradeId.ANABOLICSYNTHESIS):
                self.research(UpgradeId.ANABOLICSYNTHESIS)

    async def produce_units(self):
        if self.macroing:
            # get first gas
            if self.supply_workers >= 16 and self.gas_buildings.amount <= 0 and not self.already_pending(UnitTypeId.EXTRACTOR):
                gas_location = self.vespene_geyser.closest_to(self.townhalls.first)
                await self.build(UnitTypeId.EXTRACTOR, gas_location)

            # expand
            if self.already_pending(UnitTypeId.HATCHERY) == 0 and self.supply_workers >= self.townhalls.amount * 8 and self.can_afford(UnitTypeId.HATCHERY):
                await self.expand_now()
            
            # gas
            if self.townhalls.amount >= 3 and self.supply_workers >= 3*16:
                for t in self.townhalls.ready:
                    gas_spots = self.vespene_geyser.closer_than(10, t)
                    for g in gas_spots:
                        if not self.is_geyser_at_location(g.position) and self.can_afford(UnitTypeId.EXTRACTOR):
                            await self.build(UnitTypeId.EXTRACTOR, g)
            
            # drones
            while self.supply_workers < (self.townhalls.ready.amount * 16) + (self.gas_buildings.ready.amount * 3) and self.can_afford(UnitTypeId.DRONE) and self.larva:
                self.larva.random(AbilityId.LARVATRAIN_DRONE, subtract_cost=True, subtract_supply=True)

        else:
            if self.structures.ready.of_type(UnitTypeId.ULTRALISKCAVERN).amount >= 1:
                while self.can_afford(UnitTypeId.ULTRALISK) and self.larva:
                    self.larva.random(AbilityId.LARVATRAIN_ULTRALISK, subtract_cost=True, subtract_supply=True)
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
    
    def count_supply(self, units):
        supply = 0
        if units:
            for u in units:
                supply += self.game_data.units[u.type_id.value]._proto.food_required
        return supply
    
    def is_geyser_at_location(self, location):
        for g in self.gas_buildings:
            if g.position.is_same_as(location):
                return True
        return False
    
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
'''
run_game(maps.get("AcropolisLE"), [
    Bot(Race.Zerg, ZergoBot()),
    Bot(Race.Protoss, IncrediBot())
], realtime=True)'''