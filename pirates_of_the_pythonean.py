import arcade
import arcade.gui as gui
import arcade.gui.widgets as widgets
import arcade.gui.widgets.text as text
import math
import time

UI_FONT = ("Bradley Hand", "calibri", "arial")
COMMAND_HUD_WIDTH = 200
SCREEN_TITLE = "Pirates of the Pythonean"
TILEMAP_SCALING = 0.2


def load_frames(file_name, frame_count):
    return [arcade.load_texture(f"./assets/sprites/{file_name}{i+1}.png") for i in range(frame_count)]


class AnimatedSprite(arcade.Sprite):

    def __init__(self, frames, fps, once=False):
        self.frames = frames
        self.fps = fps
        self.once = once
        self.timer = 0
        self.current_index = 0
        super().__init__(self.frames[0])

    def _load_frames(self, file_name, frame_count):
        self.frames = [arcade.load_texture(f"{file_name}{i+1}.png") for i in range(frame_count)]

    def update(self, delta_time = 1 / 60, *args, **kwargs):
        self.timer += delta_time
        if self.timer > (1 / self.fps):
            self.timer -= (1/self.fps)
            self.current_index = (self.current_index + 1) % len(self.frames)
            if self.once and self.current_index == 0:
                self.remove_from_sprite_lists()
            self.texture = self.frames[self.current_index]

class CannonBall(arcade.Sprite):
    def __init__(self, scene: arcade.Scene, x, y, angle, speed=12, max_range=500):
        super().__init__("assets/sprites/cannonball.png")

        self.scene = scene
        self.scene.game.sound_cannon_shoot.play()
        self.center_x = x
        self.center_y = y
        self.angle = angle

        angle_rad = math.radians(-angle)

        self.velocity_x = math.cos(angle_rad) * speed
        self.velocity_y = math.sin(angle_rad) * speed

        self.max_range = max_range
        self.distance_travelled = 0

        # Lose about 2% of speed every frame
        self.drag = 0.98

        self.is_dropping = False
        self.drop_timer = 0
        self.drop_duration = 0.2

    def update(self, delta_time=1 / 60):

        if self.is_dropping:
            self.drop_timer += delta_time

            progress = self.drop_timer / self.drop_duration
            self.scale = max(0.01, 1 * (1 - progress))

            if self.drop_timer >= self.drop_duration:
                self.remove_from_sprite_lists()
                if not arcade.check_for_collision_with_list(self, self.scene["Island"]):
                    self.scene.game.create_splash_effect(self.center_x, self.center_y)
                    self.scene.game.sound_cannon_water.play()

            return

        # Move
        self.center_x += self.velocity_x
        self.center_y += self.velocity_y

        # Distance travelled this frame
        frame_distance = math.hypot(self.velocity_x, self.velocity_y)
        self.distance_travelled += frame_distance

        # Slow down
        self.velocity_x *= self.drag
        self.velocity_y *= self.drag

        # Drop when out of energy
        if (
            self.distance_travelled >= self.max_range
            or frame_distance < 0.4
        ):
            self.start_drop()

    def start_drop(self):
        self.is_dropping = True
        self.velocity_x = 0
        self.velocity_y = 0


class Cannon(arcade.Sprite):
    def __init__(self, scene: arcade.Scene, offset, angle_offset):
        super().__init__("assets/sprites/cannon.png", scale=TILEMAP_SCALING*1.4)
        self.scene = scene
        self.offset = offset
        self.angle_offset = angle_offset
        self.cooldown = 1.5
        self.last_shot_time = 0

    def update_from_ship(self, ship):
        ox, oy = self.offset
        angle = math.radians(-ship.angle)

        world_x = ox * math.cos(angle) - oy * math.sin(angle)
        world_y = ox * math.sin(angle) + oy * math.cos(angle)

        self.center_x = ship.center_x + world_x
        self.center_y = ship.center_y + world_y
        self.angle = ship.angle + self.angle_offset

    def can_shoot(self):
        return time.time() - self.last_shot_time > self.cooldown

    def shoot(self):
        self.last_shot_time = time.time()

        ball = CannonBall(self.scene, self.center_x, self.center_y, self.angle)
        ball.center_x = self.center_x
        ball.center_y = self.center_y
        ball.angle = self.angle

        speed = 10
        angle = math.radians(-self.angle)

        ball.change_x = math.cos(angle) * speed
        ball.change_y = math.sin(angle) * speed

        self.scene.add_sprite("Cannonballs", ball)
        return ball


