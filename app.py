import streamlit as st
import pandas as pd
import random

# --- 網頁設定 ---
st.set_page_config(page_title="社心名詞測驗", page_icon="🧠")
st.title("🧠 社會心理學：名詞大會考")
st.write("請根據題目顯示的「名詞」，選出正確的「解釋」。")

# --- 1. 讀取資料 ---
@st.cache_data
def load_data():
    # 讀取 CSV，如果遇到編碼問題可以試試 encoding='utf-8'
    df = pd.read_csv("data.csv")
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"讀取資料失敗，請檢查 data.csv 是否存在 GitHub！錯誤訊息：{e}")
    st.stop()

# 檢查資料量
if len(df) < 4:
    st.warning("題庫資料不足 4 筆，無法產生選擇題選項。")
    st.stop()

# --- 2. 側邊欄設定 (控制要考幾題) ---
st.sidebar.header("⚙️ 測驗設定")
max_questions = len(df)
# 預設考 5 題，最多可以拉到全部題目 (例如 20)
num_questions = st.sidebar.slider("這次要考幾題？", min_value=1, max_value=max_questions, value=min(5, max_questions))

# 重新出題按鈕
if st.sidebar.button("🔄 重新出題 / 洗牌"):
    # 清除 session state 讓題目重抽
    if 'quiz_data' in st.session_state:
        del st.session_state['quiz_data']
    st.rerun()

# --- 3. 出題邏輯 (只在第一次或重置時執行) ---
if 'quiz_data' not in st.session_state:
    # 從資料庫隨機抽出指定數量的題目
    selected_rows = df.sample(n=num_questions)
    
    quiz_list = []
    for index, row in selected_rows.iterrows():
        term = row['term']             # 題目 (名詞)
        correct_def = row['definition'] # 正解 (解釋)
        
        # 找 3 個錯誤選項 (排除掉正確答案的那一列)
        wrong_options = df[df['term'] != term]['definition'].sample(3).tolist()
        
        # 組合選項並打亂
        options = wrong_options + [correct_def]
        random.shuffle(options)
        
        # 存起來
        quiz_list.append({
            "term": term,
            "correct_def": correct_def,
            "options": options
        })
    
    st.session_state.quiz_data = quiz_list

# --- 4. 顯示考卷 (使用 Form 表單) ---
with st.form("exam_form"):
    user_answers = {}
    
    for i, q in enumerate(st.session_state.quiz_data):
        st.markdown(f"### 第 {i+1} 題：**{q['term']}**")
        # radio button 的 key 必須唯一，所以加上 index
        user_answers[i] = st.radio(f"請選擇 {q['term']} 的正確解釋：", q['options'], key=f"q_{i}", index=None)
        st.markdown("---") # 分隔線
    
    # 交卷按鈕
    submitted = st.form_submit_button("📝 交卷計分")

    # --- 5. 改考卷與顯示結果 ---
    if submitted:
        score = 0
        st.divider()
        st.subheader("📊 測驗結果")
        
        for i, q in enumerate(st.session_state.quiz_data):
            user_ans = user_answers[i]
            correct_ans = q['correct_def']
            
            if user_ans == correct_ans:
                score += 1
                # 答對顯示綠色文字
                st.success(f"第 {i+1} 題 ({q['term']})：答對了！")
            else:
                # 答錯顯示紅色區塊與詳解
                st.error(f"第 {i+1} 題 ({q['term']})：答錯囉 ❌")
                st.write(f"**您的選擇：** {user_ans}")
                st.info(f"**正確解答：** {correct_ans}")
        
        # 計算總分
        final_score = int((score / num_questions) * 100)
        st.markdown(f"## 總分： **{final_score} 分** (答對 {score}/{num_questions} 題)")
        
        if final_score == 100:
            st.balloons()
            st.markdown("太強了！全部答對！🎉")
        elif final_score >= 60:
            st.markdown("及格了，繼續保持！👍")
        else:
            st.markdown("再多複習一下名詞解釋吧！💪")
