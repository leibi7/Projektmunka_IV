from __future__ import annotations

import gradio as gr
import pandas as pd

from energy_app.webapp.state import get_demo_user_id


def build_interface(run_save_profile, run_forecast, run_recommendations):
    with gr.Blocks(title="Energy Forecasting") as demo:
        gr.Markdown("# Energy Forecasting & Recommendations")
        with gr.Tab("Profile"):
            location = gr.Textbox(label="Location")
            area = gr.Number(label="Area (m2)")
            occupants = gr.Number(label="Occupants", precision=0)
            heating = gr.Textbox(label="Heating type", placeholder="gas/electric/heat pump")
            save_btn = gr.Button("Save profile")
            save_status = gr.Markdown()

        with gr.Tab("Forecast"):
            horizon = gr.Radio([24, 168], value=24, label="Horizon (hours)")
            model_choice = gr.Dropdown(["Baseline", "PatchTST", "Granite TTM"], value="Baseline", label="Model")
            forecast_btn = gr.Button("Run forecast")
            forecast_plot = gr.Plot(label="Forecast vs history")

        with gr.Tab("Recommendations"):
            rec_btn = gr.Button("Generate recommendations")
            rec_output = gr.JSON(label="Recommendations")

        def _save_profile(loc, area, occ, heat, request: gr.Request):
            user_id = get_demo_user_id(request.session_state)
            msg = run_save_profile(user_id, loc, area, occ, heat)
            return msg

        def _run_forecast(hor, model_name, request: gr.Request):
            user_id = get_demo_user_id(request.session_state)
            fig = run_forecast(user_id, int(hor), model_name)
            return fig

        def _run_recs(request: gr.Request):
            user_id = get_demo_user_id(request.session_state)
            result = run_recommendations(user_id)
            return result

        save_btn.click(_save_profile, inputs=[location, area, occupants, heating], outputs=save_status)
        forecast_btn.click(_run_forecast, inputs=[horizon, model_choice], outputs=forecast_plot)
        rec_btn.click(_run_recs, outputs=rec_output)

    return demo
