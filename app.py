import streamlit as st
import pandas as pd
import random

# --- 0. 網站設定 (必須放在第一行) ---
st.set_page_config(
    page_title="社心名詞解釋大會考",
    page_icon="🎓",
    layout="centered", # 設為 centered 會讓內容集中在中間，比較像閱讀文章，質感較好
    initial_sidebar_state="expanded"
)

# 自訂 CSS 來美化介面 (隱藏預設選單、調整字體等)
st.markdown("""
    <style>
    .stRadio p {font-size: 16px;}
    .big-font {font-size:20px !important; font-weight: bold;}
    div.stButton > button:first-child {
        background-color: #4CAF50;
        color: white;
        font-size: 18px;
        border-radius: 10px;
        padding: 10px 24px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 讀取資料 ---
@st.cache_data
def load_data():
    df = pd.read_csv("scusocpsy.csv")
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"❌ 找不到資料檔 (data.csv)，請檢查 GitHub！錯誤訊息：{e}")
    st.stop()

if len(df) < 4:
    st.warning("⚠️ 題庫資料不足，請至少準備 4 筆名詞解釋。")
    st.stop()

# --- 2. 側邊欄：設定區 ---
with st.sidebar:
    st.header("⚙️ 考試設定")
    st.write("準備好迎接挑戰了嗎？")
    
    max_q = len(df)
    num_questions = st.slider("選擇題數", min_value=1, max_value=max_q, value=min(5, max_q))
    
    st.markdown("---")
    if st.button("🔄 重新出題 / 洗牌"):
        if 'quiz_data' in st.session_state:
            del st.session_state['quiz_data']
        st.rerun()
        
    st.markdown("---")
    st.caption("Designed by 柏澔 | Social Psychology Quiz")

# --- 3. 標題區 ---
st.title("🎓 社會心理學：名詞解釋大會考")
st.markdown("請根據 **「名詞」**，選出正確的 **「解釋」**。")
st.progress(0) # 裝飾用的進度條，增加儀式感

# --- 4. 出題邏輯 ---
if 'quiz_data' not in st.session_state:
    selected_rows = df.sample(n=num_questions)
    quiz_list = []
    for index, row in selected_rows.iterrows():
        term = row['term']
        correct_def = row['definition']
        # 挑錯選項
        wrong_options = df[df['term'] != term]['definition'].sample(3).tolist()
        options = wrong_options + [correct_def]
        random.shuffle(options)
        
        quiz_list.append({
            "term": term,
            "correct_def": correct_def,
            "options": options
        })
    st.session_state.quiz_data = quiz_list

# --- 5. 考卷區 (使用 Container 增加層次) ---
with st.form("exam_form"):
    user_answers = {}
    
    for i, q in enumerate(st.session_state.quiz_data):
        st.markdown(f"### <span class='big-font'>Q{i+1}. {q['term']}</span>", unsafe_allow_html=True)
        # 這裡 index=None 預設不選，強迫同學思考
        user_answers[i] = st.radio(f"請選擇 {q['term']} 的定義：", q['options'], key=f"q_{i}", index=None, label_visibility="collapsed")
        st.divider() # 質感分隔線
    
    # 交卷按鈕
    submitted = st.form_submit_button("📝 交卷計分")

# --- 6. 結果分析區 ---
if submitted:
    score = 0
    wrong_list = []
    
    # 判斷對錯
    for i, q in enumerate(st.session_state.quiz_data):
        user_ans = user_answers[i]
        if user_ans == q['correct_def']:
            score += 1
        else:
            wrong_list.append((i+1, q['term'], q['correct_def'], user_ans))

    final_score = int((score / num_questions) * 100)
    
    # 顯示成績單
    st.markdown("---")
    st.subheader("📊 測驗分析")
    
    # 使用 columns 讓成績並排顯示，比較好看
    col1, col2, col3 = st.columns(3)
    col1.metric("最終得分", f"{final_score} 分")
    col2.metric("答對題數", f"{score} / {num_questions}")
    col3.metric("準確率", f"{final_score}%")
    
    # 根據分數給評語
    if final_score == 100:
        st.balloons()
        st.success("🎉 太神啦！完全制霸！社會學霸就是你！")
    elif final_score >= 80:
        st.success("👍 表現優秀！觀念很清楚喔！")
    elif final_score >= 60:
        st.warning("🙂 及格邊緣，再多複習一下會更好！")
    else:
        st.error("💪 加油！這些名詞有點陌生喔，快看看下面的解析！")
    
    # 錯誤檢討 (如果有錯題才顯示)
    if wrong_list:
        st.markdown("### ❌ 錯題訂正")
        for w in wrong_list:
            # 用 expander 摺疊錯誤題目，版面才不會太長
            with st.expander(f"第 {w[0]} 題：{w[1]} (點擊查看詳解)", expanded=True):
                st.write(f"**你的選擇：** {w[3] if w[3] else '未作答'}")
                st.info(f"**✅ 正確解答：** {w[2]}")
