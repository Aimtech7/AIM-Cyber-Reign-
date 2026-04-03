"""
upgrades.py — Cybernetics Upgrades Menu (Phase 9.2)
=====================================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : UI for spending Cyber-Credits on permanent player buffs.
"""

from ursina import Entity, Text, color, camera, Button, destroy as ursina_destroy
from src.config import MENU_BG, NEON_CYAN, NEON_MAGENTA, NEON_GREEN, NEON_YELLOW, BUTTON_COLOR, SFX_CLICK
from src.save_system import load_profile, save_profile

class UpgradesMenu:
    """
    Shows available cybernetic upgrades and handles purchasing logic.
    """

    def __init__(self, back_callback, audio_manager=None):
        self._audio = audio_manager
        self.back_callback = back_callback
        self.elements = []
        
        # Load profile
        self.credits, self.upgrades = load_profile()
        
        # Baseline prices
        self.prices = {
            'max_health': 300,
            'speed': 300,
            'hack_time': 300,
        }

        # Background
        bg = Entity(parent=camera.ui, model='quad', scale=(3, 3),
                     color=color.rgb(*MENU_BG), z=1)
        self.elements.append(bg)

        # Title
        title = Text(text='[ CYBERNETIC UPGRADES ]', parent=camera.ui,
                      position=(0, 0.40), origin=(0, 0),
                      scale=2.5, color=color.rgb(*NEON_CYAN),
                      font='VeraMono.ttf')
        self.elements.append(title)

        # Credits display
        self.credits_text = Text(text=f'AVAILABLE CREDITS: {self.credits} CR',
                                 parent=camera.ui, position=(0, 0.32), origin=(0, 0),
                                 scale=1.5, color=color.rgb(*NEON_YELLOW),
                                 font='VeraMono.ttf')
        self.elements.append(self.credits_text)
        
        sep = Entity(parent=camera.ui, model='quad', scale=(0.6, 0.002),
                     position=(0, 0.28), color=color.rgb(*NEON_CYAN), z=0)
        self.elements.append(sep)

        # Build store items
        self._build_item(0.15, 'max_health', 'SUB-DERMAL PLATING (+HP)')
        self._build_item(0.00, 'speed', 'SYNTHETIC MUSCLES (+SPEED)')
        self._build_item(-0.15, 'hack_time', 'NEURAL PROCESSOR (-HACK TIME)')

        # Back Button
        btn = Button(
            text='>> BACK <<', parent=camera.ui, position=(0, -0.35),
            scale=(0.3, 0.06), color=color.rgb(*BUTTON_COLOR),
            highlight_color=color.rgb(*NEON_PURPLE) if 'NEON_PURPLE' in globals() else color.rgb(150, 0, 150)
        )
        btn.text_entity.font = 'VeraMono.ttf'
        btn.text_entity.color = color.rgb(200, 200, 200)

        def click_wrapper():
            if self._audio: self._audio.play_sfx(SFX_CLICK)
            self.back_callback()
            
        btn.on_click = click_wrapper
        self.elements.append(btn)
        
    def _build_item(self, y_pos, key, label):
        """Build UI elements for a single upgrade row."""
        current_lvl = self.upgrades.get(key, 0)
        cost = self.prices[key] + (current_lvl * 150) # Price scales with level
        max_level = 5
        
        # Name
        name_txt = Text(text=f'{label}', parent=camera.ui,
                        position=(-0.35, y_pos), origin=(-0.5, 0),
                        scale=1.1, color=color.rgb(200, 200, 220), font='VeraMono.ttf')
        self.elements.append(name_txt)
        
        # Level indicator
        lvl_txt = Text(text=f'LVL {current_lvl}/{max_level}', parent=camera.ui,
                       position=(0.0, y_pos), origin=(0, 0),
                       scale=1.1, color=color.rgb(*NEON_CYAN) if current_lvl < max_level else color.rgb(*NEON_GREEN),
                       font='VeraMono.ttf')
        self.elements.append(lvl_txt)
        
        # Purchase Button
        if current_lvl < max_level:
            btn_txt = f'BUY ({cost} CR)'
            btn_clr  = BUTTON_COLOR
        else:
            btn_txt = 'MAXED'
            btn_clr  = (50, 50, 50)
            
        btn = Button(text=btn_txt, parent=camera.ui, position=(0.25, y_pos),
                     scale=(0.25, 0.05), color=color.rgb(*btn_clr))
        btn.text_entity.font = 'VeraMono.ttf'
        
        if current_lvl < max_level:
            btn.on_click = lambda k=key, c=cost, bt=btn, lt=lvl_txt: self._purchase(k, c, bt, lt)
            
        self.elements.append(btn)

    def _purchase(self, key, cost, btn_ref, lvl_ref):
        if self.credits >= cost:
            # Play sound
            if self._audio: self._audio.play_sfx(SFX_CLICK)
            
            # Update data
            self.credits -= cost
            self.upgrades[key] = self.upgrades.get(key, 0) + 1
            
            # Save
            save_profile(self.credits, self.upgrades)
            
            # Refresh UI (lazy way is to just rebuild but we'll try in-place)
            self.credits_text.text = f'AVAILABLE CREDITS: {self.credits} CR'
            
            new_lvl = self.upgrades[key]
            new_cost = self.prices[key] + (new_lvl * 150)
            
            if new_lvl < 5:
                lvl_ref.text = f'LVL {new_lvl}/5'
                btn_ref.text = f'BUY ({new_cost} CR)'
                # update the lambda to reflect new cost
                btn_ref.on_click = lambda k=key, c=new_cost, bt=btn_ref, lt=lvl_ref: self._purchase(k, c, bt, lt)
            else:
                lvl_ref.text = f'LVL 5/5'
                lvl_ref.color = color.rgb(*NEON_GREEN)
                btn_ref.text = 'MAXED'
                btn_ref.color = color.rgb(50, 50, 50)
                btn_ref.on_click = None

    def destroy(self):
        for e in self.elements:
            try:
                ursina_destroy(e)
            except Exception:
                pass
        self.elements.clear()
