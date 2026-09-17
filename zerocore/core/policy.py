from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from .config import CONSTITUTION
from .models import Action, TopicDecision

@dataclass
class PolicyResult:
    allowed: bool
    action: Action
    reason: str

class PolicyEngine:
    def __init__(self, db):
        self.db=db
        self.c=CONSTITUTION

    async def validate(self, d: TopicDecision) -> PolicyResult:
        life=self.c["channel_lifecycle"]
        if d.is_social_invite:
            return PolicyResult(False, Action.keep_in_general,
                "Ajakan sosial adalah fungsi #general; frekuensi tidak pernah menjadi alasan pembuatan channel.")
        if d.is_repetitive_or_spammy:
            return PolicyResult(False, Action.observe, "Repetisi/spam tidak dihitung sebagai kebutuhan komunitas.")
        if d.is_short_lived_trend:
            return PolicyResult(False, Action.observe, "Tren sementara belum membuktikan kebutuhan struktur.")
        if d.existing_channel_sufficient:
            return PolicyResult(False, Action.keep_in_general, "Ruang yang ada masih cukup.")
        if d.unique_users_estimate < life["minimum_unique_users"]:
            return PolicyResult(False, Action.observe, "Peserta unik belum cukup.")
        if d.active_days_estimate < life["minimum_active_days"]:
            return PolicyResult(False, Action.observe, "Topik belum bertahan cukup lama.")
        if d.meaningful_messages_estimate < life["minimum_meaningful_messages"]:
            return PolicyResult(False, Action.observe, "Percakapan bermakna belum cukup.")
        if d.confidence < life["minimum_ai_confidence"]:
            return PolicyResult(False, Action.observe, "Confidence AI di bawah threshold.")
        if d.structural_need < life["minimum_structural_need"]:
            return PolicyResult(False, Action.observe, "Kebutuhan struktural di bawah threshold.")

        last=await self.db.topic_last_action(d.normalized_topic)
        if last and datetime.now(timezone.utc)-last < timedelta(days=life["topic_cooldown_days"]):
            return PolicyResult(False, Action.observe, "Topik sedang cooldown.")

        if d.action in {Action.create_thread,Action.propose_trial_channel,Action.create_trial_channel}:
            return PolicyResult(True,d.action,"Memenuhi guardrail low-risk/reversible.")
        return PolicyResult(False,d.action,"Tidak ada tindakan otomatis yang lolos guardrail.")
