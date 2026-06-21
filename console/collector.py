"""Interactive 11-field collector — same NLP + 3-strikes + progressive
rephrasing pipeline the Streamlit smart-chat uses, just driven through
``input()`` instead of a text box."""
from typing import Optional

from core.integrated_chatbot import IntegratedSelfReasoningChatbot
from config.translations import get_field_names_dict, get_field_name
from .colors import cyan, green, yellow, red, blue, magenta, bold, subheader


ALL_FIELDS = (
    'Age', 'Sex', 'ChestPain', 'BloodPressure', 'Cholesterol',
    'FastingBS', 'RestingECG', 'MaxHR', 'ExerciseAngina', 'Oldpeak', 'ST_Slope',
)


# Tiny i18n dict — local to this module to keep collector strings together.
_STR = {
    'ar': {
        'intro':         'سأطرح عليك أسئلة لجمع 11 معلومة طبية. أجب بأسلوبك الطبيعي.',
        'asking':        'السؤال {n} من 11',
        'your_answer':   'إجابتك',
        'understood':    'تم تسجيل',
        'rephrase':      'إعادة صياغة السؤال:',
        'dodge':         'لم تُجب على السؤال المطروح — دعني أعيد صياغته:',
        'auto_skipped':  'تم تخطّي السؤال تلقائياً بعد 3 محاولات. تم تسجيل القيمة الافتراضية: {value}',
        'done':          'تم جمع جميع الـ 11 معلومة بنجاح.',
    },
    'en': {
        'intro':         "I'll ask 11 medical questions. Answer naturally in your own words.",
        'asking':        'Question {n} of 11',
        'your_answer':   'Your answer',
        'understood':    'Recorded',
        'rephrase':      'Let me rephrase the question:',
        'dodge':         "You haven't answered the question I asked — let me rephrase it:",
        'auto_skipped':  'Skipped automatically after 3 attempts. Recorded default: {value}',
        'done':          'All 11 fields collected.',
    },
}


def _ask_one(chatbot: IntegratedSelfReasoningChatbot, field: str, lang: str) -> None:
    """Ask the chatbot's next question for ``field``, loop until it's
    answered (or auto-skipped after 3 misses). Mutates chatbot.facts."""
    field_names = get_field_names_dict(lang)
    pretty_field = field_names.get(field, field)
    s = _STR[lang]

    # Start fresh: clear any leftover attempt counter for this field.
    chatbot._field_attempts.pop(field, None)
    chatbot._last_asked_field = field

    attempt_level = 0  # 0 = original L1, 1 = with example, 2 = last try
    while True:
        prompt = chatbot.get_rephrased_question(field, attempt_level, lang) or pretty_field
        print()
        print(magenta(f'> {prompt}'))
        user_text = input(cyan(f'  {s["your_answer"]}: ')).strip()

        if not user_text:
            user_text = ' '  # avoid empty-string short-circuit in NER

        result = chatbot.process_smart_input(user_text)

        extracted_fields = {
            it.get('field') for it in (result.get('extracted_fields') or [])
        }
        if field in extracted_fields:
            value = chatbot.facts.get(field)
            print(green(f'  ✓ {s["understood"]}: {pretty_field} = {value}'))
            return

        # Wrong field (or nothing) — register a failed attempt for this field
        attempt = chatbot.register_failed_attempt(field_name=field)

        if attempt.get('auto_skipped'):
            print(yellow('  ' + s['auto_skipped'].format(value=attempt['skipped_value'])))
            return

        # Tell the patient they dodged + rephrase via the next attempt level
        if extracted_fields:
            captured = ', '.join(
                f'{field_names.get(f, f)}={chatbot.facts.get(f)}'
                for f in extracted_fields
            )
            print(blue(f'  • {s["understood"]}: {captured}'))
            print(yellow(f'  {s["dodge"]}'))
        attempt_level = min(attempt['attempts'], 2)


def collect_eleven_fields(chatbot: IntegratedSelfReasoningChatbot, lang: str) -> None:
    """Walk the 11 fields in priority order, asking one at a time."""
    s = _STR[lang]
    print(subheader(s['intro']))

    for i, field in enumerate(ALL_FIELDS, 1):
        if field in chatbot.answered_fields:
            continue
        print(bold(s['asking'].format(n=i)))
        _ask_one(chatbot, field, lang)

    print()
    print(green(bold('  ' + s['done'])))
