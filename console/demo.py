"""Top-level orchestrator for the console demo.

Flow:
    1. Parse --lang flag (ar | en)
    2. Spin up an IntegratedSelfReasoningChatbot (same brain the
       Streamlit app uses — BioBERT NER, 3-strikes, hallucination
       guard, progressive rephrasing, auto-skip with clinical default)
    3. Walk the patient through the 11 medical questions
    4. Pull the final assessment and replay the 7-stage walkthrough
"""
import argparse
import os
import sys

# Make the parent project importable when run as ``python -m console`` from
# the project root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.integrated_chatbot import IntegratedSelfReasoningChatbot
from .colors import header, cyan, bold, green, yellow
from .collector import collect_eleven_fields
from .stages import render_stages


_BANNER = {
    'ar': 'نظام تشخيص أمراض القلب — وضع وحدة التحكم',
    'en': 'Heart-Disease Assessment System — Console Mode',
}


def main() -> int:
    parser = argparse.ArgumentParser(
        prog='python -m console',
        description='Run the heart-disease assessment demo in the terminal.',
    )
    parser.add_argument(
        '--lang', choices=('ar', 'en'), default='ar',
        help='UI language for prompts and stage output (default: ar).',
    )
    args = parser.parse_args()
    lang = args.lang

    print(header(_BANNER[lang]))

    # The chatbot runs offline by default — Groq key is optional. The
    # 11-field collector and the 7 stage views below all work without it.
    groq_key = os.environ.get('GROQ_API_KEY') or None
    chatbot = IntegratedSelfReasoningChatbot(language=lang, groq_api_key=groq_key)

    if not groq_key:
        print(yellow(
            '  ⓘ ' + (
                'Groq غير مفعّل — النظام يعمل بـ BioBERT المحلي فقط.'
                if lang == 'ar'
                else 'Groq not configured — using local BioBERT NER only.'
            )
        ))

    # ─── Step 1: collect the 11 fields interactively ──────────────────
    collect_eleven_fields(chatbot, lang)

    # ─── Step 2: run the full pipeline & display 7 stages ─────────────
    print(header(
        'تجهيز التقييم الشامل…' if lang == 'ar'
        else 'Building the comprehensive assessment…'
    ))
    final_assessment = chatbot.get_final_assessment()

    if final_assessment.get('status') != 'complete':
        print(yellow(
            'لم يتمكّن النظام من إكمال التقييم — راجع سجل الـ logs.'
            if lang == 'ar'
            else "Assessment did not complete — check the logs."
        ))
        return 1

    render_stages(
        final_assessment,
        facts=dict(chatbot.facts),
        field_meta=dict(chatbot.get_field_metadata() or {}),
        lang=lang,
    )

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
