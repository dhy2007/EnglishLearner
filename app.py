# app.py
import streamlit as st
import json
from utils.ai_helper import call_qwen_ai

# 设置网页标题和布局
st.set_page_config(page_title="我的 AI 英语学习助手", page_icon="📚", layout="wide")
st.title("📚 AI 英语学习助手")

# ----------------- 侧边栏导航 -----------------
st.sidebar.header("导航菜单")
menu = st.sidebar.radio("选择功能", ["背单词", "作文模板与批改", "AI 口语对话"])

# --- 读取词库的通用函数 ---
@st.cache_data
def load_words(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            processed_data = []
            for item in data:
                if isinstance(item, dict):
                    word = item.get("word", "")
                    meaning = item.get("meaning", "")
                    phonetic = item.get("phonetic", "") 
                    example = item.get("example", "")
                    phrase = item.get("phrase", "")

                    if not meaning and "translations" in item and len(item["translations"]) > 0:
                        meaning = item["translations"][0].get("translation", "")
                else:
                    word = str(item)
                    meaning = "请查阅词典"
                    phonetic, example, phrase = "", "", ""
                
                if word:
                    processed_data.append({
                        "word": word, 
                        "meaning": meaning,
                        "phonetic": phonetic,
                        "example": example,
                        "phrase": phrase
                    })
            return processed_data
    except Exception as e:
        st.error(f"读取词库出错: {e}")
        return []

# ----------------- 功能 1：背单词 -----------------
if menu == "背单词":
    st.header("📖 词汇练习")
    word_type = st.selectbox("选择词库", ["四六级词汇", "程序员常用词汇"])
    
    if word_type == "四六级词汇":
        word_list = load_words("data/cet4.json")
    else:
        word_list = load_words("data/programmer.json")
        
    if not word_list:
        st.error("词库为空！请检查文件是否存在或格式是否正确。")
    else:
        st.success(f"🎉 当前词库已成功加载，共计 **{len(word_list)}** 个单词！")
        
        if 'current_type' not in st.session_state or st.session_state.current_type != word_type:
            st.session_state.current_type = word_type
            st.session_state.current_index = 0  
            st.session_state.show_meaning = False 
        
        st.checkbox("自动显示释义 (记住你的选择)", key="auto_show_meaning", value=False)

        current_word_data = word_list[st.session_state.current_index]
        
        st.info(f"### 当前单词 (进度: {st.session_state.current_index + 1} / {len(word_list)})：")
        
        st.markdown(f"<h1 style='text-align: center; color: #1f77b4; margin-bottom: 10px;'>{current_word_data['word']}</h1>", unsafe_allow_html=True)
        
        col_ph, col_audio = st.columns([1, 1])
        with col_ph:
            if current_word_data.get('phonetic'):
                st.markdown(f"<h4 style='text-align: center; color: gray;'>[{current_word_data['phonetic']}]</h4>", unsafe_allow_html=True)
            else:
                st.markdown("<h4 style='text-align: center; color: gray;'>暂无音标</h4>", unsafe_allow_html=True)
                
        with col_audio:
            tts_url = f"https://dict.youdao.com/dictvoice?audio={current_word_data['word']}&type=2"
            st.audio(tts_url, format="audio/mp3")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("⬅️ 上一个", use_container_width=True):
                if st.session_state.current_index > 0:
                    st.session_state.current_index -= 1
                else:
                    st.toast("已经是第一个单词啦！")
                    
        with col2:
            if st.button("👁️ 手动显示/隐藏", use_container_width=True):
                st.session_state.show_meaning = not st.session_state.show_meaning
                
        with col3:
            if st.button("下一个 ➡️", use_container_width=True):
                if st.session_state.current_index < len(word_list) - 1:
                    st.session_state.current_index += 1
                else:
                    st.toast("已经是最后一个单词啦！🎉")
        
        st.markdown("<br>", unsafe_allow_html=True) 
        
        if st.session_state.get("auto_show_meaning", False) or st.session_state.show_meaning:
            st.success(f"**词义：** {current_word_data['meaning']}")
            
            if current_word_data.get('phrase'):
                st.info(f"**短语：** {current_word_data['phrase']}")
            if current_word_data.get('example'):
                st.warning(f"**例句：** {current_word_data['example']}")

# ----------------- 功能 2：作文模板与 AI 批改 -----------------
elif menu == "作文模板与批改":
    st.header("✍️ 作文模板与 AI 批改")
    
    tab1, tab2 = st.tabs(["背诵模板", "AI 批改作文"])
    
    with tab1:
        st.subheader("1. 四级模板 (对比选择类)")
        st.text_area("适用话题：网购/传统购物、线上/线下学习等", "With the rapid development of society, the issue of ______ has aroused wide concern. Some people hold the view that ______. However, others argue that ______. As far as I am concerned, ______.", height=100, key="t1")
        st.divider()
        
        st.subheader("2. 四级模板 (解决问题类)")
        st.text_area("适用话题：环境污染、交通拥堵、沉迷手机等", "With the rapid development of society, there is a growing concern over ______. It is urgent for us to take effective measures to solve this problem. First and foremost, ______. Secondly, ______. Only in this way can we ______.", height=100, key="t2")
        st.divider()
        
        st.subheader("3. 四级模板 (利弊分析类)")
        st.text_area("适用话题：兼职工作、出国留学、网络交友等", "Nowadays, ______ has become a common phenomenon in our daily life. Like a coin has two sides, it has both advantages and disadvantages. On the one hand, ______. On the other hand, ______. In conclusion, we should ______.", height=100, key="t3")
        st.divider()
        
        st.subheader("4. 六级模板 (现象分析类)")
        st.text_area("适用话题：考公热、考研热、传统文化复兴等", "It is universally acknowledged that ______. The reasons for this phenomenon are varied. To begin with, ______. In addition, ______. Therefore, it is high time that we paid attention to this issue and took actions to ______.", height=100, key="t4")
        st.divider()
        
        st.subheader("5. 六级模板 (观点论证类)")
        st.text_area("适用话题：是否应该做某事、对某现象的看法", "When it comes to ______, opinions vary from person to person. Some people believe that ______. While others hold the opposite view. From my perspective, I firmly believe that ______. The main reason is that ______.", height=100, key="t5")
        st.divider()

        st.subheader("6. 六级模板 (谚语警句类)")
        st.text_area("适用话题：名言警句启发、如'知识就是力量'", "There is an old saying goes, \"______\". Simple as the saying is, its meaning is profound. It tells us that ______. To sum up, we should bear in mind that ______.", height=100, key="t6")
        st.divider()

        st.subheader("7. 实用模板 (书信/倡议书类)")
        st.text_area("适用话题：给校长写信、建议信、倡议捐款等", "Dear ______, I am writing this letter to ______. The main purpose of my writing is to ______. I would appreciate it if you could ______. I am looking forward to your reply. Yours sincerely, Li Ming", height=100, key="t7")
        st.divider()

        st.subheader("8. 六级高级句型（加分必备）")
        st.text_area("写作时直接套用这些句型，瞬间提升档次", "1. It is high time that we took effective measures to... (是时候采取有效措施去...)\n2. There is no denying that... (不可否认的是...)\n3. Only by doing so can we... (只有这样我们才能...)\n4. It is universally acknowledged that... (众所周知...)\n5. What's more important is that... (更重要的是...)", height=150, key="t8")
        
    with tab2:
        st.subheader("把你的作文发给 AI 老师")
        essay = st.text_area("在这里输入你的作文（不少于50词）", height=200)
        
        if st.button("提交 AI 批改"):
            if len(essay) < 10:
                st.warning("字数太少了，多写一点吧！")
            else:
                with st.spinner('AI 老师正在批改中，请稍候...'):
                    prompt = f"请以英语老师的身份批改以下四六级作文：\n{essay}\n\n请按以下格式回复：\n1. 评分（满分15分）\n2. 语法和拼写修改意见\n3. 词汇替换建议\n4. 总体评价"
                    result = call_qwen_ai(prompt)
                    st.success("批改完成！")
                    st.markdown(result)

# ----------------- 功能 3：AI 对话练口语 -----------------
elif menu == "AI 口语对话":
    st.header("🗣️ AI 口语陪练")
    st.info("你可以设定一个场景，然后和 AI 进行英文对话。")
    
    scenario = st.selectbox("选择对话场景", ["Software Engineer Interview (程序员面试)", "Ordering Food (餐厅点餐)", "Daily Chat (日常闲聊)"])
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": f"Let's start the '{scenario}' conversation! I am ready."}]
        
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    if user_input := st.chat_input("Type your English here..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
            
        with st.chat_message("assistant"):
            with st.spinner('Thinking...'):
                prompt = f"We are doing a roleplay: {scenario}. Please reply to my last sentence naturally in English, keep it under 50 words. My input: {user_input}"
                ai_reply = call_qwen_ai(prompt)
                st.write(ai_reply)
                
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})