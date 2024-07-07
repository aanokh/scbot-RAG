from sc2.bot_ai import BotAI 
from sc2.data import Difficulty, Race  
from sc2.main import run_game  
from sc2.player import Bot, Computer
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId  
from sc2 import maps  
import time
import random
#from zergo import ZergoBot



class IncrediBot(BotAI): 
    async def on_step(self, iteration: int):
        nexus = self.townhalls.random
        
        time.sleep(0.01)

        await self.distribute_workers()

        if nexus.is_idle and self.can_afford(UnitTypeId.PROBE) and self.workers.amount < (17 * self.structures(UnitTypeId.NEXUS).amount):
            nexus.train(UnitTypeId.PROBE)

        if self.can_afford(UnitTypeId.PYLON) and self.already_pending(UnitTypeId.PYLON) == 0 and self.supply_used/self.supply_cap > 0.9:
            await self.build(UnitTypeId.PYLON, near=nexus)

        if self.can_afford(UnitTypeId.GATEWAY) and self.structures(UnitTypeId.GATEWAY).amount < 3 and self.structures(UnitTypeId.NEXUS).amount == 2:
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            await self.build(UnitTypeId.GATEWAY, near=pylon)

        if self.can_afford(UnitTypeId.NEXUS) and self.structures(UnitTypeId.NEXUS).amount < 3 and self.already_pending(UnitTypeId.NEXUS) == 0:
            await self.expand_now()
        #take gas
        if self.structures(UnitTypeId.ASSIMILATOR).amount < 3 and self.structures(UnitTypeId.NEXUS).amount > 1:
            vespenes = self.vespene_geyser.closer_than(15, nexus)
            for vespene in vespenes:
                if self.can_afford(UnitTypeId.ASSIMILATOR) and not self.already_pending(UnitTypeId.ASSIMILATOR):
                    await self.build(UnitTypeId.ASSIMILATOR, vespene)

        if self.structures(UnitTypeId.CYBERNETICSCORE).amount < 1 and self.can_afford(UnitTypeId.CYBERNETICSCORE) and self.structures(UnitTypeId.GATEWAY).ready.amount > 0 and self.structures(UnitTypeId.FORGE).amount > 0:
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            await self.build(UnitTypeId.CYBERNETICSCORE, near=pylon)

        if self.structures(UnitTypeId.CYBERNETICSCORE).ready.amount == 1 and self.can_afford(UnitTypeId.ROBOTICSFACILITY) and self.structures(UnitTypeId.ROBOTICSFACILITY).amount < 3 and self.structures(UnitTypeId.NEXUS).amount > 2:
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            await self.build(UnitTypeId.ROBOTICSFACILITY, near=pylon)

        if self.structures(UnitTypeId.ROBOTICSFACILITY).ready.amount > 0 and self.can_afford(UnitTypeId.ROBOTICSBAY) and self.structures(UnitTypeId.ROBOTICSBAY).amount < 1:
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            await self.build(UnitTypeId.ROBOTICSBAY, near=pylon)

        if self.structures(UnitTypeId.FORGE).amount < 1 and self.can_afford(UnitTypeId.FORGE) and self.structures(UnitTypeId.NEXUS).amount > 2:
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            await self.build(UnitTypeId.FORGE, near=pylon)
        
        if self.structures(UnitTypeId.FORGE).ready.idle.amount > 0 and self.can_afford(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL1):
            forge = self.structures(UnitTypeId.FORGE).ready.random
            self.do(forge.research(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL1))

        if self.structures(UnitTypeId.ROBOTICSFACILITY).amount > 0 and self.can_afford(UnitTypeId.GATEWAY) and self.structures(UnitTypeId.GATEWAY).amount < 4:
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            await self.build(UnitTypeId.GATEWAY, near=pylon)

        if self.structures(UnitTypeId.ROBOTICSFACILITY).ready.amount > 0 and self.units(UnitTypeId.OBSERVER).amount < 1:
            for r in self.structures(UnitTypeId.ROBOTICSFACILITY).ready.idle:
                if self.can_afford(UnitTypeId.OBSERVER):
                    r.train(UnitTypeId.OBSERVER)
        

        if self.structures(UnitTypeId.ROBOTICSFACILITY).ready.amount > 0:
            for r in self.structures(UnitTypeId.ROBOTICSFACILITY).ready.idle:
                if self.can_afford(UnitTypeId.COLOSSUS):
                    r.train(UnitTypeId.COLOSSUS)

        if self.structures(UnitTypeId.ROBOTICSFACILITY).ready.amount > 0:
            for r in self.structures(UnitTypeId.ROBOTICSFACILITY).ready.idle:
                if self.can_afford(UnitTypeId.IMMORTAL):
                    r.train(UnitTypeId.IMMORTAL)



        if self.structures(UnitTypeId.GATEWAY).ready.amount > 0 and self.structures(UnitTypeId.CYBERNETICSCORE).amount > 0:
            for g in self.structures(UnitTypeId.GATEWAY).ready.idle:
                if random.randint(1,2) == 1:
                    if self.can_afford(UnitTypeId.ZEALOT):
                        g.train(UnitTypeId.ZEALOT)
                else:
                    if self.can_afford(UnitTypeId.STALKER):
                        g.train(UnitTypeId.STALKER)
            

        # attack
        if self.units(UnitTypeId.ZEALOT).amount + self.units(UnitTypeId.STALKER).amount >= 4:
            if self.enemy_units:
                for z in self.units(UnitTypeId.ZEALOT).idle:
                    z.attack(random.choice(self.enemy_units))
                for i in self.units(UnitTypeId.IMMORTAL).idle:
                    i.attack(random.choice(self.enemy_units))
                for c in self.units(UnitTypeId.COLOSSUS).idle:
                    c.attack(random.choice(self.enemy_units))
                for o in self.units(UnitTypeId.OBSERVER).idle:
                    o.attack(random.choice(self.enemy_units))
                for s in self.units(UnitTypeId.STALKER).idle:
                    s.attack(random.choice(self.enemy_units))
            
            elif self.enemy_structures:
                for z in self.units(UnitTypeId.ZEALOT).idle:
                    z.attack(random.choice(self.enemy_structures))
                for i in self.units(UnitTypeId.IMMORTAL).idle:
                    i.attack(random.choice(self.enemy_structures))
                for c in self.units(UnitTypeId.COLOSSUS).idle:
                    c.attack(random.choice(self.enemy_structures))
                for o in self.units(UnitTypeId.OBSERVER).idle:
                    o.attack(random.choice(self.enemy_structures))
                for s in self.units(UnitTypeId.STALKER).idle:
                    s.attack(random.choice(self.enemy_structures))

            # attack enemy spawn
            elif self.units(UnitTypeId.IMMORTAL).amount > 0 and self.units(UnitTypeId.COLOSSUS).amount > 1:
                for z in self.units(UnitTypeId.ZEALOT).idle:
                    z.attack(self.enemy_start_locations[0])
                for i in self.units(UnitTypeId.IMMORTAL).idle:
                    i.attack(self.enemy_start_locations[0])
                for c in self.units(UnitTypeId.COLOSSUS).idle:
                    c.attack(self.enemy_start_locations[0])
                for o in self.units(UnitTypeId.OBSERVER).idle:
                    o.attack(self.enemy_start_locations[0])
                for s in self.units(UnitTypeId.STALKER).idle:
                    s.attack(self.enemy_start_locations[0])
                

        

run_game(
    maps.get("AcropolisLE"), 
    [Bot(Race.Protoss, IncrediBot()), 
     Computer(Race.Zerg, Difficulty.Hard)], 
    realtime=False, 
)