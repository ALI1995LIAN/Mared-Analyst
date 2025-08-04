import streamlit as st
from openai import OpenAI
import base64
from PIL import Image
import io

# --------------------------------------------------------------------------
# 1. إعدادات الصفحة والواجهة
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="المارد المحلل",
    page_icon="🧞‍♂️",
    layout="wide"
)

# عرض العنوان الرئيسي
st.title("المارد المحلل 🧞‍♂️")
st.markdown("خبير التحليل الفني الذي يحول صور الشارتات إلى تحليل متقدم.")
st.divider()

# --------------------------------------------------------------------------
# 2. الاتصال بـ OpenAI وإدارة المفتاح السري
# --------------------------------------------------------------------------
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("لم يتم العثور على مفتاح OpenAI السري. يرجى إضافته في إعدادات التطبيق (Secrets) عند النشر.")
    st.stop()

# --------------------------------------------------------------------------
# 3. منطق رفع الصور وتحليلها
# --------------------------------------------------------------------------
uploaded_file = st.file_uploader(
    "ارفع صورة الشارت هنا للتحليل",
    type=["png", "jpg", "jpeg", "webp"]
)

ANALYSIS_PROMPT = """
أنت 'المارد المحلل'، خبير عالمي في تحليل الأسواق المالية. مهمتك هي تحليل صورة الشارت المقدمة لك وتقديم خطة تداول كاملة.

**الخطوة الأولى والأكثر أهمية (العين السحرية):**
قبل أي شيء آخر، قم بإجراء مسح بصري دقيق (OCR) للصورة. يجب عليك استخراج جميع الأرقام الظاهرة على محور السعر (المحور العمودي) بدقة متناهية. يجب أن يكون تحليلك بالكامل مبنيًا على هذه الأرقام الحقيقية.

**منهجية التحليل:**
بناءً على الأرقام الدقيقة، قم بتحليل الشارت باستخدام مفاهيم المال الذكي (SMC).

**تنسيق المخرجات (مهم جدًا):**
يجب أن يكون ردك **حصراً** كائن JSON باللغة العربية، بدون أي نصوص إضافية قبله أو بعده. يجب أن يحتوي الـ JSON على المفاتيح التالية بالضبط:
{
  "decision": "شراء/بيع/انتظار",
  "confidence": "عالي/متوسط/منخفض",
  "analysis_summary": {
    "market_structure": "وصف موجز لهيكل السوق الحالي.",
    "liquidity_targets": "تحديد مستويات السيولة المستهدفة.",
    "key_zone": "تحديد أهم منطقة طلب أو عرض."
  },
  "trade_plan": {
    "entry_point": "السعر المقترح للدخول",
    "stop_loss": "السعر المقترح لوقف الخسارة",
    "take_profit_1": "الهدف الأول",
    "take_profit_2": "الهدف الثاني"
  },
  "final_reasoning": "ملخص نهائي لسبب اتخاذ هذا القرار."
}
"""

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="الشارت المرفوع للتحليل", width=600)

    if st.button("🔮 ابدأ التحليل السحري", use_container_width=True):
        with st.spinner("المارد يعكف على تحليل الشارت... الرجاء الانتظار..."):
            try:
                buffered = io.BytesIO()
                image.save(buffered, format=image.format)
                img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                img_url = f"data:image/png;base64,{img_str}"

                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": ANALYSIS_PROMPT},
                                {"type": "image_url", "image_url": {"url": img_url}},
                            ],
                        }
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.2,
                )
                
                analysis_result = response.choices[0].message.content
                st.success("تم التحليل بنجاح!")
                st.json(analysis_result)

            except Exception as e:
                st.error(f"حدث خطأ فادح أثناء الاتصال بـ OpenAI: {e}")
