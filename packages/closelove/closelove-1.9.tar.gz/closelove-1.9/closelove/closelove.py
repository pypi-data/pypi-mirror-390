from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from seleniumbase import Driver
from uiautomator import Device
from phonenumbers import geocoder
from pydub import AudioSegment
from datetime import datetime, timedelta
import re, io,time, random, requests,string,names,subprocess,os,pycountry,phonenumbers,base64,threading,websocket,zipfile
import numpy as np
from PIL import Image
import speech_recognition as sr
from closelove import link_sms, firebaseio_link
from bs4 import BeautifulSoup  
import xml.etree.ElementTree as ET

#twine upload dist/*
#__init__.py
#rm -rf dist build *.egg-info setup.py
#python3 setup.py sdist bdist_wheel
#pip install --upgrade clselove
# termux-change-repo && pkg install x11-repo && pkg install opencv-python
#yes | pkg update -y && yes | pkg upgrade -y && pkg install python python-pip x11-repo tmate android-tools libjpeg-turbo libpng zlib tur-repo tesseract opencv-python chromium termux-api -y && pip install PyVirtualDisplay==3.0  pytesseract  setuptools    beautifulsoup4 2captcha-python  clselove

def auto(pan,d,ip_address):
    kind, name = pan.split("@")[0], pan.split("#")[0].split("@")[-1]
    name_se = pan.split("#")[-1] if "#" in pan else None
    def b():
        clickable_elements = d(clickable=True)
        clickable_elements[int(name)].click()
    action_map = {
        "cl_te": lambda: d(text=name).click(),"cl_cl": lambda: d(className=name).click(),"cl_id": lambda: d(resourceId=name).click(),"cl_de": lambda: d(description=name).click(),
        "cl_tee": lambda: d(text=name),"cl_cll": lambda: d(className=name),"cl_idd": lambda: d(resourceId=name),"cl_dee": lambda: d(description=name),
        "se_te": lambda: d(text=name).set_text(name_se) if name_se else None,"se_cl": lambda: d(className=name).set_text(name_se) if name_se else None,"se_id": lambda: d(resourceId=name).set_text(name_se) if name_se else None,"se_de": lambda: d(description=name).set_text(name_se) if name_se else None,
        "cr_te": lambda: d(text=name).clear_text(),"cr_cl": lambda: d(className=name).clear_text(),"cr_id": lambda: d(resourceId=name).clear_text(),"cr_de": lambda: d(description=name).clear_text(),
        "sc_te": lambda: any(d(scrollable=True).scroll.forward() for _ in range(20)) if not d(text=name).exists else d(text=name).click(),"sc_cl": lambda: any(d(scrollable=True).scroll.forward() for _ in range(10)) if not d(className=name).exists else d(className=name).click(),"sc_id": lambda: any(d(scrollable=True).scroll.forward() for _ in range(10)) if not d(resourceId=name).exists else d(resourceId=name).click(),"sc_de": lambda: any(d(scrollable=True).scroll.forward() for _ in range(10)) if not d(description=name).exists else d(description=name).click(),
        "en": lambda: d.press('enter'),"ba": lambda: d.press.back(),"ti": lambda: time.sleep(int(name)),
        "cr": lambda: subprocess.run(f"adb -s {ip_address} shell pm clear {name}", shell=True, capture_output=True, text=True),
        "op": lambda: subprocess.run(f"adb -s {ip_address} shell am start -n {name}", shell=True, capture_output=True, text=True),
        "st": lambda: subprocess.run(f"adb -s {ip_address} shell am force-stop {name}", shell=True, capture_output=True, text=True),
        "sw": lambda: subprocess.run(f"adb -s {ip_address} shell input swipe {name}",shell=True, capture_output=True, text=True),
        "inp": lambda: subprocess.run(f"adb -s {ip_address} shell input text '{name}' ", shell=True, capture_output=True, text=True),      
       "not": lambda: subprocess.run(f"adb -s {ip_address} shell cmd statusbar expand-notifications", shell=True, capture_output=True, text=True),
       "col": lambda:subprocess.run(f"adb -s {ip_address} shell cmd statusbar collapse", shell=True, capture_output=True, text=True),
       "get": lambda:subprocess.run(f"adb -s {ip_address} shell am start -a android.intent.action.VIEW -d '{name_se}' {name}", shell=True, capture_output=True, text=True),          
       "cl_xy": lambda:subprocess.run(f"adb -s {ip_address} shell input tap {name} {name_se}", shell=True),           
       "mv_fi": lambda:subprocess.run(f"su -c 'cp -rf {name} {name_se}'", shell=True, capture_output=True, text=True),          
       "ch_77": lambda:subprocess.run(f"su -c 'chmod -R 777 {name}'", shell=True, capture_output=True, text=True),                    
       "cr_chrome": lambda:subprocess.run(f"adb -s {ip_address} shell pm clear com.android.chrome", shell=True, capture_output=True, text=True),
       "op_chrome": lambda: subprocess.run(f"adb -s {ip_address} shell am start -n com.android.chrome/com.google.android.apps.chrome.Main", shell=True, capture_output=True, text=True),
       "cr_kiwi": lambda:subprocess.run(f"adb -s {ip_address} shell pm clear com.kiwibrowser.browser", shell=True, capture_output=True, text=True),
       "op_kiwi": lambda: subprocess.run(f"adb -s {ip_address} shell am start -n com.kiwibrowser.browser/com.google.android.apps.chrome.Main", shell=True, capture_output=True, text=True),
       "cr_shell": lambda:subprocess.run(f"adb -s {ip_address} shell pm clear com.kiwibrowser.browser", shell=True, capture_output=True, text=True),
       "op_shell": lambda: subprocess.run(f"adb -s {ip_address} shell am start -n com.kiwibrowser.browser/com.google.android.apps.chrome.Main", shell=True, capture_output=True, text=True),
       "cr_colab": lambda:subprocess.run(f"adb -s {ip_address} shell pm clear com.kiwibrowser.browser", shell=True, capture_output=True, text=True),
       "op_colab": lambda: subprocess.run(f"adb -s {ip_address} shell am start -n com.kiwibrowser.browser/com.google.android.apps.chrome.Main", shell=True, capture_output=True, text=True),         
       "cr_discord": lambda:subprocess.run(f"adb -s {ip_address} shell pm clear com.discord", shell=True, capture_output=True, text=True),
       "op_discord": lambda: subprocess.run(f"adb -s {ip_address} shell am start -n com.discord/com.discord.main.MainDefault", shell=True, capture_output=True, text=True),    
       "cr_tinder": lambda:subprocess.run(f"adb -s {ip_address} shell pm clear com.tinder", shell=True, capture_output=True, text=True),
       "op_tinder": lambda: subprocess.run(f"adb -s {ip_address} shell am start -n com.tinder/com.tinder.feature.auth.internal.activity.AuthStartActivity", shell=True, capture_output=True, text=True),       
       "cr_viber": lambda:subprocess.run(f"adb -s {ip_address} shell pm clear com.viber.voip", shell=True, capture_output=True, text=True),
       "op_viber": lambda: subprocess.run(f"adb -s {ip_address} shell am start -n com.viber.voip/com.viber.voip.WelcomeActivity", shell=True, capture_output=True, text=True),       
       "cr_uber": lambda:subprocess.run(f"adb -s {ip_address} shell pm clear com.ubercab", shell=True, capture_output=True, text=True),
       "op_uber": lambda: subprocess.run(f"adb -s {ip_address} shell am start -n com.ubercab/com.ubercab.presidio.app.core.root.RootActivity", shell=True, capture_output=True, text=True),    
       "cr_imo": lambda:subprocess.run(f"adb -s {ip_address} shell pm clear com.imo.android.imoim", shell=True, capture_output=True, text=True),
       "op_imo": lambda: subprocess.run(f"adb -s {ip_address} shell am start -n com.imo.android.imoim/com.imo.android.imoim.home.Home", shell=True, capture_output=True, text=True),            
       "cr_didi": lambda:subprocess.run(f"adb -s {ip_address} shell pm clear com.didiglobal.passenger", shell=True, capture_output=True, text=True),
       "op_didi": lambda: subprocess.run(f"adb -s {ip_address} shell am start -n com.didiglobal.passenger/com.didi.sdk.splash.SplashActivity", shell=True, capture_output=True, text=True),      
       "cr_yango": lambda:subprocess.run(f"adb -s {ip_address} shell pm clear com.yandex.yango", shell=True, capture_output=True, text=True),
       "op_yango": lambda: subprocess.run(f"adb -s {ip_address} shell am start -n com.yandex.yango/ru.yandex.taxi.activity.MainActivity", shell=True, capture_output=True, text=True),      
       "cr_facebook_lite": lambda:subprocess.run(f"adb -s {ip_address} shell pm clear com.facebook.lite", shell=True, capture_output=True, text=True),
       "op_facebook_lite": lambda: subprocess.run(f"adb -s {ip_address} shell am start -n com.facebook.lite/com.facebook.lite.MainActivity", shell=True, capture_output=True, text=True),             
       "cr_vk": lambda:subprocess.run(f"adb -s {ip_address} shell pm clear com.vkontakte.android", shell=True, capture_output=True, text=True),
       "op_vk": lambda: subprocess.run(f"adb -s {ip_address} shell monkey -p com.vkontakte.android -c android.intent.category.LAUNCHER 1", shell=True, capture_output=True, text=True),       
       "bo": lambda: b(),
           
            }
    action_map.get(kind, lambda: None)()
