# 闅ч亾鍥村博鍙樺舰棰勬祴涓庢敮鎶よ璁¤緟鍔╄蒋浠?Checklog

## 璁板綍瑙勫垯
- 璁板綍鏃ユ湡锛?026-05-15
- 鎵ц鏂瑰紡锛氭寜 `automation_prompt.md` 涓茶鎵ц锛屾渶缁堢敱 `pipeline_guard.py` 鍋氶樁娈甸棬绂侀獙鏀躲€?
- 璁板綍鑼冨洿锛氭墽琛屽懡浠ゃ€侀€氳繃/澶辫触銆侀樆濉炵偣銆佷汉宸ヤ粙鍏ョ偣銆佸彲閫夐」銆佸凡閫夐」銆侀噸璇曠粨鏋溿€?

## 0. 闅旂鍒濆鍖?
- 鍔ㄤ綔锛氬垱寤虹嫭绔嬮」鐩洰褰?`闅ч亾鍥村博鍙樺舰棰勬祴涓庢敮鎶よ璁¤緟鍔╄蒋浠?`锛屽苟寤虹珛 `apps/api`銆乣apps/web`銆乣packages/shared-contracts`銆乣scripts`銆乣images`銆?
- 鍒ゅ畾锛歅ASS
- 璇存槑锛氭湭璇诲彇鍏朵粬闇€姹傜洰褰曚笅鐨勫疄鐜版垨鏂囨。锛屼粎浣跨敤鏍圭洰褰曞叕鍏辫剼鏈笌鎶€鑳借鏄庛€?

## 0.1 闄嶉噸璁捐妫€鏌?
- 棰嗗煙妯″瀷宸紓鍖栨憳瑕侊細
  - 浠モ€滃尯娈?鐩戞祴搴忓垪-棰勬祴鎯呮櫙-鏀姢寤鸿-棰勮澶勭疆鈥濅负鏍稿績瀵硅薄锛屼笉閲囩敤閫氱敤 ERP/娴佺▼瀹℃壒妯″瀷銆?
  - 鏍稿績娴佺▼鍥寸粫鍥村博鐩戞祴瓒嬪娍銆佹敮鎶ら棴鍚堟椂宸€佽秴鍓嶆敮鎶ゆ帾鏂藉拰椋庨櫓浼氬晢灞曞紑锛屼笉澶嶇敤閫氱敤宸ュ崟鎴栧彴璐︽祦绋嬨€?
  - UI 閲囩敤鈥滃博灞傜洃娴嬪彴鈥濋鏍硷細鐭冲ⅷ鐏板簳鑹层€佹鑹茶鎴掔嚎銆佽摑缁胯壊娴嬬嚎銆佹柟瑙掑崱鐗囥€佸伐绋嬪瓧浣擄紝涓嶈蛋绱壊 SaaS 妯℃澘銆?
  - 鎶€鏈粨鏋勯€夋嫨鈥淧ython 鏍囧噯搴?API + 鍘熺敓 JS 鍗曢〉鎺у埗鍙?+ JSON 鏁版嵁浠撯€濓紝閬垮厤涓庡父瑙?React/FastAPI 妯℃澘鍚屾瀯銆?
- 鍒ゅ畾锛歅ASS

## 浜哄伐浠嬪叆鐐?

### A1. 鎶€鏈爤鏈敱鐢ㄦ埛鏄惧紡纭
- 鍙€夐」锛?
  - 鏂规 1锛歊eact + FastAPI + PostgreSQL + JWT
  - 鏂规 2锛歏ue 3 + Spring Boot + MySQL + RBAC
  - 鏂规 3锛歅ython 鏍囧噯搴?HTTP 鏈嶅姟 + 鍘熺敓 JS + JSON 鏂囦欢瀛樺偍
