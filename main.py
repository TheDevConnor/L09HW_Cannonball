from math import sin, cos, radians

import altair as alt
import pandas as pd
import streamlit as st
import random

class Print_Iface:
    """Handles all plot/chart rendering for the cannonball simulation."""

    def main_print(self, xs, ys, title="Cannonball Trajectory"):
        """Build and display an Altair line chart from trajectory data."""
        if not xs:
            st.warning("No trajectory points were generated.")
            return

        df = pd.DataFrame({"x": xs, "y": ys})

        chart = (
            alt.Chart(df)
            .mark_line()
            .encode(
                x=alt.X("x:Q", scale=alt.Scale(domain=[0, max(xs) * 1.1 + 10]), title="Distance (m)"),
                y=alt.Y("y:Q", scale=alt.Scale(domain=[0, max(ys) * 1.2 + 5]), title="Height (m)"),
            )
            .properties(width=700, height=400, title=title)
        )
        st.altair_chart(chart, use_container_width=True)

class Cannonball:
    """Represent a cannonball, tracking its position and velocity."""

    def __init__(self, x):
        self._x = x
        self._y = 0
        self._vx = 0
        self._vy = 0
        # Composition: Cannonball HAS-A Print_Iface
        self._printer = Print_Iface()

    def move(self, sec, grav):
        """Move the cannon ball using its current velocities."""
        dx = self._vx * sec
        dy = self._vy * sec
        self._vy = self._vy - grav * sec
        self._x = self._x + dx
        self._y = self._y + dy

    def getX(self):
        """Get the current x position."""
        return self._x

    def getY(self):
        """Get the current y position."""
        return self._y

    def shoot(self, angle, velocity, user_grav, step=0.1):
        """Shoot the cannon ball and return trajectory data."""
        self._vx = velocity * cos(angle)
        self._vy = velocity * sin(angle)
        self.move(step, user_grav)

        xs = []
        ys = []

        while self.getY() > 1e-14:
            xs.append(self.getX())
            ys.append(self.getY())
            self.move(step, user_grav)

        # Delegate plotting to the composed Print_Iface
        self._printer.main_print(xs, ys, title="Cannonball Trajectory")
        return xs, ys

class Crazyball(Cannonball):
    """
    Inherits from Cannonball.
    Overrides move() to add randomness to the trajectory
    when the ball is within the first 400 m of travel.
    """

    def __init__(self, x):
        super().__init__(x)
        self.x = x  # exposed attribute per UML

    def move(self, sec, grav):
        """Move with random jitter applied when x < 400."""
        # Call parent move first
        super().move(sec, grav)

        # Add randomness when within first 400 m
        self.rand_q = random.randrange(0, 10)
        if self.getX() < 400:
            # Randomly perturb position
            self._x += random.uniform(-self.rand_q, self.rand_q)
            self._y += random.uniform(-self.rand_q / 2, self.rand_q / 2)
            # Keep y non-negative
            if self._y < 0:
                self._y = 0

def run_app():
    st.title("Cannonball Trajectory")

    angle_deg = st.number_input(
        "Starting angle (degrees)", min_value=0.0, max_value=90.0, value=45.0
    )
    velocity = st.selectbox("Initial velocity", options=[15, 25, 40], index=1)

    gravity_options = {
        "Earth": 9.81,
        "Moon": 1.62,   # Moon surface gravity ≈ 1.62 m/s²
    }
    gravity_name = st.selectbox("Gravity", options=list(gravity_options.keys()), index=0)
    gravity = gravity_options[gravity_name]
    step = 0.1

    col1, col2 = st.columns(2)
    simulate = col1.button("Simulate")
    crazy_simulate = col2.button("Crazy Simulate")

    if simulate:
        angle_rad = radians(angle_deg)
        ball = Cannonball(0)
        ball.shoot(angle_rad, velocity, gravity, step)

    if crazy_simulate:
        angle_rad = radians(angle_deg)
        crazy_ball = Crazyball(0)
        crazy_ball.shoot(angle_rad, velocity, gravity, step)


if __name__ == "__main__":
    run_app()
