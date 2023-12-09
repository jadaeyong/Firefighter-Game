from dataclasses import dataclass
from designer import *
from random import randint

COPTER_SPEED = 5
WATER_DROP_SPEED = 5


@dataclass
class World:
    copter: DesignerObject
    copter_speed: int
    drops: list[DesignerObject]
    fires: list[DesignerObject]
    score: int
    counter: DesignerObject


def create_world() -> World:
    return World(create_copter(), COPTER_SPEED, [], [], 0,
                 text("black", "Score: 0", 20, 200, 8))


def create_copter() -> DesignerObject:
    copter = emoji("helicopter")
    copter.y = get_height() * (1 / 3)
    copter.flip_x = True
    return copter

def move_copter(world: World):
    world.copter.x += world.copter_speed


def bounce_copter(world: World):
    if world.copter.x > get_width():
        head_left(world)
    elif world.copter.x < 0:
        head_right(world)


def head_left(world: World):
    world.copter_speed = -COPTER_SPEED
    world.copter.flip_x = False


def head_right(world: World):
    world.copter_speed = COPTER_SPEED
    world.copter.flip_x = True


def flip_copter(world: World, key: str):
    if key == "left":
        head_left(world)
    elif key == "right":
        head_right(world)


def create_water_drop() -> DesignerObject:
    return circle("blue", 12)


def drop_water(world: World, key: str):
    if key == 'space':
        new_drop = create_water_drop()
        move_below(new_drop, world.copter)
        world.drops.append(new_drop)


def move_below(bottom: DesignerObject, top: DesignerObject):
    bottom.y = top.y + top.height / 2
    bottom.x = top.x


def make_water_fall(world: World):
    for drop in world.drops:
        drop.y += WATER_DROP_SPEED


def destroy_waters_on_landing(world: World):
    kept = []
    for drop in world.drops:
        if drop.y < get_height():
            kept.append(drop)
        else:
            destroy(drop)
    world.drops = kept


def create_fire() -> DesignerObject:
    fire = emoji('🔥')
    fire.scale_x = 0.1
    fire.scale_y = 0.1
    fire.anchor = 'midbottom'
    fire.x = randint(0, get_width())
    fire.y = get_height()
    return fire


def make_fires(world: World):
    if len(world.fires) < 5 and randint(0, 50) == 0:
        world.fires.append(create_fire())


def grow_fires(world: World):
    for fire in world.fires:
        fire.scale_x += 0.01
        fire.scale_y += 0.01


def there_are_big_fires(world: World) -> bool:
    """ Return True if there are any fires that are big """
    any_big_fires_so_far = False
    for fire in world.fires:
        any_big_fires_so_far = fire.scale_x > 5.0 or any_big_fires_so_far
    return any_big_fires_so_far


def colliding(obj1, obj2):
    return obj1.x < obj2.x + obj2.width and obj1.x + obj1.width > obj2.x and obj1.y < obj2.y + obj2.height and obj1.y + obj1.height > obj2.y


def collide_water_fire(world: World):
    destroyed_fires = []
    destroyed_drops = []
    for drop in world.drops:
        for fire in world.fires:
            if colliding(drop, fire):
                destroyed_drops.append(drop)
                destroyed_fires.append(fire)
                world.score += 1
    world.drops = filter_from(world.drops, destroyed_drops)
    world.fires = filter_from(world.fires, destroyed_fires)


def filter_from(old_list: list[DesignerObject], elements_to_not_keep: list[DesignerObject]) -> list[DesignerObject]:
    new_values = []
    for item in old_list:
        if item not in elements_to_not_keep:
            new_values.append(item)
        else:
            destroy(item)
    return new_values

def update_score(world: World):
    world.counter.text = "Score: " + str(world.score)

def flash_game_over(world: World):
    world.counter.text = "GAME OVER! Your score was " + str(world.score)

when("starting", create_world)
when("updating", move_copter)
when("updating", bounce_copter)
when("typing", flip_copter)
when("typing", drop_water)
when("updating", make_water_fall)
when("updating", destroy_waters_on_landing)
when("updating", make_fires)
when("updating", grow_fires)
when("updating", collide_water_fire)
when("updating", update_score)
when(there_are_big_fires, flash_game_over, pause)
start()