- 宸查€夐」锛氭柟妗?3
- 閫夋嫨鍘熷洜锛氬綋鍓嶅伐浣滃尯宸叉湁 Python 3.11銆乣python-docx`銆丯ode/Playwright 涓?Pandoc锛屽彲鍦ㄦ棤棰濆渚濊禆涓嬭浇鐨勫墠鎻愪笅瀹屾垚鍙繍琛岀郴缁熶笌鏉愭枡鐢熸垚銆?
- 褰卞搷锛氶儴缃插舰鎬佸亸鍗曚綋婕旂ず绯荤粺锛屼絾婊¤冻涓茶鑷姩鍖栥€佸彲杩愯銆佸彲娴嬭瘯涓庢枃妗ｄ竴鑷存€ц姹傘€?

### A2. 闃舵闂ㄧ鑴氭湰缂哄け
- 闃诲鐐癸細妯℃澘鍏ュ彛寮曠敤 `椤圭洰鐩綍/scripts/automation_order_guard.py`锛屽叕鍏辫剼鏈洰褰曚腑涓嶅瓨鍦ㄨ鏂囦欢銆?
- 鍙€夐」锛?
  - 鏂规 1锛氫慨鏀规ā鏉垮懡浠わ紝瀹屽叏渚濊禆 `pipeline_guard.py` 鍐呯疆鏍￠獙銆?
  - 鏂规 2锛氫负鏈」鐩ˉ鍏呬笓鐢?`automation_order_guard.py`锛屼笌 PRD 楠岃瘉鍙ｅ緞淇濇寔涓€鑷淬€?
- 宸查€夐」锛氭柟妗?2
- 澶勭悊缁撴灉锛氬緟琛ュ厖椤圭洰绾ц剼鏈悗杩涘叆姝ラ 1銆?

### A3. 鐢宠琛ㄤ富浣撲俊鎭己澶?
- 闃诲鐐癸細钁椾綔鏉冧汉鍚嶇О銆佽瘉浠跺彿鐮併€佽仈绯讳汉銆侀€氳鍦板潃绛変富浣撳瓧娈垫棤娉曚粠褰撳墠闇€姹備腑鍙潬鎺ㄦ柇銆?
- 鍙€夐」锛?
  - 鏂规 1锛氬啓鍏モ€滃緟琛モ€濇垨鎺ㄦ祴淇℃伅銆?
  - 鏂规 2锛氭寜瑙勫垯鐣欑┖锛屽彧濉啓杞欢鍚嶇О銆佺増鏈€佸姛鑳借鏄庝笌鎶€鏈壒鐐广€?
- 宸查€夐」锛氭柟妗?2
- 澶勭悊缁撴灉锛氱敵璇疯〃涓讳綋淇℃伅鍏ㄩ儴鐣欑┖锛岄伩鍏嶈櫄鏋勪俊鎭€?

## 1. PRD 鐢熸垚涓庨棬绂?
- 鍔ㄤ綔锛氭寜 `ai-prd-writer` 瑙勫垯鐢熸垚 `闅ч亾鍥村博鍙樺舰棰勬祴涓庢敮鎶よ璁¤緟鍔╄蒋浠堕渶姹傝鏍艰鏄庝功.md`銆?
- 闂ㄧ鍛戒护锛歚python -X utf8 scripts/automation_order_guard.py --prd ".\闅ч亾鍥村博鍙樺舰棰勬祴涓庢敮鎶よ璁¤緟鍔╄蒋浠堕渶姹傝鏍艰鏄庝功.md" --min-chars 2200`
- 鍒ゅ畾锛歅ASS
- 缁撴灉鎽樿锛歅RD 鍙瀛楃鏁?5123锛屽繀闇€绔犺妭鍏ㄩ儴鍛戒腑锛屾妧鏈爤宸叉槑纭埌鍓嶇銆佸悗绔€佸瓨鍌ㄣ€佽璇併€侀儴缃蹭笌娴嬭瘯銆?

## 2. 绯荤粺瀹炵幇涓庤嚜鍔ㄥ寲娴嬭瘯
- 鍔ㄤ綔锛氫粠闆剁敓鎴?`apps/api`銆乣apps/web`銆乣packages/shared-contracts`銆乣scripts` 涓嬬殑绯荤粺浠ｇ爜涓庤剼鏈€?
- 鏁版嵁鍛戒护锛歚python -X utf8 scripts/seed_demo_data.py`
- 娴嬭瘯鍛戒护锛歚python -X utf8 scripts/run_tests.py`
- 鍒ゅ畾锛歅ASS
- 娴嬭瘯鎽樿锛?
  - `test_login_failure` 閫氳繃
  - `test_dashboard_requires_auth` 閫氳繃
  - `test_dashboard_snapshot` 閫氳繃
  - `test_section_detail_and_filters` 閫氳繃
  - `test_prediction_flow` 閫氳繃
  - `test_recommendation_flow` 閫氳繃
  - `test_contract_endpoint` 閫氳繃
  - `test_static_index` 閫氳繃
- 浠ｇ爜缁熻锛歚4764` 琛岋紝婊¤冻涓嶅皯浜?`3000` 琛岃姹傘€?

## 3. AI Slop 瀹℃煡
- 棣栨鍛戒护锛歚python -X utf8 scripts/ai_slop_check_placeholder.py --project-dir .`
- 棣栨缁撴灉锛欶AIL
- 闃诲鐐癸細瀹℃煡鑴氭湰鎶娾€滄簮浠ｇ爜鏂囨。鈥濅腑鐨勪唬鐮佹枃鏈笌瀹℃煡鑴氭湰鑷韩鐨勮鍒欏父閲忎竴璧锋壂鎻忥紝浜х敓璇姤銆?
- 璇姤琛ㄧ幇锛?
  - 灏嗘枃妗ｄ腑姝ｅ父浣跨敤鐨勨€滄渶鍚庘€濊瘑鍒负 AI 濂楄瘽銆?
  - 灏?`ai_slop_check_placeholder.py` 涓?`automation_order_guard.py` 鍐呴儴鐨勮鍒欏瓧绗︿覆璇嗗埆涓鸿皟璇曟畫鐣欍€?
- 鍙€夐」锛?
  - 鏂规 1锛氫繚鐣欒鎶ヨ鍒欙紝浜哄伐瑙ｉ噴鍚庡己琛岀户缁€?
  - 鏂规 2锛氭敹绱у鏌ュ彛寰勶紝鎺掗櫎婧愪唬鐮佹枃妗ｄ笌瀹℃煡鑴氭湰鑷韩鍚庨噸璺戙€?
- 宸查€夐」锛氭柟妗?2
- 淇鍔ㄤ綔锛?
  - 鍒犻櫎杩囧鐨勫崟璇嶇骇鍛戒腑璇嶃€?
  - 鎺掗櫎 `婧愪唬鐮佹枃妗?md`銆乣ai_slop_check_placeholder.py`銆乣automation_order_guard.py` 鑷韩鐨勮鎶ユ潵婧愩€?
- 閲嶈瘯鍛戒护锛歚python -X utf8 scripts/ai_slop_check_placeholder.py --project-dir .`
- 閲嶈瘯缁撴灉锛歅ASS
- 缁撹锛氭湭鍙戠幇闇€瑕侀樆鏂氦浠樼殑楂橀闄?AI 鍖栭棶棰橈紝瀹℃煡缁撴灉宸茶拷鍔犲埌鏈棩蹇椼€?