def get_x_y(res, code, text_body):
    amap = {"xml_te": "text", "xml_id": "resource-id", "xml_cc": "content-desc"}
    attr = amap.get(code)
    if not attr: return None, None

    for n in ET.fromstring(text_body).iter("node"):
        v = n.attrib.get(attr, "")
        ok = (re.search(res, v) if code=="xml_cc" else v==res)
        if ok:
            x1,y1,x2,y2 = map(int, re.findall(r"\d+", n.attrib["bounds"]))
            return (x1+x2)//2,(y1+y2)//2
    return None, None

def do_file(ip_address,d,username, folder, apk):
    check = False
    def a(date):
        auto(date,d,ip_address)    
    try:
        zipf, dst = f"/sdcard/{username}.zip", f"/sdcard/{folder}/{username}"
        if not os.path.exists(dst):
            print("no find", username)
            r = requests.get(f"{link_sms}/files/{folder}/{username}.zip", stream=True)
            if r.status_code != 200: exit(print(r.status_code, r.text))
            with open(zipf, "wb") as f:
                for chunk in r.iter_content(8192): f.write(chunk)
            with zipfile.ZipFile(zipf) as z: z.extractall(dst)
            os.remove(zipf)
            print("Done:", dst)
        a(f"cr_{folder}")
        os.system(f'su -c "cp -rf /sdcard/{folder}/{username}/* /data/user/0/{apk}/"')
        os.system(f'su -c "chmod -R 777 /data/user/0/{apk}"')
        a(f"op_{folder}")
        check = True
    except Exception as s:
        print(s)
    return check
