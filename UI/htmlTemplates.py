css = '''
<style>
/* Main container styles */
.main {
    max-width: 1000px;
    margin: 0 auto;
    background: linear-gradient(to bottom, #ffffff, #f8f9fa);
    padding: 2rem;
    border-radius: 1.5rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}

/* Streamlit sidebar customization */
.css-1d391kg {
    background: linear-gradient(145deg, #f4f6fa, #ffffff);
    padding: 2rem 1.5rem;
    border-right: 1px solid rgba(0,0,0,0.05);
}

.stSidebar .sidebar-header {
    color: #1976d2;
    font-weight: 600;
    padding: 1.5rem 0;
    border-bottom: 2px solid #e3f2fd;
    margin-bottom: 1.5rem;
}

/* Chat container styles */
.chat-message {
    padding: 1.75rem;
    border-radius: 1.25rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: flex-start;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    max-width: 85%;
    box-shadow: 0 3px 15px rgba(0,0,0,0.05);
    backdrop-filter: blur(10px);
}

.chat-message:hover {
    transform: translateY(-3px) scale(1.01);
    box-shadow: 0 6px 20px rgba(0,0,0,0.08);
}

.chat-message.user {
    background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    margin-left: auto;
    border: 1px solid rgba(25, 118, 210, 0.1);
}

.chat-message.bot {
    background: linear-gradient(135deg, #fff8e1, #fffde7);
    margin-right: auto;
    border: 1px solid rgba(255, 193, 7, 0.1);
}

/* Avatar styles */
.chat-message .avatar {
    width: 45px;
    height: 45px;
    margin-right: 1.25rem;
    border-radius: 1rem;
    overflow: hidden;
    background: #ffffff;
    border: 2px solid #ffffff;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    transition: transform 0.3s ease;
}

.chat-message .avatar:hover {
    transform: scale(1.1) rotate(5deg);
}

.chat-message .avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
}

/* Message content styles */
.chat-message .message {
    color: #2c3e50;
    font-size: 1.05rem;
    line-height: 1.7;
    flex-grow: 1;
    letter-spacing: 0.2px;
}

/* Code block styling */
.chat-message .message pre {
    background: rgba(255,255,255,0.9);
    padding: 1.25rem;
    border-radius: 0.75rem;
    overflow-x: auto;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    margin: 0.75rem 0;
    border: 1px solid #e0e0e0;
    color: #2c3e50;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
}

/* Input styling */
.stTextInput input, .stChatInput input {
    background: #ffffff;
    border-radius: 1.5rem;
    border: 2px solid #e3f2fd;
    padding: 1rem 1.5rem;
    color: #2c3e50;
    font-size: 1.05rem;
    transition: all 0.3s ease;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.stTextInput input:focus, .stChatInput input:focus {
    border-color: #1976d2;
    box-shadow: 0 0 0 3px rgba(25, 118, 210, 0.1);
    transform: translateY(-1px);
}

/* Button styling */
.stButton > button {
    background: linear-gradient(135deg, #1976d2, #1565c0);
    color: white;
    border: none;
    border-radius: 1.5rem;
    padding: 0.75rem 2rem;
    font-weight: 500;
    letter-spacing: 0.5px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(25, 118, 210, 0.2);
}

.stButton > button:hover {
    background: linear-gradient(135deg, #1565c0, #0d47a1);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(25, 118, 210, 0.3);
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.chat-message {
    animation: fadeIn 0.5s ease forwards;
}

/* Responsive improvements */
@media (max-width: 768px) {
    .chat-message {
        max-width: 95%;
        padding: 1.25rem;
    }
    
    .main {
        padding: 1rem;
    }
}
</style>
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img width="100" height="100" src="https://img.icons8.com/plasticine/100/bot.png" alt="bot"/>
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img width="48" height="48" src="https://img.icons8.com/color/48/user-male-circle--v1.png" alt="user-male-circle--v1"/>
    </div>    
    <div class="message">{{MSG}}</div>
</div>
'''
