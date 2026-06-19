#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار عرض HTML
Test HTML Rendering
"""

import streamlit as st

st.set_page_config(page_title="HTML Test", layout="wide")

# CSS للاختبار
test_css = """
<style>
.test-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
    border-radius: 15px;
    color: white;
    margin: 20px 0;
}

.message-bubble {
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
    background: #f3e5f5;
    border-left: 4px solid #9c27b0;
}

.section-title {
    font-weight: bold;
    color: #7b1fa2;
    margin-bottom: 10px;
}
</style>
"""

# تطبيق CSS
st.markdown(test_css, unsafe_allow_html=True)

st.title("اختبار عرض HTML")

# اختبار 1: HTML بسيط
st.subheader("اختبار 1: HTML بسيط")
simple_html = """
<div class="test-box">
    <h3>هذا اختبار HTML بسيط</h3>
    <p>إذا رأيت هذا بتنسيق جميل، فالكود يعمل بشكل صحيح</p>
</div>
"""
st.markdown(simple_html, unsafe_allow_html=True)

# اختبار 2: Message Bubble
st.subheader("اختبار 2: Message Bubble")
message_html = """
<div class="message-bubble">
    <span class="section-title">التحليل</span>
    <div>هذا نص الرسالة</div>
</div>
"""
st.markdown(message_html, unsafe_allow_html=True)

# اختبار 3: النص الأصلي من المشكلة
st.subheader("اختبار 3: الكود الأصلي")

original_html = """
<div class="message-bubble bot-message bot-analysis fade-in">
    <span class="message-sender">النظام الذكي</span>
    <div class="message-content">
    <div class="analysis-section analysis-thought">
        <span class="section-title">التحليل</span>
        <div class="section-content">ألم صدر! هذا علامة تحذيرية جداً!</div>
    </div>
    <div class="analysis-section analysis-inference">
        <span class="section-title">الاستنتاج</span>
        <div class="section-content">الحمد لله، لا توجد عوامل خطر واضحة حتى الآن.</div>
    </div>
    <div class="analysis-section analysis-decision">
        <span class="section-title">القرار</span>
        <div class="section-content">ضغط الدم مهم جداً! سأسأل عنه التالي.</div>
    </div>
        <div style='margin-top: 25px; padding: 25px; 
                    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    border-radius: 14px; border: 2px solid #9c27b0;'>
            <div style='display: flex; justify-content: space-between; align-items: center; 
                        margin-bottom: 18px;'>
                <span style='font-size: 1.2rem; font-weight: 700; color: #2d3748;'>
                    السؤال التالي الأهم
                </span>
                <span class="priority-badge priority-critical">عالية جداً</span>
            </div>
            <div style='font-size: 1.5rem; font-weight: 700; color: #7b1fa2; 
                        line-height: 1.6; margin-bottom: 15px;'>
                ما قراءة ضغط دمك؟
            </div>
            <div style='margin-top: 18px; padding-top: 18px; 
                        border-top: 1px solid rgba(156,39,176,0.2); 
                        font-size: 0.95rem; color: #64748b;'>
                <strong>لماذا هذا السؤال؟</strong> تم اختياره بناءً على تحليل إجاباتك 
                السابقة وحساب الأولويات الديناميكي
            </div>
        </div>
    </div>
</div>
"""

st.markdown(original_html, unsafe_allow_html=True)

# اختبار 4: بدون unsafe_allow_html
st.subheader("اختبار 4: بدون unsafe_allow_html (سيظهر كنص)")
st.markdown(original_html)  # بدون unsafe_allow_html=True

st.success("إذا رأيت الاختبار 1 و 2 و 3 بتنسيق جميل، والاختبار 4 كنص خام، فالكود يعمل بشكل صحيح!")