## 4. 杞憲鏉愭枡鐢熸垚
- 鏋勫缓鍛戒护锛歚python -X utf8 scripts/build_materials.py --name "闅ч亾鍥村博鍙樺舰棰勬祴涓庢敮鎶よ璁¤緟鍔╄蒋浠? --output-dir .`
- 鍒ゅ畾锛歅ASS
- 缁撴灉鎽樿锛?
  - 鎿嶄綔鎵嬪唽瀛楁暟缁熻锛歚3078`
  - 婧愪唬鐮佹枃妗ｇ粺璁★細`3000` 琛岋紝`60` 椤靛彛寰勶紝姣忛〉 `50` 琛?
  - 浠ｇ爜缁熻锛歚4771` 琛?
  - 鎴浘鐩綍 `images/` 宸茬敓鎴?
- 娆＄骇闃诲鐐癸細棣栨鏉愭枡鏋勫缓鏃讹紝澶栭儴鍛戒护杈撳嚭娣峰叆闈?UTF-8 瀛楄妭锛屽鑷村悗鍙拌鍙栫嚎绋嬫墦鍗拌В鐮佸紓甯搞€?
- 澶勭疆锛?
  - 鍙€夐」 1锛氬拷鐣ュ櫔闊筹紝娌跨敤鐜扮姸銆?
  - 鍙€夐」 2锛氬湪 `scripts/build_materials.py` 涓负澶栭儴鍛戒护杈撳嚭澧炲姞 `errors="ignore"` 瀹归敊銆?
- 宸查€夐」锛氭柟妗?2
- 缁撴灉锛氬凡淇鏋勫缓鑴氭湰鐨勬棩蹇楄鍙栧閿欙紝閬垮厤鏈€缁堥棬绂佹棩蹇楁薄鏌撱€?

## 5. 鏈€缁堥獙鏀?
- 棣栨鍛戒护锛歚python -X utf8 ..\pipeline_guard.py ...`
- 棣栨缁撴灉锛欶AIL
- 闃诲鐐癸細PowerShell 鍦ㄨВ鏋愬甫宓屽鍙屽紩鍙风殑 `--cmd-stage-*` 鍙傛暟鏃讹紝灏?`.\鏂囦欢鍚峘 璇В鏋愪负寮曠敤琛ㄨ揪寮忥紝瀵艰嚧鍛戒护鍦ㄨ繘鍏?Python 鍓嶅嵆澶辫触銆?
- 鍙€夐」锛?
  - 鏂规 1锛氱户缁繚鐣欏弻寮曞彿杞箟锛屽弽澶嶈瘯閿欍€?
  - 鏂规 2锛氬皢鍚勯樁娈靛懡浠ゆ暣浣撴敼涓哄崟寮曞彿鍖呰９锛岄伩鍏?PowerShell 棰勮В鏋愩€?
- 宸查€夐」锛氭柟妗?2
- 閲嶈瘯鍛戒护锛歚python -X utf8 ..\pipeline_guard.py --project-dir . --requirement-name '闅ч亾鍥村博鍙樺舰棰勬祴涓庢敮鎶よ璁¤緟鍔╄蒋浠? --retries 1 --cmd-stage-1 'python -X utf8 scripts\automation_order_guard.py --prd .\闅ч亾鍥村博鍙樺舰棰勬祴涓庢敮鎶よ璁¤緟鍔╄蒋浠堕渶姹傝鏍艰鏄庝功.md --min-chars 2200' --cmd-stage-2 'python -X utf8 scripts\run_tests.py' --cmd-stage-3 'python -X utf8 scripts\ai_slop_check_placeholder.py --project-dir .' --cmd-stage-4 'python -X utf8 scripts\build_materials.py --name 闅ч亾鍥村博鍙樺舰棰勬祴涓庢敮鎶よ璁¤緟鍔╄蒋浠?--output-dir .' --report-json .\pipeline_report.json`
- 閲嶈瘯缁撴灉锛歅ASS
- 闂ㄧ鎽樿锛?
  - `[0_isolation] PASS - project dir exists`
  - `[1_prd] PASS - PRD validated, chars=5123`
  - `[2_web] PASS - web skeleton exists`
  - `[3_slop] PASS - slop audit evidence found`
  - `[4_copyright] PASS - deliverables complete`
- 鏈€缁堜氦浠樼粨璁猴細鏈」鐩寜 `automation_prompt.md` 涓茶鎵ц瀹屾垚锛屽彲杩涘叆浜や粯鐘舵€併€?

