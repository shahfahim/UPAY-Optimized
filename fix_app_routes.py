import re

with open('web/src/App.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# I want to swap <Route index element={<Overview />} /> and <Route path="ask" element={<Ask />} />
# Let's replace the block entirely.

old_block = """        <Route path="hishab" element={<HubLayout />}>
          <Route index element={<Overview />} />
          <Route path="calendar" element={<Calendar />} />
          <Route path="learn" element={<Learn />} />
          <Route path="ask" element={<Ask />} />
        </Route>"""

new_block = """        <Route path="hishab" element={<HubLayout />}>
          <Route index element={<Ask />} />
          <Route path="overview" element={<Overview />} />
          <Route path="calendar" element={<Calendar />} />
          <Route path="learn" element={<Learn />} />
        </Route>"""

code = code.replace(old_block, new_block)

with open('web/src/App.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("App.tsx routing updated!")
