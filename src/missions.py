"""
missions.py — Mission & Objective System
==========================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : Provides a reusable mission framework with:
            • Objective   — a single tracked goal
            • Mission     — a named collection of objectives with a status
            • MissionManager — orchestrates the active mission

Mission statuses:
    NOT_STARTED → ACTIVE → COMPLETED  or  FAILED

Objective types:
    'breach'   — hack a specific terminal (tracked by label)
    'reach'    — enter a zone (tracked by proximity check)

How it connects:
    scenes.py creates a MissionManager when starting the game.
    Terminal breaches call mission_manager.on_terminal_breached(label).
    Extraction zone proximity calls mission_manager.check_extraction().
    The HUD reads mission_manager.get_hud_info() each frame.

First playable mission — "Sector Breach":
    1. Breach "Access Node Alpha"
    2. Breach "Data Terminal Gamma"
    3. Reach extraction zone

    Failure condition: player health reaches 0.
"""


# ══════════════════════════════════════════════════════════════════════════ #
#  Status constants
# ══════════════════════════════════════════════════════════════════════════ #
STATUS_NOT_STARTED = 'not_started'
STATUS_ACTIVE      = 'active'
STATUS_COMPLETED   = 'completed'
STATUS_FAILED      = 'failed'


# ══════════════════════════════════════════════════════════════════════════ #
#  Objective class
# ══════════════════════════════════════════════════════════════════════════ #
class Objective:
    """
    A single trackable goal within a mission.

    Attributes:
        description    : str   — displayed on the HUD
        obj_type       : str   — 'breach' or 'reach'
        required_count : int   — how many times to complete
        current_count  : int   — progress so far
        target_labels  : list  — terminal labels (for 'breach' type)
        completed      : bool  — derived from count comparison
    """

    def __init__(self, description, obj_type='breach',
                 required_count=1, target_labels=None):
        """
        Create an objective.

        Args:
            description    : str  — human‑readable text
            obj_type       : str  — 'breach' or 'reach'
            required_count : int  — completions needed
            target_labels  : list — terminal labels for 'breach' objectives
        """
        self.description    = description
        self.obj_type       = obj_type
        self.required_count = required_count
        self.current_count  = 0
        self.target_labels  = target_labels or []
        self.completed      = False

    def advance(self, amount=1):
        """Increment progress and check completion."""
        if self.completed:
            return  # already done — skip
        self.current_count = min(
            self.current_count + amount,
            self.required_count,
        )
        if self.current_count >= self.required_count:
            self.completed = True

    def get_progress_text(self):
        """Return a string like '1 / 2'."""
        return f'{self.current_count} / {self.required_count}'


# ══════════════════════════════════════════════════════════════════════════ #
#  Mission class
# ══════════════════════════════════════════════════════════════════════════ #
class Mission:
    """
    A named mission containing ordered objectives.

    Attributes:
        name       : str  — mission title
        objectives : list[Objective]
        status     : str  — one of the STATUS_* constants
    """

    def __init__(self, name, objectives):
        """
        Create a mission.

        Args:
            name       : str            — e.g. "Sector Breach"
            objectives : list[Objective] — ordered list of goals
        """
        self.name       = name
        self.objectives = objectives
        self.status     = STATUS_NOT_STARTED

    def start(self):
        """Activate the mission."""
        self.status = STATUS_ACTIVE

    def fail(self):
        """Mark the mission as failed."""
        self.status = STATUS_FAILED

    def complete(self):
        """Mark the mission as completed."""
        self.status = STATUS_COMPLETED

    def get_current_objective(self):
        """
        Return the first incomplete objective, or None if all done.
        """
        for obj in self.objectives:
            if not obj.completed:
                return obj
        return None   # all objectives complete

    def all_objectives_done(self):
        """Check if every objective is completed."""
        return all(obj.completed for obj in self.objectives)


