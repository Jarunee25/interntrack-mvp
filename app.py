import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="InternTrack V.2", page_icon="📄", layout="wide")

st.title("📄 InternTrack V.2: ระบบยื่นและติดตามสถานะเอกสารขอฝึกงานออนไลน์")

# สร้าง Session State สำหรับเก็บข้อมูลคำร้อง (Synthetic Data V.2)
if "requests" not in st.session_state:
    st.session_state.requests = pd.DataFrame([
        {
            "doc_id": "IT-2026-001",
            "student_id": "64010912345",
            "student_email": "64010912345@msu.ac.th",
            "student_name": "สมชาย ใจดี",
            "doc_type": "หนังสือขอความอนุเคราะห์",
            "company_name": "บริษัท Tech Innovation จำกัด",
            "submission_date": "2026-10-20 10:30",
            "current_status": "เอกสารโดนตีกลับ",
            "rejection_reason": "ไฟล์แนบไม่ชัดเจน กรุณาแนบไฟล์หนังสือตอบรับใหม่อีกครั้ง"
        },
        {
            "doc_id": "IT-2026-002",
            "student_id": "64010954321",
            "student_email": "64010954321@msu.ac.th",
            "student_name": "สมหญิง รักเรียน",
            "doc_type": "หนังสือส่งตัวฝึกงาน",
            "company_name": "ธนาคารแห่งประเทศไทย",
            "submission_date": "2026-10-22 14:15",
            "current_status": "2-เจ้าหน้าที่ตรวจ",
            "rejection_reason": "-"
        }
    ])

tab1, tab2 = st.tabs(["📝 แบบฟอร์มยื่นเอกสาร (V.2)", "📊 ติดตามและจัดการสถานะเอกสาร"])

# --- TAB 1: ยื่นเอกสาร ---
with tab1:
    st.header("ยื่นเอกสารขอหนังสือฝึกงาน")
    st.caption("🔒 ระบบยืนยันตัวตนด้วยอีเมลมหาวิทยาลัย (V.2 Authentication)")
    
    col1, col2 = st.columns(2)
    with col1:
        std_id = st.text_input("รหัสนิสิต *")
        std_email = st.text_input("อีเมลมหาวิทยาลัย (@msu.ac.th) *")
        std_name = st.text_input("ชื่อ-นามสกุล *")
    with col2:
        doc_type = st.selectbox("ประเภทเอกสาร *", ["หนังสือขอความอนุเคราะห์", "หนังสือส่งตัวฝึกงาน"])
        company = st.text_input("ชื่อหน่วยงาน/บริษัท *")

    # V.2 รองรับไฟล์รูปภาพ JPG, PNG เพิ่มเติมจาก PDF
    uploaded_file = st.file_uploader("แนบไฟล์รายละเอียด/หนังสือตอบรับ (.pdf, .jpg, .png) *", type=["pdf", "jpg", "png"])

    if st.button("ส่งคำร้องขอเอกสาร"):
        if std_id and std_name and company and std_email:
            new_id = f"IT-2026-{len(st.session_state.requests)+1:03d}"
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            new_data = {
                "doc_id": new_id,
                "student_id": std_id,
                "student_email": std_email,
                "student_name": std_name,
                "doc_type": doc_type,
                "company_name": company,
                "submission_date": now_str,
                "current_status": "1-ยื่นเรื่องแล้ว",
                "rejection_reason": "-"
            }
            
            st.session_state.requests = pd.concat([st.session_state.requests, pd.DataFrame([new_data])], ignore_index=True)
            st.success(f"ส่งคำร้องสำเร็จ! รหัสอ้างอิงเอกสารของคุณคือ: **{new_id}**")
            st.info(f"📲 [V.2 Notification] ระบบได้ส่งข้อความยืนยันและลิงก์ติดตามสถานะไปยัง LINE / Email ({std_email}) เรียบร้อยแล้ว")
        else:
            st.error("กรุณากรอกข้อมูลที่จำเป็นให้ครบถ้วน")