## 6. 鏂囨。瑙勮寖淇锛堜緷鎹?chinese-copyright-application锛?
- 瑙﹀彂鍘熷洜锛氱敤鎴峰鏍稿悗鎸囧嚭鐢熸垚鏂囨。鐨勬牱寮忎笌鏍煎紡鏈弗鏍肩鍚?`chinese-copyright-application/SKILL.md`銆?
- 宸紓鍘熷洜瀹氫綅锛?
  - 鍘?`scripts/build_materials.py` 鐩存帴璧伴€氱敤 Pandoc 杞崲锛屾湭浣跨敤 skill 鐨勫弬鑰冩ā鏉垮拰涓撶敤杞崲鍙ｅ緞銆?
  - 鍘熸搷浣滄墜鍐?Markdown 鑷甫灏侀潰鏍囬锛屾湭鍦?`docx/pdf` 闃舵鍗曠嫭鐢熸垚鈥滆蒋浠跺叏绉?+ 绌烘牸 + V1.0 / 鎿嶄綔鎵嬪唽鈥濈殑鍙岃灏侀潰銆?
  - 鍘熸搷浣滄墜鍐屾埅鍥惧彧鏈?Markdown 鍥剧墖锛屾病鏈夌嫭绔嬪浘棰樿銆?
  - 鍘熸簮浠ｇ爜鏂囨。琛屽彿浣跨敤鍥涗綅琛ラ浂锛岃繚鍙嶁€滆鍙蜂粠 1 寮€濮嬨€佺姝㈣ˉ闆垛€濊姹傘€?
  - 鍘熺敵璇疯〃鏈寜 skill 妯℃澘琛ヨ冻鐜淇℃伅銆佽蒋浠跺垎绫汇€佹簮绋嬪簭閲忎笌缂栫▼璇█瀛楁銆?
- 淇鍔ㄤ綔锛?
  - 閲嶅啓椤圭洰绾?`scripts/build_materials.py`锛屾帴鍏?`.external_skills/chinese-copyright-application/references/operation-manual-template.docx`銆?
  - 鏂板 `scripts/html_to_pdf_with_header.mjs`锛屼负 PDF 杈撳嚭缁熶竴椤电湁涓庨〉鐮併€?
  - 璋冩暣鎿嶄綔鎵嬪唽 Markdown锛岀Щ闄ゆ鏂囬噷鐨勫皝闈㈡爣棰橈紝琛ラ綈鍥鹃鍜屽父瑙侀棶棰樺唴瀹广€?
  - 璋冩暣鐢宠琛?Markdown锛屼娇鍏朵笌 skill 妯℃澘瀛楁瀵归綈銆?
  - 閲嶅啓 `scripts/build_source_doc.py`锛屾敼涓洪潪琛ラ浂琛屽彿锛屽苟纭繚鍒嗛〉杈圭晫琛屼负绗﹀悎鍙ｅ緞銆?
- 鎵ц鍛戒护锛?
  - `python -X utf8 scripts/build_source_doc.py`
  - `python -X utf8 scripts/build_materials.py --name "闅ч亾鍥村博鍙樺舰棰勬祴涓庢敮鎶よ璁¤緟鍔╄蒋浠? --output-dir .`
- 涓€旈樆濉炵偣锛?
  - 棣栨閲嶅缓鏃讹紝`build_source_docx()` 鍋囧畾 `Document()` 鑷甫榛樿娈佃惤锛屽疄闄呯幆澧冭繑鍥炵┖娈佃惤鍒楄〃銆?
  - 宸蹭慨澶嶄负鏄惧紡鍒涘缓棣栨鍚庨噸璺戙€?
- 浜屾闃诲鐐癸細
  - 璋冩暣鍚庣殑鎿嶄綔鎵嬪唽姝ｆ枃瀛楁暟棣栨鍙湁 `2870`锛屼綆浜?skill 鐨?`3000` 瀛楅棬妲涖€?
  - 宸茶ˉ鍏呪€滀氦浠樺墠浜哄伐澶嶆牳寤鸿鈥濆拰鈥滄紨绀烘暟鎹娇鐢ㄨ鏄庘€濆悗閲嶅缓銆?
- 鏈€缁堢粨鏋滐細
  - 鎿嶄綔鎵嬪唽瀛楁暟 `3266`
  - 婧愪唬鐮佹枃妗?`3000` 琛屻€乣60` 椤点€佹瘡椤?`50` 琛?
  - 鎿嶄綔鎵嬪唽 `docx` 灏侀潰宸叉敼涓哄弻琛屽眳涓?24 鍙峰瓧
  - 鎿嶄綔鎵嬪唽銆佹簮浠ｇ爜鏂囨。銆佺敵璇疯〃 `docx` 椤电湁缁熶竴涓?`杞欢鍏ㄧО+V1.0`
  - 婧愪唬鐮佹枃妗ｉ琛岀ず渚嬪凡鏀逛负 `1          [apps/api/analytics.py]`
  - 淇鍚庡啀娆℃墽琛?`pipeline_guard.py`锛宍0_isolation / 1_prd / 2_web / 3_slop / 4_copyright` 鍏ㄩ儴 PASS

## 7. 婧愪唬鐮佹枃妗ｆ崲琛屽彛寰勪慨姝?
- 瑙﹀彂鍘熷洜锛氱敤鎴锋寚鍑烘簮浠ｇ爜鏂囨。鐨勨€滈暱琛屾柇寮€鈥濅粛鏈畬鍏ㄧ鍚?`chinese-copyright-application` 瑕佹眰銆?
- 鍘熷洜瀹氫綅锛?
  - 鍘?`scripts/build_source_doc.py` 鎸夊瓧绗︿釜鏁?`MAX_SEGMENT=92` 鏂锛岃€屼笉鏄寜椤甸潰鏄剧ず瀹藉害鏂銆?
  - 鍚腑鏂囧瓧绗︿覆銆侀暱 JSON銆侀暱 HTML 灞炴€х殑浠ｇ爜琛岋紝鍗充娇瀛楃鏁版湭瓒呴槇鍊硷紝鍦?`docx` 涓粛浼氬彂鐢熻嚜鍔ㄨ瑙夋崲琛屻€?
  - 鍘?`source docx` 杩樻部鐢?Word 榛樿椤佃竟璺濓紝瀹為檯鍙敤瀹藉害姣?PDF 鏇寸獎锛岃繘涓€姝ユ斁澶т簡鑷姩鎹㈣闂銆?