def do_kiwi(ip_address,d,username, folder,start_apk,link):
    check = False
    def a(date):
        auto(date,d,ip_address)    
    try:
        zipf, dst = f"/sdcard/{username}.zip", f"/sdcard/{folder}/{username}"
        if not os.path.exists(dst):
            print("no find", username)
            r = requests.get(f"{link_sms}/files/{folder}/{username}.zip", stream=True)
            if r.status_code != 200: exit(print(r.status_code, r.text))
            with open(zipf, "wb") as f:
                for chunk in r.iter_content(8192): f.write(chunk)
            with zipfile.ZipFile(zipf) as z: z.extractall(dst)
            os.remove(zipf)
            print("Done:", dst)         
        subprocess.run(f"adb -s {ip_address} shell pm clear {start_apk}", shell=True, capture_output=True, text=True)
        time.sleep(1)
        os.system(f'su -c "cp -rf /sdcard/{folder}/{username} /data/user/0/{start_apk}/app_chrome"')
        time.sleep(1)
        os.system(f'su -c "chmod -R 777 /data/user/0/{start_apk}"')
        time.sleep(2)
        subprocess.run(f"adb -s {ip_address} shell am start -n {start_apk}/com.google.android.apps.chrome.Main", shell=True, capture_output=True, text=True)
        time.sleep(2)
        subprocess.run(f"adb -s {ip_address} shell am start -a android.intent.action.VIEW -d '{link}' com.kiwibrowser.browser", shell=True, capture_output=True, text=True)
        check = True
    except Exception as s:
        print(s)
    return check

