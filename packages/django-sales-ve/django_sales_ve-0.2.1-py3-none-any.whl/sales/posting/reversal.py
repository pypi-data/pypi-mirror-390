from decimal import Decimal
from finacc.models.journal import JournalEntry, JournalLine


def build_reversal(entry: JournalEntry, memo_suffix: str = " REV") -> JournalEntry:
    rev = JournalEntry.objects.create(
    company=entry.company,
    date=entry.date,
    currency=entry.currency,
    memo=f"{entry.memo}{memo_suffix}",
    )
    for l in entry.lines.all():
        JournalLine.objects.create(
        entry=rev,
        account=l.account,
        description=f"Reversal of {l.description}",
        debit=l.credit,
        credit=l.debit,
        )
    return rev