class EnemyPirate(arcade.Sprite):
    def __init__(self, scene: arcade.Scene):
        super().__init__("assets/sprites/enemy.png", scale=TILEMAP_SCALING)
        self.scene = scene
        self.is_destroyed = False

        self.left_cannon = Cannon(self.scene, offset=(TILEMAP_SCALING *42, TILEMAP_SCALING * 33), angle_offset=-90)
        self.right_cannon = Cannon(self.scene, offset=(TILEMAP_SCALING * 42, TILEMAP_SCALING * -33), angle_offset=90)

        self.cannons = [
            self.left_cannon,
            self.right_cannon,
        ]

    def update(self, delta_time = 1 / 60, *args, **kwargs):
        super().update(delta_time)
        self.update_cannons()

    def update_cannons(self):
        for cannon in self.cannons:
            cannon.update_from_ship(self)

    def destroy(self, cannonball):
        self.scene.game.create_explosion_effect(cannonball.center_x, cannonball.center_y)
        self.scene.game.sound_ship_destroyed.play()
        self.texture = self.scene.game.enemy_dead_texture
        cannonball.remove_from_sprite_lists()
        self.is_destroyed = True
        print("enemy destroyed")
    

class Player(arcade.Sprite):
    def __init__(self, scene: arcade.Scene):
        super().__init__("assets/sprites/player.png", TILEMAP_SCALING)
        self.scene = scene
        self.cannon = Cannon(
            scene,
            offset=(TILEMAP_SCALING * 100, 0),
            angle_offset=0
        )

    def update(self, delta_time = 1 / 60, *args, **kwargs):
        super().update(delta_time)
        self.cannon.update_from_ship(self)


# -----------------------------
# GAME
# -----------------------------