# ══════════════════════════════════════════════════════════════════════════ #
#  MissionManager class
# ══════════════════════════════════════════════════════════════════════════ #
class MissionManager:
    """
    Manages the active mission and provides an API for the scene.

    Attributes:
        mission     : Mission or None
        _messages   : list[str] — queued feedback messages for the HUD
    """

    def __init__(self):
        """Create an empty manager."""
        self.mission   = None
        self._messages = []          # feedback message queue
        self._msg_timer = 0.0        # auto‑clear timer

    # ------------------------------------------------------------------ #
    #  Load & start
    # ------------------------------------------------------------------ #
    def load_mission(self, mission):
        """
        Set the active mission and start it.

        Args:
            mission : Mission
        """
        self.mission = mission
        self.mission.start()
        self._push_message(f'MISSION: {mission.name}')

    # ------------------------------------------------------------------ #
    #  Terminal breach hook
    # ------------------------------------------------------------------ #
    def on_terminal_breached(self, label):
        """
        Called when the player successfully hacks a terminal.
        Checks if the terminal is a mission target and advances
        the appropriate objective.

        Args:
            label : str — terminal label (e.g. "Access Node Alpha")
        """
        if self.mission is None or self.mission.status != STATUS_ACTIVE:
            return

        for obj in self.mission.objectives:
            if obj.completed:
                continue
            if obj.obj_type == 'breach' and label in obj.target_labels:
                obj.advance()
                if obj.completed:
                    self._push_message(f'OBJECTIVE COMPLETE: {obj.description}')
                else:
                    self._push_message(
                        f'Progress: {obj.get_progress_text()} — {obj.description}'
                    )
                break  # one terminal can only satisfy one objective at a time

    # ------------------------------------------------------------------ #
    #  Extraction zone check
    # ------------------------------------------------------------------ #
    def check_extraction(self):
        """
        Called when the player enters the extraction zone.

        Returns:
            str — 'complete', 'not_ready', or 'no_mission'
        """
        if self.mission is None or self.mission.status != STATUS_ACTIVE:
            return 'no_mission'

        # Find the 'reach' objective
        reach_obj = None
        for obj in self.mission.objectives:
            if obj.obj_type == 'reach':
                reach_obj = obj
                break

        if reach_obj is None:
            return 'no_mission'

        # Check if all breach objectives are done
        breach_done = all(
            o.completed for o in self.mission.objectives
            if o.obj_type == 'breach'
        )

        if not breach_done:
            self._push_message('Complete all objectives before extraction!')
            return 'not_ready'

        # All breach objectives done → complete the reach objective + mission
        reach_obj.advance()
        self.mission.complete()
        self._push_message('MISSION COMPLETE!')
        return 'complete'

    # ------------------------------------------------------------------ #
    #  Failure check
    # ------------------------------------------------------------------ #
    def check_failure(self, game_state):
        """
        Called each frame to check if the mission should fail.

        Args:
            game_state : GameState — to check player health.

        Returns:
            bool — True if the mission just failed.
        """
        if self.mission is None or self.mission.status != STATUS_ACTIVE:
            return False

        if not game_state.is_alive():
            self.mission.fail()
            self._push_message('MISSION FAILED — SYSTEMS OFFLINE')
            return True

        return False

    # ------------------------------------------------------------------ #
    #  Message queue
    # ------------------------------------------------------------------ #
    def _push_message(self, text):
        """Add a feedback message to the queue."""
        self._messages.append(text)
        self._msg_timer = 4.0   # show for 4 seconds

    def pop_message(self):
        """
        Get and remove the oldest message, or None.
        """
        if self._messages:
            return self._messages.pop(0)
        return None

    def update_timer(self, dt):
        """Tick the message display timer."""
        if self._msg_timer > 0:
            self._msg_timer -= dt

    # ------------------------------------------------------------------ #
    #  HUD info
    # ------------------------------------------------------------------ #
    def get_hud_info(self):
        """
        Return a dict of display values for the HUD.

        Returns:
            dict with keys:
                mission_name  : str
                objective     : str
                progress      : str
                status        : str
                message       : str or None
                show_message  : bool
        """
        if self.mission is None:
            return {
                'mission_name': 'NO MISSION',
                'objective':    '',
                'progress':     '',
                'status':       '',
                'message':      None,
                'show_message': False,
            }

        current_obj = self.mission.get_current_objective()

        # Determine status display
        if self.mission.status == STATUS_COMPLETED:
            status_text = '[ MISSION COMPLETE ]'
        elif self.mission.status == STATUS_FAILED:
            status_text = '[ MISSION FAILED ]'
        else:
            status_text = '[ ACTIVE ]'

        # Determine objective text
        if current_obj:
            obj_text  = current_obj.description
            prog_text = current_obj.get_progress_text()
        else:
            obj_text  = 'All objectives complete!'
            prog_text = ''

        # Pop a message if the timer is active
        msg = None
        show = False
        if self._msg_timer > 0 and self._messages:
            msg  = self._messages[0]
            show = True

        return {
            'mission_name': self.mission.name,
            'objective':    obj_text,
            'progress':     prog_text,
            'status':       status_text,
            'message':      msg,
            'show_message': show,
        }

    # ------------------------------------------------------------------ #
    #  Cleanup
    # ------------------------------------------------------------------ #
    def destroy(self):
        """Reset the manager."""
        self.mission    = None
        self._messages  = []
        self._msg_timer = 0.0


# ══════════════════════════════════════════════════════════════════════════ #
#  Mission factory — "Sector Breach"
# ══════════════════════════════════════════════════════════════════════════ #
def create_sector_breach_mission():
    """
    Build and return the first playable mission.

    Objectives:
        1. Breach 2 required terminals (Alpha + Gamma)
        2. Reach extraction zone

    Returns:
        Mission
    """
    objectives = [
        Objective(
            description='Breach required terminals',
            obj_type='breach',
            required_count=2,
            target_labels=['Access Node Alpha', 'Data Terminal Gamma'],
        ),
        Objective(
            description='Reach extraction zone',
            obj_type='reach',
            required_count=1,
        ),
    ]
    return Mission(name='SECTOR BREACH', objectives=objectives)