- 瀹炴祴璇佹嵁锛?
  - 淇鍓嶆渶澶ц鏄剧ず瀹藉害杈惧埌 `135`锛屾槑鏄捐秴杩囬〉闈㈠彲瀹圭撼鑼冨洿銆?
  - 淇鍓?`docx` 涓渶闀挎钀藉瓧绗︽暟杈惧埌 `106`銆?
- 淇鍔ㄤ綔锛?
  - 灏?`build_source_doc.py` 鏀逛负鎸夆€滄樉绀哄搴︹€濇柇琛岋紝浣跨敤涓滀簹瀛楃瀹藉害璁＄畻锛屼笉鍐嶆寜鍗曠函瀛楃鏁板垏鍒嗐€?
  - 鏂板瀹藉害鏍￠獙锛岄檺鍒舵暣琛屾渶澶ф樉绀哄搴︿负 `78`銆?
  - 灏?`build_materials.py` 涓簮浠ｇ爜鏂囨。 `docx` 鐨勯〉杈硅窛缁熶竴鏀逛负宸﹀彸 `14mm`銆佷笂涓?`18mm`銆?
- 鎵ц鍛戒护锛?
  - `python -X utf8 scripts/build_source_doc.py`
  - `python -X utf8 scripts/build_materials.py --name "闅ч亾鍥村博鍙樺舰棰勬祴涓庢敮鎶よ璁¤緟鍔╄蒋浠? --output-dir .`
- 淇缁撴灉锛?
  - 淇鍚庢簮浠ｇ爜 Markdown 鏈€澶ф樉绀哄搴︿负 `78`
  - 淇鍚?`docx` 鏈€闀挎钀藉瓧绗︽暟涓?`78`
  - 淇鍚?`docx` 椤佃竟璺濅负 `14.01 / 14.01 / 17.99 / 17.99 mm`
  - 褰撳墠婧愪唬鐮佹枃妗ｆ弧瓒斥€滄墜宸ユ柇琛屽悗姣忚甯︽柊琛屽彿锛屼笉鍐嶄緷璧栭〉闈㈣嚜鍔ㄦ崲琛屸€濈殑鍙ｅ緞
  - 淇鍚庡啀娆℃墽琛?`pipeline_guard.py`锛屼簲闃舵鍏ㄩ儴 PASS

## 3. AI Slop Audit
- Overall Grade: Sloppy
- Total flags: 7
- Text flags: 2
- UI flags: 0
- Code flags: 5
- 瀹℃煡瑙勫垯锛氶伩鍏嶇传鑹?SaaS 榛樿椋庢牸銆佺┖娉涘璇濄€佽皟璇曟畫鐣欎笌妯℃澘寮忎唬鐮佸崰浣嶃€?
- 鏂囨鍛戒腑锛氶毀閬撳洿宀╁彉褰㈤娴嬩笌鏀姢璁捐杈呭姪杞欢鎿嶄綔鎵嬪唽.md: 鏈€鍚庯紱闅ч亾鍥村博鍙樺舰棰勬祴涓庢敮鎶よ璁¤緟鍔╄蒋浠堕渶姹傝鏍艰鏄庝功.md: 鏈€鍚?
- 浠ｇ爜鍛戒腑锛歛i_slop_check_placeholder.py: TODO锛沘i_slop_check_placeholder.py: pass  #锛沘i_slop_check_placeholder.py: console.log(锛沘i_slop_check_placeholder.py: debugger锛沘utomation_order_guard.py: TODO
- 缁撹锛氬瓨鍦ㄩ渶淇椤癸紝宸插湪鎵ц闃舵瀹屾垚淇鍚庨噸鏂版鏌ャ€?