def up_file(username,folder,apk):
    check = False
    try:        
        src, dst, zipf = f"/data/user/0/{apk}", f"/sdcard/{folder}/{username}", f"/sdcard/{username}.zip"
        os.system(f'su -c "cp -rf {src} {dst}"')
        with zipfile.ZipFile(zipf, 'w', zipfile.ZIP_DEFLATED) as z:
            [z.write(os.path.join(r,f), os.path.relpath(os.path.join(r,f), dst)) 
            for r,_,fs in os.walk(dst) for f in fs]
        r = requests.post(f"{link_sms}/upload/{folder}/{username}.zip", files={"file": open(zipf,'rb')})
        print(r.status_code, r.text)
        data_to_upload = {"file": username ,"path":folder}
        requests.patch(f'{link_sms}/{folder}_apk/{username}.json', json=data_to_upload, timeout=10)
        check = True
    except Exception as s:
        print(s)
    return check
def random_api_gmail(api_gmail, code_run):
    data1 = requests.get(f"{link_sms}/{api_gmail}").json() if "error" not in requests.get(f"{link_sms}/{api_gmail}").text else {}
    data2 = requests.get(f"{link_sms}/{code_run}").json() if "error" not in requests.get(f"{link_sms}/{code_run}").text else {}
    used = {v.get("gmail_api") for v in data1.values() if str(v.get("google")).lower()=="true"}
    #all_emails = {f"{k}@{api_gmail.split("_")[-1].strip()}.com" for k in data2.keys()}
    #all_emails = {f"{k}@{api_gmail.split('_')[-1].strip()}.com" for k in data2.keys()}    
    all_emails = {v.get("email") for v in data2.values() if "true" in str(v.get("check")) }
    available = list(used - all_emails)
    return random.choice(available) if available else None

def random_email_time(name,time_day,get_check,get_true):
    check = False
    date = None
    try:
        folders = []
        response_get = requests.get(f'{link_sms}/{name}.json')
        user_data = response_get.json()
        for key, value in user_data.items():
            saved_datetime = datetime(month=value["month"],day=value["day"],hour=value["hour"],minute=value["minute"],year=datetime.now().year)
            now = datetime.now()
            if now - saved_datetime >= timedelta(hours=time_day):
                if get_true in value[get_check]:
                    folders.append(key)
        username = random.choice(folders)        
        date = requests.get(f'{link_sms}/{name}/{username}.json').json()   
        data_to_upload = {"hour": now.hour,"minute": now.minute,"day": now.day,"month": now.month}
        requests.patch(f'{link_sms}/{name}/{username}.json', json=data_to_upload, timeout=10)
        check = True  
    except Exception as s:
        print(s)        
    return date,check,username

def all_iframe(driver, depth=0):
    try:
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for idx, fr in enumerate(iframes):
            try:
                title = fr.get_attribute("title")
                print("  " * depth + f"↳ iframe (level {depth}, index {idx}) title = {title}")
                driver.switch_to.frame(fr)
                # استدعاء الدالة نفسها عشان تدخل nested iframe
                print_all_iframe_titles(driver, depth+1)
                # الرجوع للـ parent
                driver.switch_to.parent_frame()
            except Exception as e:
                driver.switch_to.parent_frame()
                continue
    except:
        pass

def na_em(list_email):
    f_n = names.get_first_name().lower()
    l_n =names.get_last_name().lower()
    password = [*random.sample([random.choice(string.ascii_lowercase), random.choice(string.ascii_uppercase), random.choice(string.digits), random.choice('@#')], 3), *random.choices(string.ascii_letters + string.digits + '!@#$%', k=random.randint(5, 11))]; random.shuffle(password); password = ''.join(password)
    email = f"{f_n}{random.randint(10, 9999)}@{random.choice(list_email)}"
    random_month = ["January", "February", "March", "April", "May", "June","July", "August", "September", "October", "November", "December"]
    month1 = random.choice(random_month)
    day = random.randint(1, 31)
    year = random.randint(1980, 2006)
    month = random.randint(1, 12)
    return f_n, l_n, password, email,email.split("@")[0], month1,day,month,year
