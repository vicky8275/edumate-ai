import streamlit as st
import time

def pomodoro_timer():
    st.subheader("Pomodoro Timer ⏰")
    work_time = st.slider("Work Duration (minutes)", 5, 60, 25)
    break_time = st.slider("Break Duration (minutes)", 5, 15, 5)
    
    timer_message_placeholder = st.empty()

    if st.button("Start Pomodoro ▶️"):
        timer_message_placeholder.info("Work session started! Focus! 🧠")
        for i in range(work_time * 60, 0, -1):
            mins, secs = divmod(i, 60)
            timer_message_placeholder.info(f"Work Time: {mins:02d}:{secs:02d} remaining ⏳")
            time.sleep(1)
        
        timer_message_placeholder.success("Time for a break! 🎉")
        for i in range(break_time * 60, 0, -1):
            mins, secs = divmod(i, 60)
            timer_message_placeholder.success(f"Break Time: {mins:02d}:{secs:02d} remaining ☕")
            time.sleep(1)
        
        timer_message_placeholder.empty()
        st.balloons()
        st.success("Pomodoro cycle completed! Ready for the next one? ✨")
    
    st.markdown("---")
    st.subheader("Productivity Tips to Supercharge Your Study! 🚀")
    st.write("- Break big tasks into smaller, manageable chunks. Think 'mini-missions'! 🎯")
    st.write("- Find your perfect study spot – quiet, comfy, and distraction-free. 🤫")
    st.write("- Take short breaks! Your brain needs a refresh to stay sharp. 💡")
    st.write("- Reward yourself after completing a study session. You earned it! 🏆")