# --- TAB 2: ติดตามและอัปเดตสถานะ ---
with tab2:
    st.header("ติดตามสถานะเอกสาร")
    
    if not st.session_state.requests.empty:
        doc_list = st.session_state.requests["doc_id"].tolist()
        selected_id = st.selectbox("เลือกรหัสเอกสาร (doc_id) เพื่อติดตามสถานะ:", doc_list)
        
        # ดึงข้อมูลของ doc_id ที่เลือก
        idx = st.session_state.requests[st.session_state.requests["doc_id"] == selected_id].index[0]
        row = st.session_state.requests.loc[idx]
        
        st.subheader(f"สถานะเอกสาร: {row['doc_id']}")
        col_a, col_b = st.columns(2)
        with col_a:
            st.write(f"**ชื่อผู้ยื่น:** {row['student_name']} ({row['student_id']})")
            st.write(f"**อีเมล:** {row['student_email']}")
            st.write(f"**ประเภทเอกสาร:** {row['doc_type']}")
            st.write(f"**บริษัท:** {row['company_name']}")
        with col_b:
            st.write(f"**วันที่ยื่น:** {row['submission_date']}")
            st.write(f"**สถานะปัจจุบัน:** `{row['current_status']}`")
            if row['rejection_reason'] != "-":
                st.error(f"**เหตุผลการตีกลับ:** {row['rejection_reason']}")

        # V.2 ปุ่มอัปโหลดไฟล์แก้ไขกรณีโดนตีกลับ
        if row['current_status'] == "เอกสารโดนตีกลับ":
            st.warning("⚠️ เอกสารของคุณถูกตีกลับ สามารถแนบไฟล์ใหม่เพื่อส่งแก้ไขได้ทันทีโดยไม่ต้องกรอกฟอร์มใหม่")
            re_file = st.file_uploader("อัปโหลดไฟล์แก้ไข (.pdf, .jpg, .png)", type=["pdf", "jpg", "png"], key="re_upload")
            if st.button("ส่งเอกสารแก้ไข"):
                if re_file:
                    st.session_state.requests.loc[idx, "current_status"] = "1-ยื่นเรื่องแล้ว (แก้ไขแล้ว)"
                    st.session_state.requests.loc[idx, "rejection_reason"] = "-"
                    st.success("ส่งเอกสารแก้ไขเรียบร้อยแล้ว! สถานะถูกเปลี่ยนเป็น 'ยื่นเรื่องแล้ว'")
                    st.rerun()
                else:
                    st.error("กรุณาเลือกไฟล์แก้ไขก่อนกดส่ง")

        st.divider()
        st.subheader("👨‍💼 ส่วนเจ้าหน้าที่/อาจารย์ (อัปเดตสถานะ)")
        col_status, col_reason = st.columns(2)
        with col_status:
            new_status = st.selectbox("เปลี่ยนสถานะ:", 
                                     ["1-ยื่นเรื่องแล้ว", "2-เจ้าหน้าที่ตรวจ", "3-รออาจารย์/ผู้มีอำนาจลงนาม", "4-อนุมัติเรียบร้อย", "เอกสารโดนตีกลับ"],
                                     index=0)
        with col_reason:
            rej_reason_input = st.text_input("ระบุเหตุผล (กรณีตีกลับ):", value=row['rejection_reason'] if row['rejection_reason'] != "-" else "")

        if st.button("บันทึกการเปลี่ยนแปลง"):
            st.session_state.requests.loc[idx, "current_status"] = new_status
            st.session_state.requests.loc[idx, "rejection_reason"] = rej_reason_input if new_status == "เอกสารโดนตีกลับ" else "-"
            st.success("บันทึกสถานะใหม่เรียบร้อยแล้ว!")
            st.info(f"📲 [V.2 Notification] ส่งการแจ้งเตือนอัปเดตสถานะไปยัง LINE/Email ของนิสิตเรียบร้อยแล้ว")
            st.rerun()