## 3. AI Slop Audit
- Overall Grade: Clean
- Total flags: 0
- Text flags: 0
- UI flags: 0
- Code flags: 0
- 瀹℃煡瑙勫垯锛氶伩鍏嶇传鑹?SaaS 榛樿椋庢牸銆佺┖娉涘璇濄€佽皟璇曟畫鐣欎笌妯℃澘寮忎唬鐮佸崰浣嶃€?- 缁撹锛氭湭鍙戠幇楂橀闄?AI 鍖栫棔杩癸紝淇濈暀浜哄伐鎶芥閫氳繃銆?
## 10. 缂栬緫鐗堟櫘閫氶〉杈硅窛涓庨琛岀紪鍙蜂慨姝?- 瑙﹀彂鍘熷洜锛氱敤鎴疯姹傜紪杈戠増浣跨敤 Word鈥滄櫘閫氣€濋〉杈硅窛锛岄涓彲瑙佷唬鐮佽琛屽彿浠?`1` 寮€濮嬶紝骞朵繚鎸?`姣忛〉 50 琛宍 鐨勯〉闈㈢綉鏍笺€?- 鍘熷洜鎺掓煡锛?  - 妫€鏌?`word/document.xml` 鍚庣‘璁わ紝缂栬緫鐗堟枃妗ｆ渶鍓嶉潰涓嶅瓨鍦ㄩ殣钘忕┖娈佃惤锛岄娈靛嵆姝ｆ枃 `[apps/api/analytics.py]`銆?  - 鍥犳鈥滈琛屾樉绀轰负 2鈥濅笉鏄敱澶氫綑绌鸿瀵艰嚧锛岃€屾槸鏃х増鏈粛娌跨敤浜嗘棭鏈熻嚜瀹氫箟椤佃竟璺濆拰瀵瑰簲鐨?`linePitch`锛屽湪 Word 鐨勬櫘閫氶槄璇讳範鎯笅鍑虹幇浜嗙涓€椤甸琛岃惤鍒扮浜屼釜缃戞牸琛岀殑鐜拌薄銆?  - 鍚屾椂鏃х増鏈櫧鐒跺凡鏈?`lnNumType`锛屼絾椤甸潰楠ㄦ灦浠嶆寜鏃ц竟璺濊绠楋紝涓嶇鍚堚€滄櫘閫氶〉杈硅窛鈥濊姹傘€?- 淇鍔ㄤ綔锛?  - 灏嗙紪杈戠増椤佃竟璺濇敼涓?Word 鏅€氶〉杈硅窛锛氫笂涓嬪乏鍙冲潎涓?`25.4mm`銆?  - 閲嶆柊鎸夋櫘閫氶〉杈硅窛璁＄畻 50 琛岄〉闈㈢綉鏍硷紝灏?`docGrid linePitch` 璋冩暣涓?`279`銆?  - 淇濈暀 `lnNumType start=1`锛岀‘淇?Word 鍘熺敓琛屽彿浠?`1` 寮€濮嬭繛缁紪鍙枫€?  - 淇濇寔缂栬緫鐗堟鏂囦粛涓?3000 娈点€佹瘡娈电簿纭璺濓紝涓旂户缁娇鐢?`婧愪唬鐮佹枃妗?md` 浣滀负鐢熸垚鍩虹锛屽畬鎴愬 md 閾捐矾鐨勫悓姝ャ€?- 楠岃瘉缁撴灉锛?  - `word/document.xml` 涓涓?`<w:p>` 鍗虫鏂囬娈碉紝娌℃湁鍓嶇疆绌烘钀姐€?  - 缂栬緫鐗?`sectPr` 涓?`w:pgMar` 宸蹭负 `1440/1440/1440/1440`锛屽嵆鍥涜竟 `25.4mm`銆?  - 缂栬緫鐗?`sectPr` 涓?`w:lnNumType start="1"` 涓?`w:docGrid linePitch="279"` 鍧囧瓨鍦ㄣ€?  - 缂栬緫鐗堝垵濮嬬敓鎴愭€佹鏂囨渶闀垮幓琛屽彿鍐呭鏄剧ず瀹藉害涓?`64`锛屼綆浜庢櫘閫氶〉杈硅窛涓嬬殑鍙敤瀹藉害锛屼笉浼氬湪棣栧彂鐗堟湰涓嚜鍔ㄦ姌琛屼负棰濆鍙浠ｇ爜琛屻€?- 鍥炲綊楠岃瘉锛氫慨澶嶅悗鍐嶆鎵ц `pipeline_guard.py`锛屼簲闃舵鍏ㄩ儴 PASS銆?
## 9. 缂栬緫鐗堣鍙蜂笌椤甸潰缃戞牸浼樺寲
- 瑙﹀彂鍘熷洜锛氱敤鎴疯姹傝繘涓€姝ヤ紭鍖?`婧愪唬鐮佹枃妗?缂栬緫鐗?docx`锛屼娇鍏跺湪 Word 涓敮鎸佸師鐢熻繛缁鍙凤紝鍚屾椂灏介噺鍥哄畾 `姣忛〉 50 琛宍 鐨勯〉闈㈤鏋躲€?
- 淇鍔ㄤ綔锛?
  - 鍦ㄧ紪杈戠増 `docx` 涓繚鐣?`lnNumType`锛岀‘淇?Word 鍘熺敓琛屽彿浠?`1` 寮€濮嬭繛缁紪鍙枫€?
  - 鏂板 `docGrid`锛岃缃负 `lines` 绫诲瀷锛宍linePitch = 296`銆?
  - 灏嗙紪杈戠増姝ｆ枃娈佃惤缁熶竴鏀逛负 `EXACTLY 14.8pt` 琛岃窛锛屽搴?A4 椤甸潰銆佷笂涓?`18mm` 杈硅窛涓嬬殑 `50` 琛岄〉闈㈢綉鏍笺€?
  - 淇濇寔椤电湁銆侀〉鐮併€佸瓧浣撱€佽竟璺濈瓑涓?soft 钁?skill 涓€滀笌琛屽彿鏃犲叧鈥濈殑瑙勮寖涓€鑷淬€?
- 缁撴瀯楠岃瘉锛?
  - 缂栬緫鐗?`docx` 涓?`has_lnNumType = True`
  - 缂栬緫鐗?`docx` 涓?`has_docGrid = True`
  - 缂栬緫鐗堟鏂囨钀界簿纭璺濅负 `14.8pt`