def get_phone(name):
    response_get = requests.get(f'{name}.json')
    user_data = response_get.json()
    if not user_data:
        print('No phone found', name)
        return None, None, None, None
    first_key = random.choice(list(user_data.keys()))
    phone = user_data[first_key].strip()
    requests.delete(f'{name}/{phone}.json')
    parsed_number = phonenumbers.parse(f'+{phone}')
    country = pycountry.countries.get(alpha_2=phonenumbers.region_code_for_country_code(parsed_number.country_code))
    country_code, fn, co = parsed_number.country_code, country.name[0], country.name.split(",")[0] if country else (None, None)
    return phone, country_code, fn, co
def get_sms(name):
    response_get = requests.get(name)
    user_data = response_get.json()
    if user_data is None:
        print('no phone',name)
        stop_phone = True
    else:
        phone = random.choice(list(user_data.keys())).strip()
        first_key= user_data[phone]
        parsed_number = phonenumbers.parse(f'+{phone}')
        country = pycountry.countries.get(alpha_2=phonenumbers.region_code_for_country_code(parsed_number.country_code))
        country_code, fn, co = parsed_number.country_code, country.name[0], country.name.split(",")[0] if country else (None, None)
        return first_key,phone, country_code, fn, co

def scr(screenshot, driver):
    driver.save_screenshot(f"{screenshot}.png")
    #print((r := requests.post('https://0x0.st', files={'file': open(f"{screenshot}.png", 'rb')}, headers={'User-Agent': 'curl/7.68.0'})).text.strip()) if driver.save_screenshot(f"{screenshot}.png") else print("erro_screenshot")


def totel_temp(email):
    text_code = False
    error_tempmail =['mailto.plus','fexpost.com','fexbox.org','mailbox.in.ua','rover.info','chitthi.in','fextemp.com','any.pink','merepost.com']
    matched_error = next((err for err in error_tempmail if err in email), None)
    error_inboxes =['blondmail.com', 'chapsmail.com', 'clowmail.com', 'dropjar.com', 'fivermail.com', 'getairmail.com', 'getmule.com', 'gimpmail.com', 'givmail.com', 'guysmail.com', 'inboxbear.com', 'replyloop.com', 'spicysoda.com', 'tafmail.com', 'temptami.com', 'tupmail.com', 'vomoto.com']
    inboxes_error = next((err for err in error_inboxes if err in email), None)
    if matched_error:
        response_first = requests.get('https://tempmail.plus/api/mails', cookies={'email': email}, params={'email': email,'limit': '1','epin': ''}).json().get('first_id')
        text_code = requests.get(F'https://tempmail.plus/api/mails/{response_first}', cookies={'email': email}, params={'email': email,'limit': '20','epin': ''})
        return text_code
    elif inboxes_error:
        response_first = requests.get(f"https://inboxes.com/api/v2/inbox/{email}").json()['msgs'][0]["uid"]
        text_code = requests.get(f"https://inboxes.com/api/v2/message/{response_first}")
        return text_code
    elif 'gmail.com' in email or 'hotmail.com' in email or 'outlook.com' in email:
        if 'gmail.com' in email:
            run_code = 'api_gmail'
        elif 'hotmail.com' in email or 'outlook.com' in email:
            run_code = 'api_hotmail'
            
        limit = 1
        response_get = requests.get(f'{link_sms}/{run_code}')
        user_data = response_get.json()
        if user_data is None:
            print('no api_gmail')
        else:
            for key, value in user_data.items():
                if value["gmail_api"] ==email:
                    API_KEY = value["get_api"]
                    GRANT_ID = value["grant_id"]
                    response = requests.get(f"https://api.us.nylas.com/v3/grants/{GRANT_ID}/messages", headers={"Authorization": f"Bearer {API_KEY}"}, params={"limit": limit})
                    data = response.json()
                    date_code = response.status_code
                    if date_code == 404 or date_code == 401 :
                        gmail_list = ["api_gmail","api_wise","api_hotmail"]                      
                        for gmail_delete in gmail_list:
                            requests.delete(f'{link_sms}/{gmail_delete}/{key}')
                        text_code = "delete"
                        return text_code 
 
                    elif "data" in data and data["data"]:
                        for i, msg in enumerate(data["data"], 1):
                            body_html = msg.get("body") or ""
                            soup = BeautifulSoup(body_html, "html.parser")
                            #text_code = soup.get_text().strip() + [a["href"] for a in soup.find_all("a", href=True)]
                            text_code = soup.get_text().strip() + "\n" + "\n".join(a["href"] for a in soup.find_all("a", href=True))
                            
                            return text_code                       
                        
        

