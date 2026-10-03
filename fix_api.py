import re

with open('backend/hishab/api/routes/savings.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Import BaseModel
if 'from pydantic import BaseModel' not in code:
    code = code.replace('from fastapi import APIRouter, Depends, Request', 'from fastapi import APIRouter, Depends, Request\nfrom pydantic import BaseModel')

# Add schema
if 'class PocketDeleteIn' not in code:
    code = code + """
class PocketDeleteIn(BaseModel):
    pass

class PocketAddIn(BaseModel):
    name_bn: str

@router.delete("/users/{uid}/savings/pockets/{pocket}")
def delete_pocket(uid: str, pocket: str, request: Request):
    return request.app.state.svc.delete_pocket(uid, pocket)

@router.post("/users/{uid}/savings/pockets/{pocket}")
def add_pocket(uid: str, pocket: str, body: PocketAddIn, request: Request):
    return request.app.state.svc.add_pocket(uid, pocket, body.name_bn)
"""

with open('backend/hishab/api/routes/savings.py', 'w', encoding='utf-8') as f:
    f.write(code)

with open('backend/hishab/services_hub.py', 'r', encoding='utf-8') as f:
    svc_code = f.read()

if 'def delete_pocket' not in svc_code:
    new_methods = """    @locked
    def delete_pocket(self, uid, pocket):
        ctx = self.ctx(uid)
        if pocket in ctx.state.pockets:
            del ctx.state.pockets[pocket]
        self.store.save_state(uid, ctx.state)
        return self.savings(uid)

    @locked
    def add_pocket(self, uid, pocket, name_bn):
        ctx = self.ctx(uid)
        ctx.state.pockets[pocket] = 0.0
        # save custom name to metadata or something, for now we will just rely on the frontend or fallback
        # Let's save it to a meta dict in state
        if not hasattr(ctx.state, 'custom_names'):
            ctx.state.custom_names = {}
        ctx.state.custom_names[pocket] = name_bn
        self.store.save_state(uid, ctx.state)
        return self.savings(uid)
"""
    svc_code = svc_code.replace("    # --- savings ", new_methods + "\n    # --- savings ")

# Update savings method to use custom_names
svc_code = svc_code.replace('name_bn = POCKET_BN.get(p, p.title())', 'name_bn = getattr(st, "custom_names", {}).get(p, POCKET_BN.get(p, p.title()))')

with open('backend/hishab/services_hub.py', 'w', encoding='utf-8') as f:
    f.write(svc_code)

print("Added backend add/delete endpoints!")
