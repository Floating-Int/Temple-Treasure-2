from displaylib import *
import keyboard


ALPHABETH = "abcdefghijklmnopqrstuvwxyz" # used for key/door color parsing

class Player(Sprite):
    left = "a"
    right = "d"
    up = "w"
    down = "s"
    inventory = []

    def is_moving_left(self) -> bool:
        return keyboard.is_pressed(self.left)
    
    def is_moving_right(self) -> bool:
        return keyboard.is_pressed(self.right)

    def is_moving_up(self) -> bool:
        return keyboard.is_pressed(self.up)

    def is_moving_down(self) -> bool:
        return keyboard.is_pressed(self.down)

class Player1(Player):
    texture = [["1"]]
    left = "a"
    right = "d"
    up = "w"
    down = "s"

class Player2(Player):
    texture = [["2"]]
    right = "l"
    left = "j"
    up = "i"
    down = "k"

class Wall(Sprite):
    texture = [["#"]]

class Key(Sprite):
    texture = [["!"]]
    code = 0

class Door(Sprite):
    texture = [["&"]]
    lock = 0

class Goal(Sprite):
    texture = [["?"]]


class App(Engine):
    def _on_start(self) -> None:
        Screen.cell_default = " "
        self.players: list[Player] = []
        self.keys: list[Key] = []
        self.doors: list[Door] = []
        self.goal: Goal = None
        # -- load map
        self.world_map = Sprite.load("./map1.txt")
        self.screen.width = self.world_map.size().x
        self.screen.height = self.world_map.size().y
        # -- parse world_data
        self.parse_world_data_from(self.world_map)
    
    def parse_world_data_from(self, world_map: list[list[str]]) -> None:
        for y, line in enumerate(world_map.texture):
            for x, char in enumerate(line):
                if char == Key.texture[0][0]:
                    key = Key(x=x, y=y).as_unique()
                    raw_code = world_map.texture[y][x+1]
                    if raw_code.isupper(): # should be replaced with wall
                        world_map.texture[y][x+1] = Wall.texture[0][0]
                    else:
                        world_map.texture[y][x+1] = Screen.cell_transparant
                    key.code = raw_code.lower()
                    key.color = color.color(fg=ALPHABETH.index(key.code))
                    self.keys.append(key)
                elif char == Door.texture[0][0]:
                    door = Door(x=x, y=y).as_unique()
                    raw_lock = self.world_map.texture[y][x+1]
                    if raw_lock.isupper(): # should be replaced with wall
                        world_map.texture[y][x+1] = Wall.texture[0][0]
                    else:
                        world_map.texture[y][x+1] = Screen.cell_transparant
                    door.lock = raw_lock.lower()
                    door.color = color.color(fg=ALPHABETH.index(door.lock))
                    self.doors.append(door)
                elif char == Goal.texture[0][0]:
                    self.goal = Goal(x=x, y=y, z_index=1, color=color.color(13)).as_unique()
                elif char == Player1.texture[0][0]:
                    player = Player1(x=x, y=y)
                    self.players.append(player)
                    world_map.texture[y][x] = Screen.cell_transparant
                elif char == Player2.texture[0][0]:
                    player = Player2(x=x, y=y)
                    self.players.append(player)
                    world_map.texture[y][x] = Screen.cell_transparant

    def _update(self, _delta: float) -> None:
        # -- move players if not blocked
        for player in self.players:
            old_position = player.position.copy()
            if player.is_moving_left():
                player.position.x -= 1
            if player.is_moving_right():
                player.position.x += 1
            # x-axis check
            self.do_collision_check_on(player, old_position)
            old_position = player.position.copy()
            if player.is_moving_up():
                player.position.y -= 1
            if player.is_moving_down():
                player.position.y += 1
            # y-axis check
            self.do_collision_check_on(player, old_position)
    
    def do_collision_check_on(self, player: Player, old_position: Vec2) -> None:
        # snaps back to old_position if player at invalid spot
        if not (0 <= player.position.x < self.world_map.size().x) or not (0 <= player.position.y < self.world_map.size().y):
            player.position = old_position
            return
        elif self.world_map.texture[player.position.y][player.position.x] == Wall.texture[0][0]:
            player.position = old_position
        elif self.world_map.texture[player.position.y][player.position.x] == Key.texture[0][0]:
            for key in self.keys:
                if key.position == player.position:
                    player.inventory.append(key.code)
                    self.keys.remove(key)
                    key.queue_free()
                    self.world_map.texture[player.position.y][player.position.x] = Screen.cell_transparant
        elif self.world_map.texture[player.position.y][player.position.x] == Door.texture[0][0]:
            found = False
            for door in self.doors:
                if door.position == player.position:
                    for code in player.inventory:
                        if code == door.lock:
                            self.doors.remove(door)
                            door.queue_free()
                            # player.inventory.remove(code)
                            self.world_map.texture[player.position.y][player.position.x] = Screen.cell_transparant
                            found = True
                            break
                    if found:
                        break
            if not found:
                player.position = old_position
        elif player.position == self.goal.position:
            self.world_map.texture[player.position.y][player.position.x] == Screen.cell_transparant
            self.is_running = False # won the game

    def _on_exit(self) -> None:
        label = Label(text="You won!", x=self.goal.position.x-4, y=self.goal.position.y-1, color=color.color(13))


if __name__ == "__main__":
    app = App()
