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
from closelove import link_sms, firebaseio_link,se,scr
from bs4 import BeautifulSoup  
def get_text_2captcha(path, api_key="b595d3040f736c6e7a5108ee7745f83a"):
    cid = requests.post("http://2captcha.com/in.php",
        files={"file": open(path,"rb")}, data={"key": api_key,"method":"post"}).text.split("|")[1]
    for _ in range(20):
        time.sleep(5)
        r = requests.get("http://2captcha.com/res.php", params={"key": api_key,"action":"get","id": cid})
        if "OK|" in r.text: return r.text.split("|")[1]
    return None
def twocaptcha_v2(sitekey, url):
    test = False
    api_key="b595d3040f736c6e7a5108ee7745f83a"
    rid = requests.post("http://2captcha.com/in.php", data={
        "key": api_key, "method": "userrecaptcha",
        "googlekey": sitekey, "pageurl": url, "json": 1
    }).json()["request"]

    for _ in range(20):
        r = requests.get("http://2captcha.com/res.php", params={
            "key": api_key, "action": "get", "id": rid, "json": 1
        }).json()
        if r["status"] == 1:
            test = r["request"]
             
        time.sleep(5)
    return test
def nope_captcha_text(image_base64):
    textcaptcha = f"textcaptcha_{random.randint(000, 999)}"
    data_to_upload = {textcaptcha: image_base64,"check": "check"}  
    requests.patch(f'{link_sms}/captcha/{textcaptcha}.json', json=data_to_upload, timeout=10)
    for _ in range(15): 
        time.sleep(2)
        value = requests.get(f'{link_sms}/captcha/{textcaptcha}').json()
        
        if "start" in value["check"]:
            code = value[textcaptcha]
            requests.delete(f'{link_sms}/captcha/{textcaptcha}.json', json=data_to_upload, timeout=10)
            break
            
    return code

def audio_file(token,captcha_audio,link,us):
    from pathlib import Path
    session = requests.Session()
    data = {"token": token,"sid":us,"render_type": "canvas","lang": "","isAudioGame": "true","analytics_tier": "40","is_compatibility_mode": "false","apiBreakerVersion": "green",}
    data = session.post(f"https://{link}-api.arkoselabs.com/fc/gfct/", data=data, timeout=15).json()
    r = session.get(f"https://{link}-api.arkoselabs.com/rtag/audio", params={"challenge": "0","gameToken": data["challengeID"],"sessionToken": data["session_token"]})
    Path(captcha_audio).write_bytes(r.content)
    print("download_audio")

def find_animal(file_path,sound):
    from transformers import pipeline
    classifier = pipeline(
    task="audio-classification",
    model="ardneebwar/wav2vec2-animal-sounds-finetuned-hubert-finetuned-animals",
    token="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"
    )
    options=[(audio:=AudioSegment.from_file(file_path))[int(s*1000):int(e*1000)].export(f,format="wav") or f for s,e,f in [(4,6,"option1.wav"),(7,9,"option2.wav"),(11,13,"option3.wav")] if len(audio[int(s*1000):int(e*1000)])>200]
    cat_option = None
    for _ in range(max_attempts := 5):
        print(sound)
        if (cat_option := next((i for i, o in enumerate(options, 1) if classifier(o)[0]['label'].lower() == sound), None)): break
    return cat_option
