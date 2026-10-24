"""
Every assumption the pipeline and the dashboard depend on, in one place.

train.py and app.py both import this file. The app recomputes all costs from
the saved test-set scores every time it starts, so after changing a cost figure
you only need to restart the app. Re-run training only if you change the
dataset or training settings.

THE COST AND OPERATIONS FIGURES BELOW ARE PLACEHOLDERS so the code runs.
Replace every one marked PLACEHOLDER with your own figure, and justify each
in REPORT.md ("I assumed X because Y, and the answer changes if X drops below Z").
"""

# ----------------------------------------------------------------------------
# Dataset on Roboflow Universe (record these exact values in REPORT.md)
# ----------------------------------------------------------------------------
WORKSPACE = "defect-detection-fxtd5"
PROJECT = "weld-defect-lze1x"
VERSION = 1

# ----------------------------------------------------------------------------
# Training settings (record these in REPORT.md too)
# ----------------------------------------------------------------------------
BASE_MODEL = "yolo11n.pt"  # finetuned model starts from this COCO checkpoint
COCO_BASELINE = "yolo11n.pt"  # same checkpoint, used zero-shot as a baseline
EPOCHS = 60
PATIENCE = 20  # stop early if validation mAP has not improved for this many epochs
IMG_SIZE = 640
BATCH = 16
SEED = 0
CONFUSION_MATRIX_CONF = 0.25  # boxes below this confidence are ignored in the detection confusion matrix

# ----------------------------------------------------------------------------
# Class names
# ----------------------------------------------------------------------------
# Version 1 of this dataset exports its classes as "0", "1" and "2", with no
# names. The meaning below is the one used by the original three-class welding
# dataset (0 = Bad Weld, 1 = Good Weld, 2 = Defect). CHECK IT by looking at the
# boxes before training (see the preview cell), and fix it here if it differs.
# Set to None to keep whatever names the dataset ships with.
CLASS_NAMES = {0: "Bad Weld", 1: "Good Weld", 2: "Defect"}

# ----------------------------------------------------------------------------
# The decision
# ----------------------------------------------------------------------------
# One case = one inspection photo of a weld. The case is "positive" (needs
# action) if it contains at least one box of a class whose name contains one of
# these words. Everything else is treated as a good weld.
POSITIVE_CLASS_KEYWORDS = ("bad", "defect")

# ----------------------------------------------------------------------------
# Costs in euros per case                                     PLACEHOLDERS
# ----------------------------------------------------------------------------
COST_FN = 100.0  # PLACEHOLDER: bad weld passed (missed)
COST_FP = 10.0  # PLACEHOLDER: good weld failed (needless rework / re-check)
COST_TP = 10.0  # PLACEHOLDER: bad weld correctly failed (the rework itself)
COST_TN = 0.0  # PLACEHOLDER: good weld correctly passed

# Production base rate: share of welds that are actually bad on the real line.
# This is NOT the share in the test set; the cost maths reweights to this.
BASE_RATE = 0.10  # PLACEHOLDER

# ----------------------------------------------------------------------------
# Human review                                                PLACEHOLDERS
# ----------------------------------------------------------------------------
DAILY_VOLUME = 1000  # PLACEHOLDER: welds photographed per day
REVIEW_SECONDS = 30  # PLACEHOLDER: time for an inspector to check one case
INSPECTOR_HOURLY_COST = 30.0  # PLACEHOLDER: fully loaded cost per hour, EUR
INSPECTOR_HOURS_PER_DAY = 6.0  # PLACEHOLDER: productive checking hours per person per day
HUMAN_MISS_RATE = 0.0  # PLACEHOLDER: share of bad welds an inspector still passes
HUMAN_FALSE_ALARM_RATE = 0.0  # PLACEHOLDER: share of good welds an inspector fails

COST_REVIEW = REVIEW_SECONDS / 3600 * INSPECTOR_HOURLY_COST  # labour per check, EUR

# ----------------------------------------------------------------------------
# Operating point
# ----------------------------------------------------------------------------
# Leave as None to use the cost-minimising values from the sweep. Set them to
# override, for example if the cost-optimal band needs more inspectors than
# you have. Scores are the model's highest defect confidence in the image.
CHOSEN_THRESHOLD = None  # model-alone threshold, e.g. 0.35
CHOSEN_BAND = None  # (low, high): below low = pass, at/above high = fail, between = human


def costs() -> dict[str, float]:
    return {
        "fn": COST_FN,
        "fp": COST_FP,
        "tp": COST_TP,
        "tn": COST_TN,
        "review": COST_REVIEW,
        "human_miss": HUMAN_MISS_RATE,
        "human_false_alarm": HUMAN_FALSE_ALARM_RATE,
    }


def as_table() -> list[tuple[str, str]]:
    """The assumptions, as rows for the dashboard."""
    return [
        ("Dataset", f"{WORKSPACE} / {PROJECT} / v{VERSION}"),
        ("Model", f"{BASE_MODEL}, {EPOCHS} epochs max, imgsz {IMG_SIZE}, batch {BATCH}"),
        ("Class names", ", ".join(f"{k} = {v}" for k, v in (CLASS_NAMES or {}).items()) or "as exported"),
        ("Positive class keywords", ", ".join(POSITIVE_CLASS_KEYWORDS)),
        ("Cost of a missed bad weld (FN)", f"€{COST_FN:,.2f}"),
        ("Cost of failing a good weld (FP)", f"€{COST_FP:,.2f}"),
        ("Cost of failing a bad weld (TP)", f"€{COST_TP:,.2f}"),
        ("Cost of passing a good weld (TN)", f"€{COST_TN:,.2f}"),
        ("Production base rate of bad welds", f"{BASE_RATE:.1%}"),
        ("Cases per day", f"{DAILY_VOLUME:,}"),
        ("Seconds per human check", f"{REVIEW_SECONDS}"),
        ("Inspector cost per hour", f"€{INSPECTOR_HOURLY_COST:,.2f}"),
        ("Productive checking hours per inspector per day", f"{INSPECTOR_HOURS_PER_DAY}"),
        ("Cost per human check", f"€{COST_REVIEW:,.2f}"),
        ("Inspector miss rate", f"{HUMAN_MISS_RATE:.1%}"),
        ("Inspector false-alarm rate", f"{HUMAN_FALSE_ALARM_RATE:.1%}"),
    ]
