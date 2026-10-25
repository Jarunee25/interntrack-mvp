import streamlit as st
import pandas as pd
from datetime import datetime

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="InternTrack MVP", page_icon="📄", layout="wide")

# สร้าง Mock Database สำหรับเก็บข้อมูลคำร้อง (Synthetic Data)
if "requests_db" not in st.session_state:
    st.session_state.requests_db = pd.DataFrame([
        {
            "doc_id": "IT-2026-001",
            "student_id": "64010001",
            "student_name": "สมชาย ใจดี",
            "company_name": "บริษัท เทคโซลูชันส์ จำกัด",
            "doc_type": "หนังสือขอความอนุเคราะห์",
            "submission_date": "2026-10-20 09:30",
            "current_status": "2. เจ้าหน้าที่กำลังตรวจสอบ",
            "assigned_to": "เจ้าหน้าที่คณะ",
            "rejection_reason": "-"
        },
        {
            "doc_id": "IT-2026-002",
            "student_id": "64010002",
            "student_name": "สมหญิง รักเรียน",
            "company_name": "ธนาคารพัฒนาไทย",
            "doc_type": "หนังสือส่งตัวฝึกงาน",
            "submission_date": "2026-10-22 14:15",
            "current_status": "4. อนุมัติเรียบร้อย",
            "assigned_to": "นิสิต (รับเอกสาร)",
            "rejection_reason": "-"
        }
    ])

st.title("📄 InternTrack: ระบบยื่นและติดตามสถานะเอกสารขอฝึกงานออนไลน์")

# เมนูแบ่งตามประเภทผู้ใช้งาน (User Roles)
role = st.sidebar.radio("เลือกมุมมองการใช้งาน (Role):", ["🎓 ฝั่งนิสิต (Student)", "🏢 ฝั่งเจ้าหน้าที่ (Admin)"])

