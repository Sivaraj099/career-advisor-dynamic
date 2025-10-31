import streamlit as st
import time, threading, random

QUOTES = [
    "🌱 “Every expert was once a beginner.”",
    "🚀 “Don’t watch the clock; do what it does. Keep going.”",
    "💡 “Learning never exhausts the mind.”",
    "🔥 “Stay curious — that’s your biggest strength.”",
    "🎯 “Consistency beats intensity.”",
    "🧠 “Smart work is the new hard work.”"
]

def show_loading_quotes(message="🤖 Processing..."):
    """
    Display a Streamlit spinner and rotating motivational quotes at the same time.
    Returns a tuple (stop_flag, thread, placeholder)
    """
    placeholder = st.empty()
    stop_flag = {"value": False}

    def cycle():
        i = 0
        while not stop_flag["value"]:
            quote = QUOTES[i % len(QUOTES)]
            placeholder.markdown(f"{message}\n\n> {quote}")
            time.sleep(5)
            i += 1
        placeholder.empty()

    # Start both spinner + quotes
    spinner = st.spinner(message)
    spinner.__enter__()

    t = threading.Thread(target=cycle)
    t.start()

    return stop_flag, t, placeholder, spinner


def stop_loading_quotes(stop_flag, t, placeholder, spinner):
    """Stop both spinner and rotating quotes"""
    stop_flag["value"] = True
    t.join()
    placeholder.empty()
    spinner.__exit__(None, None, None)
