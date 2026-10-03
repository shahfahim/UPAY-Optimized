import re
with open('web/src/pages/hub/Overview.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the chart block
chart_pattern = r'<div className="h-48 w-full">.*?</div>\s*</Card>'
replacement = """<div className="h-48 w-full [&_svg]:outline-none select-none">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 15, right: 10, left: -20, bottom: 0 }} barSize={40}>
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 13, fill: '#64748b', fontWeight: 600 }} />
                <YAxis tickFormatter={(v) => `৳ ${(v / 1000).toFixed(0)}k`} axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#94a3b8' }} />
                <Tooltip 
                  cursor={{ fill: '#f1f5f9', opacity: 0.5 }} 
                  content={({ active, payload, label }: any) => {
                    if (active && payload && payload.length) {
                      return (
                        <div className="bg-slate-800/95 backdrop-blur-md text-white text-[13px] rounded-xl py-2 px-3 shadow-xl border border-slate-700/50">
                          <p className="font-medium text-slate-300">{label}</p>
                          <p className="text-white font-bold mt-0.5 tracking-wide">
                            ৳ {payload[0].value.toLocaleString('en-US')}
                          </p>
                        </div>
                      )
                    }
                    return null
                  }}
                />
                <Bar dataKey="value" radius={[8, 8, 8, 8]} background={{ fill: '#f8fafc', radius: [8, 8, 8, 8] }} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>"""

code = re.sub(chart_pattern, replacement, code, flags=re.DOTALL)

# Ensure numbers are formatted with en-US to satisfy the English numbers rule
code = code.replace("toLocaleString('bn-BD')", "toLocaleString('en-US')")

with open('web/src/pages/hub/Overview.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated Overview.tsx")
