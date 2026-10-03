import re

with open('web/src/pages/hub/AgentLocator.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the first useEffect
old_pattern = r"  useEffect\(\(\) => \{[\s\S]*?\}, \[L\]\)"

new_use_effect = """  useEffect(() => {
    const fallbackLocation = () => {
      setGeoError(L('লোকেশন ব্লক করা হয়েছে (HTTP)। ডিফল্ট লোকেশন (ঢাকা) দেখানো হচ্ছে।', 'Location blocked (HTTP). Showing default (Dhaka).'))
      setLocation({ lat: 23.8103, lng: 90.4125 })
    }

    if (!navigator.geolocation) {
      fallbackLocation()
      return
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation({
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        })
      },
      (error) => {
        fallbackLocation()
      }
    )
  }, [L])"""

code = re.sub(old_pattern, new_use_effect, code)

with open('web/src/pages/hub/AgentLocator.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated AgentLocator.tsx with fallback location logic!")
