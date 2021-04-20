import os
import time
import requests
from selenium import webdriver


def fetch_image_urls(query: str, max_links_to_fetch: int, wd: webdriver, sleep_between_interactions: int = 1):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)

        # build the google query

    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

    # https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q=dog&oq=dog&gs_l=img
    # load the page
    wd.get(search_url.format(q=query))#it will open the images in  the previously opened url, q is the placeholder in the url

    image_urls = set()
    image_count = 0
    results_start = 0
    while image_count < max_links_to_fetch:
        scroll_to_end(wd) #it will make scroll the page, there is no href link

        # get all image thumbnail results
        thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd") #that is tag name, JS name
        number_results = len(thumbnail_results) #unless and untill we click on the image it wont generate href link, hence we have to select jsname first
        #intially it will give the binary format result of the image

        print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")

        for img in thumbnail_results[results_start:number_results]:
            # try to click every thumbnail such that we can get the real image behind it
            try:
                img.click() #it will try to click on the image of the image
                time.sleep(sleep_between_interactions)
            except Exception:
                continue

            # extract image urls
            actual_images = wd.find_elements_by_css_selector('img.n3VNCb')
            for actual_image in actual_images:
                if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                    image_urls.add(actual_image.get_attribute('src'))#clhecking the is image holding the valid http url in the link we got
#image url is a set beacause to hold only unique values
            image_count = len(image_urls)  #just getting the IMAGE url,not yet downloaded

            if len(image_urls) >= max_links_to_fetch: #checking whether it has required number of urls or not, if not go again
                print(f"Found: {len(image_urls)} image links, done!")
                break
        else:
            print("Found:", len(image_urls), "image links, looking for more ...")
            time.sleep(30)
            return
            load_more_button = wd.find_element_by_css_selector(".mye4qd")
            if load_more_button:
                wd.execute_script("document.querySelector('.mye4qd').click();")

        # move the result startpoint further down
        results_start = len(thumbnail_results)

    return image_urls


def persist_image(folder_path:str,url:str, counter): #downlod the image for me
    try:
        image_content = requests.get(url).content #got thr image in byte format

    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")

    try:#convert byte to a image
        f = open(os.path.join(folder_path, 'jpg' + "_" + str(counter) + ".jpg"), 'wb') #converting byte to image
        f.write(image_content)
        f.close()
        print(f"SUCCESS - saved {url} - as {folder_path}")
    except Exception as e:
        print(f"ERROR - Could not save {url} - {e}")

#target path we can change the destination file location
def search_and_download(search_term: str, driver_path: str, target_path='./images', number_images=5):
    target_folder = os.path.join(target_path, '_'.join(search_term.lower().split(' ')))
#'_'.join returns the string---->"iron man" as "iron_man", os dealing with folder structure, path,
    #target_folder=target_path +'/'+('_'.join (search_term.lower().split(' '))) -----> will give the sam
#but its not preferred as its not work with ubuntu and mac if its originally created in windows because writing a path in windows is differnt than both of the latter
    #but os recognises automatically and form the path automatically
    #you can change the default folder images to any folder by giving here
    if not os.path.exists(target_folder):#right now there  is no library as dog, we have to create, if not it will create
        os.makedirs(target_folder)

    with webdriver.Chrome(executable_path=driver_path) as wd: #will just open the web browser
        res = fetch_image_urls(search_term, number_images, wd=wd, sleep_between_interactions=0.5) #0.5 milli seconds for next hit
          #now get inside the function
    counter = 0
    for elem in res:
        persist_image(target_folder, elem, counter)#this will download image for me
        counter += 1

# pip install -r requirements.txt

# My chrome Version 85.0.4183.102
# My Firefox Version 80.0.1 (64-bit)

# How to execute this code
# Step 1 : pip install selenium, pillow, requests
# Step 2 : make sure you have chrome/Mozilla installed on your machine
# Step 3 : Check your chrome version ( go to three dot then help then about google chrome )87.0.4280.88
# Step 4 : Download the same chrome driver from here  " https://chromedriver.storage.googleapis.com/index.html "
# Step 5 : put it inside the same folder of this code #unzip the driver file inside the project folder
#can store these files with mongodb or any blog, chrome driver version should be same or nearer to the chrome browser version, its not mandatory, but its easy

DRIVER_PATH = './chromedriver.exe'
search_term = 'iron man'
#    num of images you can pass it from here  by default it's 10 if you are not passing, selenium is testing and automation tool
number_images = 5
search_and_download(search_term=search_term, driver_path=DRIVER_PATH, number_images = number_images)


#Version 88.0.4324.150 (Official Build) (64-bit)

#tags in HTML are fixed one and the values will varies across the websites, like jsname is the tag, value is the Q4LuWd
#this code will not download >200 images