def slove_pick(driver):
    def a(date):
        return se(date,driver)

    check_pick ="false_stop"
    for _ in range(10):
        time.sleep(2)
        scr("pick",driver)
        text_body=(lambda rec,drv:(drv.find_element(By.TAG_NAME,"body").text.strip()+"\n" if drv.find_elements(By.TAG_NAME,"body") and drv.find_element(By.TAG_NAME,"body").text.strip() else "")+"".join((drv.switch_to.frame(f),(lambda t:drv.switch_to.parent_frame() or t)(rec(rec,drv)))[1] for f in drv.find_elements(By.TAG_NAME,"iframe")))((lambda rec,drv:(drv.find_element(By.TAG_NAME,"body").text.strip()+"\n" if drv.find_elements(By.TAG_NAME,"body") and drv.find_element(By.TAG_NAME,"body").text.strip() else "")+"".join((drv.switch_to.frame(f),(lambda t:drv.switch_to.parent_frame() or t)(rec(rec,drv)))[1] for f in drv.find_elements(By.TAG_NAME,"iframe"))),driver);
        driver.switch_to.default_content()
        stop_messages = ["Pick the mouse that can't reach the cheese","Pick the image where the darts","Use the arrows to rotate the object"]
        stop_error = next((err for err in stop_messages if err in text_body), None)
        stop_animal = ["Which option is the sound of cats","Which option is the sound of bees"]
        animal_error = next((err for err in stop_animal if err in text_body), None)

        #if stop_error :
            #print(stop_error)
        if "You’ve solved all the puzzles" in  text_body:
            print("You’ve solved all the puzzles")
            break

        elif "Please solve a few puzzles" in  text_body:
            print("Please solve a few puzzles")
            driver.switch_to.default_content()
            driver.switch_to.frame(driver.find_element(By.XPATH, ".//iframe[@title='Verification challenge']"))
            code_start1 = driver.execute_script("return document.evaluate(\"//*[@id='verification-token']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
            code_start2 = driver.execute_script("return document.evaluate(\"//*[@id='FunCaptcha-Token']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
            if code_start1 or code_start2:
                print("code_start2")
                token = driver.find_element(By.ID, "verification-token" if code_start1 else "FunCaptcha-Token").get_attribute("value")
                print(token)
                print(token.split("|r=")[0],token.split("|r=")[-1].split("|")[0])
                audio_file(token.split("|r=")[0] ,"captcha_audio.mp3","tinder",token.split("|r=")[-1].split("|")[0])
            driver.switch_to.frame(driver.find_element(By.XPATH, ".//iframe[@title='Visual challenge']"))
            a('cl_cs@button[aria-label="Audio"]')
            driver.switch_to.default_content()
        elif animal_error:
            print(animal_error)
            check_pick ="true_stop"
            driver.switch_to.default_content()
            driver.switch_to.frame(driver.find_element(By.XPATH, ".//iframe[@title='Verification challenge']"))
            driver.switch_to.frame(driver.find_element(By.XPATH, ".//iframe[@title='Audio challenge']"))
            cat_option = find_animal("captcha_audio.mp3",animal_error.split("sound of ")[-1].rstrip("s"))
            print(cat_option)
            cat_option = int(cat_option)
            driver.find_element(By.ID, "answer-input").send_keys(cat_option)
            time.sleep(2)
            scr("5",driver)
            a("cl_xp@//button[text()='Done']")
            time.sleep(2)
            driver.switch_to.default_content()
            scr("6",driver)
            print("finsh_audio")
            break
        elif "Please solve this puzzle" in  text_body:
            a("cl_xp@//button[text()='Start Puzzle']")
        elif "Whoops! That's not quite right" in  text_body:
            a("cl_xp@//button[text()='Try again']")
        elif "Verification complete" in  text_body:
            print("Verification complete")
            break
        elif "Pick the image that is the correct way up" in  text_body:
            print("Pick the image that is the correct way up")
            for i in range(1, 7):
                driver.find_element(By.XPATH, f'/html/body/div/div/div[1]/div/div[3]/div/button[{i}]').screenshot(f'{i}.png')
            def score(p):
                img = cv2.resize(cv2.imread(p, 0), (200, 200))
                edges = cv2.Canny(img, 50, 150)
                lines = cv2.HoughLines(edges, 1, np.pi/180, 50)
                if lines is None: return 9999
                angles = [(l[0][1]*180/np.pi if l[0][1]*180/np.pi < 90 else l[0][1]*180/np.pi-180) for l in lines]
                return np.std(angles)
            best = min(range(1, 7), key=lambda i: score(f'{i}.png'))
            driver.find_element(By.XPATH, f'/html/body/div/div/div[1]/div/div[3]/div/button[{best}]').click()
    driver.switch_to.default_content()
    return check_pick
def cap_se(driver):
    try:
        stop_recaptcha = False
        hcaptcha = driver.execute_script("return document.evaluate(\"//iframe[@title='Main content of the hCaptcha challenge']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
        recaptcha = driver.execute_script("return document.evaluate(\"//iframe[@title='reCAPTCHA']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
        cloudflare = driver.execute_script("return document.evaluate(\"//iframe[@title='Widget containing a Cloudflare security challenge']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
        if cloudflare:
            print("cloudflare")
            driver.switch_to.frame(driver.find_element(By.XPATH, "//iframe[@title='Widget containing a Cloudflare security challenge']"))
            a("cl_xp@/html/body//div[1]/div/div[1]/div/label/input")
            time.sleep(5)
            a("en")
        if hcaptcha:
            print("hcaptcha")
            Widget_checkbox = driver.execute_script("return document.evaluate(\"//iframe[@title='Widget containing checkbox for hCaptcha security challenge']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
            if Widget_checkbox:
                driver.switch_to.frame(driver.find_element(By.XPATH, "//iframe[@title='Widget containing checkbox for hCaptcha security challenge']"))
                click_hcaptcha = driver.execute_script("""
                let el = document.evaluate("//div[@id='checkbox'][@tabindex='0']", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                if (el) { el.click(); return true; } else { return false; }
                """)
                driver.switch_to.default_content()
            driver.switch_to.frame(driver.find_element(By.XPATH, "//iframe[@title='Main content of the hCaptcha challenge']"))
            #driver.switch_to.frame(driver.execute_script("for(let f of document.getElementsByTagName('iframe')){try{let d=f.contentWindow.document;if(d.querySelector('#prompt-text,[aria-label=\"Challenge Image 3\"]'))return f;}catch(e){}}return null;"))
            code_start1 = driver.execute_script("return document.evaluate(\"//*[@aria-label='Challenge Image 3']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
            code_start2 = driver.execute_script("return document.evaluate(\"//*[text()='Please answer the following question with a single word, number, or phrase.']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")            
            text_body = driver.find_element("tag name", "body").text
            
            if "Please answer the following question" in text_body or code_start2:
                print("number, or phrase")
                mesage = driver.find_element(By.ID, "prompt-text").text
                send_massage = f"Please answer the following question with a single word, number, or phrase {mesage} please send Final Answer only"
                API_KEY = "sk-1b8ccd5f12b74efa962335cac260aa95"
                response = requests.post("https://api.deepseek.com/v1/chat/completions", headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}, json={"model": "deepseek-chat", "store": True, "messages": [{"role": "user", "content": send_massage}]}).json()
                haiku = response["choices"][0]["message"]["content"]
                print(haiku)
                Verify = driver.execute_script("return document.evaluate(\"//div[@aria-label='Verify Answers']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
                driver.find_element(By.CSS_SELECTOR, "[aria-label='Challenge Text Input']").send_keys(haiku)
                time.sleep(2)
                driver.find_element(By.CSS_SELECTOR, "[aria-label='Challenge Text Input']").send_keys(Keys.ENTER)
                if Verify:
                    print("Verify")
                    time.sleep(8)
            elif "Visual Challenge"  in text_body:
                print("Visual Challenge")
                driver.find_element(By.ID, "menu-info").click()
            elif code_start1:
                print("click Skip")
                driver.find_element(By.ID, "menu-info").click()
                #driver.find_element(By.CSS_SELECTOR, "[aria-label='Get information about hCaptcha and accessibility options.']").click()
                driver.find_element(By.ID, "text_challenge").click()
                time.sleep(3)
        elif recaptcha:
            print("recaptcha")
            
            time.sleep(3)
            captcha_frames = driver.find_elements(By.XPATH, ".//iframe[@title='reCAPTCHA']")
            for frame in captcha_frames:
                driver.switch_to.default_content()
                driver.switch_to.frame(frame)
                try:
                    anchor= driver.execute_script("return document.evaluate(\"//*[@id='recaptcha-anchor']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
                    code_start1 = driver.execute_script("return document.evaluate(\"//*[@class='rc-audiochallenge-tdownload-link']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
                    code_start2 = driver.execute_script("return document.evaluate(\"//*[text()='Try again later']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
                    code_start3 = driver.execute_script("return document.evaluate(\"//*[@id='recaptcha-audio-button']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
                    code_start4 = driver.execute_script("return document.evaluate(\"//*[@title='Get an audio challenge']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
                    if code_start2:
                        print("try agagen code_start2")
                    elif anchor:
                        driver.find_element(By.ID, 'recaptcha-anchor').click()
                        break
                    elif code_start2 or code_start1 or code_start3 or  code_start4:
                        print("recaptcha-anchor")
                        break
                except:
                    print("s")
                    driver.set_window_size(1920, 1400)
            driver.switch_to.default_content()
            for _ in range(20):
                time.sleep(1)
                two_minutes = driver.execute_script("return document.evaluate(\".//iframe[@title='recaptcha challenge expires in two minutes']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
                if two_minutes:
                    driver.switch_to.default_content()
                    driver.switch_to.frame(driver.find_element(By.XPATH, ".//iframe[@title='recaptcha challenge expires in two minutes']"))
                    code_start3 = driver.execute_script("return document.evaluate(\"//*[@id='recaptcha-audio-button']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
                    code_start4 = driver.execute_script("return document.evaluate(\"//*[@title='Get an audio challenge']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
                    if code_start3:
                        driver.find_element(By.ID, 'recaptcha-audio-button').click()
                    elif code_start4:
                        driver.find_element(By.XPATH, '//*[@title="Get an audio challenge"]').click()
                    else:
                        print("no audio")
                        break
                    for _ in range(15):
                        time.sleep(1)
                        code_start1 = driver.execute_script("return document.evaluate(\"//*[@class='rc-audiochallenge-tdownload-link']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
                        code_start2 = driver.execute_script("return document.evaluate(\"//*[text()='Try again later']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
                        if code_start1:
                            audio_link = driver.find_element(By.CLASS_NAME, 'rc-audiochallenge-tdownload-link')
                            audio_url = audio_link.get_attribute("href")
                            print(audio_url)
                            file_name = "audio.mp3"
                            response = requests.get(audio_url)
                            if response.status_code == 200:
                                with open(file_name, 'wb') as f:
                                    f.write(response.content)
                            src = "audio.mp3"
                            sound = AudioSegment.from_mp3(src)
                            sound.export("podcast.wav", format="wav")
                            file_path = os.path.join(os.getcwd(), "podcast.wav")
                            r = sr.Recognizer()
                            with sr.AudioFile(file_path) as source:
                                audio_text = r.record(source)
                            audio_text_code = r.recognize_google(audio_text)
                            driver.find_element(By.ID, 'audio-response').send_keys(audio_text_code)
                            time.sleep(3)
                            driver.find_element(By.ID, 'audio-response').send_keys(Keys.RETURN)
                            time.sleep(3)
                            break
                        elif code_start2:
                            print("try again")
                            stop_recaptcha = True
                            break


    except Exception as s:
        print("captions",s)
    driver.switch_to.default_content()
    return stop_recaptcha
def opencv_geetest(slice_url, bg_url, big, smail, totel, driver, bg_el):
    try:
        import cv2
    except:
        os.system("pip3 install opencv-python")
        import cv2     
    piece = cv2.imdecode(np.frombuffer(slice_url, np.uint8), cv2.IMREAD_UNCHANGED)
    bg = cv2.imdecode(np.frombuffer(bg_url, np.uint8), cv2.IMREAD_UNCHANGED)
    if piece is None or bg is None: return False
    if piece.shape[2] == 4: piece = cv2.cvtColor(piece, cv2.COLOR_BGRA2BGR)
    piece = cv2.GaussianBlur(piece, (5,5), 0)
    bg = cv2.GaussianBlur(bg, (5,5), 0)
    res = cv2.matchTemplate(cv2.Canny(bg,100,200), cv2.Canny(piece,100,200), cv2.TM_CCOEFF_NORMED)
    x_raw = cv2.minMaxLoc(res)[3][0]
    shot = cv2.imdecode(np.frombuffer(bg_el.screenshot_as_png, np.uint8), 1)
    scale = shot.shape[1] / bg.shape[1]
    track_el = [el for el in driver.find_elements(By.CSS_SELECTOR, ".geetest_track") if el.is_displayed()][0]
    offset = track_el.location["x"] - bg_el.location["x"]
    dist = int(x_raw * scale - offset - piece.shape[1]//2 + totel)
    dist = max(min(dist, big), smail)
    return dist
def geetest(driver):
    try:
        slice_el = [el for el in driver.find_elements(By.CSS_SELECTOR, ".geetest_slice_bg") if el.is_displayed()][0]
        bg_el = [el for el in driver.find_elements(By.CSS_SELECTOR, ".geetest_bg") if el.is_displayed()][0]
        slice_url = requests.get(re.search(r'url\("(.*?)"\)', slice_el.get_attribute("style")).group(1), timeout=10).content
        bg_url = requests.get(re.search(r'url\("(.*?)"\)', bg_el.get_attribute("style")).group(1), timeout=10).content
        dist = opencv_geetest(slice_url, bg_url, 220, 30, 37, driver, bg_el)
        print("distance =", dist)
        slider = [el for el in driver.find_elements(By.CSS_SELECTOR, "[class*='geetest_btn']") if el.is_displayed()][0]
        act = ActionChains(driver)
        act.click_and_hold(slider).perform()
        moved = 0
        while moved < dist:
            step = random.randint(3, 7)
            if moved + step > dist: step = dist - moved
            act.move_by_offset(step, random.randint(-1,1)).perform()
            moved += step
            time.sleep(random.uniform(0.01, 0.04))
        time.sleep(0.2)
        act.release().perform()
        return True
    except Exception as e:
        print("geetest error:", e)
        return False
def sign(driver):
    canvas = driver.find_element(By.TAG_NAME, "canvas")
    location = canvas.location_once_scrolled_into_view
    size = canvas.size
    x_center = size['width'] // 2
    y_center = size['height'] // 2
    action = ActionChains(driver)
    action.move_to_element_with_offset(canvas, 5, 5)
    action.click_and_hold()
    for _ in range(30):
        dx = random.randint(-3, 3)
        dy = random.randint(-3, 3)
        action.move_by_offset(dx, dy)
        time.sleep(0.015) 
    action.release()
    action.perform()

def gpt_api(massage,file,api_model):
    try:
        import openai
    except:
        os.system("pip3 install openai")
        import openai   
  
    openai.api_key = "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"
    with open(file, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    response = openai.chat.completions.create(model=api_model,messages=[{"role": "user","content": [{"type": "text", "text": massage},{"type": "image_url","image_url": {"url": f"data:image/png;base64,{base64_image}"},},],}],max_tokens=10,)
    return response.choices[0].message.content
def cap_ph(file):
    with open(file, 'rb') as f:
        r = requests.post('http://2captcha.com/in.php', files={'file': f}, data={'key': "b595d3040f736c6e7a5108ee7745f83a", 'method': 'post'})
    if 'OK|' not in r.text: return None
    cid = r.text.split('|')[1]
    for _ in range(20):
        time.sleep(5)
        res = requests.get(f'http://2captcha.com/res.php?key=b595d3040f736c6e7a5108ee7745f83a&action=get&id={cid}').text
        if 'OK|' in res:
            t = res.split('|')[1]
            pairs = [t[i:i+2] for i in range(0, len(t)-(len(t)%2), 2)]
            return pairs ,max(pairs, key=int) 
