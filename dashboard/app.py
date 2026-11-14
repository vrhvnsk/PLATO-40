"""Streamlit incident replay. Launch: streamlit run dashboard/app.py"""
import json
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title='PLATO-40 | CLARA Future',layout='wide')
st.title('PLATO-40 | CLARA Future')
st.caption('Synthetic replay only. Simulated actions do not change recorded history.')
path=Path(st.sidebar.text_input('Decision file','decisions.jsonl'))
if not path.exists():
    st.info('Run `python run.py <data_dir> --out decisions.jsonl` first, or enter an existing decisions.jsonl path.')
    st.stop()
try:records=[json.loads(x) for x in path.read_text().splitlines() if x.strip()]
except Exception as exc:st.error(f'Cannot parse file: {exc}');st.stop()
if not records:st.warning('No incidents detected. Check data availability and detector thresholds.');st.stop()
df=pd.DataFrame(records)
issues=sorted(df.issue_type.dropna().unique())
selected=st.sidebar.multiselect('Issue types',issues,default=issues)
priorities=st.sidebar.multiselect('Priorities',['critical','high','medium','low'],default=['critical','high','medium','low'])
f=df[df.issue_type.isin(selected)&df.priority.isin(priorities)].copy()
c1,c2,c3=st.columns(3)
c1.metric('Decisions',len(f));c2.metric('Episodes',f.episode_id.nunique());c3.metric('Approval required',int(f.requires_human_approval.sum()))
st.subheader('Incident timeline')
if len(f):
    chart=f.assign(day=pd.to_datetime(f.timestamp_utc).dt.date).groupby(['day','issue_type']).size().unstack(fill_value=0)
    st.line_chart(chart)
st.subheader('Decision audit')
cols=['timestamp_utc','episode_id','issue_type','priority','action','requires_human_approval']
st.dataframe(f[cols],use_container_width=True,hide_index=True)
if len(f):
    options=list(f.event_id)
    eid=st.selectbox('Inspect a decision',options,format_func=lambda e:next((f'{r["timestamp_utc"]} | {r["issue_type"]} | {r["action"]}' for r in records if r['event_id']==e),e))
    d=next(r for r in records if r['event_id']==eid)
    left,right=st.columns(2)
    with left:
        st.markdown('**Evidence and rationale**');st.write(d['reason']);st.write(d.get('evidence',[]))
        st.write('Confidence (heuristic, not calibrated):',d.get('confidence'))
    with right:
        st.markdown('**Action and verification**')
        st.write('Action:',d['action']);st.write('Human approval:',d['requires_human_approval']);st.write('Guest consent:',d.get('requires_guest_consent',False))
        st.write('Verification:',d.get('verification_plan','Not specified'))
    st.info('Approval controls here are demo-only. They do not authorize a real-world action or change decisions.jsonl.')
    if d['requires_human_approval']:
        approved=st.checkbox('Simulate human approval',key=eid)
        consent=st.checkbox('Simulate guest consent',key=eid+'consent') if d.get('requires_guest_consent') else True
        if approved and consent:st.success('Mock execution eligible; no real actuation performed.')
        else:st.warning('Pending required approval/consent.')
    else:st.success('Eligible for mock autonomous execution, subject to operational validation.')
    st.json(d)
insights=path.parent/'insights.md'
if insights.exists():
    with st.expander('Annual CLARA / PLATO feedback'):
        st.markdown(insights.read_text())
