

ENHANCED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;800&family=Tajawal:wght@300;400;500;700&display=swap');

/* 
   GLOBAL STYLES - الأنماط العامة
    */

* {
    font-family: 'Tajawal', 'Cairo', sans-serif;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.main {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    background-attachment: fixed;
}

/* 
   HEADER STYLES - أنماط الرأس
    */

.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2.5rem 2rem;
    border-radius: 20px;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    position: relative;
    overflow: hidden;
}

.main-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    animation: pulse 4s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 0.5; }
    50% { transform: scale(1.1); opacity: 0.8; }
}

.main-title {
    font-size: 2.5rem;
    font-weight: 800;
    color: white;
    margin: 0;
    text-align: center;
    text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    position: relative;
    z-index: 1;
}

.main-subtitle {
    font-size: 1.1rem;
    color: rgba(255,255,255,0.9);
    margin: 0.5rem 0 0 0;
    text-align: center;
    font-weight: 300;
    position: relative;
    z-index: 1;
}

/* 
   CARD STYLES - أنماط البطاقات
    */

.modern-card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    transition: all 0.3s ease;
    position: relative;
}

.modern-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.12);
}

.card-header {
    font-size: 1.3rem;
    font-weight: 700;
    color: #2d3748;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 2px solid #e2e8f0;
}

/* 
   MESSAGE BUBBLES - فقاعات الرسائل
    */

.message-bubble {
    padding: 1.25rem 1.5rem;
    border-radius: 18px;
    margin: 1rem 0;
    animation: slideIn 0.4s ease-out;
    position: relative;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.user-message {
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    border-left: 4px solid #2196f3;
    margin-right: 2rem;
}

.bot-message {
    background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
    border-left: 4px solid #9c27b0;
    margin-left: 2rem;
}

.message-sender {
    font-weight: 700;
    font-size: 1rem;
    margin-bottom: 0.75rem;
    display: block;
}

.user-message .message-sender {
    color: #1976d2;
}

.bot-message .message-sender {
    color: #7b1fa2;
}

.message-content {
    color: #2d3748;
    line-height: 1.8;
    font-size: 1.05rem;
}

/* 
   QUESTION BOX - صندوق السؤال
    */

.question-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 20px;
    margin: 2rem 0;
    box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    position: relative;
    overflow: hidden;
}

.question-box::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
    animation: shine 3s infinite;
}

@keyframes shine {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

.question-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    position: relative;
    z-index: 1;
}

.question-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: white;
    margin: 0;
}

.question-badge {
    background: rgba(255,255,255,0.25);
    padding: 0.5rem 1.25rem;
    border-radius: 25px;
    font-size: 0.9rem;
    font-weight: 600;
    color: white;
    backdrop-filter: blur(10px);
}

.question-text {
    font-size: 1.6rem;
    font-weight: 700;
    color: white;
    margin: 1rem 0;
    line-height: 1.5;
    position: relative;
    z-index: 1;
}

.question-examples {
    background: rgba(255,255,255,0.15);
    padding: 1.25rem;
    border-radius: 12px;
    margin-top: 1.5rem;
    backdrop-filter: blur(10px);
    position: relative;
    z-index: 1;
}

.examples-title {
    font-weight: 700;
    color: white;
    margin-bottom: 0.75rem;
    font-size: 1.05rem;
}

.examples-list {
    color: rgba(255,255,255,0.95);
    line-height: 2;
    font-size: 1rem;
}

.question-note {
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid rgba(255,255,255,0.3);
    font-size: 0.95rem;
    color: rgba(255,255,255,0.9);
    position: relative;
    z-index: 1;
}

/* 
   BOT RESPONSE - رد النظام
    */

.bot-analysis {
    background: white;
    padding: 1.5rem;
    border-radius: 16px;
    margin: 1rem 0;
    border-left: 4px solid #9c27b0;
    box-shadow: 0 4px 15px rgba(156, 39, 176, 0.1);
}

.analysis-section {
    margin: 1.25rem 0;
    padding: 1rem;
    border-radius: 10px;
    background: #f8f9fa;
}

.section-title {
    font-weight: 700;
    font-size: 1.1rem;
    margin-bottom: 0.75rem;
    display: block;
}

.analysis-thought {
    border-left-color: #2196f3;
}

.analysis-thought .section-title {
    color: #1976d2;
}

.analysis-inference {
    border-left-color: #4caf50;
}

.analysis-inference .section-title {
    color: #388e3c;
}

.analysis-decision {
    border-left-color: #ff9800;
}

.analysis-decision .section-title {
    color: #f57c00;
}

.analysis-warning {
    background: #fff3e0;
    border-left-color: #f44336;
}

.analysis-warning .section-title {
    color: #d32f2f;
}

.section-content {
    color: #2d3748;
    line-height: 1.7;
    font-size: 1.05rem;
}

/* 
   PRIORITY BADGE - شارة الأولوية
    */

.priority-badge {
    display: inline-block;
    padding: 0.4rem 1rem;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.priority-critical {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    color: white;
    box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
}

.priority-high {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    color: white;
    box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
}

.priority-medium {
    background: linear-gradient(135deg, #eab308 0%, #ca8a04 100%);
    color: white;
    box-shadow: 0 4px 15px rgba(234, 179, 8, 0.3);
}

.priority-normal {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
}

/* 
   INPUT AREA - منطقة الإدخال
    */

.input-container {
    background: white;
    padding: 2rem;
    border-radius: 16px;
    margin: 2rem 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

.input-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #2d3748;
    margin-bottom: 1.5rem;
}

/* 
   PROGRESS STYLES - أنماط التقدم
    */

.progress-container {
    background: white;
    padding: 1.5rem;
    border-radius: 16px;
    margin: 1rem 0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.06);
}

.progress-title {
    font-weight: 700;
    color: #2d3748;
    margin-bottom: 1rem;
    font-size: 1.1rem;
}

.progress-bar-container {
    background: #e2e8f0;
    height: 12px;
    border-radius: 10px;
    overflow: hidden;
    position: relative;
}

.progress-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    border-radius: 10px;
    transition: width 0.5s ease;
    position: relative;
    overflow: hidden;
}

