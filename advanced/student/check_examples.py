"""Public examples only. Python drives a browser, JavaScript is the submission."""
from pathlib import Path
import json,sys
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
if len(sys.argv)!=2:raise SystemExit('python check_examples.py TASK_KEY')
key=sys.argv[1];cases=json.loads((ROOT/'examples'/f'{key}.json').read_text(encoding='utf-8'))
with sync_playwright() as p:
 browser=p.chromium.launch()
 try:
  page=browser.new_page();page.add_script_tag(path=str(ROOT/'tasks'/f'{key}.js'))
  for n,c in enumerate(cases,1):
   result=json.loads(page.evaluate('(raw)=>JSON.stringify(solve(JSON.parse(raw)))',json.dumps(c['input'],ensure_ascii=False)))
   assert json.dumps(result,sort_keys=True,ensure_ascii=False)==json.dumps(c['expected'],sort_keys=True,ensure_ascii=False),(n,result,c['expected'])
  print('Открытые примеры пройдены. Скрытые и UI проверки выполняются отдельно.')
 finally:browser.close()
