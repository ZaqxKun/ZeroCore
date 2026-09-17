from collections import Counter
from google import genai
from google.genai import types
from zerocore.core.config import GEMINI_API_KEY, GEMINI_MODEL, CONSTITUTION
from zerocore.core.models import CommunityReview

SYSTEM = """
You are ZeroCore, the structural community analyst for District Zerø.
You do NOT maximize engagement. You minimize unnecessary structure.
Hard rules:
1. Frequency alone NEVER justifies a channel.
2. Casual invitations (ngopi, nongkrong, mabar, makan, nonton, jalan, hangout)
   belong in #general regardless of volume.
3. Repetitive phrases, memes, coordinated spam and one-night trends are weak evidence.
4. Prefer an existing channel, then a temporary thread, then a proposal, then a trial channel.
5. Never recommend Administrator, ownership transfer, mass deletion, or core-channel deletion.
6. A new channel requires durable distinct discussion AND meaningful structural need.
7. Reasons and summaries must be in Indonesian.
"""

class AIService:
    def __init__(self):
        self.client=genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

    async def review(self,messages,existing_channels):
        if not self.client:
            return None
        payload={
          "existing_channels": sorted(existing_channels),
          "rules":{
            "social":CONSTITUTION["social"],
            "channel_lifecycle":CONSTITUTION["channel_lifecycle"],
          },
          "stats":{
            "messages":len(messages),
            "unique_users":len({m["author_hash"] for m in messages}),
            "channels":Counter(m["channel_name"] for m in messages).most_common(20),
          },
          "messages":[
            {"channel":m["channel_name"],"user":m["author_hash"],"text":m["content"][:500],"time":m["created_at"]}
            for m in messages
          ],
        }
        r=await self.client.aio.models.generate_content(
            model=GEMINI_MODEL,
            contents=f"{SYSTEM}\n\nData komunitas:\n{payload}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=CommunityReview,
            ),
        )
        if not r.text:
            raise RuntimeError("Gemini mengembalikan respons kosong.")
        return CommunityReview.model_validate_json(r.text)