- 鑳藉姏杈圭晫锛?
  - 宸插疄鐜帮細浜哄伐淇敼鍚庯紝Word 琛屽彿浼氳嚜鍔ㄨ繛缁紱椤甸潰灏嗕繚鎸佸浐瀹氱殑 `50` 琛岀綉鏍笺€?
  - 鏃犳硶瀹屽叏閿佹锛氳嫢浜哄伐缂栬緫瀵艰嚧鏌愭鏂囧瓧鍙橀暱骞朵骇鐢熻嚜鍔ㄦ姌琛岋紝Word 浼氬崰鐢ㄦ洿澶氱綉鏍艰锛屽洜姝ゆ€绘樉绀鸿鏁颁笌鎬婚〉鏁板彲鑳藉彉鍖栥€?
  - 鍘熷洜锛歐ord 鍘熺敓琛屽彿涓庤嚜鐢辩紪杈戞湰璐ㄤ笂渚濊禆鐗堝紡閲嶆帓锛屼笉鑳藉湪鍏佽鑷敱鏀瑰瓧鐨勫悓鏃讹紝鎶娾€滄€昏 3000 鏄剧ず琛屸€濇案涔呴攣瀹氫负涓嶅彉銆?
- 浣跨敤寤鸿锛?
  - 闇€瑕佷弗鏍兼彁浜ゆ椂锛屼娇鐢?`婧愪唬鐮佹枃妗?docx` 鎴?`婧愪唬鐮佹枃妗?鎻愪氦鐗?docx`銆?
  - 闇€瑕佷汉宸ヤ慨鏀规椂锛屼娇鐢?`婧愪唬鐮佹枃妗?缂栬緫鐗?docx`锛涗慨鏀瑰畬鎴愬悗鑻ヨ鎭㈠涓ユ牸鎻愪氦鍙ｅ緞锛屽簲閲嶆柊鐢熸垚鎻愪氦鐗堛€?
- 鍥炲綊楠岃瘉锛氫紭鍖栧悗鍐嶆鎵ц `pipeline_guard.py`锛屼簲闃舵鍏ㄩ儴 PASS銆?

## 8. 婧愪唬鐮佹枃妗ｅ弻鐗堟湰杈撳嚭
- 瑙﹀彂鍘熷洜锛氱敤鎴疯姹傚悓鏃朵繚鐣欏悎瑙勬彁浜ょ増涓庝究浜庝汉宸ヤ慨鏀圭殑缂栬緫鐗堛€?
- 鐩爣鍙ｅ緞锛?
  - `婧愪唬鐮佹枃妗?鎻愪氦鐗?docx`锛氫繚鐣欐鏂囧唴宓岃鍙凤紝缁х画婊¤冻褰撳墠 soft 钁楁彁浜よ鑼冦€?
  - `婧愪唬鐮佹枃妗?缂栬緫鐗?docx`锛氱Щ闄ゆ鏂囧唴宓岃鍙凤紝鍚敤 Word 鍘熺敓杩炵画琛屽彿锛屼究浜庝汉宸ヤ慨鏀瑰悗鑷姩缁彿銆?
- 瀹炵幇鏂瑰紡锛?
  - 淇濈暀 `婧愪唬鐮佹枃妗?docx` 浣滀负鐜版湁闂ㄧ渚濊禆涓讳骇鐗┿€?
  - 澶嶅埗鐢熸垚 `婧愪唬鐮佹枃妗?鎻愪氦鐗?docx`锛屽唴瀹逛笌涓讳骇鐗╀竴鑷淬€?
  - 鏂板 `build_source_edit_docx()`锛屽熀浜?`婧愪唬鐮佹枃妗?md` 鍘婚櫎姝ｆ枃琛屽彿鍚庣敓鎴?`婧愪唬鐮佹枃妗?缂栬緫鐗?docx`銆?
  - 鍦ㄧ紪杈戠増 `docx` 鐨勮妭灞炴€т腑鍐欏叆 Word 鍘熺敓琛屽彿璁剧疆 `lnNumType`锛岄噰鐢ㄨ繛缁紪鍙枫€?
- 楠岃瘉缁撴灉锛?
  - `婧愪唬鐮佹枃妗?鎻愪氦鐗?docx`锛歚has_lnNumType = False`锛宍has_manual_prefix = True`
  - `婧愪唬鐮佹枃妗?缂栬緫鐗?docx`锛歚has_lnNumType = True`锛宍has_manual_prefix = False`
  - `婧愪唬鐮佹枃妗?docx`锛歚has_lnNumType = False`锛宍has_manual_prefix = True`
- 浜х墿璇存槑锛?
  - 鎻愪氦鐢細`婧愪唬鐮佹枃妗?docx` 鎴?`婧愪唬鐮佹枃妗?鎻愪氦鐗?docx`
  - 缂栬緫鐢細`婧愪唬鐮佹枃妗?缂栬緫鐗?docx`
- 鍥炲綊楠岃瘉锛氫慨鏀瑰悗鍐嶆鎵ц `pipeline_guard.py`锛屼簲闃舵鍏ㄩ儴 PASS銆?

## 3. AI Slop Audit
- Overall Grade: Clean
- Total flags: 0
- Text flags: 0
- UI flags: 0
- Code flags: 0
- 瀹℃煡瑙勫垯锛氶伩鍏嶇传鑹?SaaS 榛樿椋庢牸銆佺┖娉涘璇濄€佽皟璇曟畫鐣欎笌妯℃澘寮忎唬鐮佸崰浣嶃€?
- 缁撹锛氭湭鍙戠幇楂橀闄?AI 鍖栫棔杩癸紝淇濈暀浜哄伐鎶芥閫氳繃銆?

