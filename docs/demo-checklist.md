# Demo checklist

Run on the live URL (and locally) before submission and before the 7 Oct final.

**How to use it:**

- Start with **আরো → Demo reset**.
- The default user is Rina (U0001), unless a line says otherwise.
- Tick each line only after seeing it work.

## Shell and auth (Task 22)

- [ ] Splash plays (yellow → mark → blue stroke), then the Welcome screen; tapping skips it.
- [ ] The permanent ribbon "Prototype — upay-এর অফিসিয়াল app নয়" is visible on every screen.
- [ ] Login shows "Demo — আসল PIN দেবেন না". Tapping the demo user রিনা আক্তার opens Home.
- [ ] Registration: the demo OTP is shown on screen; Bangla digits are accepted; the new user lands on Home with history.
- [ ] Header: avatar, ব্যালেন্স reveal (shows the safe-to-spend line), bell with an unread count, and the আরো menu.
- [ ] Message strip rotates; the first line is "সাবধান: টাকা আর প্রায় ১১ দিন চলবে". Tapping it opens the Hishab hub.
- [ ] Bottom nav হোম · অ্যাকাউন্ট · QR · হিস্টরি · হিসাব, with the red "১১ দিন" badge.
- [ ] The সাম্প্রতিক পেমেন্ট row shows 4 items, and tapping one opens the prefilled flow.
- [ ] Non-Hishab entries open "এই ফিচার demo-তে চালু নেই".
- [ ] No horizontal scroll at 375 px.
- [ ] আরো → time travel +7 days creates a notification; the 60-day total cap shows a message; Demo reset restores 18 Sep.

## Hishab hub (Task 24)

- [ ] Risk card "২৯ সেপ্টেম্বরের দিকে প্রায় ৳১,১৪৫ কম পড়তে পারে · ৮৩%"; "কেন?" lists the reasons.
- [ ] Forecast chart shows the band, the expected line, the ৳২০০ line and the shortfall dot. "কী হবে দেখো" draws the green what-if line.
- [ ] রাজি / বাদ removes the card and shows a toast.
- [ ] Budget (day/week/month, auto/manual), Calendar (past + predicted days) and Learn (lessons) load.
- [ ] Health page: indicators, habits ("শুক্রবারে খরচ বেশি হয়"), the monthly report, and readiness signals with the disclaimer.

## সঞ্চয় (Task 25)

- [ ] Savings home order: আমার পকেট, সঞ্চয় লেভেল, জরুরি টাকা, ডিপিএস, ই-টিন (static sheet).
- [ ] The paisa toggle turns on and stays on after reload.
- [ ] Pocket in/out works; withdraw is never blocked beyond the pocket balance.
- [ ] Eid card "সপ্তাহে ৳১২০"; "ঈদ pocket-এ লক্ষ্য বসাও" sets a goal with a progress bar.
- [ ] Goal planner returns the monthly amount, the likelihood and the helpful actions.
- [ ] Levels page: Rina is at level 0, with the 5/10/15/30 path and the note "লেভেল কোনো সেবা বন্ধ করে না".
- [ ] DPS: Rina sees Smart DPS "এখন না" with the reason. U0005 সুমি sees ৳৩,০০০ pre-highlighted, "আনুমানিক, মুনাফা ছাড়া", and dropdowns that stay selectable.
- [ ] Emergency for U0005 with ৳৩০০০: the emergency pocket is listed first; a DPS loan, if any, is last with "চূড়ান্ত সিদ্ধান্ত ব্যাংক নেবে".

## Flows (Task 26)

- [ ] Send money: ৳৫০০০ to "মা (অন্য wallet)" shows NPSB as cheapest, fee ৳২৫, "cash-out পথের চেয়ে ৳৬৭.৫০ কম". "সব পথ দেখো" lists both routes.
- [ ] Sending more than the balance shows "পর্যাপ্ত ব্যালেন্স নেই".
- [ ] Cash-out shows the NPSB nudge once; after "তবুও cash-out" it is gone.
- [ ] With paisa on, pay ৳১২০.৪০ at a merchant (any 6-digit PIN). The success screen shows ৳০.৯৮ to paisa saving and the new balance ৳১,২৯৬.০০.
- [ ] Pay bill and mobile recharge open with AI category chips.

## Ask + Impact (Task 27)

- [ ] All 4 suggested chips return Bangla answers, and "যে তথ্য দেখে উত্তর" lists the sources.
- [ ] The mic button shows in Chrome, and a Bangla voice question is transcribed.
- [ ] An empty question, or one over 500 characters, shows an inline error.
- [ ] With `ANTHROPIC_API_KEY` set on the live Space, answers carry the AI badge.
- [ ] `/impact` shows the headline tiles, models table, bandit curves, fairness flags, readiness table and assumptions, at both 375 px and desktop width.
