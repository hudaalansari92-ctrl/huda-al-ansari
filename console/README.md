# Console Mode — Heart-Disease Assessment

A terminal-driven version of the heart-disease assessment system.
Same brain as the Streamlit app (BioBERT NER, 48 domain rules, ERPM
neural network, 3-strikes + progressive rephrasing, auto-skip with
clinical defaults) — only the I/O is `input()` / `print()`.

## Why

- **No browser needed** — runs inside PyCharm's Run window or any
  terminal.
- **Same NLP pipeline** as the Streamlit smart-chat: you answer the
  11 medical questions in free text and the system extracts them with
  BioBERT.
- **Step-by-step** — after the 11 fields are in, the 7 diagnostic
  stages render one at a time with an `Enter` pause between each,
  so an examiner can read along.
- **Bilingual** — `--lang ar` (default) or `--lang en`.

## Run it

From the project root:

```bash
python -m console            # Arabic
python -m console --lang en  # English
```

In PyCharm: right-click `console/__main__.py` → Run.

(Optional) set `GROQ_API_KEY` in your environment for richer NLP; the
demo runs fully offline if it's not set.

## What the conversation looks like

```
══════════════════════════════════════════════════════════════════════
  نظام تشخيص أمراض القلب — وضع وحدة التحكم
══════════════════════════════════════════════════════════════════════
  ⓘ Groq غير مفعّل — النظام يعمل بـ BioBERT المحلي فقط.

──────────────────────────────────────────────────────────────────────
  سأطرح عليك أسئلة لجمع 11 معلومة طبية. أجب بأسلوبك الطبيعي.
──────────────────────────────────────────────────────────────────────

السؤال 1 من 11

> ما هو عمرك؟
  إجابتك: عمري 55 سنة
  ✓ تم تسجيل: العمر = 55

السؤال 2 من 11
...
```

If you answer something unrelated, the system follows the same
3-strikes flow as the chatbot:

```
> ما هو ضغط دمك؟
  إجابتك: ما أعرف

  لم تُجب على السؤال المطروح — دعني أعيد صياغته:

> اكتب ضغطك بصيغة الانقباضي/الانبساطي (مثل: 120/80)، أو اكتب 'طبيعي'.
  إجابتك: ...
```

After all 11 fields are in, the 7 stages render one Enter at a time:

```
══════════════════════════════════════════════════════════════════════
  المرحلة 1 من 7 — البيانات الخام للمريض
══════════════════════════════════════════════════════════════════════
  ما يحدث الآن: هذه هي الـ 11 معلومة التي جمعناها…

  ┌──────────────────────┬─────────┬──────────┐
  │ الحقل                │ القيمة   │ المصدر    │
  ├──────────────────────┼─────────┼──────────┤
  │ العمر                │ 55      │ المريض    │
  │ …                    │ …       │ …        │
  └──────────────────────┴─────────┴──────────┘

  ▸ اضغط Enter للمرحلة التالية...
```

## Files

| File              | Role                                                    |
|-------------------|---------------------------------------------------------|
| `__init__.py`     | Package marker + docstring                              |
| `__main__.py`     | Makes `python -m console` work                          |
| `demo.py`         | Top-level orchestrator (CLI args, banner, pipeline)     |
| `collector.py`    | 11-field interactive loop, reuses the chatbot's NER     |
| `stages.py`       | 7-stage walkthrough with `Enter` pauses                 |
| `colors.py`       | Thin `colorama` helpers                                 |