# ---------------------------------------------------------
# 1. มุมมองฝั่งนิสิต (Student Interface)
# ---------------------------------------------------------
if role == "🎓 ฝั่งนิสิต (Student)":
    tab1, tab2 = st.tabs(["📝 แบบฟอร์มยื่นเอกสาร", "📊 ติดตามสถานะเอกสาร"])
    
    # Tab 1: Smart Pre-validation Form
    with tab1:
        st.subheader("ยื่นเอกสารขอหนังสือฝึกงาน")
        with st.form("internship_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                student_id = st.text_input("รหัสนิสิต *")
                student_name = st.text_input("ชื่อ-นามสกุล *")
            with col2:
                doc_type = st.selectbox("ประเภทเอกสาร *", ["หนังสือขอความอนุเคราะห์", "หนังสือส่งตัวฝึกงาน"])
                company_name = st.text_input("ชื่อหน่วยงาน/บริษัท *")
            
            # Smart Pre-validation: บังคับแนบไฟล์ PDF เท่านั้น
            uploaded_file = st.file_uploader("แนบไฟล์รายละเอียด/หนังสือตอบรับ (.pdf เท่านั้น) *", type=["pdf"])
            
            submit_btn = st.form_submit_button("ส่งคำร้องขอเอกสาร")
            
            if submit_btn:
                # Rule-based Check
                if not student_id or not student_name or not company_name:
                    st.error("❌ กรุณากรอกข้อมูลที่มีเครื่องหมาย * ให้ครบถ้วน")
                elif uploaded_file is None:
                    st.error("❌ กรุณาแนบไฟล์ PDF ประกอบการยื่นเรื่อง")
                else:
                    new_id = f"IT-2026-00{len(st.session_state.requests_db) + 1}"
                    new_entry = {
                        "doc_id": new_id,
                        "student_id": student_id,
                        "student_name": student_name,
                        "company_name": company_name,
                        "doc_type": doc_type,
                        "submission_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "current_status": "1. ยื่นเรื่องแล้ว",
                        "assigned_to": "เจ้าหน้าที่คณะ",
                        "rejection_reason": "-"
                    }
                    st.session_state.requests_db = pd.concat([st.session_state.requests_db, pd.DataFrame([new_entry])], ignore_index=True)
                    st.success(f"✅ ยื่นเรื่องสำเร็จ! รหัสติดตามเอกสารของคุณคือ: **{new_id}**")

    # Tab 2: Visual Progress Tracker & Dashboard
    with tab2:
        st.subheader("สถานะคำร้องขอเอกสารของคุณ")
        search_id = st.text_input("กรอกรหัสนิสิตเพื่อค้นหา:", value="64010001")
        
        user_docs = st.session_state.requests_db[st.session_state.requests_db["student_id"] == search_id]
        
        if not user_docs.empty:
            for idx, row in user_docs.iterrows():
                with st.expander(f"📌 เลขที่ {row['doc_id']} - {row['doc_type']} ({row['company_name']})", expanded=True):
                    # แสดง Visual Progress Tracker
                    st.write(f"**สถานะปัจจุบัน:** `{row['current_status']}` | **ผู้ถือเรื่อง:** `{row['assigned_to']}`")
                    
                    # Progress Bar แสดงขั้นตอน
                    status_map = {
                        "1. ยื่นเรื่องแล้ว": 25,
                        "2. เจ้าหน้าที่กำลังตรวจสอบ": 50,
                        "3. รออาจารย์/ผู้มีอำนาจลงนาม": 75,
                        "4. อนุมัติเรียบร้อย": 100,
                        "❌ เอกสารโดนตีกลับ": 0
                    }
                    progress = status_map.get(row['current_status'], 0)
                    st.progress(progress)
                    
                    if row['current_status'] == "❌ เอกสารโดนตีกลับ":
                        st.error(f"⚠️ เหตุผลที่โดนตีกลับ: {row['rejection_reason']} (กรุณายื่นแบบฟอร์มใหม่)")
                    elif progress == 100:
                        st.success("🎉 เอกสารออกเรียบร้อยแล้ว ติดต่อรับได้ที่ห้องฟ้า/ดาวน์โหลดไฟล์")
        else:
            st.info("ไม่พบรายการคำร้องสำหรับรหัสนิสิตนี้")

# ---------------------------------------------------------
# 2. มุมมองฝั่งเจ้าหน้าที่ (Admin Interface)
# ---------------------------------------------------------
else:
    st.subheader("🏢 แดชบอร์ดจัดการคำร้องสำหรับเจ้าหน้าที่ (Admin Manager)")
    
    # แสดงรายการคำร้องทั้งหมด
    df = st.session_state.requests_db
    st.dataframe(df, use_container_width=True)
    
    st.markdown("---")
    st.subheader("⚙️ Update สถานะคำร้อง (One-Click Manager)")
    
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_doc_id = st.selectbox("เลือกรหัสเอกสารที่ต้องการอัปเดต:", df["doc_id"].tolist())
        
        # ดึงข้อมูลรายการที่เลือก
        current_row = df[df["doc_id"] == selected_doc_id].iloc[0]
        
        with col2:
            new_status = st.selectbox("เปลี่ยนสถานะเป็น:", [
                "1. ยื่นเรื่องแล้ว",
                "2. เจ้าหน้าที่กำลังตรวจสอบ",
                "3. รออาจารย์/ผู้มีอำนาจลงนาม",
                "4. อนุมัติเรียบร้อย",
                "❌ เอกสารโดนตีกลับ"
            ], index=["1. ยื่นเรื่องแล้ว", "2. เจ้าหน้าที่กำลังตรวจสอบ", "3. รออาจารย์/ผู้มีอำนาจลงนาม", "4. อนุมัติเรียบร้อย", "❌ เอกสารโดนตีกลับ"].index(current_row["current_status"]))
            
        with col3:
            rej_reason = st.selectbox("สาเหตุการตีกลับ (ถ้ามี):", [
                "-",
                "ข้อมูลรายละเอียดไม่ครบถ้วน",
                "แนบไฟล์ผิดประเภท/อ่านไม่ได้",
                "ชื่อสถานประกอบการไม่ถูกต้อง"
            ])

         if st.button("บันทึกการเปลี่ยนแปลง"):
             st.success("บันทึกการเปลี่ยนแปลงเรียบร้อยแล้ว")