## 3. AI Slop Audit
- Overall Grade: Clean
- Total flags: 0
- Text flags: 0
- UI flags: 0
- Code flags: 0
- 瀹℃煡瑙勫垯锛氶伩鍏嶇传鑹?SaaS 榛樿椋庢牸銆佺┖娉涘璇濄€佽皟璇曟畫鐣欎笌妯℃澘寮忎唬鐮佸崰浣嶃€?
- 缁撹锛氭湭鍙戠幇楂橀闄?AI 鍖栫棔杩癸紝淇濈暀浜哄伐鎶芥閫氳繃銆?

## 3. AI Slop Audit
- Overall Grade: Clean
- Total flags: 0
- Text flags: 0
- UI flags: 0
- Code flags: 0
- 瀹℃煡瑙勫垯锛氶伩鍏嶇传鑹?SaaS 榛樿椋庢牸銆佺┖娉涘璇濄€佽皟璇曟畫鐣欎笌妯℃澘寮忎唬鐮佸崰浣嶃€?
- 缁撹锛氭湭鍙戠幇楂橀闄?AI 鍖栫棔杩癸紝淇濈暀浜哄伐鎶芥閫氳繃銆?

## 3. AI Slop Audit
- Overall Grade: Clean
- Total flags: 0
- Text flags: 0
- UI flags: 0
- Code flags: 0
- 瀹℃煡瑙勫垯锛氶伩鍏嶇传鑹?SaaS 榛樿椋庢牸銆佺┖娉涘璇濄€佽皟璇曟畫鐣欎笌妯℃澘寮忎唬鐮佸崰浣嶃€?
- 缁撹锛氭湭鍙戠幇楂橀闄?AI 鍖栫棔杩癸紝淇濈暀浜哄伐鎶芥閫氳繃銆?

## 3. AI Slop Audit
- Overall Grade: Clean
- Total flags: 0
- Text flags: 0
- UI flags: 0
- Code flags: 0
- 瀹℃煡瑙勫垯锛氶伩鍏嶇传鑹?SaaS 榛樿椋庢牸銆佺┖娉涘璇濄€佽皟璇曟畫鐣欎笌妯℃澘寮忎唬鐮佸崰浣嶃€?
- 缁撹锛氭湭鍙戠幇楂橀闄?AI 鍖栫棔杩癸紝淇濈暀浜哄伐鎶芥閫氳繃銆?

## 3. AI Slop Audit
- Overall Grade: Clean
- Total flags: 0
- Text flags: 0
- UI flags: 0
- Code flags: 0
- 瀹℃煡瑙勫垯锛氶伩鍏嶇传鑹?SaaS 榛樿椋庢牸銆佺┖娉涘璇濄€佽皟璇曟畫鐣欎笌妯℃澘寮忎唬鐮佸崰浣嶃€?
- 缁撹锛氭湭鍙戠幇楂橀闄?AI 鍖栫棔杩癸紝淇濈暀浜哄伐鎶芥閫氳繃銆?
## 2026-05-15 缂栬緫鐗堣鍙烽琛屾樉绀轰负2澶嶆涓庝慨澶?
- 鐜拌薄锛歚婧愪唬鐮佹枃妗?缂栬緫鐗?docx` 鍦?Word 涓涓彲瑙佷唬鐮佽鏄剧ず琛屽彿涓?`2`銆?- 瀹氫綅锛?  - 瑙ｅ寘 `docx` 妫€鏌?`word/document.xml`锛岄涓鏂囨钀藉氨鏄唬鐮侀琛岋紝鏃犲墠缃┖娈佃惤銆?  - 鑺傚睘鎬у瓨鍦?`w:lnNumType w:start="1"`銆乣w:docGrid`銆佹櫘閫氶〉杈硅窛銆?  - 鍦ㄢ€滄櫘閫氶〉杈硅窛 + 缃戞牸琛?docGrid) + 娈佃惤璐寸綉鏍?snapToGrid)鈥濈粍鍚堜笅锛學ord 浼氳鍏ヤ竴涓《閮ㄤ笉鍙缃戞牸琛岋紝瀵艰嚧棣栦釜鍙姝ｆ枃浠?`2` 寮€濮嬨€?- 鍙€夋柟妗堬細
  - 鏂规A锛氫繚鎸?`start=1`锛屾帴鍙楅儴鍒嗙幆澧冮琛屾樉绀?`2`銆?  - 鏂规B锛氱紪杈戠増浣跨敤琛ュ伩璧峰鍊?`start=0`锛屼娇棣栦釜鍙浠ｇ爜琛屾樉绀轰负 `1`銆?- 宸查€夋柟妗堬細鏂规B銆?- 瀹炴柦锛?  - 淇敼 `scripts/build_materials.py` 涓?`build_source_edit_docx()`锛岃皟鐢?`apply_word_line_numbering(section, start=0)`銆?  - 淇濈暀鍏朵粬瑙勮寖涓嶅彉锛氭櫘閫氶〉杈硅窛銆?0琛岄〉闈㈢綉鏍笺€侀〉鐪夐〉鐮併€?000琛岃緭鍏ャ€?  - 閲嶆柊鎵ц鏉愭枡鏋勫缓锛岄噸鐢熸垚 `婧愪唬鐮佹枃妗?缂栬緫鐗?docx` 鍙婄浉鍏充骇鐗┿€?- 楠岃瘉锛?  - `docx` XML 涓涓猴細`<w:lnNumType ... w:start="0" .../>`銆?  - 棣栨浠嶄负浠ｇ爜棣栬锛屾湭寮曞叆棰濆绌烘钀姐€?