class PirateGame(arcade.Window):
    def __init__(self, level, commands):
        self.level = level
        self.commands = commands
        # load tilemap to set the size
        layer_options = {
            "Island": {
                "use_spatial_hash": True
            },
            "Water": {
                "use_spatial_hash": True
            }
        }
        self.tilemap = arcade.load_tilemap(self.level, scaling=TILEMAP_SCALING, layer_options=layer_options)
        window_width = self.tilemap.width * self.tilemap.tile_width * TILEMAP_SCALING + COMMAND_HUD_WIDTH
        window_height = self.tilemap.height * self.tilemap.tile_height * TILEMAP_SCALING
        

        super().__init__(title=SCREEN_TITLE, width=window_width, height=window_height)
        viewport_scene = arcade.rect.LBWH(COMMAND_HUD_WIDTH, 0, self.width-COMMAND_HUD_WIDTH, self.height)
        self.scene_camera = arcade.Camera2D(viewport=viewport_scene)
        viewport_hud = arcade.rect.LBWH(0, 0, self.width, self.height)
        self.hud_camera = arcade.Camera2D(viewport=viewport_hud)
        arcade.set_background_color(arcade.color.LIGHT_SKY_BLUE)
        
        self.explosion_frames = load_frames("explosion", 3)
        self.splash_frames = load_frames("splash", 4)
        self.player_dead_texture = arcade.load_texture("assets/sprites/player_dead.png")
        self.enemy_dead_texture = arcade.load_texture("assets/sprites/enemy_dead.png")
        self.collected_goals = 0
        self.collecting_sprite = arcade.Sprite("./assets/sprites/collecting.png", scale=1)
        self.collecting_sprite.change_angle = 5
        self.collecting_sprite_list = arcade.SpriteList()
        self.collecting_sprite_list.append(self.collecting_sprite)
        
        self.load_sound()
        self.start()

    def get_scene_bounds(self):
        map_width = self.tilemap.width * self.tilemap.tile_width * TILEMAP_SCALING
        map_height = self.tilemap.height * self.tilemap.tile_height * TILEMAP_SCALING
        return 0, map_width, 0, map_height

    def get_player_move_bounds(self):
        min_x, max_x, min_y, max_y = self.get_scene_bounds()
        player_radius = max(self.player.width, self.player.height) / 2
        return (
            min_x + player_radius,
            max_x - player_radius,
            min_y + player_radius,
            max_y - player_radius,
        )

    def clamp_player_position_to_scene(self, x, y):
        min_x, max_x, min_y, max_y = self.get_player_move_bounds()
        return (
            max(min_x, min(max_x, x)),
            max(min_y, min(max_y, y)),
        )
        

    def load_sound(self):
        self.sound_chest_moving = arcade.load_sound("./assets/sounds/chest_moving.wav")
        self.sound_chest_open = arcade.load_sound("./assets/sounds/chest_open.wav")
        self.sound_no_chest = arcade.load_sound("./assets/sounds/no_chest.wav")
        self.sound_cannon_shoot = arcade.load_sound("./assets/sounds/cannon_shoot.wav")
        self.sound_cannon_water = arcade.load_sound("./assets/sounds/cannon_water.wav")
        self.sound_ship_destroyed = arcade.load_sound("./assets/sounds/ship_destroyed.wav")
        self.sound_ship_move = arcade.load_sound("./assets/sounds/ship_move.wav")
        self.sound_win = arcade.load_sound("./assets/sounds/win.wav")
        self.sound_playback = None

        # start playing ambience sound in a loop
        self.ambience_sound = arcade.load_sound("./assets/sounds/ambience.wav")
        self.ambience_sound.play(volume=0.5, loop=True)

    def create_hud(self):
        self.hud = gui.UIManager()
        layout = gui.UIAnchorLayout()

        # TREASURE HUD
        treasure_hud = gui.UIBoxLayout(vertical=False, space_between=15)
        treasure_img = gui.UIImage(texture=arcade.load_texture("./assets/sprites/chest.png"), width=45, height=45)
        self.collected_label = text.UILabel("0/1", font_size=20, font_name=UI_FONT, text_color=arcade.color.DARK_BLUE)
        treasure_hud.add(treasure_img)
        treasure_hud.add(self.collected_label)
        layout.add(treasure_hud, anchor_x="right", anchor_y="top", align_x=-10, align_y=-5)

        # COMMAND HUD
        print("Height: ", self.height)
        self.command_hud = gui.UIBoxLayout(vertical=True, space_between=10, width=COMMAND_HUD_WIDTH, height=self.height, align="left")
        self.command_hud.with_background(color=arcade.color.LIGHT_SKY_BLUE)
        for c in self.commands:
            c, *args = c
            c_text = f"{c}({", ".join(map(str,args))})"
            label = text.UILabel(
                c_text, font_size=12, font_name=("Menlo", "Monaco", "Courier New"), 
                text_color=arcade.color.DARK_BLUE, bold=True)
            self.command_hud.add(label)

        layout.add(self.command_hud, anchor_x="left", anchor_y="top", align_x=10, align_y=-10)

        self.hud.add(layout)


    def start(self):
        self.create_hud()
        self.is_game_over = False
        self.command_index = -1
        self.scene = arcade.Scene.from_tilemap(self.tilemap)
        self.scene.game = self # a bit hacky back reference


        self.current_action = None
        self.current_cannon_ball = None

        self.move_target_x = 0
        self.move_target_y = 0
        self.turn_target_angle = 0

        self.message = "Drücke LEERTASTE, um deinen Code zu starten!"

        self.spawn_entities()
    
    def go(self):
        self.command_index = 0
        self.message = "Läuft..."

    def spawn_entities(self):
        entity_sprites = self.scene["Entities"]
        self.goal_target = 0
        
        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("Goals")
        self.scene.add_sprite_list("Enemies", True)
        self.scene.add_sprite_list("Cannons")
        self.scene.add_sprite_list("Cannonballs", True)
        self.scene.add_sprite_list("Effects")

        for obj in entity_sprites:
            entity_type = obj.properties.get("type")

            if entity_type == "player":
                self.player = Player(self.scene)
                self.player.center_x = obj.center_x
                self.player.center_y = obj.center_y
                self.player.angle = obj.angle
                self.scene.add_sprite("Cannons", self.player.cannon)
                self.player.cannon.update_from_ship(self.player)
                self.scene.add_sprite("Player", self.player)

            if entity_type == "goal":
                print("add goal")
                self.goal_target += 1
                goal = arcade.Sprite("assets/sprites/goal.png", scale=TILEMAP_SCALING)
                goal.center_x = obj.center_x
                goal.center_y = obj.center_y
                goal.angle = obj.angle
                self.scene.add_sprite("Goals", goal)

            elif entity_type == "enemy":
                enemy = EnemyPirate(self.scene)
                enemy.center_x = obj.center_x
                enemy.center_y = obj.center_y
                enemy.angle = obj.angle
                self.scene.add_sprite("Enemies", enemy)

                for cannon in enemy.cannons:
                    self.scene.add_sprite("Cannons", cannon)

        self.scene.remove_sprite_list_by_name("Entities")

    def on_draw(self):
        self.clear()
        self.scene_camera.use()
        self.scene.draw()

        arcade.draw_text(self.message, 20, 20, arcade.color.DARK_BLUE, 18, font_name=UI_FONT)

        if self.current_action == "collect":
            self.collecting_sprite_list.draw()
        
        self.hud_camera.use()
        self.hud.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            if self.is_game_over:
                self.start()
            else:
                self.go()
            
        elif key == arcade.key.R:
            self.__init__()

    def create_animation_effect(self, frames, x, y, fps=4, once=True):
        effect = AnimatedSprite(frames, fps, once)
        effect.scale = TILEMAP_SCALING * 4
        effect.center_x = x
        effect.center_y = y
        self.scene.add_sprite("Effects", effect)

    def create_splash_effect(self, x, y):
        self.create_animation_effect(self.splash_frames, x, y, 10, True)

    def create_explosion_effect(self, x, y):
        self.create_animation_effect(self.explosion_frames, x, y, 4, True)

    def on_update(self, delta_time):
        # update whole scene
        self.scene.update(delta_time)
        self.collecting_sprite.update(delta_time)

        # cannonballs hit player?
        for b in arcade.check_for_collision_with_list(self.player, self.scene["Cannonballs"]):
            b.remove_from_sprite_lists()
            self.create_explosion_effect(b.center_x, b.center_y)
            self.game_over()

        # current cannonball hits enemy?
        if self.current_cannon_ball:
            hit_enemies = arcade.check_for_collision_with_list(self.current_cannon_ball, self.scene["Enemies"])
            if len(hit_enemies) > 0:
                hit_enemies[0].destroy(self.current_cannon_ball)
                self.current_cannon_ball = None
                

        if self.is_game_over:
            return
        
        if self.current_action is None and self.command_index != -1:
            self.start_next_action()

        if self.current_action:
            self.update_action()


        # player hits island?
        for colliding_island in arcade.check_for_collision_with_list(self.player, self.scene["Island"]):
            distance = math.dist(self.player.position, colliding_island.position)
            if distance < 160 * TILEMAP_SCALING:
                self.game_over()
                break
        
        # update enemy cannons
        for enemy in self.scene["Enemies"]:
            if enemy.is_destroyed:
                continue

            for cannon in enemy.cannons:
                if self.player_is_in_cannon_line(cannon):
                    if cannon.can_shoot():
                        cannon.shoot()

    def game_over(self):
        self.is_game_over = True
        self.current_action = None
        self.player.texture = self.player_dead_texture
        self.sound_ship_destroyed.play()
        self.message = "Spiel vorbei! Drücke LEERTASTE um Dich zurückzusetzen."


    def player_is_in_cannon_line(self, cannon):
        dx = self.player.center_x - cannon.center_x
        dy = self.player.center_y - cannon.center_y

        distance = math.hypot(dx, dy)

        if distance > 400:
            return False

        angle_to_player = math.degrees(math.atan2(dy, dx))

        # Convert because Arcade angles are clockwise
        cannon_angle_math = -cannon.angle

        difference = abs((angle_to_player - cannon_angle_math + 180) % 360 - 180)

        return difference < 10

    def start_next_action(self):
        command = self.commands[self.command_index]
        if self.command_index > 0:
            self.command_hud.children[self.command_index-1].with_background(color=(0,0,0,0))
        self.command_hud.children[self.command_index].with_background(color=arcade.color.YELLOW)
        self.command_index += 1
        command_name = command[0]
        print("start next action", command_name)

        if command_name == "fd":
            distance = command[1]
            angle_rad = math.radians(self.player.angle)
            target_x = self.player.center_x + math.cos(angle_rad) * distance
            target_y = self.player.center_y - math.sin(angle_rad) * distance
            self.move_target_x, self.move_target_y = self.clamp_player_position_to_scene(target_x, target_y)
            self.current_action = "move"

        elif command_name == "rt":
            self.turn_target_angle = self.player.angle + command[1]
            self.current_action = "turn"

        elif command_name == "lt":
            self.turn_target_angle = self.player.angle - command[1]
            self.current_action = "turn"

        elif command_name == "shoot":
            self.player.cannon.shoot()
            self.current_action = "shoot"
            self.current_cannon_ball = self.player.cannon.shoot()

        elif command_name == "collect":
            self.sound_playback = self.sound_chest_moving.play()
            self.collecting_sprite.center_x = self.player.center_x
            self.collecting_sprite.center_y = self.player.center_y + 30
            self.current_action = "collect"


    def update_action(self):
        if self.current_action == "move":
            speed = 1.5

            dx = self.move_target_x - self.player.center_x
            dy = self.move_target_y - self.player.center_y
            distance = math.hypot(dx, dy)

            if distance < speed:
                self.player.center_x = self.move_target_x
                self.player.center_y = self.move_target_y
                self.current_action = None
            else:
                new_x = self.player.center_x + dx / distance * speed
                new_y = self.player.center_y + dy / distance * speed
                self.player.center_x, self.player.center_y = self.clamp_player_position_to_scene(new_x, new_y)

        elif self.current_action == "turn":
            turn_speed = 2
            diff = self.turn_target_angle - self.player.angle

            if abs(diff) < turn_speed:
                self.player.angle = self.turn_target_angle
                self.current_action = None
            else:
                self.player.angle += turn_speed if diff > 0 else -turn_speed

        elif self.current_action == "shoot":
            if not (self.current_cannon_ball in self.scene["Cannonballs"]):
                self.current_action = None

        elif self.current_action == "collect":
            if not self.sound_chest_moving.is_playing(self.sound_playback):
                
                found_chest = False
                for goal in arcade.check_for_collision_with_list(self.player, self.scene["Goals"]):
                    self.sound_chest_open.play()
                    found_chest = True
                    self.collected_goals += 1
                    self.collected_label.text = f"{self.collected_goals}/{self.goal_target}"
                    if self.collected_goals == self.goal_target:
                        self.game_over = True
                        self.sound_win.play()
                        self.message = "Wunderbar, alle Schätze eingesammelt. Drücke die LEERTASTE, um neu zu starten."
                    break
                
                if not found_chest:
                    self.sound_no_chest.play()
                
                self.current_action = None