.progress-bar-fill::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
    animation: shimmer 2s infinite;
}

@keyframes shimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

.progress-text {
    margin-top: 0.5rem;
    color: #64748b;
    font-size: 0.95rem;
    text-align: center;
}

/* 
   FACTS TABLE - جدول الحقائق
    */

.facts-table {
    background: white;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    margin: 1rem 0;
}

.facts-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.25rem 1.5rem;
    font-weight: 700;
    font-size: 1.2rem;
}

.fact-row {
    padding: 1rem 1.5rem;
    border-bottom: 1px solid #e2e8f0;
    transition: background 0.2s ease;
}

.fact-row:hover {
    background: #f8f9fa;
}

.fact-row:last-child {
    border-bottom: none;
}

.fact-label {
    font-weight: 600;
    color: #4a5568;
    margin-bottom: 0.25rem;
}

.fact-value {
    color: #2d3748;
    font-size: 1.1rem;
    font-weight: 500;
}

/* 
   SIDEBAR STYLES - أنماط الشريط الجانبي
    */

.sidebar .sidebar-content {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    margin: 0.5rem 0;
}

/* 
   BUTTONS - الأزرار
    */

.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.75rem 2rem;
    font-size: 1.05rem;
    font-weight: 600;
    border-radius: 12px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.stButton > button:active {
    transform: translateY(0);
}

/* 
   ANIMATIONS - الحركات
    */

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.fade-in {
    animation: fadeIn 0.5s ease-out;
}

@keyframes bounceIn {
    0% {
        opacity: 0;
        transform: scale(0.3);
    }
    50% {
        opacity: 1;
        transform: scale(1.05);
    }
    70% {
        transform: scale(0.9);
    }
    100% {
        transform: scale(1);
    }
}

.bounce-in {
    animation: bounceIn 0.6s ease-out;
}

/* 
   RESPONSIVE - التجاوب
    */

@media (max-width: 768px) {
    .main-title {
        font-size: 1.8rem;
    }
    
    .question-text {
        font-size: 1.3rem;
    }
    
    .message-bubble {
        margin-left: 0;
        margin-right: 0;
    }
}

/* 
   UTILITIES - الأدوات المساعدة
    */

.text-center {
    text-align: center;
}

.mt-1 { margin-top: 0.5rem; }
.mt-2 { margin-top: 1rem; }
.mt-3 { margin-top: 1.5rem; }
.mt-4 { margin-top: 2rem; }

.mb-1 { margin-bottom: 0.5rem; }
.mb-2 { margin-bottom: 1rem; }
.mb-3 { margin-bottom: 1.5rem; }
.mb-4 { margin-bottom: 2rem; }

.p-1 { padding: 0.5rem; }
.p-2 { padding: 1rem; }
.p-3 { padding: 1.5rem; }
.p-4 { padding: 2rem; }

/*
   PLOTLY HOVER TOOLTIPS — RTL FIX (STRONGER VERSION)
   When the page is in RTL mode (Arabic UI) the browser uses an
   inverted coordinate system for absolute positioning, so Plotly's
   hover tooltip appears far from the data point the cursor is on.
   The fix is to force the *entire* Plotly wrapper (Streamlit's
   stPlotlyChart container, the Plotly chart div, the hover layer
   and every descendant) into a fixed LTR coordinate system. We
   also re-center the tooltip text inside its box for readability.
 */

/* (1) Force the Streamlit Plotly wrapper itself to LTR — this is
       what stops the tooltip rectangle from jumping to the wrong
       half of the chart on RTL pages */
[data-testid="stPlotlyChart"],
[data-testid="stPlotlyChart"] *,
div.stPlotlyChart,
div.stPlotlyChart *,
.js-plotly-plot,
.js-plotly-plot * {
    direction: ltr !important;
    unicode-bidi: isolate !important;
}

/* (2) The hover layer that holds the tooltip rectangle + labels */
.js-plotly-plot .hoverlayer,
.js-plotly-plot .hoverlayer .hovertext,
.js-plotly-plot .hoverlayer .hovertext * {
    direction: ltr !important;
    unicode-bidi: isolate !important;
}

/* (3) Glue the hover text labels back inside the rectangle */
.js-plotly-plot .hoverlayer .hovertext .name,
.js-plotly-plot .hoverlayer .hovertext .nums,
.js-plotly-plot .hoverlayer .hovertext text {
    text-anchor: middle !important;
    dominant-baseline: middle !important;
    direction: ltr !important;
    unicode-bidi: isolate !important;
}

/* (4) Slightly thicker tooltip border keeps text from visually
       drifting past the edge on fractional-pixel layouts */
.js-plotly-plot .hoverlayer .hovertext path,
.js-plotly-plot .hoverlayer .hovertext rect {
    stroke-width: 1.5 !important;
}

/* (5) Same direction reset for the legend and modebar, otherwise
       legend swatches and modebar buttons end up on the wrong side */
.js-plotly-plot .legend text,
.js-plotly-plot .modebar text,
.js-plotly-plot .modebar-container {
    direction: ltr !important;
    unicode-bidi: isolate !important;
}

/* (6) Reset text-align on the chart wrapper so Plotly's annotations
       and axis ticks are placed where Plotly expects them */
[data-testid="stPlotlyChart"] {
    text-align: left !important;
}

</style>
"""