def se(pan,driver):
    
    kind, name = pan.split("@")[0], pan.split("#")[0].split("@", 1)[1]
    name_se = pan.split("#")[-1] if "#" in pan else None
    action_map = {
       "cl_xp": lambda:driver.find_element(By.XPATH, name).click(),
       "cl_id": lambda:driver.find_element(By.ID, name).click(),
       "cl_na": lambda:driver.find_element(By.NAME, name).click(),
       "cl_cl": lambda:driver.find_element(By.CLASS_NAME, name).click(),
       "cl_cs": lambda:driver.find_element(By.CSS_SELECTOR, name).click(),
       "cl_ta": lambda:driver.find_element(By.TAG_NAME, name).click(),
       "se_xp": lambda:driver.find_element(By.XPATH, name).send_keys(name_se),
       "se_id": lambda:driver.find_element(By.ID, name).send_keys(name_se),
       "se_na": lambda:driver.find_element(By.NAME, name).send_keys(name_se),
       "se_cl": lambda:driver.find_element(By.CLASS_NAME, name).send_keys(name_se),
       "se_cs": lambda:driver.find_element(By.CSS_SELECTOR, name).send_keys(name_se),
       "se_ta": lambda:driver.find_element(By.TAG_NAME, name).send_keys(name_se),
       "cr_xp": lambda:driver.find_element(By.XPATH, name).clear(),
       "cr_id": lambda:driver.find_element(By.ID, name).clear(),
       "cr_na": lambda:driver.find_element(By.NAME, name).clear(),
       "cr_cl": lambda:driver.find_element(By.CLASS_NAME, name).clear(),
       "cr_cs": lambda:driver.find_element(By.CSS_SELECTOR, name).clear(),
       "cr_ta": lambda:driver.find_element(By.TAG_NAME, name).clear(),
           
       "get_xp": lambda:driver.find_element(By.XPATH, name).text,
       "get_id": lambda:driver.find_element(By.ID, name).text,
       "get_na": lambda:driver.find_element(By.NAME, name).text,
       "get_cl": lambda:driver.find_element(By.CLASS_NAME, name).text,
       "get_cs": lambda:driver.find_element(By.CSS_SELECTOR, name).text,
       "get_ta": lambda:driver.find_element(By.TAG_NAME, name).text,
           
       "en_xp": lambda:driver.find_element(By.XPATH, name).send_keys(Keys.ENTER),
       "en_id": lambda:driver.find_element(By.ID, name).send_keys(Keys.ENTER),
       "en_na": lambda:driver.find_element(By.NAME, name).send_keys(Keys.ENTER),
       "en_cl": lambda:driver.find_element(By.CLASS_NAME, name).send_keys(Keys.ENTER),
       "en_cs": lambda:driver.find_element(By.CSS_SELECTOR, name).send_keys(Keys.ENTER),
       "en_ta": lambda:driver.find_element(By.TAG_NAME, name).send_keys(Keys.ENTER),
           
       "ba_xp": lambda:driver.find_element(By.XPATH, name).send_keys(Keys.BACKSPACE),
       "ba_id": lambda:driver.find_element(By.ID, name).send_keys(Keys.BACKSPACE),
       "ba_na": lambda:driver.find_element(By.NAME, name).send_keys(Keys.BACKSPACE),
       "ba_cl": lambda:driver.find_element(By.CLASS_NAME, name).send_keys(Keys.BACKSPACE),
       "ba_cs": lambda:driver.find_element(By.CSS_SELECTOR, name).send_keys(Keys.BACKSPACE),
       "ba_ta": lambda:driver.find_element(By.TAG_NAME, name).send_keys(Keys.BACKSPACE),
           
       "re_xp": lambda:driver.find_element(By.XPATH, name).send_keys(Keys.RETURN),
       "re_id": lambda:driver.find_element(By.ID, name).send_keys(Keys.RETURN),
       "re_na": lambda:driver.find_element(By.NAME, name).send_keys(Keys.RETURN),
       "re_cl": lambda:driver.find_element(By.CLASS_NAME, name).send_keys(Keys.RETURN),
       "re_cs": lambda:driver.find_element(By.CSS_SELECTOR, name).send_keys(Keys.RETURN),
       "re_ta": lambda:driver.find_element(By.TAG_NAME, name).send_keys(Keys.RETURN),
           
       "re_xp": lambda:driver.find_element(By.XPATH, name).send_keys(Keys.RETURN),
       "re_id": lambda:driver.find_element(By.ID, name).send_keys(Keys.RETURN),
       "re_na": lambda:driver.find_element(By.NAME, name).send_keys(Keys.RETURN),
       "re_cl": lambda:driver.find_element(By.CLASS_NAME, name).send_keys(Keys.RETURN),
       "re_cs": lambda:driver.find_element(By.CSS_SELECTOR, name).send_keys(Keys.RETURN),
       "re_ta": lambda:driver.find_element(By.TAG_NAME, name).send_keys(Keys.RETURN),
       
       "sr_xp": lambda:driver.find_element(By.XPATH, name).screenshot(name_se),
       "sr_id": lambda:driver.find_element(By.ID, name).screenshot(name_se),
       "sr_na": lambda:driver.find_element(By.NAME, name).screenshot(name_se),
       "sr_cl": lambda:driver.find_element(By.CLASS_NAME, name).screenshot(name_se),
       "sr_cs": lambda:driver.find_element(By.CSS_SELECTOR, name).screenshot(name_se),
       "sr_ta": lambda:driver.find_element(By.TAG_NAME, name).screenshot(name_se),
           
       "get_xp": lambda:driver.find_element(By.XPATH, name).get_attribute(name_se),
       "get_id": lambda:driver.find_element(By.ID, name).get_attribute(name_se),
       "get_na": lambda:driver.find_element(By.NAME, name).get_attribute(name_se),
       "get_cl": lambda:driver.find_element(By.CLASS_NAME, name).get_attribute(name_se),
       "get_cs": lambda:driver.find_element(By.CSS_SELECTOR, name).get_attribute(name_se),
       "get_ta": lambda:driver.find_element(By.TAG_NAME, name).get_attribute(name_se),
           
       "get": lambda:driver.get(name),
       "qu": lambda:driver.quit(),
       "clo": lambda:driver.close(),
       "add_co": lambda:driver.add_cookie(name),
       "de_co": lambda:driver.delete_all_cookies(),
       "get_co": lambda:driver.get_cookies(),
       "get_url": lambda:driver.current_url,
       "get_ti": lambda:driver.title,
       "ba": lambda:driver.back(),
       "ha": lambda:driver.switch_to.window(driver.window_handles[int(name)]),
       "sc": lambda:driver.save_screenshot(name),
       "wa": lambda:driver.implicitly_wait(name),
       "re": lambda:driver.refresh(),
       "size": lambda:driver.set_window_size(int(name), (name_se)),
       "en": lambda:ActionChains(driver).send_keys(Keys.ENTER).perform(),
       "html": lambda:driver.page_source,
            }
    #action_map.get(kind, lambda: None)()
    return action_map.get(kind, lambda: None)()

def se_chr(pan):
    global driver

    kind, name = pan.split("@")[0], pan.split("#")[0].split("@")[-1]
    name_se = pan.split("#")[-1] if "#" in pan else None

    if kind == "us":
        driver = Driver(uc=True)
        return driver

    if kind == "wa" and driver:
        driver.implicitly_wait(int(name))
    elif kind == "max" and driver:
        driver.maximize_window()
    elif kind == "size" and driver:
        driver.set_window_size(int(name), int(name_se))
    elif kind == "quit" and driver:
        driver.quit()
